use std::fs;
use std::io::Read;
use std::path::{Path, PathBuf};

use clap::Parser;
use flate2::read::GzDecoder;
use serde::Serialize;
use serde_json::{Deserializer, Map, Value};

const GZIP_MAGIC: [u8; 2] = [0x1f, 0x8b];
const INTERNAL_SCHEMES: &[&str] = &["about", "chrome", "edge", "file", "microsoft-edge"];
const NESTED_JSON_HINTS: &[&str] = &[
    "\"content\"",
    "\"subdirectories\"",
    "\"tabstripmodel\"",
    "\"favorites\"",
    "\"webcontents\"",
    "\"navigationStack\"",
];
const MAX_PAYLOAD_BYTES: usize = 64 * 1024 * 1024;

#[derive(Parser)]
struct Args {
    #[arg(short, long)]
    input: PathBuf,
    #[arg(long)]
    pretty: bool,
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
struct LinkRecord {
    url: String,
    title: String,
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
struct ExportRow {
    source: String,
    url: String,
    title: String,
}

#[derive(Debug, Clone, Serialize)]
struct Exports {
    both: Vec<ExportRow>,
    tabs: Vec<ExportRow>,
    favorites: Vec<ExportRow>,
    exclude_internal: Vec<ExportRow>,
}

#[derive(Debug, Clone, Serialize)]
struct FileOutput {
    workspace_file: String,
    status: String,
    tabs: Vec<LinkRecord>,
    favorites: Vec<LinkRecord>,
    exports: Exports,
}

#[derive(Debug, Clone, Serialize)]
struct RunOutput {
    files: Vec<FileOutput>,
}

fn empty_exports() -> Exports {
    Exports {
        both: Vec::new(),
        tabs: Vec::new(),
        favorites: Vec::new(),
        exclude_internal: Vec::new(),
    }
}

fn iter_edge_files(input: &Path) -> Result<Vec<PathBuf>, String> {
    if input.is_file() {
        return Ok(vec![input.to_path_buf()]);
    }
    if input.is_dir() {
        let mut files = Vec::new();
        let entries = fs::read_dir(input).map_err(|err| err.to_string())?;
        for entry in entries {
            let entry = entry.map_err(|err| err.to_string())?;
            let path = entry.path();
            if path.extension().and_then(|value| value.to_str()) == Some("edge") {
                files.push(path);
            }
        }
        files.sort();
        return Ok(files);
    }
    Err(format!("Input path not found: {}", input.display()))
}

fn scan_gzip_payloads(data: &[u8]) -> (bool, Vec<Vec<u8>>) {
    let mut had_gzip_magic = false;
    let mut payloads: Vec<Vec<u8>> = Vec::new();

    for index in 0..data.len().saturating_sub(1) {
        if data[index..index + 2] != GZIP_MAGIC {
            continue;
        }
        had_gzip_magic = true;
        let mut decoder = GzDecoder::new(&data[index..]);
        let mut out = Vec::new();
        let limit = u64::try_from(MAX_PAYLOAD_BYTES + 1).unwrap();
        if decoder.by_ref().take(limit).read_to_end(&mut out).is_err()
            || out.is_empty()
            || out.len() > MAX_PAYLOAD_BYTES
        {
            continue;
        }
        if !payloads.iter().any(|existing| existing == &out) {
            payloads.push(out);
        }
    }

    (had_gzip_magic, payloads)
}

fn clean_json_text(payload: &[u8]) -> String {
    let translated: Vec<u8> = payload
        .iter()
        .map(|byte| if *byte < 0x20 { b' ' } else { *byte })
        .collect();
    String::from_utf8_lossy(&translated).into_owned()
}

fn iter_json_objects(text: &str) -> Vec<Value> {
    let mut objects = Vec::new();
    let mut idx = 0;
    while idx < text.len() {
        let next_object = text[idx..].find('{').map(|found| idx + found);
        let next_array = text[idx..].find('[').map(|found| idx + found);
        let Some(start) = (match (next_object, next_array) {
            (Some(left), Some(right)) => Some(left.min(right)),
            (Some(left), None) => Some(left),
            (None, Some(right)) => Some(right),
            (None, None) => None,
        }) else {
            break;
        };

        let slice = &text[start..];
        let mut stream = Deserializer::from_str(slice).into_iter::<Value>();
        match stream.next() {
            Some(Ok(value)) => {
                let consumed = stream.byte_offset();
                if consumed == 0 {
                    idx = start + 1;
                } else {
                    idx = start + consumed;
                    objects.push(value);
                }
            }
            _ => idx = start + 1,
        }
    }
    objects
}

fn collect_content_objects(root: &Value) -> Vec<Value> {
    let mut found = Vec::new();
    let mut stack = vec![root.clone()];

    while let Some(current) = stack.pop() {
        match current {
            Value::Object(map) => {
                if let Some(content) = map.get("content") {
                    if content.is_object() {
                        found.push(content.clone());
                    }
                }
                for value in map.values().cloned().collect::<Vec<_>>().into_iter().rev() {
                    if matches!(value, Value::Object(_) | Value::Array(_) | Value::String(_)) {
                        stack.push(value);
                    }
                }
            }
            Value::Array(items) => {
                for value in items.into_iter().rev() {
                    if matches!(value, Value::Object(_) | Value::Array(_) | Value::String(_)) {
                        stack.push(value);
                    }
                }
            }
            Value::String(text) => {
                if !(text.contains('{') || text.contains('[')) {
                    continue;
                }
                let candidate = text.trim();
                if !(candidate.starts_with('{') || candidate.starts_with('[')) {
                    continue;
                }
                if !NESTED_JSON_HINTS.iter().any(|hint| candidate.contains(hint)) {
                    continue;
                }
                if let Ok(nested) = serde_json::from_str::<Value>(candidate) {
                    stack.push(nested);
                }
            }
            _ => {}
        }
    }

    found
}

fn typed_value<'a>(value: &'a Value) -> &'a Value {
    value
        .as_object()
        .and_then(|object| object.get("value"))
        .unwrap_or(value)
}

fn as_object<'a>(value: &'a Value) -> Option<&'a Map<String, Value>> {
    value.as_object()
}

fn get_object_path<'a>(value: &'a Value, path: &[&str]) -> Option<&'a Map<String, Value>> {
    let mut current = value;
    for key in path {
        current = as_object(current)?.get(*key)?;
    }
    as_object(current)
}

fn value_to_string(value: &Value) -> Option<String> {
    match typed_value(value) {
        Value::String(text) => Some(text.clone()),
        Value::Number(number) => Some(number.to_string()),
        _ => None,
    }
}

fn value_to_index(value: &Value) -> Option<String> {
    match typed_value(value) {
        Value::Number(number) => Some(number.to_string()),
        Value::String(text) => Some(text.clone()),
        _ => None,
    }
}

fn has_workspace_markers(content: &Value) -> bool {
    get_object_path(content, &["subdirectories"]).map_or(false, |subdirs| {
        subdirs.contains_key("tabstripmodel") || subdirs.contains_key("favorites")
    })
}

fn extract_tabs_from_content(content: &Value) -> Vec<LinkRecord> {
    let Some(webcontents) = get_object_path(
        content,
        &["subdirectories", "tabstripmodel", "subdirectories", "webcontents", "subdirectories"],
    ) else {
        return Vec::new();
    };

    let mut links = Vec::new();
    for tab_data in webcontents.values() {
        let Some(tab_object) = as_object(tab_data) else {
            continue;
        };
        let current_index = tab_object
            .get("storage")
            .and_then(as_object)
            .and_then(|storage| storage.get("currentNavigationIndex"))
            .and_then(value_to_index);
        let Some(current_key) = current_index else {
            continue;
        };

        let Some(nav_stack) = get_object_path(
            tab_data,
            &["subdirectories", "navigationStack", "subdirectories"],
        ) else {
            continue;
        };

        let entry = nav_stack.get(&current_key).or_else(|| {
            nav_stack
                .keys()
                .filter_map(|key| key.parse::<u32>().ok().map(|value| (value, key)))
                .max_by_key(|(value, _)| *value)
                .and_then(|(_, key)| nav_stack.get(key))
        });
        let Some(entry_storage) = entry.and_then(|value| value.get("storage")).and_then(as_object) else {
            continue;
        };

        let mut url = None;
        for key in ["virtualUrl", "originalRequestUrl", "url"] {
            if let Some(value) = entry_storage.get(key).and_then(value_to_string) {
                if !value.is_empty() {
                    url = Some(value);
                    break;
                }
            }
        }
        let Some(url) = url else {
            continue;
        };
        let title = entry_storage
            .get("title")
            .and_then(value_to_string)
            .unwrap_or_default();
        links.push(LinkRecord { url, title });
    }

    links
}

fn extract_favorites_from_content(content: &Value) -> Vec<LinkRecord> {
    let Some(storage) = get_object_path(content, &["subdirectories", "favorites", "storage"]) else {
        return Vec::new();
    };

    let mut links = Vec::new();
    for entry in storage.values() {
        let Some(node) = as_object(typed_value(entry)) else {
            continue;
        };
        if node.get("nodeType").and_then(|value| value.as_str()) != Some("1") {
            continue;
        }
        let Some(url) = node.get("url").and_then(|value| value.as_str()).map(str::to_owned) else {
            continue;
        };
        if url.is_empty() {
            continue;
        }
        let title = node
            .get("title")
            .and_then(|value| value.as_str())
            .unwrap_or_default()
            .to_owned();
        links.push(LinkRecord { url, title });
    }

    links
}

fn extract_workspace_data(payloads: &[Vec<u8>]) -> (usize, usize, Vec<LinkRecord>, Vec<LinkRecord>) {
    let mut json_objects_found = 0;
    let mut workspace_markers_found = 0;
    let mut tabs = Vec::new();
    let mut favorites = Vec::new();

    for payload in payloads {
        let clean = clean_json_text(payload);
        for object in iter_json_objects(&clean) {
            json_objects_found += 1;
            for content in collect_content_objects(&object) {
                if has_workspace_markers(&content) {
                    workspace_markers_found += 1;
                }
                tabs.extend(extract_tabs_from_content(&content));
                favorites.extend(extract_favorites_from_content(&content));
            }
        }
    }

    (json_objects_found, workspace_markers_found, tabs, favorites)
}

fn filter_links(links: &[LinkRecord], exclude_schemes: &[&str]) -> Vec<LinkRecord> {
    links
        .iter()
        .filter(|link| {
            let scheme = link.url.split(':').next().unwrap_or_default().to_ascii_lowercase();
            !exclude_schemes.contains(&scheme.as_str())
        })
        .cloned()
        .collect()
}

fn ordered_unique(links: &[LinkRecord]) -> Vec<LinkRecord> {
    let mut unique: Vec<LinkRecord> = Vec::new();
    for link in links {
        if let Some(existing) = unique.iter_mut().find(|value| value.url == link.url) {
            if existing.title.is_empty() && !link.title.is_empty() {
                existing.title = link.title.clone();
            }
        } else {
            unique.push(link.clone());
        }
    }
    unique
}

fn build_exports(tabs: &[LinkRecord], favorites: &[LinkRecord], mode: &str, exclude_schemes: &[&str]) -> Vec<ExportRow> {
    let filtered_tabs = filter_links(tabs, exclude_schemes);
    let filtered_favorites = filter_links(favorites, exclude_schemes);

    let tab_rows = if matches!(mode, "both" | "tabs") {
        ordered_unique(&filtered_tabs)
    } else {
        Vec::new()
    };
    let favorite_rows = if matches!(mode, "both" | "favorites") {
        ordered_unique(&filtered_favorites)
    } else {
        Vec::new()
    };

    let mut combined = Vec::new();
    for favorite in favorite_rows {
        combined.push(ExportRow {
            source: "favorite".to_owned(),
            url: favorite.url,
            title: favorite.title,
        });
    }
    for tab in tab_rows {
        if combined.iter().any(|row| row.url == tab.url) {
            continue;
        }
        combined.push(ExportRow {
            source: "tab".to_owned(),
            url: tab.url,
            title: tab.title,
        });
    }
    combined
}

fn process_file(path: &Path) -> FileOutput {
    let workspace_file = path.file_name().unwrap().to_string_lossy().into_owned();
    let data = match fs::read(path) {
        Ok(data) => data,
        Err(_) => {
            return FileOutput {
                workspace_file,
                status: "read_error".to_owned(),
                tabs: Vec::new(),
                favorites: Vec::new(),
                exports: empty_exports(),
            };
        }
    };
    let (had_magic, payloads) = scan_gzip_payloads(&data);
    if !had_magic {
        return FileOutput {
            workspace_file,
            status: "not_workspace".to_owned(),
            tabs: Vec::new(),
            favorites: Vec::new(),
            exports: empty_exports(),
        };
    }
    if payloads.is_empty() {
        return FileOutput {
            workspace_file,
            status: "parse_error".to_owned(),
            tabs: Vec::new(),
            favorites: Vec::new(),
            exports: empty_exports(),
        };
    }

    let (json_objects_found, workspace_markers_found, tabs, favorites) = extract_workspace_data(&payloads);
    let status = if json_objects_found == 0 {
        "parse_error"
    } else if workspace_markers_found == 0 {
        "not_workspace"
    } else if tabs.is_empty() && favorites.is_empty() {
        "no_links"
    } else {
        "ok"
    };

    FileOutput {
        workspace_file,
        status: status.to_owned(),
        tabs: tabs.clone(),
        favorites: favorites.clone(),
        exports: Exports {
            both: build_exports(&tabs, &favorites, "both", &[]),
            tabs: build_exports(&tabs, &favorites, "tabs", &[]),
            favorites: build_exports(&tabs, &favorites, "favorites", &[]),
            exclude_internal: build_exports(&tabs, &favorites, "both", INTERNAL_SCHEMES),
        },
    }
}

fn main() -> Result<(), String> {
    let args = Args::parse();
    let files = iter_edge_files(&args.input)?;
    let mut outputs = Vec::new();
    for path in files {
        outputs.push(process_file(&path));
    }
    let payload = RunOutput { files: outputs };
    let rendered = if args.pretty {
        serde_json::to_string_pretty(&payload)
    } else {
        serde_json::to_string(&payload)
    }
    .map_err(|err| err.to_string())?;
    println!("{rendered}");
    Ok(())
}
