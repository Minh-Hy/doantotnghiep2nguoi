import 'package:exam_entry/app.dart';
import 'package:exam_entry/core/health/health_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class AvailableHealthRepository implements HealthRepository {
  @override
  Future<bool> isAvailable() async => true;
}

void main() {
  testWidgets('shows backend status and keeps intake closed until setup', (
    tester,
  ) async {
    await tester.pumpWidget(
      ExamEntryApp(healthRepository: AvailableHealthRepository()),
    );
    await tester.pumpAndSettle();

    expect(find.text('Máy chủ đã kết nối'), findsOneWidget);
    expect(find.text('Bắt đầu lượt'), findsOneWidget);
    final button = tester.widget<FilledButton>(find.byType(FilledButton));
    expect(button.onPressed, isNull);
  });
}
