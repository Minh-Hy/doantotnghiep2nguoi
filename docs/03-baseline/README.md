# Giai đoạn 03 — baseline

Ghi giao thức tại `protocol.md` khi bắt đầu: nguồn và phiên bản dữ liệu, split, preprocessing, model, cấu hình, seed, metric, thiết bị và cách chạy lại. Mỗi run có hồ sơ riêng trong `runs/` theo cùng mẫu ở `../05-evaluation/RUN-TEMPLATE.md`.

**Điều kiện chuyển giai đoạn:** baseline chạy lại được và có kết quả làm mốc so sánh với proposed.

[T-011 baseline nghiên cứu](T-011-baseline-summary.md) tổng hợp E1 detection, E2 1:1 và M1 thời gian tham chiếu cùng giới hạn. Đây là mốc cho T-012 phân tích lỗi; E3/app và đo thiết bị đích vẫn là việc cần làm trước kết luận triển khai.

[T-012 phân tích lỗi](T-012-error-analysis.md) đối chiếu các run E1/E2/M1, giữ rõ giới hạn miền và mẫu số, rồi ưu tiên câu hỏi S4 chọn đúng người mục tiêu/giữ trường hợp chưa kết luận. [Điều kiện thí nghiệm S4](T-012-S4-experiment-readiness.md) nêu dữ liệu/nhãn và protocol còn thiếu; chưa có kết quả S4 hoặc quyết định kỹ thuật cuối.
