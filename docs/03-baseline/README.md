# Giai đoạn 03 — baseline

Đọc [T-010 — giao thức baseline](T-010-protocol.md) và [logic quyết định phase 03](DECISION_LOGIC.md). T-010 đã chốt phương pháp đo và phạm vi phép thử E2 học thuật đầu tiên; từng run phải pin nguồn/phiên bản dữ liệu, split, preprocessing, weight, cấu hình, seed, metric, thiết bị và cách chạy lại **trước khi xem kết quả**. Baseline so sánh đầy đủ chưa freeze vì các gate dữ liệu/policy/tiêu chí chấp nhận chưa hoàn tất. Mỗi run có hồ sơ riêng trong `runs/` theo cùng mẫu ở `../05-evaluation/RUN-TEMPLATE.md`.

**Điều kiện chuyển giai đoạn:** baseline chạy lại được và có kết quả làm mốc so sánh với proposed.

[T-011 baseline nghiên cứu](T-011-baseline-summary.md) tổng hợp E1 detection, E2 1:1 và M1 thời gian tham chiếu cùng giới hạn. Đây là mốc cho T-012 phân tích lỗi; E3/app và đo thiết bị đích vẫn là việc cần làm trước kết luận triển khai.
