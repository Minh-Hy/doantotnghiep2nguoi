# T-012 M2 — Chi phí encoder MBF/R50 trên cùng CPU runner

**Ngày:** 27/09/2026. **Câu hỏi:** R50 có ít lỗi hơn MobileFaceNet (MBF) trên cặp XQLFW hợp lệ ở E2; chi phí thời gian tạo embedding của hai encoder khác nhau ra sao khi đầu vào đã căn chỉnh và môi trường chạy được giữ giống nhau?

## Protocol và kiểm nguồn

- [Protocol M2](../T-012-M2-reference-encoder-protocol.md) commit `84a6683` trước run; [script](../../../scripts/t012_m2_reference_encoder.py), test và workflow commit `d6c4170`. [GitHub Actions run 36330836246](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36330836246) thành công toàn job; summary ở log, ảnh/crop/weight/embedding và JSON tạm không được upload/commit.
- XQLFW ZIP SHA-256 `1af459679fba23a12f4d83c82a81523eb930a4aec759eebefcbdde69a678962c`; `buffalo_sc.zip` `57d31b56b6ffa911c8a73cfc1707c73cab76efe7f13b675a05223bf42de47c72`; `buffalo_l.zip` `80ffe37d8a5940d59a7384c201a2a38d4741f2f3c51eef46ebb28218a7b0ca2f`. Script đã kiểm cả ba hash, R50 ONNX hash và MBF ONNX sau giải nén. Đây là cùng archive/model pack với E2, **không dùng nhãn pair để chọn ảnh timing**.
- ZIP có 13.233 JPG; duyệt thứ tự tên, 77 ảnh đầu cho ra 60 crop có đúng một mặt, 5 ảnh không mặt, 12 ảnh nhiều mặt, 0 lỗi decode/landmark. Cùng 60 crop BGR `112×112` từ detector/alignment E2 được giữ trong RAM cho cả hai encoder; output MBF trên crop đầu khớp `FaceAnalysis.get`. Mỗi ứng viên warm-up 8 crop rồi đo 3 lượt × 60 crop = **180 call/encoder**; thứ tự MBF→R50, R50→MBF, MBF→R50. Không có seed ngẫu nhiên.
- Runner Ubuntu `Linux-6.17.0-1022-azure-x86_64`, 4 logical CPU; Python 3.12.14, OpenCV 5.0.0, NumPy 2.2.6, ONNX Runtime 1.20.1, InsightFace 0.7.3, `CPUExecutionProvider`, ba biến thread OMP/OPENBLAS/MKL đặt `1`. Đồng hồ `perf_counter_ns` chỉ bao quanh `get_feat(crop)`: gồm tạo blob/chuẩn hóa input và ONNX inference, **không** gồm giải mã, detection, alignment, load model, L2/cosine hay toàn lượt app.
- Phạm vi `get_feat` được đối chiếu với [mã nguồn InsightFace ArcFaceONNX](https://github.com/deepinsight/insightface/blob/master/python-package/insightface/model_zoo/arcface_onnx.py); run còn kiểm embedding MBF trên crop đầu khớp `FaceAnalysis.get` trước đo. Link mã nguồn dùng để giải thích phép đo, version thực chạy được pin ở trên.

## Kết quả

| Encoder | ONNX bytes | Calls | Median ms/call | p95 ms/call | Min–max ms/call |
|---|---:|---:|---:|---:|---:|
| MBF | 13.616.099 | 180 | 8,35 | 14,55 | 8,21–22,29 |
| R50 | 174.383.860 | 180 | 67,33 | 72,81 | 67,02–113,70 |

Trên **runner và 60 crop này**, median R50 khoảng **8,1 lần** MBF; p95 khoảng **5,0 lần**; file ONNX lớn khoảng **12,8 lần**. Đây là số đo mô tả, không là hệ số chuyển sang thiết bị đích. Trong [E2 pair-fold](T-011-E2-xqlfw-mbf-vs-r50.md) trên 4.215 cặp hợp lệ, MBF FA/FR `133/125`, R50 `76/74`; [split tách danh tính custom](T-011-E2-xqlfw-identity-disjoint.md) tiếp tục thấy R50 ít lỗi hơn trên cặp được chấm. E2 đo chất lượng và M2 đo chi phí ở **hai lần chạy/môi trường khác nhau**; không cộng thời gian M2 với [M1 detector](T-011-M1-reference-detection.md) để suy latency đầu-cuối.

## Diễn giải và bước suy ra

**Observed:** R50 cho ít lỗi xác minh hơn trên cặp XQLFW hợp lệ trong E2, còn MBF tạo embedding nhanh hơn và dùng weight nhỏ hơn trên CPU runner M2. Hai ứng viên thể hiện đánh đổi chất lượng–chi phí cần giữ trong so sánh; M2 không làm thay đổi coverage `unresolved` do detector/rule một mặt và không giải quyết S4 chọn người đưa mã.

**Chưa quyết định:** không có thiết bị đích, mục tiêu thời gian theo lượt, phép đo RAM đỉnh hay dữ liệu gần miền cửa phòng. M2 chỉ có 60 crop chọn tất định từ ảnh XQLFW, cùng runner ảo có thể thay đổi tài nguyên; không ước lượng hàng chờ hoặc mức giảm nhân sự. Giữ cả MBF và R50 là ứng viên; chưa chốt model/threshold cuối. Khi có thiết bị và profile vận hành, cần đo cùng pipeline detection→chọn người→alignment→encoder→business outcome trên chính thiết bị đó và xem rủi ro sai người/chưa kết luận cùng thời gian xử lý.
