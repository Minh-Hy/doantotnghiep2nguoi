import 'package:exam_entry/app.dart';
import 'package:exam_entry/core/api/system_status.dart';
import 'package:exam_entry/core/api/exam_api.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class FakeStatusRepository implements StatusRepository {
  FakeStatusRepository(this.result);

  final SystemStatus result;

  @override
  Future<SystemStatus> check() async => result;
}

class FakeExamRepository implements ExamRepository {
  @override
  Future<StaffSession> login(String username, String password) async =>
      const StaffSession(token: 'test-token', username: 'operator-test');

  @override
  Future<List<ExamContextSummary>> contexts(String token) async => [
    const ExamContextSummary(
      key: 'CTX-SIM-01',
      sessionKey: 'SESSION-SIM-01',
      roomKey: 'ROOM-SIM-01',
      status: 'SETUP',
      policyApproved: false,
    ),
  ];

  @override
  Future<void> logout(String token) async {}
}

void main() {
  testWidgets('Hiển thị kết nối API và DB khi sẵn sàng', (tester) async {
    await tester.pumpWidget(
      ExamEntryApp(
        repository: FakeStatusRepository(
          const SystemStatus(apiOnline: true, databaseReady: true),
        ),
        examRepository: FakeExamRepository(),
        serverLabel: 'http://10.0.2.2:8000',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Đã kết nối'), findsOneWidget);
    expect(find.text('Sẵn sàng'), findsOneWidget);
    expect(find.text('Đăng nhập nhân sự'), findsOneWidget);
    await tester.scrollUntilVisible(find.text('Bắt đầu tiếp nhận'), 200);
    final button = tester.widget<FilledButton>(
      find.widgetWithText(FilledButton, 'Bắt đầu tiếp nhận'),
    );
    expect(button.onPressed, isNull);
  });

  testWidgets('Báo lỗi khi chưa kết nối máy chủ', (tester) async {
    await tester.pumpWidget(
      ExamEntryApp(
        repository: FakeStatusRepository(
          const SystemStatus(apiOnline: false, databaseReady: false),
        ),
        examRepository: FakeExamRepository(),
        serverLabel: 'http://10.0.2.2:8000',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Không kết nối được'), findsOneWidget);
    expect(find.text('Chưa sẵn sàng'), findsOneWidget);
  });

  testWidgets('Đăng nhập và thấy ca giả lập còn khóa', (tester) async {
    await tester.pumpWidget(
      ExamEntryApp(
        repository: FakeStatusRepository(
          const SystemStatus(apiOnline: true, databaseReady: true),
        ),
        examRepository: FakeExamRepository(),
        serverLabel: 'http://10.0.2.2:8000',
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Đăng nhập nhân sự'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.widgetWithText(TextField, 'Tên đăng nhập'),
      'operator-test',
    );
    await tester.enterText(
      find.widgetWithText(TextField, 'Mật khẩu'),
      'only-for-test',
    );
    await tester.tap(find.text('Đăng nhập'));
    await tester.pumpAndSettle();

    expect(find.text('CTX-SIM-01'), findsOneWidget);
    expect(find.text('Đang chuẩn bị — chưa tiếp nhận'), findsOneWidget);
  });
}
