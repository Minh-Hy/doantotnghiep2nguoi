# T-008 — Bàn giao bản review BA, task còn đang làm

> **Ghi chú cập nhật 2026-09-26:** đây là bàn giao lịch sử của bản BA trước refactor. [T-008 hiện tại](../01-problem/T-008-requirements.md) đã chuyển thành Generic Exam Entry Business Baseline; G9/GI/GO và yêu cầu có As-Is để freeze bên dưới không còn là kế hoạch hiện hành. Bước tiếp theo là Quốc An và Minh Hy review cấu trúc generic, authority, policy/state và downstream contract ở mục 20; task vẫn chưa freeze.

> **Cập nhật 2026-09-28:** [D-003](../00-project/decisions/T-008-D-003-chap-nhan-baseline-nghien-cuu.md) chấp nhận T-008 làm mốc generic cho nghiên cứu theo xác nhận của Quốc An rằng Minh Hy đã review và đồng ý. Tám góp ý trong review GitHub cũ chưa được sửa; phần policy/case/authority/correction chuyển sang nhánh app của Minh Hy và trước E3 theo profile. Các dòng bên dưới giữ nguyên như lịch sử bàn giao ngày 26/09, không phải trạng thái hiện tại.

- **Ngày / người làm:** 2026-09-26, Quốc An với AI hỗ trợ; Minh Hy là người review theo Sheet.
- **Trạng thái:** bàn giao phần cập nhật tài liệu để nhóm review; chưa hoàn tất/freeze T-008.
- **Nguồn:** bản phân tích 20 mục đã thảo luận và phản hồi BA của Quốc An trong chat: giữ nền tảng, bổ sung Core Decisions, As-Is và gates, không viết lại từ đầu để chọn công nghệ.
- **PR:** [PR #3 — draft](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3); commit của lần cập nhật trong lịch sử PR.
- **Đầu ra:** [T-008-requirements.md](../01-problem/T-008-requirements.md); logic phase 01/02; hướng dẫn đọc, status/questions và nguyên tắc thẩm quyền trong workflow.
- **Thay đổi:** đưa bản phân tích trong chat vào file T-008; giữ 24 SC, 17 BR, 19 FR, 10 NFR, 12 risk và 23 OQ; thêm lớp đọc nhanh, kế hoạch thu bằng chứng As-Is, phân loại FR theo độ sẵn sàng, G9/GI/GO và điều kiện freeze. Mục 19 nối ID BR-01–BR-08 của bản repo cũ sang ID mới để không mất traceability.
- **Kiểm tra:** đủ 20 mục và dải ID; tham chiếu ID có định nghĩa; bảng đủ cột; code fence Mermaid cân bằng; liên kết file Markdown tương đối tồn tại; đọc lại authority, absent/check-in, fallback và gate. Chưa chạy pilot hoặc xác minh quy chế; chưa render Mermaid bằng renderer.
- **Còn thiếu:** As-Is thực địa; định nghĩa attendance, bằng chứng xác minh, hồ sơ/roster và ranh giới quyền được nhóm duyệt; người/cách fallback thực tế.
- **Bước tiếp:** Quốc An tổng hợp câu trả lời G9 theo mục 18, Minh Hy review. T-009 có thể audit nguồn/khả dụng song song, nhưng không chốt mức phù hợp phụ thuộc gate còn mở. Freeze nghiên cứu theo mục 20; chưa tuyên bố được triển khai thật hoặc giảm nhân sự.
- **File ngoài Git:** không có dữ liệu/tài liệu đầu vào mới cần trao riêng.
