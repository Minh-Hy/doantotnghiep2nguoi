# D-007 — Phạm vi dữ liệu cho app T-018

- **Ngày ghi nhận:** 2026-09-29.
- **Người chọn:** Minh Hy, phụ trách T-018; Quốc An review qua PR T-018.
- **Nguồn:** năm câu trả lời của Minh Hy trong cuộc trò chuyện ngày 2026-09-29 về thiết kế DB.
- **Phạm vi:** thiết kế cấu trúc dữ liệu cho app tham chiếu; không phê duyệt policy kỳ thi thật hoặc kết quả E3.

## Đã chọn

1. Một trường, thiết kế cho nhiều môn, kỳ thi, ca và phòng về sau; chưa cần nhiều tenant/trường.
2. Roster sau dữ liệu giả sẽ nhập qua CSV/Excel theo batch có version.
3. PostgreSQL chỉ lưu metadata và tham chiếu tới tệp ảnh/embedding được bảo vệ ngoài DB; không chứa nội dung khuôn mặt.
4. Chuẩn bị các bảng riêng cho check-in, review, đồng bộ offline, correction, quyền vào phòng và attendance; chỉ bật chức năng theo từng giai đoạn và quyết định nghiệp vụ.
5. Chưa có retention và quyền xem/sửa dữ liệu thí sinh chính thức; giữ `TBD`, chỉ dùng dữ liệu giả cho mốc hiện tại.

[Thiết kế DB T-018](../../06-mobile/T-018-thiet-ke-co-so-du-lieu.md) cụ thể hóa lựa chọn này. Nếu nhóm đổi phạm vi hoặc có quy định của trường, ghi nguồn và migration/phiên bản mới; không sửa ngầm dữ liệu đã ghi.
