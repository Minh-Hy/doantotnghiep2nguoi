import 'package:flutter/material.dart';

import '../../core/api/exam_api.dart';

class ContextScreen extends StatefulWidget {
  const ContextScreen({super.key, required this.api, required this.session});

  final ExamApi api;
  final AuthSession session;

  @override
  State<ContextScreen> createState() => _ContextScreenState();
}

class _ContextScreenState extends State<ContextScreen> {
  late Future<List<ExamContext>> _contexts;

  @override
  void initState() {
    super.initState();
    _contexts = widget.api.contexts(widget.session);
  }

  void _reload() {
    setState(() => _contexts = widget.api.contexts(widget.session));
  }

  Future<void> _logout() async {
    await widget.api.logout(widget.session);
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ca và phòng'),
        actions: [
          IconButton(
            onPressed: _reload,
            tooltip: 'Tải lại',
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            onPressed: _logout,
            tooltip: 'Đăng xuất',
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: FutureBuilder<List<ExamContext>>(
              future: _contexts,
              builder: (context, snapshot) {
                if (!snapshot.hasData && !snapshot.hasError) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  final message = switch (snapshot.error) {
                    ApiException(:final message) => message,
                    _ => 'Chưa tải được ca và phòng.',
                  };
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(message),
                        TextButton(
                          onPressed: _reload,
                          child: const Text('Thử lại'),
                        ),
                      ],
                    ),
                  );
                }
                final contexts = snapshot.data!;
                if (contexts.isEmpty) {
                  return const Center(
                    child: Text('Tài khoản chưa được phân công ca/phòng.'),
                  );
                }
                return ListView.separated(
                  padding: const EdgeInsets.all(20),
                  itemCount: contexts.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final item = contexts[index];
                    final status = switch (item.status) {
                      'OPEN' => 'Đang tiếp nhận',
                      'CLOSED' => 'Đã đóng tiếp nhận',
                      _ => 'Chưa mở tiếp nhận',
                    };
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '${item.sessionCode} · ${item.roomCode}',
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            const SizedBox(height: 8),
                            Text(status),
                            Text('Vai trò: ${item.roles.join(', ')}'),
                            const SizedBox(height: 16),
                            const Text(
                              'Bước tiếp theo: nhập mã thí sinh và tạo lượt.',
                            ),
                            const SizedBox(height: 8),
                            FilledButton.icon(
                              onPressed: null,
                              icon: const Icon(Icons.arrow_forward),
                              label: const Text('Tiếp nhận thí sinh'),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}
