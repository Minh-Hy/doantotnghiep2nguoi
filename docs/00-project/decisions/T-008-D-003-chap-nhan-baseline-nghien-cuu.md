# D-003 — Chấp nhận T-008 làm mốc nghiệp vụ generic cho nghiên cứu

- **Ngày:** 2026-09-28.
- **Người xác nhận:** Quốc An, thông báo trong cuộc trò chuyện rằng Minh Hy đã review T-008 và thấy ổn. Đây là nguồn nhóm cung cấp; trên GitHub chưa có review `APPROVED` mới thay cho review `CHANGES_REQUESTED` ngày 2026-09-26.
- **Phạm vi quyết định:** dùng [T-008](../../01-problem/T-008-requirements.md) làm mốc *Generic Exam Entry Business Baseline* cho phân rã capability, nghiên cứu T-009–T-012 và lập kế hoạch stage tiếp theo; cho phép đưa PR #3 vào `main` cùng giới hạn được ghi ở đây.

## Vì sao quyết định này đủ cho bước tiếp

Nhóm đã chọn bài toán cửa phòng thi ở D-001 và hướng survey ở D-002. T-008 diễn đạt luồng generic, actor/quyền, trạng thái, ngoại lệ, dữ liệu và câu hỏi kỹ thuật mà chưa gán quy chế một kỳ thi cụ thể. T-009–T-012 đã dùng đúng phạm vi đó để kiểm candidate, đo baseline B0 và phân tích lỗi; các phép thử không cần profile application hoàn chỉnh để trả lời câu hỏi thành phần. Vì vậy nhóm chấp nhận cấu trúc T-008 làm nguồn truy ngược cho nghiên cứu tiếp.

## Giới hạn và việc cần xử lý khi xây application

Review của Minh Hy trên PR #3 ngày 2026-09-26 còn 6 góp ý P1 và 2 góp ý P2 về trùng lượt/quyền xem, case chưa có hồ sơ duy nhất, hiệu lực policy/roster, giới hạn override, arrival ngoài cửa sổ, correction, nhiều điều kiện đồng thời và khóa registration. Quyết định này **không xác nhận các góp ý đã được sửa** và không đặt giá trị policy, quyền triển khai, hiệu quả giảm nhân sự, model hay dataset cuối. Trước khi dùng T-008 như contract để thực thi các nhánh tương ứng của app hoặc chấm E3, nhóm phải rà các góp ý, chọn profile nghiệp vụ và ghi lại thay đổi BR/FR/SC/TQ có liên quan.

Quốc An xác nhận bài toán AI chính vẫn là **người khai báo hồ sơ → chọn đúng người trong khung hình có thể nhiều mặt → xác minh 1:1 → trả kết quả hoặc chưa kết luận**. Các chi tiết nghiệp vụ nêu trên được chuyển sang phần application do Minh Hy phụ trách nghiên cứu và hoàn thiện. Chúng không tự động mở lại lựa chọn pipeline B0 hay các kết quả đo AI đã có. Chỉ khi thay đổi trực tiếp đầu vào, đối tượng mục tiêu hoặc output cần xác minh thì rà lại capability/protocol AI bị ảnh hưởng.

**Bước sau:** các task nghiên cứu truy ngược quyết định từ T-008; nhánh application của Minh Hy xử lý các điểm review theo phạm vi triển khai. Nếu thay đổi capability cốt lõi, đối chiếu lại protocol và evidence đã tạo.
