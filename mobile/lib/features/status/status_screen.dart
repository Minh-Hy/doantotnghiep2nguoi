import 'package:flutter/material.dart';

import '../../core/api/system_status.dart';
import '../../core/api/exam_api.dart';
import '../auth/sign_in_screen.dart';

class StatusScreen extends StatefulWidget {
  const StatusScreen({
    super.key,
    required this.repository,
    required this.examRepository,
    required this.serverLabel,
  });

  final StatusRepository repository;
  final ExamRepository examRepository;
  final String serverLabel;

  @override
  State<StatusScreen> createState() => _StatusScreenState();
}

class _StatusScreenState extends State<StatusScreen> {
  SystemStatus? status;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    setState(() => loading = true);
    final result = await widget.repository.check();
    if (!mounted) return;
    setState(() {
      status = result;
      loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Cửa phòng thi')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: colors.primary,
                borderRadius: BorderRadius.circular(24),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'CA THI GIẢ LẬP',
                    style: TextStyle(color: Colors.white70, letterSpacing: 1.2),
                  ),
                  SizedBox(height: 12),
                  Text(
                    'Sẵn sàng bắt đầu từng bước',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Kiểm tra kết nối trước khi tiếp nhận thí sinh.',
                    style: TextStyle(color: Colors.white, fontSize: 15),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Trạng thái hệ thống',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            _StatusCard(
              icon: Icons.cloud_outlined,
              title: 'Máy chủ',
              detail: loading
                  ? 'Đang kiểm tra...'
                  : status!.apiOnline
                  ? 'Đã kết nối'
                  : 'Không kết nối được',
              good: !loading && status!.apiOnline,
            ),
            const SizedBox(height: 10),
            _StatusCard(
              icon: Icons.storage_outlined,
              title: 'Cơ sở dữ liệu',
              detail: loading
                  ? 'Đang kiểm tra...'
                  : status!.databaseReady
                  ? 'Sẵn sàng'
                  : 'Chưa sẵn sàng',
              good: !loading && status!.databaseReady,
            ),
            const SizedBox(height: 14),
            OutlinedButton.icon(
              onPressed: loading ? null : _refresh,
              icon: const Icon(Icons.refresh),
              label: const Text('Kiểm tra lại'),
            ),
            if (!loading && status!.apiOnline && status!.databaseReady) ...[
              const SizedBox(height: 10),
              FilledButton.icon(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) =>
                        SignInScreen(repository: widget.examRepository),
                  ),
                ),
                icon: const Icon(Icons.login),
                label: const Text('Đăng nhập nhân sự'),
              ),
            ],
            const SizedBox(height: 28),
            Card(
              elevation: 0,
              color: colors.surface,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Tiếp nhận thí sinh',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Chức năng này sẽ mở sau khi ca thi và quy tắc xử lý được duyệt.',
                    ),
                    const SizedBox(height: 16),
                    const FilledButton(
                      onPressed: null,
                      child: Text('Bắt đầu tiếp nhận'),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            Text(
              'Máy chủ: ${widget.serverLabel}',
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusCard extends StatelessWidget {
  const _StatusCard({
    required this.icon,
    required this.title,
    required this.detail,
    required this.good,
  });

  final IconData icon;
  final String title;
  final String detail;
  final bool good;

  @override
  Widget build(BuildContext context) {
    final color = good ? const Color(0xFF16836B) : const Color(0xFF9B5B14);
    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 3),
                  Text(detail, style: TextStyle(color: color)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
