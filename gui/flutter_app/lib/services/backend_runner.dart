import 'dart:convert';
import 'dart:io';

import '../models/analysis_response.dart';

enum AnalysisMode {
  both('both'),
  tabs('tabs'),
  favorites('favorites');

  const AnalysisMode(this.value);

  final String value;
}

class BackendRunner {
  const BackendRunner();

  Future<AnalysisResponse> run({
    required String inputPath,
    required AnalysisMode mode,
    required bool excludeInternal,
    required bool sort,
  }) async {
    final repoRoot = _resolveRepoRoot();
    final pythonPath = _joinPaths([
      _joinSegments([repoRoot, 'src']),
      Platform.environment['PYTHONPATH'],
    ]);

    final candidates = <_PythonCommand>[
      if (Platform.isWindows) const _PythonCommand('py', ['-3']),
      const _PythonCommand('python3', []),
      const _PythonCommand('python', []),
    ];

    final backendArgs = [
      '-m',
      'edge_workspace_links_app.gui_backend',
      '--input',
      inputPath,
      '--mode',
      mode.value,
      if (excludeInternal) '--exclude-internal',
      if (sort) '--sort',
    ];

    ProcessResult? lastFailure;
    Object? lastError;

    for (final candidate in candidates) {
      try {
        final result = await Process.run(
          candidate.executable,
          [...candidate.leadingArgs, ...backendArgs],
          environment: {...Platform.environment, 'PYTHONPATH': pythonPath},
          runInShell: Platform.isWindows,
        );

        if (result.stdout.toString().trim().isEmpty) {
          lastFailure = result;
          continue;
        }

        final payload =
            json.decode(result.stdout.toString()) as Map<String, dynamic>;
        return AnalysisResponse.fromJson(payload);
      } on ProcessException catch (error) {
        lastError = error;
      } on FormatException catch (error) {
        lastError = error;
      }
    }

    final failureMessage = switch ((lastError, lastFailure)) {
      (ProcessException error, _) => error.message,
      (FormatException error, _) => error.message,
      (_, ProcessResult result?) => result.stderr.toString().trim(),
      _ => 'The backend could not be started from this Flutter prototype.',
    };

    return AnalysisResponse(
      status: 'error',
      code: 'backend_unavailable',
      message: failureMessage.isEmpty
          ? 'The backend could not be started from this Flutter prototype.'
          : failureMessage,
      notices: const [],
      result: null,
    );
  }

  String backendLocationHint() {
    final repoRoot = _resolveRepoRoot();
    return _joinSegments([
      repoRoot,
      'src',
      'edge_workspace_links_app',
      'gui_backend.py',
    ]);
  }

  String _resolveRepoRoot() {
    final current = Directory.current.absolute;
    return current.parent.parent.path;
  }

  String _joinSegments(List<String> parts) {
    final separator = Platform.isWindows ? r'\' : '/';
    return parts.join(separator);
  }

  String _joinPaths(List<String?> parts) {
    final filtered = parts
        .whereType<String>()
        .where((part) => part.isNotEmpty)
        .toList();
    return filtered.join(Platform.isWindows ? ';' : ':');
  }
}

class _PythonCommand {
  const _PythonCommand(this.executable, this.leadingArgs);

  final String executable;
  final List<String> leadingArgs;
}
