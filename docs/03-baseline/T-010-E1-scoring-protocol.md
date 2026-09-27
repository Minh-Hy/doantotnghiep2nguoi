# T-010 — Giao thức chấm E1 trên WIDER FACE validation

**Ngày đặt trước:** 2026-09-27. **Người đặt:** Codex theo yêu cầu tiếp tục của Quốc An. **Trạng thái:** quy tắc đánh giá component được đặt trước khi có prediction/điểm E1; wrapper detector và evaluator code còn phải qua preflight trước run. Đây là addendum của [T-010-protocol.md](T-010-protocol.md), không thay đổi protocol E2 đã chạy.

## 1. Câu hỏi và phạm vi

T-008 TQ-002/FR-006 cần một khả năng cung cấp vùng mặt khi nhánh nghiên cứu dùng ảnh mặt; T-005 S3 và T-009 giữ YuNet, BlazeFace full-range, SCRFD-500MF làm detector candidate. E1 hỏi: **trên cùng ảnh nguyên khung, detector nào đạt chất lượng phát hiện mặt và chi phí tính toán ra sao?**

E1 chỉ chấm bbox phát hiện mặt. Nó **không** chấm chọn đúng người mục tiêu S4, xác minh danh tính S7–S8, check-in, quyền vào, attendance hoặc hiệu quả nhân sự. Không có acceptance target nghiệp vụ định lượng cho E1 ở thời điểm này; kết quả là so sánh mô tả để chọn candidate cho phép thử tiếp.

[Trang kết quả của tác giả WIDER FACE](https://mmlab.ie.cuhk.edu.hk/projects/WIDERFace/WiderFace_Results.html) nêu giao nhau trên hợp `>0,5` và cách đánh giá theo PASCAL VOC. Giao thức dưới đây là **AP nội bộ của project trên validation TXT**, không tự nhận là điểm `Easy/Medium/Hard` hoặc bảng xếp hạng WIDER chính thức. Những điểm chính thức cần đúng `.mat` difficulty subsets và evaluator tương ứng; hiện T-011 mới audit TXT.

## 2. Dữ liệu và đơn vị đo

- Dùng **toàn bộ 3.226 ảnh WIDER FACE validation** trong cùng một manifest đường dẫn sắp tăng dần; không lấy subset vì thuận tiện hoặc bỏ ảnh detector lỗi. Nguồn và hash của `WIDER_val.zip` (F9EFBD09F28C5D2D884BE8C0EAEF3967158C866A593FC36AB0413E4B2A58A17A) và `wider_face_split.zip` (C7561E4F5E7A118C249E0A5C5C902B0DE90BBF120D7DA9FA28D99041F68A8A5C) đã kiểm ở [T-011 data gate](T-011-E1-widerface-data-gate.md).
- Ground truth lấy từ `wider_face_split/wider_face_val_bbx_gt.txt`, mỗi dòng gồm `x,y,width,height,blur,expression,illumination,invalid,occlusion,pose`. Bản audit đếm 39.708 dòng box; 585 có `invalid=1`, 11 có width/height không dương, có thể chồng nhau. **Không cộng trừ số này để đoán mẫu số**; evaluator phải parse và báo số valid/ignored/excluded thực.
- Đơn vị đánh giá là **prediction bbox trên ảnh gốc** và **ground-truth bbox hợp lệ**. Tọa độ GT chuyển từ `xywh` sang `xyxy=(x,y,x+w,y+h)`; diện tích theo tọa độ liên tục `w×h`, không cộng `+1` pixel. Box GT ngoài biên ảnh được giữ nguyên và đếm riêng trong preflight; nếu phát hiện nhiều box ngoài biên, dừng để review protocol trước khi chấm, không tự sửa sau khi xem điểm.
- Box GT có `width>0,height>0,invalid=0` là **valid positive**. Box có `width>0,height>0,invalid=1` là **ignored region**. Box không dương bị loại khỏi cả hai nhóm và được đếm. Cờ `invalid` ngoài `{0,1}`, path trùng/thiếu, ảnh không giải mã, box có số không hữu hạn hoặc parse sai 10 trường là lỗi preflight, không tự bỏ dòng.

## 3. Chuẩn hóa prediction và ghép box

Mỗi wrapper trả về `image_path, bbox_xyxy_original_pixels, native_score, prediction_index` sau preprocessing/NMS **riêng đã pin**. Prediction score phải hữu hạn, box có diện tích dương. Box prediction được đưa về hệ tọa độ ảnh gốc, cắt vào biên ảnh rồi loại box rỗng sau cắt; số bị loại được báo. Không chuẩn hóa score của ba detector sang thang chung để quyết định theo một threshold; AP chỉ cần thứ tự score trong từng detector. Mỗi wrapper phải báo input size, color order, resize/letterbox, chuyển tọa độ, threshold đầu ra tối thiểu, NMS và phiên bản runtime **trước khi tạo prediction trên validation**.

- Sắp tất cả prediction của một detector trên toàn validation theo score giảm dần; khi bằng điểm, dùng `image_path` rồi `prediction_index` để tái lập thứ tự.
- Với mỗi prediction, tính IoU với các valid GT cùng ảnh. Nếu IoU cao nhất với valid GT **>0,5** và GT đó chưa được ghép, ghi **TP** và đánh dấu GT đã ghép. Nếu IoU cao nhất với valid GT >0,5 nhưng GT đã được ghép, ghi **FP trùng**, kể cả prediction cũng chạm ignored region.
- Nếu không chạm valid GT nào với IoU >0,5, nhưng chạm ít nhất một ignored region với IoU >0,5, prediction là **neutral**: không TP, không FP. Còn lại là **FP**. Một ignored region có thể neutralize nhiều prediction; nó không tăng mẫu số recall.
- Mỗi valid GT có tối đa một TP. Ảnh không có valid GT vẫn tham gia và prediction không bị neutralize trên ảnh đó là FP. Prediction từ ảnh detector lỗi phải được biểu diễn bằng danh sách rỗng và lỗi được báo riêng; không bỏ ảnh khỏi manifest.

## 4. Metric và cách diễn giải

**Metric chính:** project AP tại IoU >0,5 trên toàn bộ valid GT. Bỏ neutral prediction khỏi chuỗi precision–recall; tính TP/FP tích lũy theo thứ tự score, `recall=TP/tổng valid GT`, `precision=TP/(TP+FP)`. AP là diện tích dưới đường precision envelope all-points: thêm sentinel `(0,0)` và `(1,0)`, lấy maximum precision ngược, cộng `Δrecall × precision` tại các điểm recall thay đổi. Báo đúng mẫu số GT và tổng TP/FP/neutral, số ảnh lỗi/0 prediction, số box loại do tọa độ.

**Metric phụ:** recall cực đại trong output đã pin; AP/recall theo lát kích thước hoặc thuộc tính chỉ sau khi protocol lát và mẫu số được ghi trước run riêng. Chưa báo `Easy/Medium/Hard` hay landmark accuracy từ TXT này. AP giữa candidate chỉ so trong cùng manifest/evaluator; khác biệt score không tự thành khác biệt chất lượng cửa phòng.

**Chi phí:** đo preprocessing + inference + postprocessing cùng một phạm vi thời gian, cùng thiết bị và quy tắc warm-up; báo median/p95 và RAM đỉnh nếu đo được. Không dùng thời gian E2 hoặc smoke test B0 làm số latency E1. Candidate thiếu wrapper hợp lệ được ghi **không chấm**, không điền điểm giả.

## 5. Gate trước khi xem điểm

1. Pin exact weight/hash từ T-009 và config wrapper của YuNet, BlazeFace, SCRFD. Threshold đầu ra tối thiểu phải được chọn từ khả năng runtime/preflight **trước** prediction validation; không đổi theo AP. Nếu phải thay, lập run revision mới và giữ kết quả cũ.
2. Kiểm manifest/GT count khớp T-011 data gate; đếm valid/ignored/excluded và box ngoài biên, không suy bằng phép trừ khi có overlap.
3. Kiểm evaluator bằng fixture tổng hợp: một TP, một FP, detection trùng, ignored region, valid+ignored overlap, ảnh không GT, score tie và box không dương. Các assertion phải qua trước khi chạy candidate.
4. Chạy wrapper trên ảnh preflight **không dùng để chọn cấu hình theo điểm validation**; xác nhận tọa độ gốc, score, output rỗng và thời gian đo. Lưu raw prediction có kiểm soát ngoài Git; chỉ đưa số tổng hợp không chứa ảnh/identity vào repo.
5. Mọi thay đổi evaluator/config sau khi xem prediction hoặc AP phải có revision, lý do và phép đánh giá mới; không âm thầm sửa số cũ.

**Quyết định tại thời điểm đặt trước:** khóa định nghĩa AP nội bộ và quy tắc GT/ignore/match nêu trên. **Chưa chạy benchmark** vì wrapper/evaluator implementation chưa qua preflight; chưa chọn detector cuối. T-011 phải ghi chính xác phiên bản protocol này trong run report.
