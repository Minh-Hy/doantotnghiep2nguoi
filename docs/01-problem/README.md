# Giai đoạn 01 — xác định bài toán

Quốc An và Minh Hy **mỗi người tự chuẩn bị một phương án** trước khi thảo luận. Mỗi phương án có thể nêu 1–2 use case nhận dạng khuôn mặt, nhưng cuối giai đoạn nhóm chỉ chọn **một** bối cảnh và use case cụ thể.

- Quốc An ghi ở `T-002-quoc-an-proposal.md` (task T-002).
- Minh Hy ghi ở `T-003-minh-hy-proposal.md` (task T-003).
- Mỗi file trả lời: ai dùng, camera nhận gì, hệ thống trả gì, logic điểm danh/hiện diện, tiêu chí thành công, dữ liệu có thể dùng và giả định chưa xác nhận.

Sau khi cả hai hoàn thành, trình bày và hỏi chéo. Task T-004 chọn **một phương án chính** dựa trên tính rõ ràng của bài toán, dữ liệu, khả năng làm baseline/đo cải thiện, khả năng demo mobile và công sức cần có. Ghi phương án được chọn, phương án không chọn và lý do ở `T-004-scope.md`; tạo quyết định trong `../00-project/decisions/`. Nếu cần thầy xác nhận, giữ trạng thái chờ xác nhận thay vì coi như đã được thầy duyệt.

**Điều kiện chuyển giai đoạn:** một use case và câu hỏi nghiên cứu đủ rõ để khảo sát dữ liệu, baseline, điểm tối ưu và metric.

Logic từ bài toán nghiệp vụ đến câu hỏi khảo sát: [DECISION_LOGIC.md](DECISION_LOGIC.md).

**Trạng thái hiện tại:** nhóm đã chọn hướng cửa phòng thi ở T-004; xem [T-004-scope.md](T-004-scope.md) và [D-001](../00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md). Các câu hỏi về quy chế và quy trình cụ thể vẫn mở.

## Đặc tả nghiệp vụ sau khi chọn bài toán

[T-008 — Generic Exam Entry Business Baseline](T-008-requirements.md) được chấp nhận làm mốc nghiệp vụ cho nghiên cứu theo [D-003](../00-project/decisions/T-008-D-003-chap-nhan-baseline-nghien-cuu.md). Đọc mục 1 (Core Flow/Decisions), mục 3 (cấu trúc generic, policy cấu hình, triển khai kỹ thuật), mục 18 (phần còn mở) và mục 20 (contract cho task sau). BR/FR mô tả capability generic; các chi tiết policy/case/authority/correction còn được Minh Hy xử lý khi xây app. Thiếu As-Is thực địa chỉ giới hạn kết luận về hiệu quả tại kỳ thi thật. [Logic phase 01](DECISION_LOGIC.md) nối các nhu cầu này với T-009/T-010/T-011.
