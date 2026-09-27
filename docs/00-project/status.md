# Trạng thái dự án

- Cập nhật: 2026-09-27
- Giai đoạn: phạm vi bài toán 01 đã được nhóm chọn; khảo sát 02 đã chọn hướng; baseline nghiên cứu T-011 có E1/E2/M1 tham chiếu trong PR #7; phân tích lỗi T-012 hoàn tất phạm vi hiện tại trong PR #8.
- Thành viên: Quốc An (TV-A), Minh Hy (TV-B).

## Đã làm và đã chọn

- **T-004:** Quốc An xác nhận mình và Minh Hy chọn đề tài T-002: thiết bị kiểm tra thí sinh tại cửa phòng thi, có mã khai báo và xác minh mặt 1:1. [D-001](decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md) và [scope](../01-problem/T-004-scope.md) ghi lý do, phạm vi, nguồn xác nhận và giới hạn. T-003 của Minh Hy là đề xuất độc lập để so sánh, không là bài toán chính.
- **T-005 ở mức Survey:** [bộ tài liệu Quốc An](../02-survey/README.md) đã có phân rã S0–S11, yêu cầu/shortlist dataset theo stage, model family/candidate và thiết kế baseline/thí nghiệm. [T-007](../02-survey/T-007-selection.md) chọn hướng này làm cơ sở nghiên cứu vì khớp T-004; [D-002](decisions/T-007-D-002-chon-huong-khao-sat-t005.md) ghi quyết định. Khảo sát T-006 của Minh Hy vẫn được giữ làm nguồn đối chiếu.
- [PR #1](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/1) chứa T-002/T-005 và hai quyết định nhóm T-004/T-007; [PR #2](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/2) giữ đề xuất độc lập T-003/T-006 để đối chiếu. Hai quyết định đã được nhóm chốt theo xác nhận của Quốc An.

## Baseline nghiên cứu đang có

- T-008 [PR #3](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3) được Quốc An xác nhận **đủ xác định bài toán cho nghiên cứu**; các góp ý chi tiết của Minh Hy về policy/case/authority/correction được giữ để xử lý khi xây app và trước khi chấm E3 theo một profile nghiệp vụ cụ thể. Chúng không chặn E1/E2/T-012 hiện tại.
- T-009 [PR #5](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/5) kiểm ứng viên dữ liệu/weight; T-010 [PR #6](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6) đặt protocol E1/E2/E3/M1. Hai PR này là đầu vào nghiên cứu, không tự động là quyết định model/dataset cuối.
- T-011 [PR #7](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/7) có [mốc baseline nghiên cứu](../03-baseline/T-011-baseline-summary.md): E1 ba detector trên 3.226 ảnh WIDER, E2 MBF/R50 trên 4.215 cặp XQLFW hợp lệ và phép kiểm ngưỡng tách danh tính custom trên 3.138 cặp hợp lệ, M1 timing detection trên cùng CPU runner. Các kết quả chỉ có giá trị trong protocol/cấu hình đã ghi, chưa là lựa chọn triển khai. Theo phạm vi Quốc An xác nhận 27/09, chi tiết E3/app và phép đo thiết bị đích để giai đoạn sau; không gọi là đã kiểm đạt.
- T-012 [PR #8](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/8) đối chiếu lỗi E1 theo cỡ mặt, ba outcome E2, phép kiểm split tách danh tính và M1 tham chiếu. [Phân tích lỗi](../03-baseline/T-012-error-analysis.md) ưu tiên câu hỏi S4 chọn đúng người mục tiêu/giữ trạng thái chưa kết luận, đồng thời nêu điều kiện dữ liệu và phép thử tiếp. Đây là quyết định về **câu hỏi nghiên cứu kế tiếp**, chưa chọn rule/model triển khai.
- **Phạm vi dữ liệu S4 (Quốc An xác nhận 27/09):** chỉ dùng nguồn có sẵn, không thu mới. [Audit LTFT](../03-baseline/T-012-S4-ltft-label-audit.md) xác nhận nhãn nhiều mặt ở ChokePoint S5, nhưng archive video Zenodo không khớp frame/hướng dẫn ghép LTFT; proxy **có ảnh** chưa chạy được. [Proxy chỉ dùng bbox](../03-baseline/runs/T-012-S4-ltft-box-proxy.md) đã chạy trên 1.024 cửa sổ–ID, chỉ kiểm liên kết hình học với box khởi đầu do nhãn cấp. Nguồn thiếu claim–actor theo lượt; X-012-A nghiệp vụ chưa chạy và chưa chọn rule/model cuối.
- [D1 đường đi P1](../03-baseline/runs/T-012-S4-ltft-path-diagnostic.md) là chẩn đoán hậu nghiệm: 41/1.024 cửa sổ từng chọn sai ID ở frame giữa, 38 còn sai cuối. Cả 41 lần sai đầu khi annotation không có box target hợp lệ; đây là rủi ro mất dấu trong **proxy**, chưa là đo người vắng hay lỗi check-in.
- [D2 kiểm nhãn thô](../03-baseline/runs/T-012-S4-ltft-faceflag-audit.md) tách 41 lần sai đầu: 0 còn target ID với `face=0`, 41 không có target ID trong dòng gốc. Nguyên nhân thiếu ID và cách tránh chọn nhầm trong ứng dụng vẫn chưa được kiểm.
- **Điểm dừng X-012-A:** các nguồn đã rà chưa có bộ được kiểm đủ claim–actor và nhãn nhiều người theo lượt; [readiness S4](../03-baseline/T-012-S4-experiment-readiness.md) ghi rõ từng gap. Không tiếp tục vòng tìm kiếm/lặp proxy khi không có nguồn mới phù hợp; T-011/T-012 vẫn hoàn tất đúng phạm vi nghiên cứu, không tuyên bố hoàn tất ứng dụng.

## Chưa có bằng chứng để chốt kỹ thuật cuối

T-005 **hoàn thiện phần phân tích/survey**. Quốc An xác nhận T-008 đủ mốc bài toán cho nghiên cứu và T-009/T-010 hoàn tất phạm vi hiện tại; góp ý nghiệp vụ chi tiết của T-008 để khi xây app. T-011 đã bổ sung kiểm nguồn/file, pin cấu hình, E1/E2 và M1 tham chiếu; vẫn chưa có main test phù hợp miền cửa phòng thi, phép đo trên thiết bị đích, kiểm E3/app hoặc phân tích bottleneck đủ để chốt kỹ thuật. Shortlist dataset/model, threshold, hướng tối ưu và mobile stack vẫn là candidate/câu hỏi. Chưa có pilot để tuyên bố giảm nhân sự; dữ liệu công khai và fixture giả lập không thay thế đánh giá tại kỳ thi thật.

## Bước tiếp theo theo thứ tự

1. **Chuẩn bị X-012-A:** tìm tập giao dịch/camera được phép dùng có nhãn người mục tiêu hoặc không có mục tiêu; khóa cách gán nhãn, split, ba outcome và mức rủi ro được chấp nhận trước khi thử A0/A1/A2. Nếu chưa có nhãn, giữ thí nghiệm ở trạng thái chưa chạy.
2. **Bằng chứng triển khai còn thiếu:** main test xác minh gần miền cửa phòng, thiết bị đích để đo encoder/attempt, E3/app logic theo policy sau và As-Is thực địa nếu muốn tuyên bố giảm công sức. Không lấy timing GitHub runner làm kết luận triển khai.
3. **Experiment rồi mới chốt kỹ thuật:** từ uncertainty và rủi ro T-012, đặt điều kiện kiểm và acceptance criteria trước experiment; dùng kết quả đó để cân nhắc candidate/configuration, threshold và kiến trúc app.

**Task, người phụ trách và trạng thái chi tiết:** [Google Sheet chung](https://docs.google.com/spreadsheets/d/14BQCQ_LbGkZS15Grfi4AZNWBX15h479XjoyQvP9jHcU/edit?gid=0#gid=0). Trang này tóm tắt tiến độ và việc kế tiếp, không sao chép bảng task.
