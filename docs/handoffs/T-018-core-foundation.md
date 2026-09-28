# Bàn giao T-018 — lõi ứng dụng tham chiếu, mốc 1

- **Người làm, ngày:** Minh Hy, 2026-09-28.
- **Task trên Sheet:** [T-018](https://docs.google.com/spreadsheets/d/14BQCQ_LbGkZS15Grfi4AZNWBX15h479XjoyQvP9jHcU/edit?gid=0#gid=0); Quốc An review.
- **Commit/PR:** [PR #9](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/9); commit của mốc này được ghi trong PR.
- **Đã làm:** khởi tạo Django REST Framework + PostgreSQL schema, API v1 giới hạn ở attempt/tra cứu roster/review, quyền theo context, idempotency và audit; khởi tạo Flutter Material 3 với kiểm tra kết nối. [Hợp đồng và cách chạy](../../backend/README.md), [Flutter](../../mobile/README.md), [logic quyết định](../06-mobile/DECISION_LOGIC.md).
- **Kiểm tra tại máy:** 9 test backend qua SQLite trong bộ nhớ; `flutter analyze`, `flutter test` và `flutter build apk --debug` đạt. PostgreSQL và chuỗi camera/AI/check-in chưa được thử tích hợp.
- **Quyết định/giả định:** theo [D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md); B0 là pipeline AI tham chiếu, chưa phải quyết định model triển khai cuối. Các chuỗi `fixture-*` trong test là dữ liệu giả lập, không phải policy được phê duyệt.
- **Còn mở:** Quốc An review PR; cần profile nghiệp vụ và phân quyền được thống nhất, PostgreSQL thật, thiết bị đích, nơi chạy AI, tích hợp camera/B0, xác minh và quy trình ghi check-in/review/correction. Không gọi mốc này là E3 hoàn thành.
- **File ngoài Git:** không có file mới cần trao; weight/dữ liệu mặt theo [external-assets](../00-project/external-assets.md), chưa được đưa vào app.
