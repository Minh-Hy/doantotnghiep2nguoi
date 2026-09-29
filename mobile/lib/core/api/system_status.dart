import 'dart:convert';
import 'dart:io';

class SystemStatus {
  const SystemStatus({required this.apiOnline, required this.databaseReady});

  final bool apiOnline;
  final bool databaseReady;
}

abstract class StatusRepository {
  Future<SystemStatus> check();
}

class HttpStatusRepository implements StatusRepository {
  HttpStatusRepository(this.baseUrl);

  final String baseUrl;

  Future<({int code, Map<String, dynamic> body})> _get(
    HttpClient client,
    String path,
  ) async {
    final root = baseUrl.replaceFirst(RegExp(r'/$'), '');
    final request = await client.getUrl(Uri.parse('$root/api/v1/$path'));
    final response = await request.close().timeout(const Duration(seconds: 6));
    final body = await utf8.decoder.bind(response).join();
    return (
      code: response.statusCode,
      body: jsonDecode(body) as Map<String, dynamic>,
    );
  }

  @override
  Future<SystemStatus> check() async {
    final client = HttpClient()..connectionTimeout = const Duration(seconds: 6);
    try {
      final health = await _get(client, 'health/');
      if (health.code != 200 || health.body['status'] != 'ok') {
        return const SystemStatus(apiOnline: false, databaseReady: false);
      }
      try {
        final ready = await _get(client, 'ready/');
        return SystemStatus(
          apiOnline: true,
          databaseReady: ready.code == 200 && ready.body['status'] == 'ready',
        );
      } catch (_) {
        return const SystemStatus(apiOnline: true, databaseReady: false);
      }
    } catch (_) {
      return const SystemStatus(apiOnline: false, databaseReady: false);
    } finally {
      client.close(force: true);
    }
  }
}
