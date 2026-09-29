import 'package:flutter/material.dart';

import '../../core/api/exam_api.dart';
import '../auth/sign_in_screen.dart';

class ContextScreen extends StatefulWidget {
  const ContextScreen({
    super.key,
    required this.repository,
    required this.session,
  });

  final ExamRepository repository;
  final StaffSession session;

  @override
  State<ContextScreen> createState() => _ContextScreenState();
}

class _ContextScreenState extends State<ContextScreen> {
  late Future<List<ExamContextSummary>> contexts;

  @override
  void initState() {
    super.initState();
    contexts = widget.repository.contexts(widget.session.token);
  }

  Future<void> _logout() async {
    try {
      await widget.repository.logout(widget.session.token);
    } catch (_) {
      // Phiên ở ứng dụng vẫn được xóa khi máy chủ không phản hồi.
    }
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => SignInScreen(repository: widget.repository),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ca thi được phân công'),
        actions: [
          IconButton(
            onPressed: _logout,
            tooltip: 'Đăng xuất',
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: SafeArea(
        child: FutureBuilder<List<ExamContextSummary>>(
          future: contexts,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(
                child: TextButton(
                  onPressed: () => setState(
                    () => contexts = widget.repository.contexts(
                      widget.session.token,
                    ),
                  ),
                  child: const Text('Không tải được ca thi. Chạm để thử lại.'),
                ),
              );
            }
            final items = snapshot.data!;
            if (items.isEmpty) {
              return const Center(
                child: Text('Bạn chưa được phân công ca thi nào.'),
              );
            }
            return ListView.builder(
              padding: const EdgeInsets.all(20),
              itemCount: items.length,
              itemBuilder: (context, index) {
                final item = items[index];
                return Card(
                  elevation: 0,
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.key,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Ca: ${item.sessionKey}  •  Phòng: ${item.roomKey}',
                        ),
                        const SizedBox(height: 8),
                        Text(
                          item.status == 'OPEN' && item.policyApproved
                              ? 'Đang tiếp nhận'
                              : 'Đang chuẩn bị — chưa tiếp nhận',
                        ),
                        const SizedBox(height: 12),
                        const FilledButton(
                          onPressed: null,
                          child: Text('Bắt đầu tiếp nhận'),
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
    );
  }
}
