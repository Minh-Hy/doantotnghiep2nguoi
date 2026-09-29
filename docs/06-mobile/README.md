# Giai đoạn 06 — ứng dụng mobile

[D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md) ghi lựa chọn Flutter + Django REST Framework + PostgreSQL và B0 của Quốc An cho app tham chiếu. [D-005](../00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md) chọn Android trước, AI trên điện thoại và ca thi học phần giả lập; cần đo B0 trên thiết bị đích. [T-018](T-018-app-reference.md) ghi luồng, ranh giới AI/nghiệp vụ và các điều kiện còn mở.

[DECISION_LOGIC.md](DECISION_LOGIC.md) nối yêu cầu nghiệp vụ với mốc triển khai hiện tại. Mã thử nghiệm cũ được gỡ ngày 2026-09-29; theo yêu cầu tiếp theo của Minh Hy, mốc kết nối mới đang được xây trong `backend/` và `mobile/`. Xem [hướng dẫn chạy trong VS Code](T-018-vscode-local-setup.md) và [tiến độ thực tế](T-018-ke-hoach-trien-khai-app.md#6-tiến-độ-thực-tế--cập-nhật-2026-09-29).

[Kế hoạch T-018](T-018-ke-hoach-trien-khai-app.md) chia các mốc FE/BE/DB/AI, phụ thuộc và điều kiện kiểm tra; đây là kế hoạch để nhóm review, không đặt policy hoặc deadline khi chưa được chốt.

[Profile ca thi học phần giả lập T-018](T-018-profile-ca-thi-gia-lap.md) là bản nháp M0 để Minh Hy và Quốc An review trước khi dùng làm nguồn expected outcome E3; chưa là quy chế kỳ thi thật hay profile được phê duyệt.

**Mốc hiện có:** API health/readiness/login/logout/context/attempt và Flutter kiểm kết nối, đăng nhập, xem ca được gán. Có bản xem thử trên Edge cho máy yếu; Android vẫn là đích chính. Chưa có camera, AI hoặc check-in. **Kiểm thử đích:** mở app → camera → xác minh 1:1 → check-in hoặc review → xem kết quả theo quyền.
