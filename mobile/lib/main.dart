import 'package:flutter/material.dart';

import 'app.dart';
import 'core/health/health_repository.dart';

void main() {
  const baseUrl = String.fromEnvironment(
    'EXAM_API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );
  runApp(ExamEntryApp(healthRepository: HttpHealthRepository(baseUrl)));
}
