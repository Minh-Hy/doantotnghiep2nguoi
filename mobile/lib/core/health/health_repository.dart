import 'dart:convert';

import 'package:http/http.dart' as http;

abstract class HealthRepository {
  Future<bool> isAvailable();
}

class HttpHealthRepository implements HealthRepository {
  HttpHealthRepository(String baseUrl, {http.Client? client})
    : _baseUri = Uri.parse(baseUrl),
      _client = client ?? http.Client();

  final Uri _baseUri;
  final http.Client _client;

  @override
  Future<bool> isAvailable() async {
    try {
      final response = await _client
          .get(_baseUri.resolve('/api/v1/health/'))
          .timeout(const Duration(seconds: 5));
      if (response.statusCode != 200) return false;
      final body = jsonDecode(response.body);
      return body is Map<String, dynamic> && body['status'] == 'ok';
    } catch (_) {
      return false;
    }
  }
}
