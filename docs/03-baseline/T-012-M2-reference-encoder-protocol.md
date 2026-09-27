# T-012 M2 — Protocol thời gian encoder trên CPU tham chiếu

**Câu hỏi từ T-012:** R50 ít lỗi hơn MobileFaceNet (MBF) trên các cặp XQLFW được chấm ở E2. Đổi lại, thời gian tạo embedding và dung lượng weight của R50 so với MBF trong cùng môi trường là bao nhiêu? [E2](runs/T-011-E2-xqlfw-mbf-vs-r50.md) chưa tách thời gian encoder; [M1](runs/T-011-M1-reference-detection.md) chỉ đo detector. M2 bổ sung trục chi phí cho so sánh ứng viên, **không thay E2/M1 hoặc chốt model cuối**.

## Dữ liệu, biến và điều kiện cố định

- Dùng đúng XQLFW ZIP, `buffalo_sc.zip` và `buffalo_l.zip` đã pin SHA-256 ở T-011 E2; script dừng khi hash sai. Không dùng nhãn genuine/impostor để chọn mẫu thời gian, không đặt threshold.
- Sắp xếp đường dẫn JPG trong ZIP theo từ điển. Dùng cùng SCRFD-500MF trong `buffalo_sc`, cấu hình E2 `640×640`, `det_thresh=0,5` để lấy **60 ảnh đầu tiên có đúng một mặt và landmark hợp lệ**. Giới hạn quét tối đa 300 ảnh đầu trong thứ tự đó; nếu không đủ 60 thì dừng, không tự đổi mẫu. Căn chỉnh mỗi mặt một lần thành ảnh BGR `112×112` bằng cùng `norm_crop` InsightFace; 60 crop ở RAM dùng cho cả hai encoder. Không lưu ảnh, crop, embedding hoặc đường dẫn từng ảnh vào Git/log.
- Chỉ đổi encoder `w600k_mbf.onnx` (MBF) và `w600k_r50.onnx` (R50), cùng `CPUExecutionProvider`, phiên bản dependency cố định, một process và `OMP/OPENBLAS/MKL_NUM_THREADS=1`. Kiểm mỗi output có 512 giá trị hữu hạn; kiểm output MBF trên crop khớp embedding của `FaceAnalysis.get` ở mức số học trước đo. Kiểm input shape của cả hai là `112×112`.
- Warm-up **8 crop đầu cho từng encoder**. Đo **3 lượt × 60 crop = 180 call/encoder**, đảo thứ tự candidate theo lượt (MBF→R50, R50→MBF, MBF→R50). Đồng hồ `perf_counter_ns`; mỗi call là `model.get_feat(crop)` gồm chuẩn hóa input/blob và ONNX inference, **không gồm** tải model, giải mã JPG, detector, alignment, L2/cosine, hàng chờ hoặc vận hành app.
- Trên cùng runner báo median, p95, min, max ms/call; số call, hash nguồn/weight, kích thước ONNX, phiên bản runtime, CPU/OS. Không suy tỉ số thời gian trên máy khác hoặc latency toàn lượt. Không chọn winner bằng một số đo duy nhất; E2 quality và M2 cost giữ hai trục riêng.

## Cổng kiểm và cách đọc

Chỉ báo kết quả khi đủ 60 crop hợp lệ trong 300 ảnh đầu, các hash/schema/output qua kiểm, mỗi encoder đúng 180 call và không có call lỗi. Báo cả hai trên **cùng 60 crop**; nếu không qua cổng thì dừng và ghi nguyên nhân, không thay dữ liệu/tham số sau khi xem thời gian. Kết quả có thể cho thấy trade-off nghiên cứu MBF/R50 trên CPU runner này; acceptance theo throughput cửa phòng, RAM tổng và thiết bị đích vẫn chưa xác định. [Decision logic](DECISION_LOGIC.md) tiếp tục trace về nhu cầu xác minh 1:1 và vận hành ở T-008.
