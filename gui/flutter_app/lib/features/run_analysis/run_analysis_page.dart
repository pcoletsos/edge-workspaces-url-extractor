import 'package:flutter/material.dart';

import '../../models/analysis_response.dart';
import '../../services/backend_runner.dart';
import '../../services/path_picker.dart';

class RunAnalysisPage extends StatefulWidget {
  const RunAnalysisPage({super.key});

  @override
  State<RunAnalysisPage> createState() => _RunAnalysisPageState();
}

class _RunAnalysisPageState extends State<RunAnalysisPage> {
  final _pathController = TextEditingController();
  final _backendRunner = const BackendRunner();
  final _pathPicker = const PathPicker();

  AnalysisMode _mode = AnalysisMode.both;
  bool _excludeInternal = true;
  bool _sort = true;
  bool _isRunning = false;
  AnalysisResponse? _response;
  String? _pickerError;

  @override
  void dispose() {
    _pathController.dispose();
    super.dispose();
  }

  Future<void> _runAnalysis() async {
    if (_pathController.text.trim().isEmpty) {
      return;
    }

    setState(() {
      _isRunning = true;
    });

    final response = await _backendRunner.run(
      inputPath: _pathController.text.trim(),
      mode: _mode,
      excludeInternal: _excludeInternal,
      sort: _sort,
    );

    if (!mounted) {
      return;
    }

    setState(() {
      _response = response;
      _isRunning = false;
    });
  }

  Future<void> _pickDirectory() async {
    await _pickPath(() => _pathPicker.pickDirectory());
  }

  Future<void> _pickWorkspaceFile() async {
    await _pickPath(() => _pathPicker.pickWorkspaceFile());
  }

  Future<void> _pickPath(Future<String?> Function() chooser) async {
    try {
      final selectedPath = await chooser();
      if (!mounted || selectedPath == null || selectedPath.trim().isEmpty) {
        return;
      }

      setState(() {
        _pickerError = null;
        _pathController.text = selectedPath;
        _pathController.selection = TextSelection.collapsed(
          offset: selectedPath.length,
        );
      });
    } on PathPickerException catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _pickerError = error.message;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final result = _response?.result;

    return Scaffold(
      body: Stack(
        children: [
          const _Backdrop(),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(28),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 1180),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Edge Workspace Studio',
                        style: theme.textTheme.displayLarge?.copyWith(
                          color: const Color(0xFF102A43),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'A Flutter desktop prototype for a cross-platform, design-forward UI layered on top of the existing extraction engine.',
                        style: theme.textTheme.bodyLarge,
                      ),
                      const SizedBox(height: 28),
                      Wrap(
                        spacing: 20,
                        runSpacing: 20,
                        crossAxisAlignment: WrapCrossAlignment.start,
                        children: [
                          SizedBox(
                            width: 700,
                            child: _glassCard(
                              context,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Run analysis',
                                    style: theme.textTheme.titleLarge,
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Choose a workspace folder or a single .edge file with native desktop dialogs. You can still edit the path directly.',
                                    style: theme.textTheme.bodyMedium,
                                  ),
                                  const SizedBox(height: 24),
                                  TextField(
                                    controller: _pathController,
                                    decoration: const InputDecoration(
                                      labelText:
                                          'Workspace file or folder path',
                                      hintText:
                                          r'C:\Users\you\OneDrive\Apps\Microsoft Edge\Edge Workspaces',
                                    ),
                                  ),
                                  const SizedBox(height: 14),
                                  Wrap(
                                    spacing: 12,
                                    runSpacing: 12,
                                    children: [
                                      OutlinedButton.icon(
                                        onPressed: _isRunning
                                            ? null
                                            : _pickDirectory,
                                        icon: const Icon(Icons.folder_open),
                                        label: const Text('Choose folder'),
                                      ),
                                      FilledButton.tonalIcon(
                                        onPressed: _isRunning
                                            ? null
                                            : _pickWorkspaceFile,
                                        icon: const Icon(
                                          Icons.insert_drive_file_outlined,
                                        ),
                                        label: const Text('Choose file'),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 14),
                                  Text(
                                    _pickerError ??
                                        'Native browsing is available through the app shell on Windows, macOS, and Linux.',
                                    style: theme.textTheme.bodySmall?.copyWith(
                                      color: _pickerError == null
                                          ? const Color(0xFF486581)
                                          : const Color(0xFFC05621),
                                    ),
                                  ),
                                  const SizedBox(height: 24),
                                  SegmentedButton<AnalysisMode>(
                                    showSelectedIcon: false,
                                    segments: const [
                                      ButtonSegment(
                                        value: AnalysisMode.both,
                                        label: Text('Both'),
                                      ),
                                      ButtonSegment(
                                        value: AnalysisMode.tabs,
                                        label: Text('Tabs'),
                                      ),
                                      ButtonSegment(
                                        value: AnalysisMode.favorites,
                                        label: Text('Favorites'),
                                      ),
                                    ],
                                    selected: {_mode},
                                    onSelectionChanged: (selection) {
                                      setState(() {
                                        _mode = selection.first;
                                      });
                                    },
                                  ),
                                  const SizedBox(height: 18),
                                  Wrap(
                                    spacing: 18,
                                    runSpacing: 12,
                                    children: [
                                      FilterChip(
                                        selected: _excludeInternal,
                                        onSelected: (value) {
                                          setState(() {
                                            _excludeInternal = value;
                                          });
                                        },
                                        label: const Text(
                                          'Exclude internal URLs',
                                        ),
                                      ),
                                      FilterChip(
                                        selected: _sort,
                                        onSelected: (value) {
                                          setState(() {
                                            _sort = value;
                                          });
                                        },
                                        label: const Text(
                                          'Sort exported links',
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 24),
                                  FilledButton.icon(
                                    onPressed: _isRunning ? null : _runAnalysis,
                                    icon: _isRunning
                                        ? const SizedBox.square(
                                            dimension: 18,
                                            child: CircularProgressIndicator(
                                              strokeWidth: 2,
                                            ),
                                          )
                                        : const Icon(Icons.play_arrow_rounded),
                                    label: Text(
                                      _isRunning
                                          ? 'Running...'
                                          : 'Run extraction',
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          SizedBox(
                            width: 420,
                            child: Column(
                              children: [
                                _glassCard(
                                  context,
                                  accent: const Color(0xFFE07A5F),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Backend seam',
                                        style: theme.textTheme.titleLarge,
                                      ),
                                      const SizedBox(height: 12),
                                      Text(
                                        'This prototype prefers the packaged sibling backend executable when it is bundled with the app and falls back to the Python module during development.',
                                        style: theme.textTheme.bodyMedium,
                                      ),
                                      const SizedBox(height: 18),
                                      SelectableText(
                                        _backendRunner.backendLocationHint(),
                                        style: theme.textTheme.bodySmall
                                            ?.copyWith(
                                              fontFamily: 'Consolas',
                                              color: const Color(0xFF102A43),
                                            ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(height: 20),
                                _glassCard(
                                  context,
                                  accent: const Color(0xFF0F766E),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Prototype notes',
                                        style: theme.textTheme.titleLarge,
                                      ),
                                      const SizedBox(height: 12),
                                      Text(
                                        'This pass now covers layout, backend invocation, native desktop path selection, and packaged backend resolution across the desktop targets. Development still falls back to the Python module when the packaged backend is absent.',
                                        style: theme.textTheme.bodyMedium,
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 28),
                      AnimatedSwitcher(
                        duration: const Duration(milliseconds: 280),
                        child: _response == null
                            ? const _EmptyState(key: ValueKey('empty'))
                            : Column(
                                key: const ValueKey('result'),
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Wrap(
                                    spacing: 16,
                                    runSpacing: 16,
                                    children: [
                                      _MetricCard(
                                        label: 'Status',
                                        value: _response!.status.toUpperCase(),
                                        tone: _response!.isSuccess
                                            ? const Color(0xFF0F766E)
                                            : const Color(0xFFE07A5F),
                                      ),
                                      _MetricCard(
                                        label: 'Workspaces',
                                        value:
                                            '${result?.summary['workspace_files_processed'] ?? 0}',
                                        tone: const Color(0xFF2F855A),
                                      ),
                                      _MetricCard(
                                        label: 'Exported links',
                                        value:
                                            '${result?.summary['exported_links_total'] ?? 0}',
                                        tone: const Color(0xFFDD6B20),
                                      ),
                                      _MetricCard(
                                        label: 'Unique URLs',
                                        value:
                                            '${result?.summary['unique_exported_urls'] ?? 0}',
                                        tone: const Color(0xFF0F766E),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 20),
                                  _glassCard(
                                    context,
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          'Run summary',
                                          style: theme.textTheme.titleLarge,
                                        ),
                                        const SizedBox(height: 10),
                                        Text(
                                          _response!.message,
                                          style: theme.textTheme.bodyLarge,
                                        ),
                                        if (_response!.notices.isNotEmpty) ...[
                                          const SizedBox(height: 18),
                                          ..._response!.notices.map(
                                            (notice) => Padding(
                                              padding: const EdgeInsets.only(
                                                bottom: 8,
                                              ),
                                              child: Row(
                                                crossAxisAlignment:
                                                    CrossAxisAlignment.start,
                                                children: [
                                                  const Padding(
                                                    padding: EdgeInsets.only(
                                                      top: 2,
                                                    ),
                                                    child: Icon(
                                                      Icons.info_outline,
                                                      size: 16,
                                                    ),
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Expanded(
                                                    child: Text(
                                                      notice,
                                                      style: theme
                                                          .textTheme
                                                          .bodyMedium,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ),
                                  const SizedBox(height: 20),
                                  Wrap(
                                    spacing: 20,
                                    runSpacing: 20,
                                    crossAxisAlignment:
                                        WrapCrossAlignment.start,
                                    children: [
                                      SizedBox(
                                        width: 540,
                                        child: _glassCard(
                                          context,
                                          child: _StatusTable(
                                            files: result?.files ?? const [],
                                          ),
                                        ),
                                      ),
                                      SizedBox(
                                        width: 600,
                                        child: _glassCard(
                                          context,
                                          child: _LinkPreview(
                                            links: result?.links ?? const [],
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _glassCard(
    BuildContext context, {
    required Widget child,
    Color accent = const Color(0xFF0F766E),
  }) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.78),
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: accent.withValues(alpha: 0.18)),
        boxShadow: [
          BoxShadow(
            color: accent.withValues(alpha: 0.08),
            blurRadius: 40,
            offset: const Offset(0, 24),
          ),
        ],
      ),
      child: Padding(padding: const EdgeInsets.all(24), child: child),
    );
  }
}

class _Backdrop extends StatelessWidget {
  const _Backdrop();

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFF6EFE1), Color(0xFFF0E4D4), Color(0xFFE8F1ED)],
        ),
      ),
      child: Stack(
        children: const [
          _GlowOrb(
            alignment: Alignment(-0.92, -0.78),
            color: Color(0xFFF2CC8F),
            size: 280,
          ),
          _GlowOrb(
            alignment: Alignment(0.86, -0.62),
            color: Color(0xFFE07A5F),
            size: 320,
          ),
          _GlowOrb(
            alignment: Alignment(0.7, 0.9),
            color: Color(0xFF0F766E),
            size: 360,
          ),
        ],
      ),
    );
  }
}

class _GlowOrb extends StatelessWidget {
  const _GlowOrb({
    required this.alignment,
    required this.color,
    required this.size,
  });

  final Alignment alignment;
  final Color color;
  final double size;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: alignment,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [
              color.withValues(alpha: 0.28),
              color.withValues(alpha: 0.0),
            ],
          ),
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.label,
    required this.value,
    required this.tone,
  });

  final String label;
  final String value;
  final Color tone;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      width: 180,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.84),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: tone.withValues(alpha: 0.14)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: theme.textTheme.bodyMedium),
          const SizedBox(height: 10),
          Text(
            value,
            style: theme.textTheme.displayMedium?.copyWith(
              color: tone,
              fontSize: 28,
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusTable extends StatelessWidget {
  const _StatusTable({required this.files});

  final List<FileStatus> files;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Per-file status', style: theme.textTheme.titleLarge),
        const SizedBox(height: 16),
        if (files.isEmpty)
          Text('No files processed yet.', style: theme.textTheme.bodyMedium)
        else
          ...files.map(
            (file) => Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFF9F7F2),
                borderRadius: BorderRadius.circular(18),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          file.workspaceFile,
                          style: theme.textTheme.bodyLarge?.copyWith(
                            fontWeight: FontWeight.w700,
                            color: const Color(0xFF102A43),
                          ),
                        ),
                      ),
                      _StatusBadge(status: file.status),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(file.detail, style: theme.textTheme.bodyMedium),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.status});

  final String status;

  @override
  Widget build(BuildContext context) {
    final color = switch (status) {
      'ok' => const Color(0xFF0F766E),
      'no_links' => const Color(0xFFDD6B20),
      'favorite' => const Color(0xFF0F766E),
      'tab' => const Color(0xFF2F855A),
      _ => const Color(0xFFE07A5F),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        status,
        style: TextStyle(color: color, fontWeight: FontWeight.w700),
      ),
    );
  }
}

class _LinkPreview extends StatelessWidget {
  const _LinkPreview({required this.links});

  final List<ExportLink> links;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final preview = links.take(8).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Export preview', style: theme.textTheme.titleLarge),
        const SizedBox(height: 16),
        if (preview.isEmpty)
          Text(
            'Run analysis to preview exported links.',
            style: theme.textTheme.bodyMedium,
          )
        else
          ...preview.map(
            (link) => Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.68),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      _StatusBadge(status: link.source),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          link.workspaceFile,
                          style: theme.textTheme.bodySmall,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    link.title.isEmpty ? '(Untitled)' : link.title,
                    style: theme.textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: const Color(0xFF102A43),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(link.url, style: theme.textTheme.bodyMedium),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.62),
        borderRadius: BorderRadius.circular(30),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Ready for the first run', style: theme.textTheme.titleLarge),
          const SizedBox(height: 10),
          Text(
            'This prototype already knows how to call the backend and render the JSON response. Choose a path or edit it manually, then run it to see the workflow.',
            style: theme.textTheme.bodyLarge,
          ),
        ],
      ),
    );
  }
}
