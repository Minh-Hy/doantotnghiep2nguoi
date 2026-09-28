# D-004 — Chọn stack và pipeline AI tham chiếu cho T-018

- **Trạng thái:** Minh Hy chốt phạm vi triển khai app tham chiếu T-018; Quốc An review theo phân công trên Sheet. Chưa là quyết định model AI tối ưu/cuối cùng cho kỳ thi thật.
- **Ngày ghi nhận:** 2026-09-28.
- **Người chốt:** Minh Hy, người phụ trách T-018 theo Sheet và tài khoản Git của lượt làm việc này.
- **Nguồn:** yêu cầu của Minh Hy trong cuộc trò chuyện ngày 2026-09-28: chọn `Flutter + Django REST Framework + PostgreSQL` và dùng model AI Quốc An đã chọn làm mốc B0; [T-012 B0](../../03-baseline/T-012-B0-pipeline-choice.md). Quốc An chưa review quyết định stack này trong repo.

## Lựa chọn và phạm vi

| Thành phần | Lựa chọn cho app tham chiếu |
|---|---|
| Giao diện | Flutter/Dart; giao diện hiện đại, dễ thao tác cho thiết bị tại cửa và các màn hình nhân sự theo scope T-018. |
| Backend | Python, Django và Django REST Framework để cung cấp API và thực thi workflow/quyền nghiệp vụ. |
| Cơ sở dữ liệu | PostgreSQL cho roster, attempt, check-in, case, đối soát và audit theo contract T-008. |
| AI thị giác tham chiếu | B0: SCRFD-500MF phát hiện mặt và landmark, A0 chỉ tiếp tục khi đúng một mặt, MobileFaceNet tạo embedding và xác minh 1:1. Không hoặc nhiều mặt trả `unresolved` để thử lại/chuyển người xử lý. |

Chọn B0 cho **app tham chiếu** để xây và kiểm luồng Flutter ↔ backend ↔ AI trên một pipeline đã có mã và run nghiên cứu. [D-003](T-008-D-003-chap-nhan-baseline-nghien-cuu.md) và [T-008](../../01-problem/T-008-requirements.md) vẫn là mốc nghiệp vụ: kết quả AI không tự cấp quyền vào phòng hoặc kết luận attendance; attempt, check-in, entry authorization và attendance là kết quả riêng.

## Phần còn mở

- Chưa quyết định AI chạy trên thiết bị hay server; cần thiết bị đích, yêu cầu mất mạng, quyền dùng weight/ảnh và phép đo trước khi chọn nơi chạy. Stack backend không mặc định ảnh camera phải gửi lên server.
- Chưa có model/ngưỡng tối ưu hoặc lựa chọn triển khai cuối của T-013–T-017. Khi T-017 có quyết định kỹ thuật, T-019 sẽ tích hợp và so với app tham chiếu này.
- Policy kỳ thi, quyền override/correction, hiệu lực roster và tám góp ý review T-008 còn phải xử lý theo profile ứng dụng trước khi gọi là contract vận hành hoặc chấm E3. Không mặc định thu/lưu ảnh, video hoặc embedding.
- Quốc An review lựa chọn stack và ranh giới B0 trong PR của T-018. Nếu review đổi phạm vi, cập nhật quyết định và tài liệu T-018 có liên kết hai chiều.

**Tài liệu triển khai:** [T-018 app tham chiếu](../../06-mobile/T-018-app-reference.md).
