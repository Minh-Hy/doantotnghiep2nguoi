# Bàn giao T-010 — phương pháp đo đã chốt, run chờ gate

- **Người làm, ngày:** Quốc An, 2026-09-26; Minh Hy review trước khi freeze.
- **Task trên Sheet:** [T-010, dòng 11](https://docs.google.com/spreadsheets/d/14BQCQ_LbGkZS15Grfi4AZNWBX15h479XjoyQvP9jHcU/edit?gid=0#gid=0).
- **Commit/PR:** [PR #6 sẵn sàng review](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6), base main; không merge trước review.
- **File chính:** [T-010-protocol.md](../03-baseline/T-010-protocol.md), [decision logic](../03-baseline/DECISION_LOGIC.md), [README](../03-baseline/README.md).
- **Cách kiểm tra / kết quả thực tế:** đọc trace E1/E2/E3/M1 và freeze gate. XQLFW archive 195.229.543 byte, SHA-256 1AF459679FBA23A12F4D83C82A81523EB930A4AEC759EEBEFCBDDE69A678962C, kiểm CRC và đối chiếu 6.000 pairs: 0 path thiếu; cả 45/45 cặp fold có identity overlap. Không chạy model hay xem benchmark score.
- **Quyết định / giả định:** Theo yêu cầu Quốc An ngày 2026-09-26, đã tự rà và chốt phương pháp đo E1/E2/E3/M1; E2 đầu tiên dùng XQLFW 10 fold, mỗi fold đánh giá với threshold chọn từ 9 fold còn lại, MobileFaceNet làm mốc ban đầu sau khi pin cấu hình run. XQLFW chưa là main identity-disjoint test; T-008 PR #3 và T-009 PR #5 còn draft. Không có model/dataset/threshold/acceptance target cuối.
- **Điều chưa xong:** Minh Hy review T-008 và T-010; ghi điều kiện sử dụng nguồn cho phạm vi học thuật, chọn main protocol, pin preprocessing/weight/split, duyệt policy profile, thiết bị và target rủi ro. Chỉ sau đó mới freeze cho T-011; với target còn TBD chỉ được báo số liệu mô tả.
- **File ngoài Git:** archive XQLFW và file pairs chỉ ở thư mục tạm của máy kiểm tra, chưa trao cho Minh Hy; tải lại từ [nguồn tác giả](https://martlgap.github.io/xqlfw/pages/download.html) và đối chiếu hash. Không commit ảnh, tên identity, embedding hay checkpoint.

## Bổ sung E1/E3 trước run (2026-09-27)

- [T-010 E1 scoring protocol](../03-baseline/T-010-E1-scoring-protocol.md) đã đặt trước AP nội bộ WIDER validation, xử lý valid/ignored GT, matching và preflight. Nguồn dữ liệu đã được T-011 kiểm; evaluator code/wrapper chưa qua preflight nên chưa có điểm detector.
- [T-010 E3 fixture contract](../03-baseline/T-010-E3-fixture-contract.md) có 12 nhóm case trace về T-008 theo mốc Quốc An yêu cầu dùng. Đây là thiết kế input/invariant, chưa có profile được duyệt hoặc implementation để chấm pass/fail.
- Lượt này không chạy được phép thử tại máy vì helper khởi tạo tiến trình báo `helper_unknown_error: setup refresh had errors` cho cả PowerShell và Node REPL. Không coi việc ghi protocol là kết quả benchmark.

## Đính chính hash SCRFD trong E1 (2026-09-27)

[T-011 preflight run 36294478001](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294478001) phát hiện giá trị SHA-256 `det_500m.onnx` trong bảng adapter v1 bị chép sai một ký tự. ZIP `buffalo_sc.zip` đúng hash; file ONNX bên trong 2.524.817 byte có SHA-256 `5E4447F50245BBD7966BD6C0FA52938C61474A04EC7DEF48753668A9D8B4EA3A`. Đã sửa [T-010 E1 protocol](../03-baseline/T-010-E1-scoring-protocol.md) và runner T-011 trước mọi điểm AP; không đổi candidate, score threshold hoặc evaluator. [Run 36294608464](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294608464) xác nhận cả ba adapter qua preflight 8 ảnh.
