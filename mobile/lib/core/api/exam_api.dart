import 'dart:convert';

import 'package:http/http.dart' as http;

class AuthSession {
  const AuthSession({required this.token, required this.username});

  final String token;
  final String username;
}

class ExamContext {
  const ExamContext({
    required this.id,
    required this.sessionCode,
    required this.roomCode,
    required this.status,
    required this.roles,
  });

  final int id;
  final String sessionCode;
  final String roomCode;
  final String status;
  final List<String> roles;

  bool get canOperate =>
      status == 'OPEN' &&
      (roles.contains('OPERATOR') || roles.contains('ADMIN'));
}

class ApiException implements Exception {
  const ApiException(this.message);

  final String message;
}

abstract class ExamApi {
  Future<AuthSession> login(String username, String password);
  Future<void> logout(AuthSession session);
  Future<List<ExamContext>> contexts(AuthSession session);
}

class HttpExamApi implements ExamApi {
  HttpExamApi(String baseUrl, {http.Client? client})
    : _baseUri = Uri.parse(baseUrl),
      _client = client ?? http.Client();

  final Uri _baseUri;
  final http.Client _client;

  @override
  Future<AuthSession> login(String username, String password) async {
    try {
      final response = await _client
          .post(
            _baseUri.resolve('/api/v1/auth/login/'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'username': username, 'password': password}),
          )
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 401 || response.statusCode == 400) {
        throw const ApiException('Tài khoản hoặc mật khẩu chưa đúng.');
      }
      if (response.statusCode != 200) {
        throw const ApiException('Chưa thể đăng nhập. Hãy thử lại.');
      }
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return AuthSession(
        token: data['token'] as String,
        username: data['username'] as String,
      );
    } on ApiException {
      rethrow;
    } catch (_) {
      throw const ApiException(
        'Không kết nối được máy chủ. Hãy kiểm tra mạng.',
      );
    }
  }

  @override
  Future<List<ExamContext>> contexts(AuthSession session) async {
    try {
      final response = await _client
          .get(
            _baseUri.resolve('/api/v1/contexts/'),
            headers: {'Authorization': 'Token ${session.token}'},
          )
          .timeout(const Duration(seconds: 8));
      if (response.statusCode == 401) {
        throw const ApiException('Phiên đăng nhập không còn hiệu lực.');
      }
      if (response.statusCode != 200) {
        throw const ApiException('Chưa tải được ca và phòng.');
      }
      final data = jsonDecode(response.body) as List<dynamic>;
      return data.map((item) {
        final value = item as Map<String, dynamic>;
        return ExamContext(
          id: value['id'] as int,
          sessionCode: value['session_code'] as String,
          roomCode: value['room_code'] as String,
          status: value['status'] as String,
          roles: (value['roles'] as List<dynamic>).cast<String>(),
        );
      }).toList();
    } on ApiException {
      rethrow;
    } catch (_) {
      throw const ApiException(
        'Không kết nối được máy chủ. Hãy kiểm tra mạng.',
      );
    }
  }

  @override
  Future<void> logout(AuthSession session) async {
    try {
      await _client
          .post(
            _baseUri.resolve('/api/v1/auth/logout/'),
            headers: {'Authorization': 'Token ${session.token}'},
          )
          .timeout(const Duration(seconds: 5));
    } catch (_) {
      // The mobile session is dropped even when the server cannot be reached.
    }
  }
}
