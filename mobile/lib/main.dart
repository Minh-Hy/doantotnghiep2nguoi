import 'package:flutter/material.dart';

import 'app.dart';
import 'core/api/system_status.dart';
import 'core/api/exam_api.dart';

const apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

void main() {
  runApp(
    ExamEntryApp(
      repository: HttpStatusRepository(apiBaseUrl),
      examRepository: HttpExamRepository(apiBaseUrl),
      serverLabel: apiBaseUrl,
    ),
  );
}
