# Logic triển khai giai đoạn 06

- **Bài toán:** hỗ trợ tiếp nhận tại cửa phòng thi và ghi nhận các kết quả riêng biệt của lượt kiểm tra, check-in, quyền vào phòng và attendance. [T-008](../01-problem/T-008-requirements.md) và [D-003](../00-project/decisions/T-008-D-003-chap-nhan-baseline-nghien-cuu.md) không cho phép điểm AI tự quyết định quyền vào.
- **Yêu cầu của T-018:** app tham chiếu phải ghi attempt trước tra cứu, giữ các trường hợp không tìm thấy/nhiều hồ sơ/sai phòng, kiểm quyền theo ca/phòng và chống ghi trùng. Kết quả `unresolved` theo A0 đi vào thử lại/review. [Luồng T-018](T-018-app-reference.md).
- **Lựa chọn kỹ thuật đã ghi:** [D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md) chọn Flutter, Django REST Framework, PostgreSQL và B0 của Quốc An; [D-005](../00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md) chọn Android trước, AI trên điện thoại và check-in do nhân sự xác nhận sau đồng bộ. Ngưỡng, thiết bị và policy kỳ thi thật còn mở.
- **Trạng thái mã hiện tại:** mã Django/Flutter thử nghiệm đã được gỡ khỏi nhánh T-018 ngày 2026-09-29 theo yêu cầu của Minh Hy để tự dựng lại từng bước. Kết quả test và migration trước đó chỉ là lịch sử; không mô tả mã hiện tại. PostgreSQL cục bộ chưa bị xóa.
- **Bước kế tiếp:** theo [hướng dẫn làm thủ công](T-018-huong-dan-lam-thu-cong.md), bắt đầu M0 rồi dựng M1. Chỉ mở các nhánh check-in sau khi profile và hợp đồng liên quan được review.

Đây là bản đồ lập luận của giai đoạn, không thay thế quyết định chính thức hoặc phê duyệt vận hành thật.
