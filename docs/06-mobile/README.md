# Giai đoạn 06 — ứng dụng mobile

[D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md) ghi lựa chọn Flutter + Django REST Framework + PostgreSQL và B0 của Quốc An cho app tham chiếu. [D-005](../00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md) chọn Android trước, AI trên điện thoại và ca thi học phần giả lập; cần đo B0 trên thiết bị đích. [T-018](T-018-app-reference.md) ghi luồng, ranh giới AI/nghiệp vụ và các điều kiện còn mở.

[DECISION_LOGIC.md](DECISION_LOGIC.md) nối yêu cầu nghiệp vụ với mốc triển khai hiện tại. Theo yêu cầu của Minh Hy ngày 2026-09-29, mã `backend/` và `mobile/` trên nhánh T-018 đã được gỡ để tự dựng lại. Bắt đầu với [hướng dẫn làm thủ công](T-018-huong-dan-lam-thu-cong.md).

[Kế hoạch T-018](T-018-ke-hoach-trien-khai-app.md) chia các mốc FE/BE/DB/AI, phụ thuộc và điều kiện kiểm tra; đây là kế hoạch để nhóm review, không đặt policy hoặc deadline khi chưa được chốt.

**Kiểm thử tối thiểu dự kiến:** mở app → camera hoạt động → xác minh 1:1 → ghi attempt/check-in hoặc chuyển review → xem kết quả. Khi có mã, bổ sung hướng dẫn build, thiết bị đã thử và giới hạn thực tế.
