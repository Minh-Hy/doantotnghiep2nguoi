# Logic quyết định — 01: Bài toán nghiệp vụ

File này ghi **vì sao mỗi bước của [đề xuất T-002](T-002-quoc-an-proposal.md) dẫn tới câu hỏi kỹ thuật ở [02](../02-survey/DECISION_LOGIC.md)**. Chi tiết actor, luồng và ngoại lệ nằm trong đề xuất; file này chỉ giữ chuỗi quyết định, nguồn và điều còn mở.

## Trạng thái và nguồn

- **BP-01, định hướng nhóm cung cấp ngày 2026-09-25:** thiết bị tại cửa phòng thi xử lý bước kiểm tra đầu vào thường lệ để giảm nhu cầu người chỉ đứng đối chiếu ở từng phòng; ghi nhận hợp lệ, muộn, nhầm phòng, chưa đến và ngoại lệ.
- **T-002, đề xuất cá nhân của Quốc An:** [T-002-quoc-an-proposal.md](T-002-quoc-an-proposal.md) cụ thể hóa luồng có mã dự thi, ảnh đăng ký, xác minh 1:1, kiểm tra phòng/ca/giờ và ghi lượt.
- **T-004, quyết định nhóm:** Quốc An xác nhận cả Quốc An và Minh Hy đã chốt bối cảnh cửa phòng thi. [D-001](../00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md) ghi ngày xác nhận, nguồn và giới hạn; không coi đây là xác nhận của thầy hoặc quyết định kỹ thuật cuối.

## BP-01 → hướng thiết bị tại cửa

**Context → question.** Trước ca có danh sách thí sinh, phòng, ca và ảnh đăng ký; tại cửa giám thị phải đối chiếu và ghi nhận từng lượt. Nếu nhiều phòng đều bố trí người chuyên làm bước này, công đối chiếu lặp lại. Người muộn, nhầm phòng hoặc chưa đến cần đối soát theo từng ca. Câu hỏi nghiệp vụ là: bước nào thiết bị có thể đảm nhận mà vẫn bảo đảm người có thẩm quyền xử lý ngoại lệ?

**Requirements trước solution.** Mỗi lượt phải gắn đúng người, phòng, ca, thời điểm và trạng thái; cho phép chụp lại/chuyển xử lý khi không chắc; tránh ghi trùng và lưu vết sửa sai. Quy trình kỳ thi mục tiêu phải xác định giám thị còn phải làm bước nào. Chưa có pilot hoặc phép đo chứng minh giảm nhân sự.

**Alternatives → lý do khảo sát hướng cửa.** Nhân sự đối chiếu hoàn toàn, một điểm kiểm tra tập trung, hoặc thiết bị tại từng cửa. Điểm cửa gắn trực tiếp lượt vào với phòng/ca và có thể xử lý thường lệ ngay nơi phát sinh sự kiện; đổi lại phải giải quyết camera hành lang, hàng chờ, dữ liệu phiên và xử lý ngoại lệ. Lý do này đủ để khảo sát, chưa đủ để kết luận mức tự động hóa được phép hoặc hiệu quả vận hành.

**Decision T-004.** Nhóm đã chọn hướng thiết bị tại cửa theo [D-001](../00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md). Quy chế của kỳ thi cụ thể và bằng chứng pilot vẫn cần trước khi tuyên bố thay thế bước giám thị hoặc giảm nhân sự thực tế.

## UC-01 → khai báo mã trước → xác minh 1:1

**Vì sao có bước khai báo.** Danh sách có mã duy nhất và ảnh tham chiếu cho từng thí sinh. Mã chọn đúng một hồ sơ để đối chiếu; bản thân mã không chứng minh người đứng trước camera là chủ hồ sơ. Từ đó bài toán thị giác là so người đang làm thủ tục với ảnh của **hồ sơ đã khai báo**, tức verification 1:1 trong đề xuất T-002. Identification 1:N chỉ cần nếu bỏ bước khai báo; classifier cố định theo từng thí sinh không khớp danh sách thay đổi theo kỳ thi.

**Yêu cầu kéo theo.** Cần tra hồ sơ đúng phiên; camera phải chọn mặt của người vừa khai báo dù có người nền; chất lượng ảnh đủ cho so khớp; hệ thống có kết quả không chắc/retry thay vì ép chấp nhận hoặc từ chối. Các bước này tạo ra S0–S8b trong [phân rã T-005](../02-survey/T-005-quoc-an-task-decomposition.md), chưa chọn detector hay encoder ở phase 01.

## UC-02/03 → trạng thái nghiệp vụ và ngoại lệ

Xác minh khuôn mặt **không tự trả lời** đúng phòng, đúng ca, đến muộn hay đã ghi lượt. Những câu hỏi này cần danh sách, mốc giờ và quy tắc kỳ thi; vì vậy có S9–S10 theo rule/database và audit. “Chưa đến” chỉ suy ra khi đối soát sau mốc phù hợp, không phải nhãn của một ảnh. Ảnh kém, mã không có, sai phòng, trùng lượt hoặc điểm so khớp không chắc phải có đường xử lý bởi người có thẩm quyền; chưa tự đặt chính sách cho phép/từ chối.

## Điều phải giải quyết trước khi chốt phạm vi và đo lợi ích

1. Kỳ thi mục tiêu và quy chế: mức tự động hóa nào được phép, bước nào giám thị vẫn phải làm?
2. Quy trình hiện tại có số đo nào về thời gian, nhân sự, lỗi đối chiếu và xử lý ngoại lệ?
3. Ai cung cấp/chốt danh sách và ảnh tham chiếu, ai sửa/duyệt một trạng thái sai?
4. Quy tắc giờ vào, muộn, nhầm phòng, trùng lượt, chưa đến và trường hợp đặc biệt là gì?
5. Với dữ liệu công khai cho thị giác và hồ sơ giả lập cho nghiệp vụ, kết luận nào chỉ là benchmark/prototype, kết luận nào cần pilot thực địa?

**Vì sao có 02:** các câu hỏi trên xác định output và rủi ro của từng bước. Survey phải suy ra stage requirements, data/technical requirements, candidate và experiment từ chúng; không bắt đầu bằng một dataset/model đã có. Các giả định còn mở tiếp tục ở [questions.md](../00-project/questions.md) cho tới khi có nguồn và quyết định.

## T-008 → generic business baseline → câu hỏi kỹ thuật

**Context / Question.** D-001 chọn bối cảnh cửa phòng thi, nhưng nhóm chưa chọn kỳ thi hay quy chế cụ thể. [T-008](T-008-requirements.md) định nghĩa workflow tham chiếu: hệ thống cần phục vụ nghiệp vụ nào trước khi đánh giá cách thực hiện?

**Requirements / Alternatives.** Từ BP-001–BP-004, T-008 suy ra sáu Core Decisions, các bước P-001–P-012, ngoại lệ SC-001–SC-024, BR-001–BR-017 và FR-001–FR-019. Tách cấu trúc nghiệp vụ dùng chung, policy cấu hình theo kỳ thi và triển khai kỹ thuật. Thiết bị chỉ tự kết luận trong quyền được duyệt; không chắc hoặc thiếu quyền thì chuyển review/giữ unresolved. Attempt, check-in, entry authorization và attendance có nghĩa riêng.

**Evidence / Review status.** Đây là thiết kế generic theo yêu cầu refactor ngày 2026-09-26 và [D-003](../00-project/decisions/T-008-D-003-chap-nhan-baseline-nghien-cuu.md) ghi nhận chấp nhận làm mốc nghiên cứu ngày 2026-09-28. Nó chưa phải quy trình As-Is của một tổ chức hay profile ứng dụng đã duyệt. Tám góp ý review chi tiết của Minh Hy được chuyển sang phần application; các thay đổi policy/case/authority chỉ kéo theo rà lại AI nếu đổi đầu vào, đối tượng hoặc output xác minh. Thiếu As-Is thực địa chỉ giới hạn tuyên bố giảm nhân sự.

**Why / Next.** T-008 đi từ scenario → BR → FR/capability → TQ-001–TQ-008. T-009 audit mức khả dụng và phù hợp của candidate T-005/T-007 với capability liên quan; T-010 đặt profile, câu hỏi, metric và tiêu chí chấp nhận trước thử; T-011 tạo evidence; T-012 phân tích lỗi. Survey chọn candidate đáng thử, chưa chốt giải pháp cuối. D-001/D-002 là hướng nhóm đã chọn, không biến lựa chọn kỹ thuật cũ thành business fact. Nguyên tắc Business decision / System decision / Human-authorized decision / Technical implementation được duy trì trong [workflow](../00-project/workflow.md).
