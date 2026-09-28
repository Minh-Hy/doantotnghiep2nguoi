import 'package:flutter/material.dart';

import 'app.dart';
import 'core/api/exam_api.dart';
import 'core/readiness/readiness_repository.dart';

void main() {
  const baseUrl = String.fromEnvironment(
    'EXAM_API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );
  runApp(
    ExamEntryApp(
      readinessRepository: HttpReadinessRepository(baseUrl),
      api: HttpExamApi(baseUrl),
    ),
  );
}
