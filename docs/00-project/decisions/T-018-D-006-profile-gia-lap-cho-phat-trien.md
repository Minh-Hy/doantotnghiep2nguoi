# D-006 — Dùng profile ca thi giả lập để phát triển T-018

- **Ngày ghi nhận:** 2026-09-29.
- **Người chọn:** Minh Hy, người phụ trách T-018. Quốc An review trong PR T-018.
- **Nguồn:** Minh Hy trả lời trong cuộc trò chuyện ngày 2026-09-29: “Profile ca thi thì theo những gì bạn đề xuất đi”. Phương án được nhắc đến là [profile T-018](../../06-mobile/T-018-profile-ca-thi-gia-lap.md).
- **Phạm vi quyết định:** chọn profile đó làm **fixture và hợp đồng phát triển tạm thời** cho một ca học phần, một phòng, roster và mã giả. Quyết định này không xác nhận quy chế của trường, không phê duyệt policy để mở ca/check-in và chưa khóa expected outcome để chấm E3.

## Nội dung được chọn cho mốc phát triển

1. Dùng context `EXAM-SIM-01` / `SESSION-SIM-01` / `ROOM-SIM-01`, hai registration/mã `SIM001`, `SIM002`, roster/policy có version nháp. Giữ ca ở `SETUP` cho đến khi các điều kiện mở ca được duyệt.
2. Giữ attempt, check-in, quyền vào phòng và attendance là bốn kết quả riêng. Check-in chỉ có hiệu lực sau khi backend kiểm điều kiện và operator được phân quyền xác nhận; khi mất mạng giữ `PENDING_SYNC`.
3. Dùng bốn outcome AI `satisfied`, `unmet`, `unavailable`, `inconclusive`; không mặt/nhiều mặt/AI lỗi được thử lại một lần rồi chuyển review theo profile. AI không tự ghi check-in.
4. Dùng các nhánh, mã lỗi và dữ liệu audit trong profile làm **đầu vào thiết kế**. Chỉ biến thành test oracle E3 sau khi Quốc An và Minh Hy review phiên bản profile/fixture, quyền và điều kiện áp dụng.

## Giới hạn còn mở

Quy tắc giờ đến, quyền reviewer/override/correction, retention, fallback, thiết bị Android, policy kỳ thi thật, nguồn roster thật và tiêu chí AI vẫn là `TBD` như trong [câu hỏi mở](../questions.md). Không tự gán giá trị để chuyển context sang `OPEN`. Khi nhóm chốt phần nào, cập nhật profile có phiên bản, người/ngày duyệt, nguồn và các fixture E3 bị ảnh hưởng.
