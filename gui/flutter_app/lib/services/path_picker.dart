import 'package:flutter/services.dart';

class PathPicker {
  const PathPicker();

  static const MethodChannel _channel = MethodChannel(
    'edge_workspace_links_ui/path_picker',
  );

  Future<String?> pickDirectory() => _invoke('pickDirectory');

  Future<String?> pickWorkspaceFile() => _invoke('pickWorkspaceFile');

  Future<String?> _invoke(String method) async {
    try {
      return await _channel.invokeMethod<String>(method);
    } on PlatformException catch (error) {
      throw PathPickerException(
        error.message ??
            'Native path selection is unavailable in this desktop build.',
      );
    } on MissingPluginException {
      throw const PathPickerException(
        'Native path selection is unavailable in this desktop build.',
      );
    }
  }
}

class PathPickerException implements Exception {
  const PathPickerException(this.message);

  final String message;

  @override
  String toString() => message;
}
