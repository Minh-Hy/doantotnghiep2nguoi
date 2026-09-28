# Bàn giao T-018 — đăng nhập và ca/phòng giả lập

- **Người làm, ngày:** Minh Hy, 2026-09-28.
- **Task trên Sheet:** [T-018](https://docs.google.com/spreadsheets/d/14BQCQ_LbGkZS15Grfi4AZNWBX15h479XjoyQvP9jHcU/edit?gid=0#gid=0); Quốc An review.
- **Commit/PR:** [PR #9](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/9); commit của mốc này trong PR.
- **Đã làm:** ghi [D-005](../00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md); API kiểm DB, đăng nhập/đăng xuất và trả context theo quyền; Flutter có màn hình đăng nhập và danh sách ca/phòng; `seed_demo` tạo ca học phần và mã giả ở `SETUP`.
- **Cách chạy/kiểm:** xem [backend](../../backend/README.md) và [Flutter](../../mobile/README.md). 12 test backend trên SQLite, Flutter analyze/2 widget test/build APK đạt; kiểm PostgreSQL thật cần `.env` cục bộ và database/tài khoản do người giữ máy tạo.
- **Giới hạn:** máy đã có PostgreSQL 18 chạy port 5432, nhưng chưa có `backend/.env` nên chưa migration hay test schema trên PostgreSQL. Tài khoản/token mốc này cần mạng, token chỉ ở bộ nhớ app; đồng bộ offline, camera/B0, tạo lượt và check-in chưa có. Nút tiếp nhận vẫn khóa.
- **File ngoài Git:** không có file mới; `.env` và mật khẩu chỉ ở máy. Ảnh mẫu/weight tương lai theo [external-assets](../00-project/external-assets.md).
