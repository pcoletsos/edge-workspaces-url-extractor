# Flutter Desktop UI Evaluation

## Decision

Issue `#21` will target a Flutter desktop frontend first.

Reasoning:

- the goal is a super modern interface with one design language across Windows, macOS, and Linux
- Flutter is the preferred path when visual consistency matters more than keeping the GUI in the same language as the backend
- the current Python extractor can remain the backend initially so the UI work does not force an immediate parser rewrite

## Current repository direction

The extractor and reporting engine stay in Python for the first desktop UI milestone.

The Flutter app should call a stable machine-readable backend entry point rather than parsing human CLI stderr output.
That backend contract now lives in `src/edge_workspace_links_app/gui_backend.py`.

Its responsibilities are:

- accept the same input, mode, sort, and filter choices the GUI needs
- emit JSON to stdout for both success and failure paths
- keep per-file statuses and summary metrics aligned with the shipped CLI

## Backend contract

The GUI backend returns a JSON object with this shape:

```json
{
  "status": "ok",
  "code": "ok",
  "message": "Processed 1 workspace file(s) and exported 2 link(s).",
  "notices": [],
  "result": {
    "links": [],
    "summary": {},
    "files": []
  }
}
```

Failure cases still return JSON, for example `input_not_found`, `no_edge_files`, or
`no_successful_workspaces`, so the GUI can render explicit user-facing states without scraping stderr.

## Current Flutter prototype

The Flutter SDK was installed locally on March 26, 2026 and a desktop app was scaffolded under `gui/flutter_app/`.

Current structure:

- `gui/flutter_app/lib/main.dart`
- `gui/flutter_app/lib/app_shell.dart`
- `gui/flutter_app/lib/features/run_analysis/`
- `gui/flutter_app/lib/services/backend_runner.dart`
- `gui/flutter_app/lib/models/analysis_response.dart`

The current prototype flow is:

1. choose a workspace file or directory with the native desktop picker, or edit the path manually
2. choose mode and basic filters
3. run extraction
4. show per-file notices and summary metrics
5. preview exported links

## Current native path selection

The desktop shell now exposes native path selection on Windows, macOS, and Linux without relying on Flutter picker plugins.

Reasoning:

- the UI still needs first-class path navigation on every desktop OS
- Flutter plugin-based pickers created avoidable setup friction on this Windows machine
- a small platform-channel layer in each desktop runner avoids that tooling dependency while keeping native dialogs

## Desktop packaging contract

The Flutter desktop shell now resolves a packaged sibling backend executable first on all three supported desktop targets:

- Windows: `edge-workspace-links-gui-backend.exe`
- Linux: `edge-workspace-links-gui-backend`
- macOS: `edge_workspace_links_ui.app/Contents/MacOS/edge-workspace-links-gui-backend`

The Python module path remains intentionally available only as a development fallback when the packaged backend is absent.
That keeps local iteration simple while making release-style bundles self-contained.

## Validation policy

Local validation on this Windows host covers:

- Python regression and GUI backend smoke checks
- packaged GUI backend build and smoke on Windows
- `flutter analyze`, `flutter test`, and `flutter build windows`

OS-native verification for Linux and macOS is handled in GitHub Actions:

- build the GUI backend with PyInstaller on the matching host
- build the Flutter desktop bundle on the matching host
- verify the bundled backend exists at the expected release path
- smoke the bundled backend artifact directly from the built desktop output

Manual validation is still required for interactive GUI behavior, native dialog UX, and release signing/notarization concerns.
