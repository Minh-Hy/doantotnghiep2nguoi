import 'package:flutter/material.dart';

import 'core/api/system_status.dart';
import 'core/api/exam_api.dart';
import 'features/status/status_screen.dart';

class ExamEntryApp extends StatelessWidget {
  const ExamEntryApp({
    super.key,
    required this.repository,
    required this.examRepository,
    required this.serverLabel,
  });

  final StatusRepository repository;
  final ExamRepository examRepository;
  final String serverLabel;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cửa phòng thi',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF3159C9)),
        scaffoldBackgroundColor: const Color(0xFFF5F7FB),
      ),
      home: StatusScreen(
        repository: repository,
        examRepository: examRepository,
        serverLabel: serverLabel,
      ),
    );
  }
}
