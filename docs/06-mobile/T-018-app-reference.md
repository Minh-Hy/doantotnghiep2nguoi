# T-018 — App cửa phòng thi tham chiếu

- **Trạng thái:** đã có lõi Django/Flutter ở nhánh T-018 để review; PostgreSQL, AI, camera và luồng check-in chưa được kiểm tích hợp.
- **Quyết định:** [D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md).
- **Người thực hiện/review:** Minh Hy / Quốc An theo Sheet.
- **Lộ trình:** [kế hoạch triển khai T-018](T-018-ke-hoach-trien-khai-app.md).

## Kiến trúc dự kiến

`Flutter (thiết bị tại cửa và màn hình nhân sự theo scope) ↔ API Django REST Framework ↔ PostgreSQL`.

Pipeline AI tham chiếu là [B0 T-012](../03-baseline/T-012-B0-pipeline-choice.md): SCRFD-500MF → A0 đúng một mặt → căn chỉnh 5 landmark 112×112 → MobileFaceNet → L2/cosine → kết quả xác minh 1:1 hoặc `unresolved`. Đây là baseline nghiên cứu để app chạy được, chưa là model/ngưỡng triển khai cuối. Giao diện gọi một hợp đồng kiểm tra danh tính ổn định, không gắn quyết định nghiệp vụ trực tiếp vào điểm cosine.

## Luồng app cần hiện thực

1. Người có quyền gán kỳ thi/ca/phòng, roster và policy có hiệu lực; kiểm tra điều kiện sẵn sàng trước khi mở tiếp nhận.
2. Thí sinh khai báo mã; tạo attempt trước khi tra cứu, giữ cả trường hợp không có hoặc có nhiều hồ sơ.
3. Kiểm phòng/ca/thời gian và kết quả trước; thực hiện xác minh người đang làm lượt với đúng hồ sơ đã chọn.
4. Phân biệt `satisfied`, `unmet`, `unavailable`, `inconclusive`; nhiều hoặc không có mặt theo A0 đi theo đường thử lại/review, không tự chọn một box.
5. Chỉ ghi check-in có hiệu lực khi đủ policy và thẩm quyền; chống trùng khi retry/mất xác nhận ghi. Entry authorization và attendance là kết quả riêng.
6. Case ngoại lệ có người nhận, bước tiếp và audit; cuối ca đối soát cả bản ghi thủ công, sự cố và case mở; correction giữ lịch sử.

Giao diện Flutter ưu tiên chữ/trạng thái dễ đọc, thao tác chính rõ ràng, phản hồi lỗi và bước tiếp theo cụ thể. Màn hình tại cửa chỉ hiển thị thông tin tối thiểu theo quyền. Thiết kế chi tiết UX, thiết bị, cách build và kết quả thử sẽ bổ sung cùng mã T-018.

## Mốc 1 — lõi có thể mở rộng

- [Backend](../../backend/README.md): mô hình ca/phòng/context, quyền operator/reviewer, roster theo phiên bản, attempt, review case, check-in và audit; API v1 mới cho health, danh sách context, tạo/đọc attempt.
- [Flutter](../../mobile/README.md): Material 3, màn hình trạng thái kết nối và khung thao tác tiếp nhận; nút bắt đầu còn khóa trong khi chưa có đăng nhập, context và camera.
- Lượt tra cứu đúng hồ sơ chỉ ở `IN_PROGRESS`; trường hợp thiếu/mơ hồ/sai phòng vào `REVIEW_PENDING`. Chưa ghi check-in, không suy ra quyền vào phòng hoặc attendance.
- Kiểm thử hiện tại dùng SQLite trong bộ nhớ cho backend; cần PostgreSQL thật và thiết bị/emulator cho chuỗi end-to-end.

## Điều kiện trước khi gọi là chạy được

- Chọn và ghi rõ AI chạy trên thiết bị hay server sau khi kiểm thiết bị đích và phương án mất mạng; hiện chưa chốt.
- Chọn profile nghiệp vụ giả lập đã duyệt để kiểm E3; rà tám góp ý T-008 về quyền, case, policy/roster, override, arrival và correction.
- Kiểm chuỗi mở app → camera → xác minh → ghi attempt/check-in hoặc review → xem kết quả trên thiết bị/emulator được nêu tên; ghi nguồn dữ liệu/weight, cấu hình, kết quả và giới hạn.
- Không commit ảnh khuôn mặt, danh tính cá nhân, embedding, weight, mật khẩu hoặc file môi trường. Dữ liệu thử nghiệp vụ dùng fixture giả lập; nguồn AI và file ngoài Git theo [external-assets](../00-project/external-assets.md).
