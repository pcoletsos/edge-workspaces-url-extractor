#include "flutter_window.h"

#include <flutter/method_channel.h>
#include <flutter/standard_method_codec.h>
#include <shobjidl.h>
#include <optional>
#include <sstream>
#include <string>
#include <wrl/client.h>

#include "flutter/generated_plugin_registrant.h"

namespace {

constexpr char kPathPickerChannel[] = "edge_workspace_links_ui/path_picker";
constexpr char kPickDirectoryMethod[] = "pickDirectory";
constexpr char kPickWorkspaceFileMethod[] = "pickWorkspaceFile";

struct PathDialogResult {
  std::optional<std::string> path;
  std::string error;
};

std::string HResultToMessage(const std::string& action, HRESULT hr) {
  std::ostringstream stream;
  stream << action << " failed (0x" << std::hex << std::uppercase
         << static_cast<unsigned long>(hr) << ")";
  return stream.str();
}

std::string WideToUtf8(const std::wstring& value) {
  if (value.empty()) {
    return {};
  }

  const int required = WideCharToMultiByte(
      CP_UTF8, 0, value.c_str(), static_cast<int>(value.size()), nullptr, 0,
      nullptr, nullptr);
  std::string result(required, '\0');
  WideCharToMultiByte(CP_UTF8, 0, value.c_str(), static_cast<int>(value.size()),
                      result.data(), required, nullptr, nullptr);
  return result;
}

PathDialogResult ShowPathDialog(HWND owner, bool pick_directory) {
  PathDialogResult result;

  Microsoft::WRL::ComPtr<IFileOpenDialog> dialog;
  HRESULT hr = CoCreateInstance(CLSID_FileOpenDialog, nullptr,
                                CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&dialog));
  if (FAILED(hr)) {
    result.error = HResultToMessage("Creating the path picker", hr);
    return result;
  }

  DWORD options = 0;
  hr = dialog->GetOptions(&options);
  if (FAILED(hr)) {
    result.error = HResultToMessage("Configuring the path picker", hr);
    return result;
  }

  options |= FOS_FORCEFILESYSTEM | FOS_PATHMUSTEXIST;
  options |= pick_directory ? FOS_PICKFOLDERS : FOS_FILEMUSTEXIST;
  dialog->SetOptions(options);
  dialog->SetTitle(pick_directory ? L"Select Edge Workspace folder"
                                  : L"Select Edge Workspace file");

  if (!pick_directory) {
    COMDLG_FILTERSPEC filters[] = {
        {L"Edge Workspace files", L"*.edge"},
        {L"All files", L"*.*"},
    };
    dialog->SetFileTypes(2, filters);
    dialog->SetFileTypeIndex(1);
  }

  hr = dialog->Show(owner);
  if (hr == HRESULT_FROM_WIN32(ERROR_CANCELLED)) {
    return {};
  }
  if (FAILED(hr)) {
    result.error = HResultToMessage("Opening the path picker", hr);
    return result;
  }

  Microsoft::WRL::ComPtr<IShellItem> item;
  hr = dialog->GetResult(&item);
  if (FAILED(hr)) {
    result.error = HResultToMessage("Reading the selected path", hr);
    return result;
  }

  PWSTR raw_path = nullptr;
  hr = item->GetDisplayName(SIGDN_FILESYSPATH, &raw_path);
  if (FAILED(hr)) {
    result.error = HResultToMessage("Resolving the selected path", hr);
    return result;
  }

  std::wstring selected_path(raw_path);
  CoTaskMemFree(raw_path);
  result.path = WideToUtf8(selected_path);
  return result;
}

}  // namespace

FlutterWindow::FlutterWindow(const flutter::DartProject& project)
    : project_(project) {}

FlutterWindow::~FlutterWindow() {}

bool FlutterWindow::OnCreate() {
  if (!Win32Window::OnCreate()) {
    return false;
  }

  RECT frame = GetClientArea();

  // The size here must match the window dimensions to avoid unnecessary surface
  // creation / destruction in the startup path.
  flutter_controller_ = std::make_unique<flutter::FlutterViewController>(
      frame.right - frame.left, frame.bottom - frame.top, project_);
  // Ensure that basic setup of the controller was successful.
  if (!flutter_controller_->engine() || !flutter_controller_->view()) {
    return false;
  }
  RegisterPlugins(flutter_controller_->engine());

  path_picker_channel_ =
      std::make_unique<flutter::MethodChannel<flutter::EncodableValue>>(
          flutter_controller_->engine()->messenger(), kPathPickerChannel,
          &flutter::StandardMethodCodec::GetInstance());
  path_picker_channel_->SetMethodCallHandler(
      [this](const flutter::MethodCall<flutter::EncodableValue>& call,
             std::unique_ptr<flutter::MethodResult<flutter::EncodableValue>>
                 result) {
        const std::string& method = call.method_name();
        if (method != kPickDirectoryMethod &&
            method != kPickWorkspaceFileMethod) {
          result->NotImplemented();
          return;
        }

        const PathDialogResult selection =
            ShowPathDialog(GetHandle(), method == kPickDirectoryMethod);
        if (!selection.error.empty()) {
          result->Error("picker_unavailable", selection.error);
          return;
        }

        if (!selection.path.has_value()) {
          result->Success(flutter::EncodableValue());
          return;
        }

        result->Success(flutter::EncodableValue(*selection.path));
      });
  SetChildContent(flutter_controller_->view()->GetNativeWindow());

  flutter_controller_->engine()->SetNextFrameCallback([&]() {
    this->Show();
  });

  // Flutter can complete the first frame before the "show window" callback is
  // registered. The following call ensures a frame is pending to ensure the
  // window is shown. It is a no-op if the first frame hasn't completed yet.
  flutter_controller_->ForceRedraw();

  return true;
}

void FlutterWindow::OnDestroy() {
  path_picker_channel_ = nullptr;
  if (flutter_controller_) {
    flutter_controller_ = nullptr;
  }

  Win32Window::OnDestroy();
}

LRESULT
FlutterWindow::MessageHandler(HWND hwnd, UINT const message,
                              WPARAM const wparam,
                              LPARAM const lparam) noexcept {
  // Give Flutter, including plugins, an opportunity to handle window messages.
  if (flutter_controller_) {
    std::optional<LRESULT> result =
        flutter_controller_->HandleTopLevelWindowProc(hwnd, message, wparam,
                                                      lparam);
    if (result) {
      return *result;
    }
  }

  switch (message) {
    case WM_FONTCHANGE:
      if (flutter_controller_) {
        flutter_controller_->engine()->ReloadSystemFonts();
      }
      break;
  }

  return Win32Window::MessageHandler(hwnd, message, wparam, lparam);
}
