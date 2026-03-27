# Flutter Desktop Shell

This directory contains the Flutter desktop UI track for issue `#21`.
It is a cross-platform shell over the Python extraction and reporting backend.

## Runtime contract

The app prefers a packaged sibling backend executable for release-style runs:

- Windows: `edge-workspace-links-gui-backend.exe`
- Linux: `edge-workspace-links-gui-backend`
- macOS: `edge_workspace_links_ui.app/Contents/MacOS/edge-workspace-links-gui-backend`

If that packaged backend is absent, the app falls back to launching `edge_workspace_links_app.gui_backend` from the repo checkout for local development.

## Local development

From the repository root:

```bash
python -m pip install -e .[dev]
cd gui/flutter_app
flutter pub get
flutter analyze
flutter test
flutter run -d windows
```

## Release-style validation

Build the packaged GUI backend on the same host OS that will build the Flutter desktop bundle:

```bash
python -m PyInstaller --noconfirm edge-workspace-links-gui-backend.spec
cd gui/flutter_app
flutter build windows
flutter build linux
flutter build macos
```

Use only the platform build command that matches the current host OS.
GitHub Actions provides native Windows, Linux, and macOS verification for the packaged backend and bundle layout.
