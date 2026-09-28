import 'package:flutter/material.dart';

import '../../core/api/exam_api.dart';
import '../contexts/context_screen.dart';

class SignInScreen extends StatefulWidget {
  const SignInScreen({super.key, required this.api});

  final ExamApi api;

  @override
  State<SignInScreen> createState() => _SignInScreenState();
}

class _SignInScreenState extends State<SignInScreen> {
  final _formKey = GlobalKey<FormState>();
  final _username = TextEditingController();
  final _password = TextEditingController();
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _username.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _signIn() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final session = await widget.api.login(
        _username.text.trim(),
        _password.text,
      );
      if (!mounted) return;
      _password.clear();
      await Navigator.of(context).push(
        MaterialPageRoute<void>(
          builder: (_) => ContextScreen(api: widget.api, session: session),
        ),
      );
    } on ApiException catch (error) {
      if (mounted) setState(() => _error = error.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Đăng nhập nhân sự')),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 460),
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Icon(Icons.verified_user_outlined, size: 48),
                    const SizedBox(height: 16),
                    Text(
                      'Tài khoản được phân quyền',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 8),
                    const Text('Đăng nhập để xem ca và phòng được giao.'),
                    const SizedBox(height: 24),
                    TextFormField(
                      controller: _username,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Tên đăng nhập',
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) =>
                          value == null || value.trim().isEmpty
                          ? 'Nhập tên đăng nhập'
                          : null,
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _password,
                      obscureText: true,
                      onFieldSubmitted: (_) => _busy ? null : _signIn(),
                      decoration: const InputDecoration(
                        labelText: 'Mật khẩu',
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) => value == null || value.isEmpty
                          ? 'Nhập mật khẩu'
                          : null,
                    ),
                    if (_error != null) ...[
                      const SizedBox(height: 16),
                      Text(
                        _error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                    ],
                    const SizedBox(height: 24),
                    FilledButton(
                      onPressed: _busy ? null : _signIn,
                      child: Text(_busy ? 'Đang đăng nhập…' : 'Đăng nhập'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
