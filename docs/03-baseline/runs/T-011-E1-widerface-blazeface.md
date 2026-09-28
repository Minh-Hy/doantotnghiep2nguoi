# T-011 — E1 WIDER FACE: BlazeFace full-range full validation

**Ngày chạy:** 2026-09-27. **Trạng thái:** component detection run hoàn tất; chưa có quyết định detector cuối.

## Câu hỏi và phạm vi

Theo [T-010 E1 scoring protocol](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md), run này đo bbox phát hiện mặt của BlazeFace full-range trên cùng WIDER validation và evaluator nội bộ với YuNet. Không đo chọn đúng thí sinh, xác minh 1:1 hoặc check-in. Project AP này không phải WIDER Easy/Medium/Hard chính thức.

## Đầu vào và cấu hình

- 3.226 ảnh WIDER validation, 39.112 valid GT, 585 ignored GT; 0 GT ngoài biên. Hai ZIP khớp SHA-256 đã ghi ở [data gate](../T-011-E1-widerface-data-gate.md).
- Weight blaze_face_full_range.tflite float16 SHA-256 3698B18F063835BC609069EF052228FBE86D9C9A6DC8DCB7C7C2D69AED2B181B.
- Config ID T-010-E1-v1-blazeface-full-0.01-0.3: MediaPipe Tasks IMAGE mode, ảnh BGR đổi RGB, min_detection_confidence=0,01, min_suppression_threshold=0,3, bbox đưa về pixel ảnh gốc.
- Python 3.12 trên GitHub ubuntu-latest CPU runner, MediaPipe 1.0.0. [Run 36296108522, job BlazeFace](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36296108522/job/108555142384) chạy từ commit 00d3b1471c38d74e2f655ecaf68fcf19bf9314e7, protocol T-010-E1-2026-09-27.
- Prediction JSON và summary chỉ ở RUNNER_TEMP, được xóa cuối job. Git chỉ nhận số tổng hợp.

## Kết quả

| Chỉ số | Giá trị |
|---|---:|
| Prediction rows | 477.622 |
| Box được chấm sau clip | 474.431 |
| Box rỗng sau clip | 3.191 |
| Box có tọa độ bị clip | 14.206 |
| Ảnh không có prediction | 1 |
| TP / FP / neutral | 7.063 / 467.368 / 0 |
| Project AP tại IoU > 0,5 | **0,1360090961** |
| Recall cực đại | **0,1805839640** |

Thời gian phần preprocessing + inference + postprocessing sau decode ảnh trên runner này: median 13,68 ms, p95 38,89 ms. Runner không phải thiết bị đích và tải máy không được kiểm soát; không dùng số này để kết luận BlazeFace nhanh hơn YuNet.

## Diễn giải và bước tiếp

Trên protocol và cấu hình đã pin, BlazeFace trả ít TP hơn YuNet và project AP/recall thấp hơn. Đây là **so sánh component detection trên WIDER**, chưa phải quyết định cuối: còn SCRFD, phân tích chất lượng theo điều kiện ảnh/cửa phòng và chi phí trên cùng thiết bị đích. Số FP lớn do output threshold 0,01 được chọn trước để tính đường precision–recall; không suy ra threshold triển khai từ run này.
