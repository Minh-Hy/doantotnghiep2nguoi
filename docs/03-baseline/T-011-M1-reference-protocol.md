# T-011 — M1 tham chiếu: thời gian detection trên cùng runner

**Ngày đặt phép đo:** 2026-09-27, trước khi chạy. **Trạng thái:** protocol tham chiếu; không đặt target triển khai và không chọn detector cuối.

## Câu hỏi và phạm vi

[E1](runs/T-011-E1-widerface-comparison.md) có AP/recall của YuNet, BlazeFace full-range và SCRFD-500MF trên cùng WIDER validation, nhưng thời gian trong các run riêng không đủ để so tốc độ. M1 tham chiếu hỏi: **với cùng tiến trình/runner, cùng các frame đã giải mã và cấu hình E1 v1, thời gian `adapter.detect` của ba candidate khác nhau thế nào?** Phép đo này chỉ trả lời chi phí component detection ở môi trường CPU tham chiếu. Không đo check-in đầu-cuối, hàng chờ hoặc khả năng giảm nhân sự.

## Điều kiện khóa trước khi xem kết quả

- **Dữ liệu:** chính `WIDER_val.zip` và hash của E1; chọn 60 ảnh từ 3.226 ảnh theo vị trí cách đều trên manifest path đã sắp xếp, không chọn theo nhãn/kết quả E1. Báo phân bố kích thước frame của mẫu. Ảnh được giải mã **một lần trước khi bấm giờ** và ba adapter nhận cùng BGR frame. Mẫu này nhằm đo runtime, không dùng để báo accuracy.
- **Ứng viên:** ba model/weight/config v1 của [E1](runs/T-011-E1-widerface-comparison.md), kiểm SHA-256 từng file; không tune threshold/resize. Mỗi adapter khởi tạo một lần ngoài phần đo. Dùng CPU runner Ubuntu trong **một GitHub Actions job**; ghi OS, CPU/vCPU, runtime, commit, package version.
- **Warm-up:** tám frame đầu của mẫu được chạy một lần cho cả ba adapter trước khi đo. Chạy ba vòng qua toàn bộ 60 frame; mỗi vòng luân phiên thứ tự candidate để giảm lệch do thứ tự chạy. Mỗi `detect` được đo bằng `perf_counter_ns`; không gồm tải model, đọc ZIP, giải mã ảnh hay ghi output. Không dùng timing của E1 run cũ để so sánh.
- **Chỉ số:** 180 lần gọi/candidate, median, p95, min/max ms và tổng bbox để kiểm lệnh thực sự chạy. Báo chênh lệch mô tả trên cùng runner; không dùng p-value hoặc diễn giải là khác biệt phổ quát. RAM đỉnh riêng từng model và latency thiết bị đích **chưa đo**.
- **Tài sản:** ảnh/weight và JSON tạm chỉ ở `RUNNER_TEMP`, không upload artifact; chỉ số tổng hợp trong log và báo cáo Markdown. Các hash công bố ở [external-assets](../00-project/external-assets.md).

## Tiêu chí diễn giải

Run hợp lệ khi tất cả hash, manifest 3.226 ảnh, giải mã 60/60 ảnh, 8 warm-up và 180 lần gọi/candidate hoàn tất cùng job; một candidate lỗi thì không xếp hạng tốc độ. Đây là phép đo **tham chiếu mô tả**, nên không có ngưỡng “đạt” theo nghiệp vụ. Sau run, ghi cả AP/recall E1 và thời gian M1 cạnh nhau nhưng không gộp thành một điểm hay chọn model. Thiết bị đích, tải và giá trị chấp nhận vẫn phải quyết định ở thí nghiệm sau.
