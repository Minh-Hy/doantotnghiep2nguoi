# T-011 — E1 WIDER FACE: YuNet full validation

**Ngày chạy:** 2026-09-27. **Trạng thái:** run component detection đã hoàn tất; so sánh ba detector được ghi ở báo cáo E1; chưa có quyết định detector cuối.

## Câu hỏi và phạm vi

Theo [T-010 E1 scoring protocol](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md), run này kiểm chất lượng bbox của cấu hình YuNet v1 trên WIDER FACE validation. Kết quả không đo chọn người mục tiêu, xác minh 1:1, check-in hoặc hiệu quả vận hành phòng thi. Đây là project AP từ validation TXT, không phải WIDER Easy/Medium/Hard chính thức.

## Dữ liệu, cấu hình và mã

- 3.226 ảnh WIDER validation; 39.708 dòng annotation, gồm 39.112 valid GT, 585 ignored GT và 11 dòng box không dương. GT ngoài biên: 0.
- `WIDER_val.zip` SHA-256 `F9EFBD09F28C5D2D884BE8C0EAEF3967158C866A593FC36AB0413E4B2A58A17A`; `wider_face_split.zip` SHA-256 `C7561E4F5E7A118C249E0A5C5C902B0DE90BBF120D7DA9FA28D99041F68A8A5C`.
- YuNet `face_detection_yunet_2026may.onnx` SHA-256 `EBAFCE4E3C118D6554634BE5C27AB333B4C047A9A8C3FAF1D7CF93101C22F0F0`. Config ID `T-010-E1-v1-yunet-dynamic-0.01-0.3-top5000`: ảnh BGR gốc, input dynamic, score threshold 0,01, NMS 0,3, top_k 5.000, `OPENCV_FORCE_DNN_ENGINE=4`.
- Python 3.12 trên GitHub `ubuntu-latest` CPU runner, NumPy 2.2.6, OpenCV contrib 5.0.0.93. Job [run 36294898744](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294898744) tại commit `19bb9b0dfec930b321adacefa63c0afb6658cbd6` chạy `scripts/t011_widerface_predict.py` và `scripts/t011_widerface_evaluate.py`, protocol `T-010-E1-2026-09-27`.
- Raw prediction JSON và summary chỉ ở `RUNNER_TEMP`; job đã xóa cuối lượt. Git chỉ nhận số tổng hợp, không nhận ảnh hoặc prediction theo ảnh.

## Kết quả

| Chỉ số | Giá trị |
|---|---:|
| Prediction rows | 1.195.480 |
| Box được chấm sau clip | 1.195.298 |
| Box rỗng bị loại sau clip | 182 |
| Box có tọa độ bị clip | 56.316 |
| TP / FP / neutral | 28.922 / 1.166.280 / 96 |
| Project AP tại IoU > 0,5 | **0,6483041468** |
| Recall cực đại | **0,7394661485** |

Thời gian phần preprocessing + inference + postprocessing sau giải mã ảnh trên runner này: median 25,79 ms, p95 52,65 ms cho 3.226 ảnh. Runner không phải thiết bị đích; tải CPU, RAM và warm-up chưa được kiểm soát để so thời gian với candidate khác. Không có ảnh nào có 0 prediction trong output YuNet ở cấu hình score thấp này.

## Diễn giải và bước tiếp

Điểm AP và recall trả lời cho **một cấu hình YuNet** trên bộ validation và evaluator đã pin. Số FP lớn gắn với ngưỡng output thấp được đặt trước để quan sát đường precision–recall; không suy từ đây rằng ngưỡng triển khai nên là 0,01. [Báo cáo so sánh E1](T-011-E1-widerface-comparison.md) đối chiếu ba run trên cùng manifest/evaluator. Cần dữ liệu tương tự cửa phòng thi và phép đo trên thiết bị đích trước final technical decision.

**Trạng thái đồng bộ:** báo cáo đã được đẩy lên draft PR #7.
