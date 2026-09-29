import 'dart:io';

import 'package:exam_entry/core/api/system_status.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('API còn hoạt động khi database chưa sẵn sàng', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    server.listen((request) async {
      request.response.headers.contentType = ContentType.json;
      if (request.uri.path.endsWith('/health/')) {
        request.response.write('{"status":"ok"}');
      } else {
        request.response.statusCode = 503;
        request.response.write('{"status":"not_ready"}');
      }
      await request.response.close();
    });

    try {
      final status = await HttpStatusRepository(
        'http://127.0.0.1:${server.port}',
      ).check();
      expect(status.apiOnline, isTrue);
      expect(status.databaseReady, isFalse);
    } finally {
      await server.close(force: true);
    }
  });
}
