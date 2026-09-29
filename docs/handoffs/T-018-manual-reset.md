# Bàn giao T-018 — gỡ mã thử nghiệm để Minh Hy tự dựng

- **Người yêu cầu, ngày:** Minh Hy, 2026-09-29; Quốc An review T-018 theo Sheet.
- **Đầu ra:** gỡ mã trong `backend/` và `mobile/` khỏi nhánh T-018, giữ [kế hoạch](../06-mobile/T-018-ke-hoach-trien-khai-app.md), [hướng dẫn làm thủ công](../06-mobile/T-018-huong-dan-lam-thu-cong.md), quyết định D-004/D-005 và tài liệu nghiên cứu. Commit cũ của [PR #9](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/9) vẫn là lịch sử để đối chiếu; không dùng kết quả test cũ làm bằng chứng cho mã mới.
- **Cách kiểm:** `git ls-files backend mobile` phải rỗng sau commit; mở README và tài liệu giai đoạn 06 để chắc các link chạy mã cũ đã đổi sang hướng dẫn mới. `flutter/uv` chỉ được thử qua phiên bản/câu lệnh `--help`, chưa chạy test ứng dụng mới vì chưa có mã.
- **Ngoài Git:** PostgreSQL 18 cục bộ với role/database `exam_entry` và schema cũ còn nguyên. Cấu hình bí mật cũ đã chuyển từ `backend/.env` sang `.env.t018-backup` ở gốc repo, bị Git ignore, không chia sẻ/commit. Mã mới cần database sạch hoặc kiểm schema cũ trước migration.
- **Giới hạn:** thư mục `backend/` đã rỗng nhưng Windows có thể khóa chính thư mục khi Notepad/terminal còn mở đường dẫn cũ; đóng ứng dụng đó rồi xóa thư mục rỗng trước khi tự tạo khung mới. `mobile/` đã được xóa. M0 chưa được nhóm review, M1/M2 dựng lại chưa bắt đầu.
- **Việc tiếp:** Minh Hy làm Bước 1 trong hướng dẫn, gửi profile cho Quốc An review, rồi gõ từng lệnh dựng khung M1 và lưu bằng chứng. Cập nhật Sheet theo trạng thái thực tế, không đánh dấu M1/M2 hoàn tất từ bản mã đã xóa.
