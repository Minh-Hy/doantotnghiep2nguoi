# T-012 X-012-H — Gating liên kết mặt S4 khi bằng chứng yếu

**Ngày khóa:** 28/09/2026, trước khi chạy candidate X-012-H. **Loại:** phép thử proxy chỉ dùng annotation bbox LTFT, không phải tối ưu đã được chứng minh cho toàn bộ B0 hoặc lượt check-in.

## Vì sao phép thử tồn tại

T-008/T-005 cần giữ đúng người đã khai báo hồ sơ giữa các frame có nhiều mặt; khi không chắc phải trả `unresolved`. B0 hiện chỉ cho qua ảnh có một detection, nên S4 nhiều mặt còn mở. Proxy [P1 sequential](runs/T-012-S4-ltft-box-proxy.md) đúng/sai/chưa kết luận `758/38/228` trên 1.024 cửa sổ–ID được cấp box đầu từ nhãn. [D1/D2](runs/T-012-S4-ltft-path-diagnostic.md) cho thấy 41 lần P1 chọn sai ID đầu tiên xảy ra ở frame không có record của target, nhưng candidate không thấy ID thật. Câu hỏi có thể đo là: **yêu cầu liên kết hình học mạnh hơn có giảm sai track khi target không được ghi nhận, và phải trả giá bao nhiêu correct-track thành unresolved?**

[SORT của Bewley và cộng sự](https://arxiv.org/abs/1602.00763) dùng gating IoU trong data association; [mã SORT của tác giả](https://github.com/abewley/sort/blob/master/sort.py) đặt giá trị tham chiếu `0,3`. X-012-H chỉ mượn **ý tưởng gate và điểm tham chiếu**; không triển khai hoặc gọi candidate là SORT, không copy mã SORT GPL, không suy `0,3` là ngưỡng phù hợp cho mặt ở cửa phòng.

## Candidate và điều kiện cố định

- **P1 đối chứng:** đúng [script T-012](../../scripts/t012_ltft_box_proxy.py): từ box mục tiêu oracle ở đầu cửa sổ, mỗi frame chọn box có IoU lớn nhất với box trước nếu duy nhất và `IoU > 0`; nếu không thì dừng `unresolved`.
- **P2 can thiệp duy nhất:** giữ mọi bước P1, thay điều kiện nối thành `IoU >= 0,3` và lớn nhất duy nhất. Khi gate không qua, dừng `unresolved`; **không** tìm lại bằng ID, không tự chuyển sang box khác ở frame sau. `0,3` cố định từ nguồn tham khảo trước khi xem output P2, không được điều chỉnh theo kết quả LTFT.
- **Input/chấm điểm:** hai file `choke1.txt`/`choke2.txt` cùng SHA-256 và parser của protocol [box-only](T-012-S4-box-only-proxy-protocol.md); chỉ box `face=1`. Cửa sổ 16 frame không chồng lặp, mỗi ID ở frame đầu là một trường hợp; cùng 1.024 cửa sổ–ID cho P1/P2. ID thật chỉ đi vào evaluator, không đi vào rule.
- **Đầu ra chính:** `correct-track`, `wrong-track`, `unresolved` ở endpoint; báo số và tỷ lệ trên **cùng 1.024 trường hợp** cho mỗi candidate, cộng phân nhóm Choke1/Choke2 và target có/không có annotation ở endpoint. Báo thêm `ever-wrong` theo toàn bộ đường đi để endpoint không che lần đã chọn sai. Kiểm tổng ba outcome bằng mẫu số và P1 tái lập chính xác report cũ trước khi diễn giải P2.
- **Giả thuyết có thể bác bỏ:** P2 giảm `wrong-track` và `ever-wrong` so P1, nhưng có thể làm tăng `unresolved` và giảm `correct-track`. Không chỉ báo một tỷ lệ “accuracy”; nêu cả ba nhánh và các trường hợp đổi outcome P1→P2. Nếu wrong không giảm, hoặc correct giảm mạnh mà wrong hầu như không đổi, giả thuyết cải thiện hữu ích không được ủng hộ.

## Phạm vi kết luận

Đây là phép thử **thăm dò đã xem kết quả P1 trên cả hai file**; không có test độc lập, không tune tham số, không gọi khác biệt là gain khái quát. ID/người có thể lặp giữa các cửa sổ và Choke1/Choke2 chưa có mapping xuyên video. Box đầu và box mỗi frame đều từ annotation, không từ SCRFD B0; không có claim–actor hoặc frame video khớp nhãn. Vì vậy P2 chỉ kiểm *giữ association sau khởi tạo oracle*, không đo chọn đúng người vừa khai mã, xác minh 1:1, lượt check-in hay hiệu năng cửa phòng. Nếu P2 có lợi trong proxy, bước sau vẫn cần đánh giá kết nối với pipeline thị giác trên nguồn có nhãn phù hợp; không đưa P2 vào app chỉ nhờ bảng này.

File nhãn công khai chỉ được đọc ở môi trường tạm, đối chiếu hash, không commit dữ liệu thô, ID, box theo người hoặc ảnh/video. Báo cáo giữ số tổng hợp, commit mã, điều kiện chạy, sai khác và giới hạn. Không đo latency nếu không có cùng runner/protocol tốc độ được khóa riêng.
