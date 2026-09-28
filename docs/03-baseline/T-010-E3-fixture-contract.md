# T-010 — E3 fixture contract từ T-008

**Ngày thiết kế:** 2026-09-27. **Nguồn nghiệp vụ:** T-008 PR #3 commit `c235b80`, được Quốc An chỉ đạo dùng làm mốc cho downstream trong lượt này. **Trạng thái:** catalog fixture và invariant generic đã thiết kế; **chưa có policy profile được phê duyệt, implementation hoặc kết quả pass/fail**. Đây là phần cụ thể hóa E3 trong [T-010-protocol.md](T-010-protocol.md), không thay đổi T-008.

## Vì sao E3 tồn tại

T-011 E1/E2 chỉ đo component thị giác. T-008 còn yêu cầu xác định hồ sơ, kiểm ca/phòng, xử lý bằng chứng không chắc, chống trùng, fallback, quyền quyết định, đối soát và correction. Những việc này cần **fixture logic nghiệp vụ** thay vì thêm dataset mặt. E3 kiểm các invariant đó trên ứng dụng/workflow sau khi có implementation; kết quả là pass/fail theo fixture và audit, không phải accuracy nhận diện.

**Ranh giới input:** `identity_evidence_outcome` là `satisfied | unmet | unavailable | inconclusive` theo IdentityEvidenceRequirement của profile. Fixture generic không buộc phải dùng ảnh mặt. Nếu profile nghiên cứu chọn mặt, tình huống “không thấy mặt” ánh xạ sang `unavailable` hoặc `inconclusive` theo cách xử lý đã duyệt; không tự suy `unmet` hay giả mạo.

## Profile fixture cần có trước khi chấm

Một test profile là dữ liệu giả lập **chỉ dùng để thử**, không phải quy chế kỳ thi thật. Mỗi fixture phải pin:

- exam/session/room context, registration key và roster/policy version có hiệu lực;
- IdentityEvidenceRequirement và cách biểu diễn bốn outcome;
- ArrivalWindow/LatePolicy, RetryPolicy, DecisionAuthority/OverrideAuthority;
- ManualFallbackPolicy, AttendanceDefinition, CorrectionAuthority và ReEntryPolicy nếu bật;
- actor/role nào được thực hiện từng quyết định trong profile;
- nguồn dữ liệu, event time và recorded time, bao gồm trường hợp đồng hồ không đáng tin;
- trạng thái trước: attempt, check-in, entry authorization (hoặc `not_applicable`), attendance;
- event đầu vào, trạng thái/kết quả mong đợi, audit event và T-008 SC/BR/FR/TQ.

Người phê duyệt profile phải được ghi cùng ngày/phiên bản **trước khi chạy**. Nếu policy cần cho một kết luận bị thiếu/mâu thuẫn, fixture mong đợi giữ kết luận đó unresolved/review, không tự điền default. Catalog dưới đây chỉ khóa invariant không phụ thuộc giá trị policy; outcome phụ thuộc profile ở cột riêng.

## Catalog fixture tối thiểu

| ID / T-008 trace | Input và trạng thái trước | Invariant có thể kiểm ở generic baseline | Giá trị/outcome phải lấy từ profile |
|---|---|---|---|
| E3-F01 — SC-001; BR-002/005/006; FR-003/006/007; TQ-002/003 | Một registration rõ, đúng context, bằng chứng `satisfied`, chưa có check-in. | Tạo attempt có audit; chỉ tạo tối đa một check-in hiệu lực nếu mọi điều kiện và quyền được thỏa; entry authorization riêng; attendance chưa tự final. | Hệ thống hay người có quyền ghi check-in; entry thuộc scope không; AttendanceDefinition. |
| E3-F02 — SC-012/022; BR-002/008; FR-003/009; TQ-001/003 | Lookup không có record hoặc có nhiều record. | Vẫn giữ attempt/case dù chưa gắn registration; không tạo registration giả hoặc check-in hiệu lực; case có vai trò nhận và bước tiếp. | Ai xác minh nguồn, cách liên kết sau khi làm rõ. |
| E3-F03 — SC-002/003; BR-001/003; FR-004/009; TQ-004 | Registration thuộc ca/phòng khác context đang phục vụ. | Ghi discrepancy và roster version, chuyển xử lý đúng quyền; không lặng lẽ hoàn tất thường lệ ở context sai. | Có cho chuyển/ngoại lệ không, ai quyết. |
| E3-F04 — SC-004/023; BR-004/016; FR-005/018; TQ-004 | Arrival time so với policy, hoặc đồng hồ/context không tin cậy. | Giữ observed time riêng với cờ late và quyền tiếp tục; thiếu mốc/giờ tin cậy không tự kết luận late/cho vào. | Mốc, late outcome, người có quyền xử lý. |
| E3-F05 — SC-006/007; BR-005/008; FR-006/009; TQ-002/003 | Evidence `unmet`, `unavailable` hoặc `inconclusive`; tạo ba biến thể. | Lưu đúng loại outcome; không chuyển thiếu/chưa rõ thành success hoặc cáo buộc giả mạo; tạo review/fallback có người nhận. | Loại bằng chứng, retry, decision authority. |
| E3-F06 — SC-008/009/020; BR-007/014; FR-008/015; TQ-005 | Attempt lặp, kết quả ghi trước hoặc retry sau gián đoạn chưa biết commit thành công. | Giữ từng attempt; tra kết quả hiệu lực trước khi ghi tiếp; không có hai check-in hiệu lực cho cùng registration/session hoặc đếm attendance lặp. | Re-entry và xử lý kết quả mâu thuẫn. |
| E3-F07 — SC-010/011; BR-010; FR-011/018; TQ-006 | Thiết bị hoặc nguồn roster không khả dụng, có bản ghi fallback khi policy cho phép. | Ghi gián đoạn/nguồn/thời điểm/actor; khi phục hồi đối soát, không tự ghi đè xung đột hay biến thiếu dữ liệu thành success. | Ai được fallback, bằng chứng thay thế và bước sync. |
| E3-F08 — SC-013/024; BR-006/008/009; FR-007/009/010; TQ-003/004 | Có đề nghị override nhưng actor thiếu quyền, hoặc không liên hệ được người có quyền. | Không áp dụng override trái quyền; giữ pending và tuyến escalation, lưu yêu cầu/lý do/actor. | Rule nào cho override và ai có quyền. |
| E3-F09 — SC-018/023; BR-001/016; FR-001/002/018; TQ-001/004/007 | Roster/policy/context đổi khi đã có attempt hoặc kết quả trước. | Gắn quyết định với version/hiệu lực đã dùng; xác định kết quả bị ảnh hưởng để review, không viết lại lịch sử im lặng. | Thời điểm hiệu lực và quyền duyệt cập nhật. |
| E3-F10 — SC-014/019; BR-011/012/017; FR-012/013; TQ-007 | Đóng routine intake khi thiếu check-in điện tử hoặc case còn mở. | Thu nguồn điện tử/thủ công và khoảng gián đoạn; không suy absent chỉ từ thiếu event; case có người nhận, attendance có thể `UNDETERMINED`. | AttendanceDefinition, bằng chứng đủ để xác nhận present/absent và người duyệt. |
| E3-F11 — SC-015/016; BR-012/013; FR-013/014/017; TQ-007 | Có bằng chứng mới phủ định check-in hoặc absence/report đã phát hành. | Mở correction riêng override; giữ bản gốc, actor/lý do/trước–sau, rà hồ sơ/báo cáo và entry authorization bị ảnh hưởng. | Ai được sửa, nguồn bằng chứng và cách phát hành lại. |
| E3-F12 — SC-021/017; BR-007/014; FR-008/015; TQ-005 | Candidate bỏ dở lượt rồi quay lại, hoặc yêu cầu tái nhập sau check-in. | Lượt cũ `INTERRUPTED` không thành success; lượt mới có liên kết; không tự tạo check-in/attendance thứ hai. | ReEntryPolicy và quyền quyết định nếu feature bật. |

## Cách chạy và báo kết quả sau này

1. Ghi fixture/profile bất biến trước run; mỗi fixture có trạng thái đầu vào và expected state/audit event cụ thể. Một catalog row có thể tạo nhiều case để tách điều kiện.
2. Chạy **business logic/app** với input giả lập, không cần ảnh người thật. Tách kết quả attempt, effective check-in, entry authorization và attendance; situation flags là field độc lập, override khác correction.
3. Với mỗi case báo `pass/fail/not-runnable`, chênh lệch actual–expected và evidence event. `not-runnable` khi chưa có implementation/profile không được tính là pass.
4. Đếm số case theo SC/BR/FR/TQ đã cover; không gộp phần trăm fixture pass với AP E1 hoặc FMR/FNMR E2 thành một accuracy hệ thống.
5. Nếu T-008 hoặc profile được sửa sau này, tạo revision fixture và chạy lại phần bị ảnh hưởng; không sửa expected outcome sau khi xem actual để làm test pass.

**Quyết định hiện tại:** catalog E3 đã truy được về T-008 và đủ để chuẩn bị input/expected invariant. Chưa chấm vì profile thử chưa được phê duyệt và chưa có implementation. Không phát minh quy chế kỳ thi, loại biometric, ngưỡng hoặc quyền override.
