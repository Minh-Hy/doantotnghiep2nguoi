import 'package:flutter/material.dart';

import '../../core/health/health_repository.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.healthRepository});

  final HealthRepository healthRepository;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool? _serverAvailable;

  @override
  void initState() {
    super.initState();
    _refreshStatus();
  }

  Future<void> _refreshStatus() async {
    setState(() => _serverAvailable = null);
    final available = await widget.healthRepository.isAvailable();
    if (mounted) setState(() => _serverAvailable = available);
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final statusText = switch (_serverAvailable) {
      null => 'Đang kiểm tra kết nối',
      true => 'Máy chủ đã kết nối',
      false => 'Chưa kết nối máy chủ',
    };

    return Scaffold(
      appBar: AppBar(
        title: const Text('Điểm tiếp nhận'),
        backgroundColor: colors.surface,
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                Text(
                  'Kiểm tra cửa phòng thi',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const SizedBox(height: 8),
                const Text(
                  'Thiết bị hỗ trợ xác minh từng thí sinh theo hồ sơ đã khai báo.',
                ),
                const SizedBox(height: 24),
                Card.filled(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Row(
                      children: [
                        Icon(
                          _serverAvailable == true
                              ? Icons.cloud_done_outlined
                              : Icons.cloud_off_outlined,
                          color: _serverAvailable == true
                              ? colors.primary
                              : colors.error,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            statusText,
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                        ),
                        IconButton(
                          onPressed: _refreshStatus,
                          tooltip: 'Kiểm tra lại',
                          icon: const Icon(Icons.refresh),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  color: colors.surface,
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(
                          Icons.badge_outlined,
                          size: 36,
                          color: colors.primary,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Tiếp nhận thí sinh',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Chọn ca và phòng, khai báo mã, rồi xác minh đúng người với hồ sơ.',
                        ),
                        const SizedBox(height: 20),
                        FilledButton.icon(
                          onPressed: null,
                          icon: Icon(Icons.arrow_forward),
                          label: Text('Bắt đầu lượt'),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Chưa mở tiếp nhận. Người phụ trách cần chuẩn bị ca, quyền và thiết bị.',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  color: colors.surface,
                  child: const ListTile(
                    leading: Icon(Icons.support_agent_outlined),
                    title: Text('Xử lý ngoại lệ'),
                    subtitle: Text(
                      'Các lượt chưa kết luận sẽ được chuyển tới người có quyền.',
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
