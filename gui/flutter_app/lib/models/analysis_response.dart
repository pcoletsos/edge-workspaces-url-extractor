class AnalysisResponse {
  const AnalysisResponse({
    required this.status,
    required this.code,
    required this.message,
    required this.notices,
    required this.result,
  });

  final String status;
  final String code;
  final String message;
  final List<String> notices;
  final AnalysisResult? result;

  bool get isSuccess => status == 'ok';

  factory AnalysisResponse.fromJson(Map<String, dynamic> json) {
    return AnalysisResponse(
      status: json['status'] as String? ?? 'error',
      code: json['code'] as String? ?? 'unknown',
      message: json['message'] as String? ?? '',
      notices: ((json['notices'] as List<dynamic>?) ?? const [])
          .map((entry) => entry.toString())
          .toList(),
      result: json['result'] is Map<String, dynamic>
          ? AnalysisResult.fromJson(json['result'] as Map<String, dynamic>)
          : null,
    );
  }
}

class AnalysisResult {
  const AnalysisResult({
    required this.links,
    required this.summary,
    required this.files,
  });

  final List<ExportLink> links;
  final Map<String, dynamic> summary;
  final List<FileStatus> files;

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      links: ((json['links'] as List<dynamic>?) ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(ExportLink.fromJson)
          .toList(),
      summary: (json['summary'] as Map<String, dynamic>?) ?? const {},
      files: ((json['files'] as List<dynamic>?) ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(FileStatus.fromJson)
          .toList(),
    );
  }
}

class ExportLink {
  const ExportLink({
    required this.workspaceFile,
    required this.source,
    required this.url,
    required this.title,
  });

  final String workspaceFile;
  final String source;
  final String url;
  final String title;

  factory ExportLink.fromJson(Map<String, dynamic> json) {
    return ExportLink(
      workspaceFile: json['workspace_file'] as String? ?? '',
      source: json['source'] as String? ?? '',
      url: json['url'] as String? ?? '',
      title: json['title'] as String? ?? '',
    );
  }
}

class FileStatus {
  const FileStatus({
    required this.workspaceFile,
    required this.status,
    required this.detail,
    required this.extractedTabCount,
    required this.extractedFavoriteCount,
    required this.exportedLinkCount,
  });

  final String workspaceFile;
  final String status;
  final String detail;
  final int extractedTabCount;
  final int extractedFavoriteCount;
  final int exportedLinkCount;

  factory FileStatus.fromJson(Map<String, dynamic> json) {
    return FileStatus(
      workspaceFile: json['workspace_file'] as String? ?? '',
      status: json['status'] as String? ?? '',
      detail: json['detail'] as String? ?? '',
      extractedTabCount: json['extracted_tab_count'] as int? ?? 0,
      extractedFavoriteCount: json['extracted_favorite_count'] as int? ?? 0,
      exportedLinkCount: json['exported_link_count'] as int? ?? 0,
    );
  }
}
