# D-005 — Phạm vi bản đầu T-018 và AI trên Android

- **Ngày ghi nhận:** 2026-09-28.
- **Người chốt:** Minh Hy, người phụ trách T-018 theo Sheet; Quốc An review trong PR T-018.
- **Nguồn:** câu trả lời của Minh Hy trong cuộc trò chuyện ngày 2026-09-28 cho bảy câu hỏi chốt phạm vi triển khai sau [kế hoạch T-018](../../06-mobile/T-018-ke-hoach-trien-khai-app.md).
- **Phạm vi:** app tham chiếu cho **một kỳ thi trong trường đại học**, ưu tiên Android. Minh Hy chọn **ca thi học phần giả lập trước** để xây/kiểm luồng; tên trường, môn, kỳ thi thật và quy chế cụ thể chưa được cung cấp. Profile giả lập không được gọi là policy của trường.

## Những điểm đã chọn

1. AI B0 tham chiếu chạy **trên điện thoại**, để bước xác minh không phụ thuộc kết nối mạng. Backend Django/PostgreSQL vẫn là nguồn dữ liệu nghiệp vụ và check-in. Khi mất mạng, thao tác ở máy giữ trạng thái **chờ đồng bộ**; chỉ sau khi backend nhận, kiểm điều kiện và nhân sự xác nhận thì mới là check-in có hiệu lực. Chi tiết hàng đợi/đồng bộ còn phải thiết kế và thử. Chọn vị trí AI không tự chứng minh B0 chạy đạt tốc độ/bộ nhớ trên thiết bị đích; phải đo trên máy được nêu tên.
2. Giai đoạn đầu dùng roster giả lập và ảnh mẫu được phép sử dụng, giữ ảnh/weight/embedding ngoài Git theo [external-assets](../external-assets.md). Chưa có dữ liệu kỳ thi thật.
3. Bản đầu chỉ **ghi check-in hoặc chuyển ngoại lệ**; không tự kết luận attendance hay cấp quyền vào phòng.
4. Khi các điều kiện được duyệt đều đạt, **nhân sự tại cửa xem kết quả và bấm xác nhận check-in**. Kết quả AI không tự ghi check-in.
5. Không tìm thấy hồ sơ, trùng mã, sai phòng hoặc xác minh không đạt được chuyển người có quyền xử lý. Không thấy mặt, nhiều mặt hoặc AI lỗi: cho thử lại **một lần**, sau đó chuyển xử lý. Quy tắc này là lựa chọn cho bản đầu; cần ghi rõ cách đếm retry, actor và evidence trong profile kiểm thử trước khi chấm E3.

## Còn phải xác định trước các nhánh phụ thuộc

- Kỳ thi đại học nào, quy chế ca/phòng/thời gian/late và ai phê duyệt profile thật. Trước mắt dùng ca thi học phần giả lập; profile kiểm thử cần được nhóm duyệt riêng trước khi chấm E3.
- Thiết kế cụ thể hàng đợi attempt/evidence trên máy, điều kiện đồng bộ/chống trùng, thời điểm nhân sự xác nhận sau đồng bộ và bảo vệ dữ liệu cục bộ. Chưa coi AI chạy offline là toàn bộ hệ thống offline.
- Thiết bị Android đích, phiên bản hệ điều hành, bộ nhớ, quyền sử dụng weight/ảnh và phép đo latency/battery trước khi chốt cách đóng gói B0.
- Vai trò/phân quyền cho reviewer, override, correction và quy tắc giờ đến của kỳ thi cụ thể vẫn theo [questions.md](../questions.md) và T-008; không tự suy từ quyết định này.

**Liên quan:** [D-004](T-018-D-004-chon-stack-app-tham-chieu.md) giữ stack Flutter + DRF + PostgreSQL và B0; D-005 bổ sung phạm vi Android/on-device và quyền xác nhận check-in. Nếu phép đo thiết bị cho thấy B0 không đáp ứng, lập kết quả và đề xuất mới để nhóm quyết định; không âm thầm đổi sang server hoặc đổi model.
