import Cocoa
import FlutterMacOS

class MainFlutterWindow: NSWindow {
  override func awakeFromNib() {
    let flutterViewController = FlutterViewController()
    let windowFrame = self.frame
    self.contentViewController = flutterViewController
    self.setFrame(windowFrame, display: true)

    let registrar = flutterViewController.registrar(forPlugin: "WorkspacePathPicker")
    let pathPickerChannel = FlutterMethodChannel(
      name: "edge_workspace_links_ui/path_picker",
      binaryMessenger: registrar.messenger)
    pathPickerChannel.setMethodCallHandler { [weak self] call, result in
      guard let self else {
        result(
          FlutterError(
            code: "picker_unavailable",
            message: "The native path picker is not attached to a window.",
            details: nil))
        return
      }

      switch call.method {
      case "pickDirectory":
        result(self.showOpenPanel(chooseDirectories: true))
      case "pickWorkspaceFile":
        result(self.showOpenPanel(chooseDirectories: false))
      default:
        result(FlutterMethodNotImplemented)
      }
    }

    RegisterGeneratedPlugins(registry: flutterViewController)

    super.awakeFromNib()
  }

  private func showOpenPanel(chooseDirectories: Bool) -> String? {
    let panel = NSOpenPanel()
    panel.title = chooseDirectories ? "Select Edge Workspace folder" : "Select Edge Workspace file"
    panel.prompt = "Select"
    panel.allowsMultipleSelection = false
    panel.canChooseDirectories = chooseDirectories
    panel.canChooseFiles = !chooseDirectories
    panel.canCreateDirectories = false
    panel.resolvesAliases = true

    if !chooseDirectories {
      panel.allowedFileTypes = ["edge"]
    }

    return panel.runModal() == .OK ? panel.url?.path : nil
  }
}
