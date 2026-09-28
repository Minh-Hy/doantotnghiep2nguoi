import 'package:exam_entry/app.dart';
import 'package:exam_entry/core/api/exam_api.dart';
import 'package:exam_entry/core/readiness/readiness_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class AvailableReadinessRepository implements ReadinessRepository {
  @override
  Future<bool> isReady() async => true;
}

class FakeExamApi implements ExamApi {
  @override
  Future<AuthSession> login(String username, String password) async =>
      AuthSession(token: 'test-token', username: username);

  @override
  Future<void> logout(AuthSession session) async {}

  @override
  Future<List<ExamContext>> contexts(AuthSession session) async => [
    const ExamContext(
      id: 1,
      sessionCode: 'HOC-PHAN-01',
      roomCode: 'P-101',
      status: 'SETUP',
      roles: ['OPERATOR'],
    ),
  ];
}

void main() {
  testWidgets('shows readiness and opens staff sign-in', (tester) async {
    await tester.pumpWidget(
      ExamEntryApp(
        readinessRepository: AvailableReadinessRepository(),
        api: FakeExamApi(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Hệ thống đã sẵn sàng'), findsOneWidget);
    await tester.tap(find.text('Đăng nhập'));
    await tester.pumpAndSettle();
    expect(find.text('Đăng nhập nhân sự'), findsOneWidget);
  });

  testWidgets('shows only assigned context and keeps intake closed', (
    tester,
  ) async {
    await tester.pumpWidget(
      ExamEntryApp(
        readinessRepository: AvailableReadinessRepository(),
        api: FakeExamApi(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Đăng nhập'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextFormField).at(0), 'operator');
    await tester.enterText(find.byType(TextFormField).at(1), 'test-password');
    await tester.tap(find.widgetWithText(FilledButton, 'Đăng nhập'));
    await tester.pumpAndSettle();

    expect(find.text('HOC-PHAN-01 · P-101'), findsOneWidget);
    expect(find.text('Chưa mở tiếp nhận'), findsOneWidget);
    final button = tester.widget<FilledButton>(
      find.widgetWithText(FilledButton, 'Tiếp nhận thí sinh'),
    );
    expect(button.onPressed, isNull);
  });
}
