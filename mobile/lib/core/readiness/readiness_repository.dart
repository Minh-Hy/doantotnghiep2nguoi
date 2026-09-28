import 'dart:convert';

import 'package:http/http.dart' as http;

abstract class ReadinessRepository {
  Future<bool> isReady();
}

class HttpReadinessRepository implements ReadinessRepository {
  HttpReadinessRepository(String baseUrl, {http.Client? client})
    : _baseUri = Uri.parse(baseUrl),
      _client = client ?? http.Client();

  final Uri _baseUri;
  final http.Client _client;

  @override
  Future<bool> isReady() async {
    try {
      final response = await _client
          .get(_baseUri.resolve('/api/v1/ready/'))
          .timeout(const Duration(seconds: 5));
      if (response.statusCode != 200) return false;
      final body = jsonDecode(response.body);
      return body is Map<String, dynamic> && body['status'] == 'ready';
    } catch (_) {
      return false;
    }
  }
}
