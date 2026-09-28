# T-011 — E1 WIDER FACE: SCRFD-500MF full validation

**Ngày chạy:** 2026-09-27. **Trạng thái:** component detection run hoàn tất; chưa có quyết định detector cuối.

## Câu hỏi và phạm vi

Theo [T-010 E1 scoring protocol](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md), run này đo bbox phát hiện mặt của SCRFD-500MF trên cùng WIDER validation và evaluator nội bộ với YuNet, BlazeFace. Không đo chọn đúng thí sinh, xác minh 1:1 hoặc check-in. Project AP này không phải WIDER Easy/Medium/Hard chính thức.

## Đầu vào và cấu hình

- 3.226 ảnh WIDER validation, 39.112 valid GT, 585 ignored GT; 0 GT ngoài biên. Hai ZIP khớp SHA-256 đã ghi ở [data gate](../T-011-E1-widerface-data-gate.md).
- `buffalo_sc.zip` SHA-256 `57D31B56B6FFA911C8A73CFC1707C73CAB76EFE7F13B675A05223BF42DE47C72`; thành phần `det_500m.onnx` SHA-256 `5E4447F50245BBD7966BD6C0FA52938C61474A04EC7DEF48753668A9D8B4EA3A`.
- Config ID `T-010-E1-v1-scrfd500-640-0.01-0.4`: InsightFace SCRFD, input 640×640, score threshold 0,01, NMS 0,4; box quy về pixel ảnh gốc. Không điều chỉnh cấu hình sau khi xem điểm.
- Python 3.12.14 trên GitHub `ubuntu-latest` CPU runner; InsightFace 0.7.3, ONNX Runtime 1.20.1, NumPy 2.2.6. [Run 36296357372, job SCRFD](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36296357372/job/108555827946) tại commit `373e4ad7d1ffd05467a39dafc92b35248903ec15`, protocol `T-010-E1-2026-09-27`.
- Prediction JSON và summary chỉ ở `RUNNER_TEMP`, được xóa cuối job. Git chỉ nhận số tổng hợp.

Workflow [run 36296108522, job SCRFD](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36296108522) đầu tiên dừng **trước inference** vì file ONNX được giải nén với tên `model` thiếu đuôi `.onnx`, khiến InsightFace không nhận diện file. [Commit 373e4ad](https://github.com/quocanwyf/doantotnghiep2nguoi/commit/373e4ad7d1ffd05467a39dafc92b35248903ec15) sửa tên file thành `det_500m.onnx`; hash weight, config, dữ liệu và evaluator không đổi. Run thành công ở trên là điểm đầu tiên của SCRFD, không phải chọn cấu hình sau khi xem AP.

## Kết quả

| Chỉ số | Giá trị |
|---|---:|
| Prediction rows | 4.858.820 |
| Box được chấm sau clip | 4.263.546 |
| Box rỗng sau clip | 595.274 |
| Box có tọa độ bị clip | 534.287 |
| Ảnh không có prediction | 0 |
| TP / FP / neutral | 24.804 / 4.238.731 / 11 |
| Project AP tại IoU > 0,5 | **0,5473701659** |
| Recall cực đại | **0,6341787687** |

Thời gian phần preprocessing + inference + postprocessing sau decode ảnh trên runner này: median 62,98 ms, p95 157,54 ms. Runner không phải thiết bị đích và tải máy không được kiểm soát; không dùng số này để kết luận chi phí vận hành tương đối. Số box bị clip/rỗng lớn cần được phân tích ở T-012; chưa kết luận nguyên nhân hoặc thay output adapter sau khi đã xem điểm.

## Diễn giải và bước tiếp

Trên protocol và cấu hình đã pin, SCRFD-500MF có project AP/recall thấp hơn YuNet và cao hơn BlazeFace. Đây là **so sánh component detection trên WIDER**; chưa suy ra kết quả ở cửa phòng thi hoặc chọn detector cuối. Số FP lớn gắn với ngưỡng output thấp đặt trước để tính đường precision–recall, không phải false acceptance nghiệp vụ và không phải ngưỡng triển khai. Xem [báo cáo so sánh E1](T-011-E1-widerface-comparison.md) và tiếp tục phân tích lỗi, dữ liệu tương tự miền triển khai, chi phí trên cùng thiết bị đích.
