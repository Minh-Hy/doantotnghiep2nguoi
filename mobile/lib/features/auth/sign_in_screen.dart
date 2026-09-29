import 'package:flutter/material.dart';

import '../../core/api/exam_api.dart';
import '../contexts/context_screen.dart';

class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key, required this.repository});

  final ExamRepository repository;

  @override
  State<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  final username = TextEditingController();
  final password = TextEditingController();
  bool busy = false;
  String? error;

  @override
  void dispose() {
    username.dispose();
    password.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (username.text.trim().isEmpty || password.text.isEmpty) {
      setState(() => error = 'Hãy nhập tên đăng nhập và mật khẩu.');
      return;
    }
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final session = await widget.repository.login(
        username.text.trim(),
        password.text,
      );
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) =>
              ContextScreen(repository: widget.repository, session: session),
        ),
      );
    } on ExamApiException catch (e) {
      if (!mounted) return;
      setState(
        () => error = e.code == 'INVALID_CREDENTIALS'
            ? 'Tên đăng nhập hoặc mật khẩu không đúng.'
            : 'Không thể đăng nhập. Kiểm tra kết nối máy chủ.',
      );
    } catch (_) {
      if (!mounted) return;
      setState(() => error = 'Không thể đăng nhập. Thử lại sau.');
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Đăng nhập nhân sự')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SizedBox(height: 20),
            Icon(
              Icons.badge_outlined,
              size: 56,
              color: Theme.of(context).colorScheme.primary,
            ),
            const SizedBox(height: 16),
            Text(
              'Chào mừng trở lại',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            const Text(
              'Đăng nhập để xem ca thi được phân công.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            TextField(
              controller: username,
              decoration: const InputDecoration(
                labelText: 'Tên đăng nhập',
                border: OutlineInputBorder(),
              ),
              textInputAction: TextInputAction.next,
              autocorrect: false,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: password,
              decoration: const InputDecoration(
                labelText: 'Mật khẩu',
                border: OutlineInputBorder(),
              ),
              obscureText: true,
              onSubmitted: (_) {
                if (!busy) _login();
              },
            ),
            if (error != null) ...[
              const SizedBox(height: 12),
              Text(
                error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ],
            const SizedBox(height: 24),
            FilledButton(
              onPressed: busy ? null : _login,
              child: Text(busy ? 'Đang đăng nhập...' : 'Đăng nhập'),
            ),
          ],
        ),
      ),
    );
  }
}
