# T-018 — App cửa phòng thi tham chiếu

- **Trạng thái:** mã thử nghiệm cũ đã gỡ; mốc mới có Django API/schema PostgreSQL riêng và Flutter kiểm kết nối, theo [tiến độ thực tế](T-018-ke-hoach-trien-khai-app.md#6-tiến-độ-thực-tế--cập-nhật-2026-09-29). Camera/AI/check-in chưa được triển khai hoặc kiểm tích hợp.
- **Quyết định:** [D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md).
- **Phạm vi bản đầu:** [D-005](../00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md) chọn Android, AI trên điện thoại, check-in do nhân sự xác nhận.
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

## Trạng thái triển khai

Mã M1/M2 trước đây đã có test và migration cục bộ, được ghi trong [bàn giao M1](../handoffs/T-018-core-foundation.md) và [bàn giao M2](../handoffs/T-018-auth-context.md). Theo yêu cầu ngày 2026-09-29, hai thư mục mã đã được gỡ khỏi nhánh để Minh Hy tự làm lại theo [hướng dẫn thủ công](T-018-huong-dan-lam-thu-cong.md). Các kết quả kiểm trước đây không xác nhận mã mới; PostgreSQL `exam_entry` trên máy Minh Hy chưa bị xóa.

Theo yêu cầu tiếp theo của Minh Hy, mốc chạy thử đã được dựng mới với bảng trong schema `exam_entry_app`, API health/readiness/login/logout/context/attempt, lệnh seed fixture giả và Flutter trạng thái/đăng nhập/xem ca. [Hướng dẫn VS Code](T-018-vscode-local-setup.md) có lệnh và URL kiểm; nút tiếp nhận còn khóa trong khi M0 chưa được duyệt. Mốc M1/M2 chưa hoàn tất.

## Điều kiện trước khi gọi là chạy được

- Đo B0 trên thiết bị Android đích; chốt cách đóng gói và xử lý check-in khi mất mạng. AI trên máy không đồng nghĩa toàn bộ workflow đã offline.
- Chọn profile nghiệp vụ giả lập đã duyệt để kiểm E3; rà tám góp ý T-008 về quyền, case, policy/roster, override, arrival và correction.
- Kiểm chuỗi mở app → camera → xác minh → ghi attempt/check-in hoặc review → xem kết quả trên thiết bị/emulator được nêu tên; ghi nguồn dữ liệu/weight, cấu hình, kết quả và giới hạn.
- Không commit ảnh khuôn mặt, danh tính cá nhân, embedding, weight, mật khẩu hoặc file môi trường. Dữ liệu thử nghiệp vụ dùng fixture giả lập; nguồn AI và file ngoài Git theo [external-assets](../00-project/external-assets.md).
