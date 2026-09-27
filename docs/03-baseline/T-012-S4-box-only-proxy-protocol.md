# T-012 — Protocol đề xuất: proxy S4 chỉ dùng bbox LTFT

**Trạng thái:** kiểm khả thi từ annotation, **chưa chạy so sánh candidate**, chưa khóa metric/acceptance cho ứng dụng. Quốc An chốt chỉ dùng dữ liệu có sẵn. [Audit LTFT](T-012-S4-ltft-label-audit.md) phát hiện video Zenodo không khớp nhãn LTFT, nên protocol này **không dùng frame ảnh** và không giả định đã giải quyết sai khác đó.

## Câu hỏi có thể kiểm, và điều không thể suy ra

T-008 cần tránh chọn nhầm người khi cảnh có nhiều mặt; T-012 đặt câu hỏi liệu liên kết qua nhiều frame có giảm `unresolved` mà không tăng chọn sai. Bằng nhãn LTFT, chỉ có thể kiểm câu hẹp: **khi đã được đưa các box mặt trong từng frame và box mục tiêu lúc đầu, một rule hình học có giữ đúng ID đã gán ở frame sau không?** Đây là phép thử association với **box oracle từ annotation**, không đo detector trên video, không nhận diện danh tính người, không gắn claim/hồ sơ với actor, và không đo check-in/attendance.

Ground truth LTFT được tạo từ detection rồi kiểm thủ công/gán ID theo [bài báo](https://arxiv.org/pdf/2010.08675). `ID không có box ở frame cuối` nghĩa là **không được annotation ghi nhận tại frame đó**; không thể gọi người thật đã rời khung hay `absent-from-window`. Box `face=0` bị loại vì README nói đó là detection sai hoặc chứa nhiều mặt.

## Kiểm khả thi trước khi thử rule

Đọc trực tiếp `choke1.txt`/`choke2.txt` tại commit LTFT `2c481e807be5cae53c5a056f39e1f1107628f1f6`, chỉ giữ `face=1`. Chia tuần tự thành cửa sổ **16 frame không chồng lặp**, từ chỉ số `0, 16, 32, ...`; mỗi ID có box tại frame đầu là một trường hợp target riêng, endpoint ở `start+15`. Quy tắc này dùng **chỉ để đếm khả thi**, không phải chọn mẫu test cuối hoặc báo hiệu năng. Không lưu bbox/ID thô trong Git.

| File nhãn | Target có box ở đầu | Có ≥2 mặt ở đầu | Có distractor trong cửa sổ | Target còn box ở endpoint | ID target không có box ở endpoint |
|---|---:|---:|---:|---:|---:|
| Choke1 | 495 | 482 | 486 | 401 | 94 |
| Choke2 | 529 | 521 | 526 | 405 | 124 |

Đây là số **cặp cửa sổ–ID**, không phải 1.024 người hay 1.024 lượt check-in. Một ID có thể tạo nhiều cửa sổ; Choke1/Choke2 có thể cùng người nhưng chưa có mapping xuyên video. Số cuối không chứng minh target vắng về mặt vật lý.

## Điều kiện phải khóa trước phép thử box-only

1. **Đầu vào cho candidate:** danh sách box `face=1` theo frame và box target ở frame đầu. ID ground truth chỉ dùng bởi evaluator, không đưa vào candidate; không dùng tọa độ/ID tương lai để chọn.
2. **Đối chứng/candidate:** A0 chỉ ra kết luận khi frame xét có đúng một box; một rule hình học theo chuỗi (A2) là candidate cần đặc tả độc lập, gồm cách liên kết, xử lý mất box, cửa sổ và abstain. Không mượn threshold từ XQLFW/ChokePoint paper hoặc tune trên test. A1 cần vùng giao dịch thật nên **không biểu diễn đúng** bằng box-only; không giả vờ đã so A1.
3. **Outcome:** `correct-track` khi box chọn tại endpoint gắn ID target; `wrong-track` khi box chọn gắn ID khác; `unresolved` khi không chọn. Báo riêng trường hợp target có/không có annotation tại endpoint, số mặt/distractor và số cửa sổ theo ID. Nếu box đầu nhiều hơn một, việc cung cấp box target là **oracle khởi tạo**, không phải khả năng app chọn người khai báo.
4. **Split và mẫu số:** không dùng frame cùng cửa sổ ở cả dev/test. Nếu muốn khóa test theo ID, phải kiểm trùng người xuyên Choke1/Choke2; hiện chưa đủ bằng chứng. Khi chưa kiểm, chỉ mô tả exploratory với mẫu số và cluster theo ID/video, không tuyên bố independent holdout hay chọn rule cuối.
5. **Quyền và báo cáo:** chỉ tải/đọc annotation công khai ở môi trường tạm, dẫn nguồn, không tái phân phối file nhãn/ID/bbox vì repository LTFT chưa công bố giấy phép rõ. Report được phép chứa số đếm tổng hợp, version/hash và giới hạn; không chứa ảnh, embedding hay track theo người.

**Điều kiện dừng:** thiếu quy tắc candidate được khóa trước khi xem test, split đáng tin, hoặc quyền dùng phù hợp thì chỉ giữ kiểm khả thi này. Nếu phép thử box-only chạy được, đặt tên và báo cáo riêng; nó không thay [X-012-A nghiệp vụ](T-012-X-012-A-label-contract.md), vốn cần claim–actor độc lập.
