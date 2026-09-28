# T-012 — Protocol đề xuất: proxy S4 chỉ dùng bbox LTFT

**Trạng thái:** protocol thăm dò **khóa trước run box-only**; chưa có kết quả candidate hay tiêu chí chấp nhận cho ứng dụng. Quốc An chốt chỉ dùng dữ liệu có sẵn. [Audit LTFT](T-012-S4-ltft-label-audit.md) phát hiện video Zenodo không khớp nhãn LTFT, nên protocol này **không dùng frame ảnh** và không giả định đã giải quyết sai khác đó.

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

## Protocol thăm dò khóa trước khi xem kết quả

1. **Đầu vào cho candidate:** danh sách box `face=1` theo frame và box target ở frame đầu. ID ground truth chỉ dùng bởi evaluator, không đưa vào candidate; không dùng tọa độ/ID tương lai để chọn.
2. **Hai candidate nhận cùng đầu vào và không tune:** `P0-static` chọn box ở **frame cuối** có IoU lớn nhất với box target ở frame đầu; `P1-sequential` chọn qua từng frame, mỗi lần IoU lớn nhất với box vừa chọn trước đó. Chỉ chọn nếu IoU **lớn hơn 0** và duy nhất; nếu không có box, không giao nhau hoặc đồng hạng lớn nhất thì `unresolved`. `P1` dừng ngay khi unresolved, không tự nối lại. Mốc IoU >0 là định nghĩa overlap tối thiểu của phép thử hình học, **không phải ngưỡng triển khai**; không mượn threshold từ XQLFW/ChokePoint paper hay tối ưu bằng kết quả.
3. **Outcome:** `correct-track` khi box chọn tại endpoint gắn ID target; `wrong-track` khi box chọn gắn ID khác; `unresolved` khi không chọn. Báo cả số đếm và mẫu số trên **mọi cửa sổ–ID ở đầu**, tách nhóm target còn/không còn annotation ở endpoint và cảnh ≥2 box ở đầu. Một ID có thể tạo nhiều cửa sổ, nên không gán khoảng tin cậy độc lập theo cửa sổ. Nếu box đầu nhiều hơn một, việc cung cấp box target là **oracle khởi tạo**, không phải khả năng app chọn người khai báo. A0 cần quyết định chọn người ban đầu và A1 cần vùng giao dịch thật; **không** diễn giải `P0/P1` thành phép so A0/A1/A2 nghiệp vụ.
4. **Split và mẫu số:** toàn bộ cửa sổ 16 frame không chồng lặp trong hai file được dùng cho **một phân tích thăm dò mô tả**, không có dev/test và không chọn winner triển khai. Không điều chỉnh candidate sau khi xem kết quả rồi báo lại cùng dữ liệu như test khóa. Nếu sau này cần locked test theo ID, phải kiểm trùng người xuyên Choke1/Choke2 trước; hiện chưa có mapping để tuyên bố independent holdout.
5. **Gate dữ liệu:** SHA-256 hai file phải khớp [audit](T-012-S4-ltft-label-audit.md); header bằng số frame; chỉ số frame tuần tự; mỗi dòng đúng `2 + 7 × số detection`; `face` thuộc `{0,1}`; box `face=1` có tọa độ hữu hạn, width/height dương và ID duy nhất trong frame. Lệch gate thì dừng, không bỏ dòng có lỗi rồi vẫn báo tỷ lệ.
6. **Quyền và báo cáo:** chỉ tải/đọc annotation công khai ở môi trường tạm, dẫn nguồn, không tái phân phối file nhãn/ID/bbox vì repository LTFT chưa công bố giấy phép rõ. Report chỉ chứa số đếm tổng hợp, version/hash, điều kiện máy nếu có đo thời gian, và giới hạn; không chứa ảnh, embedding hay track theo người.

**Điều kiện dừng:** thiếu file đúng hash, gate cấu trúc sai hoặc quyền dùng phù hợp thì chỉ giữ kiểm khả thi này. Nếu phép thử box-only chạy được, đặt tên và báo cáo riêng; nó không thay [X-012-A nghiệp vụ](T-012-X-012-A-label-contract.md), vốn cần claim–actor độc lập.

## Chẩn đoán hậu nghiệm D1 — ghi trước khi chạy phân tích đường đi

Sau khi [báo cáo P0/P1](runs/T-012-S4-ltft-box-proxy.md) đã có số ở **frame cuối**, câu hỏi mới là: endpoint có che các lần P1 tạm chọn sai ID ở frame giữa không? Đây là **phân tích thăm dò sau khi xem kết quả chính**, không là phép xác nhận độc lập và không sửa rule P1, dữ liệu, cửa sổ hoặc số endpoint cũ.

Với **cùng 1.024 cửa sổ–ID**, phát lại P1 và đếm: (a) từng chọn ID khác target ở ít nhất một frame `ever-wrong`; (b) sai ở endpoint; (c) từng sai nhưng endpoint đúng; (d) từng sai rồi endpoint unresolved; (e) frame đầu tiên sai xảy ra lúc ID target còn hay không còn **annotation box**. Báo riêng theo Choke1/Choke2, tổng và mẫu số. `Target không được annotation ghi nhận` không được diễn giải là người vắng/ra khỏi khung. Nếu số endpoint phát lại không khớp báo cáo cũ thì dừng chẩn đoán.

## Kiểm nhãn hậu nghiệm D2 — phân biệt `face=0` với không có ID

Sau [D1](runs/T-012-S4-ltft-path-diagnostic.md), cả 41 lần P1 sai ID đầu tiên xảy ra ở frame không có **box `face=1`** của target. Trước khi kiểm file thô lại, khóa hai nhóm loại trừ nhau tại đúng **41 frame sai đầu**: (a) vẫn có detection mang target ID nhưng `face=0`; (b) không có detection nào mang target ID. Báo cả hai theo Choke1/Choke2 và tổng, kiểm tổng bằng 41. Không đổi rule P1, cửa sổ, nhãn hợp lệ hoặc điểm D1. Theo README LTFT, `face=0` gộp false positive và box nhiều mặt; không diễn giải nó thành một mặt target chắc chắn nhìn thấy. Đây vẫn là audit hậu nghiệm, không đo lý do vật lý khiến detector/annotation mất box.
