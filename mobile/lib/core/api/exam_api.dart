import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

class ExamApiException implements Exception {
  const ExamApiException(this.code);

  final String code;
}

class StaffSession {
  const StaffSession({required this.token, required this.username});

  final String token;
  final String username;
}

class ExamContextSummary {
  const ExamContextSummary({
    required this.key,
    required this.sessionKey,
    required this.roomKey,
    required this.status,
    required this.policyApproved,
  });

  final String key;
  final String sessionKey;
  final String roomKey;
  final String status;
  final bool policyApproved;

  factory ExamContextSummary.fromJson(Map<String, dynamic> json) {
    return ExamContextSummary(
      key: json['key'] as String,
      sessionKey: json['session_key'] as String,
      roomKey: json['room_key'] as String,
      status: json['status'] as String,
      policyApproved: json['policy_approved'] as bool,
    );
  }
}

abstract class ExamRepository {
  Future<StaffSession> login(String username, String password);
  Future<List<ExamContextSummary>> contexts(String token);
  Future<void> logout(String token);
}

class HttpExamRepository implements ExamRepository {
  HttpExamRepository(this.baseUrl);

  final String baseUrl;

  Future<({int status, Object? body})> _request(
    String method,
    String path, {
    String? token,
    Object? body,
  }) async {
    final client = http.Client();
    try {
      final root = baseUrl.replaceFirst(RegExp(r'/$'), '');
      final uri = Uri.parse('$root/api/v1/$path');
      final headers = <String, String>{'Content-Type': 'application/json'};
      if (token != null) headers['Authorization'] = 'Token $token';
      final response =
          await (method == 'POST'
                  ? client.post(
                      uri,
                      headers: headers,
                      body: body == null ? null : jsonEncode(body),
                    )
                  : client.get(uri, headers: headers))
              .timeout(const Duration(seconds: 8));
      final raw = utf8.decode(response.bodyBytes);
      return (
        status: response.statusCode,
        body: raw.isEmpty ? null : jsonDecode(raw),
      );
    } on http.ClientException {
      throw const ExamApiException('NETWORK_ERROR');
    } on TimeoutException {
      throw const ExamApiException('NETWORK_ERROR');
    } finally {
      client.close();
    }
  }

  @override
  Future<StaffSession> login(String username, String password) async {
    final result = await _request(
      'POST',
      'auth/login/',
      body: {'username': username, 'password': password},
    );
    if (result.status != 200) {
      throw ExamApiException(_errorCode(result.body));
    }
    final data = result.body as Map<String, dynamic>;
    return StaffSession(
      token: data['token'] as String,
      username: data['username'] as String,
    );
  }

  @override
  Future<List<ExamContextSummary>> contexts(String token) async {
    final result = await _request('GET', 'contexts/', token: token);
    if (result.status != 200) throw ExamApiException(_errorCode(result.body));
    return (result.body as List<dynamic>)
        .map(
          (item) => ExamContextSummary.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  @override
  Future<void> logout(String token) async {
    await _request('POST', 'auth/logout/', token: token);
  }

  String _errorCode(Object? body) {
    if (body is Map<String, dynamic> && body['code'] is String) {
      return body['code'] as String;
    }
    return 'REQUEST_FAILED';
  }
}
