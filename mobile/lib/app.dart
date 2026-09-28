import 'package:flutter/material.dart';

import 'core/health/health_repository.dart';
import 'features/home/home_screen.dart';

class ExamEntryApp extends StatelessWidget {
  const ExamEntryApp({super.key, required this.healthRepository});

  final HealthRepository healthRepository;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Kiểm tra cửa phòng thi',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0B6A73)),
        scaffoldBackgroundColor: const Color(0xFFF5F8F8),
        cardTheme: const CardThemeData(margin: EdgeInsets.zero, elevation: 0),
      ),
      home: HomeScreen(healthRepository: healthRepository),
    );
  }
}
