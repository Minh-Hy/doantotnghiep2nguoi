# Trạng thái dự án

- Cập nhật: 2026-09-27
- Giai đoạn: phạm vi bài toán 01 đã được nhóm chọn; khảo sát 02 đã chọn hướng; baseline T-011 đang chạy trong draft PR #7.
- Thành viên: Quốc An (TV-A), Minh Hy (TV-B).

## Đã làm và đã chọn

- **T-004:** Quốc An xác nhận mình và Minh Hy chọn đề tài T-002: thiết bị kiểm tra thí sinh tại cửa phòng thi, có mã khai báo và xác minh mặt 1:1. [D-001](decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md) và [scope](../01-problem/T-004-scope.md) ghi lý do, phạm vi, nguồn xác nhận và giới hạn. T-003 của Minh Hy là đề xuất độc lập để so sánh, không là bài toán chính.
- **T-005 ở mức Survey:** [bộ tài liệu Quốc An](../02-survey/README.md) đã có phân rã S0–S11, yêu cầu/shortlist dataset theo stage, model family/candidate và thiết kế baseline/thí nghiệm. [T-007](../02-survey/T-007-selection.md) chọn hướng này làm cơ sở nghiên cứu vì khớp T-004; [D-002](decisions/T-007-D-002-chon-huong-khao-sat-t005.md) ghi quyết định. Khảo sát T-006 của Minh Hy vẫn được giữ làm nguồn đối chiếu.
- [PR #1](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/1) chứa T-002/T-005 và hai quyết định nhóm T-004/T-007; [PR #2](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/2) giữ đề xuất độc lập T-003/T-006 để đối chiếu. Hai quyết định đã được nhóm chốt theo xác nhận của Quốc An.

## Baseline nghiên cứu đang có

- T-008 [PR #3](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3) được Quốc An cho phép dùng làm business baseline tạm để tiếp tục; phản hồi review của Minh Hy vẫn cần được xử lý trước khi chốt nghiệp vụ cho E3.
- T-009 [PR #5](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/5) kiểm ứng viên dữ liệu/weight; T-010 [PR #6](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6) đặt protocol E1/E2/E3/M1. Hai PR này là đầu vào nghiên cứu, không tự động là quyết định model/dataset cuối.
- T-011 [draft PR #7](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/7) đã có E2 XQLFW pair-fold thăm dò trên 4.215/6.000 cặp hợp lệ và [E1 detection trên cùng 3.226 ảnh WIDER](../03-baseline/runs/T-011-E1-widerface-comparison.md): project AP YuNet 0,648304, SCRFD-500MF 0,547370, BlazeFace full-range 0,136009. Các kết quả chỉ có giá trị trong protocol và cấu hình đã ghi, chưa là lựa chọn triển khai.

## Chưa có bằng chứng để chốt kỹ thuật cuối

T-005 **hoàn thiện phần phân tích/survey**. T-009/T-010/T-011 đã bổ sung kiểm nguồn/file, pin cấu hình và một số baseline học thuật; vẫn chưa có main test phù hợp miền cửa phòng thi, phép đo trên thiết bị đích, kiểm E3/M1 đầy đủ hoặc phân tích bottleneck đủ để chốt kỹ thuật. Shortlist dataset/model, threshold, hướng tối ưu và mobile stack vẫn là candidate/câu hỏi. Chưa có pilot để tuyên bố giảm nhân sự; dữ liệu công khai và fixture giả lập không thay thế đánh giá tại kỳ thi thật.

## Bước tiếp theo theo thứ tự

1. **Rà T-011 và đầu vào:** Minh Hy review các PR #3/#5/#6/#7; xử lý ý kiến T-008 cho policy, authority và correction trước khi khóa E3. T-011 vẫn draft.
2. **Hoàn thiện bằng chứng baseline:** T-012 phân tích lỗi E1/E2 theo stage và domain gap; chọn main test phù hợp cửa phòng, thiết kế E3 theo business baseline đã thống nhất và đo M1 trên thiết bị/điều kiện chung. Không lấy thời gian GitHub runner làm kết luận triển khai.
3. **Experiment rồi mới chốt kỹ thuật:** từ uncertainty và rủi ro đã đo, đặt giả thuyết, điều kiện kiểm và acceptance criteria trước experiment; dùng kết quả đó để cân nhắc candidate/configuration, threshold và kiến trúc app.

**Task, người phụ trách và trạng thái chi tiết:** [Google Sheet chung](https://docs.google.com/spreadsheets/d/14BQCQ_LbGkZS15Grfi4AZNWBX15h479XjoyQvP9jHcU/edit?gid=0#gid=0). Trang này tóm tắt tiến độ và việc kế tiếp, không sao chép bảng task.
