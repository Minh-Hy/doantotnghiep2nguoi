# Bàn giao T-018 — lõi ứng dụng tham chiếu, mốc 1

- **Người làm, ngày:** Minh Hy, 2026-09-28.
- **Task trên Sheet:** [T-018](https://docs.google.com/spreadsheets/d/14BQCQ_LbGkZS15Grfi4AZNWBX15h479XjoyQvP9jHcU/edit?gid=0#gid=0); Quốc An review.
- **Commit/PR:** [PR #9](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/9); commit của mốc này được ghi trong PR.
- **Đã làm tại thời điểm đó:** khởi tạo Django REST Framework + PostgreSQL schema, API v1 giới hạn ở attempt/tra cứu roster/review, quyền theo context, idempotency và audit; khởi tạo Flutter Material 3 với kiểm tra kết nối. Mã/hướng dẫn cũ còn trong lịch sử PR #9; [hướng dẫn dựng lại](../06-mobile/T-018-huong-dan-lam-thu-cong.md) và [logic quyết định](../06-mobile/DECISION_LOGIC.md) mô tả bước hiện tại.
- **Kiểm tra tại máy:** 9 test backend qua SQLite trong bộ nhớ; `flutter analyze`, `flutter test` và `flutter build apk --debug` đạt. PostgreSQL và chuỗi camera/AI/check-in chưa được thử tích hợp.
- **Quyết định/giả định:** theo [D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md); B0 là pipeline AI tham chiếu, chưa phải quyết định model triển khai cuối. Các chuỗi `fixture-*` trong test là dữ liệu giả lập, không phải policy được phê duyệt.
- **Còn mở:** Quốc An review PR; cần profile nghiệp vụ và phân quyền được thống nhất, PostgreSQL thật, thiết bị đích, nơi chạy AI, tích hợp camera/B0, xác minh và quy trình ghi check-in/review/correction. Không gọi mốc này là E3 hoàn thành.
- **File ngoài Git:** không có file mới cần trao; weight/dữ liệu mặt theo [external-assets](../00-project/external-assets.md), chưa được đưa vào app.

**Bổ sung 2026-09-28:** [kế hoạch triển khai T-018](../06-mobile/T-018-ke-hoach-trien-khai-app.md) ghi thứ tự M0–M8, đầu ra, điều kiện qua mốc và các câu hỏi phải chốt. Kế hoạch chờ Quốc An review cùng PR #9; không thay trạng thái các mốc chưa có bằng chứng.

**Bổ sung 2026-09-29:** theo yêu cầu Minh Hy, mã backend/mobile đã gỡ để tự dựng lại; xem [note reset](T-018-manual-reset.md). Test cũ là lịch sử, không là bằng chứng cho mã mới.
