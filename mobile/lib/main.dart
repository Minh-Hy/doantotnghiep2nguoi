import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

import 'app.dart';
import 'core/api/system_status.dart';
import 'core/api/exam_api.dart';

const configuredApiBaseUrl = String.fromEnvironment('API_BASE_URL');
final apiBaseUrl = configuredApiBaseUrl.isNotEmpty
    ? configuredApiBaseUrl
    : kIsWeb
    ? 'http://127.0.0.1:8000'
    : 'http://10.0.2.2:8000';

void main() {
  runApp(
    ExamEntryApp(
      repository: HttpStatusRepository(apiBaseUrl),
      examRepository: HttpExamRepository(apiBaseUrl),
      serverLabel: apiBaseUrl,
    ),
  );
}
