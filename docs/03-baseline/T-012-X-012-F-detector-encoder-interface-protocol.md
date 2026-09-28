# T-012 X-012-F — Ảnh hưởng detector/landmark lên pipeline xác minh 1:1

**Câu hỏi:** [E1](runs/T-012-S4-widerface-size-strata.md) cho YuNet/SCRFD thế mạnh khác nhau về phát hiện mặt, nhưng [E2](runs/T-011-E2-xqlfw-mbf-vs-r50.md) chỉ dùng SCRFD trước encoder. Nếu giữ MobileFaceNet (MBF), cùng ảnh/cặp XQLFW và rule đúng một mặt, thay detector+landmark làm thay đổi tỷ lệ cặp chấm được và lỗi xác minh trên **cùng cặp hợp lệ** thế nào? Đây là phép kiểm interface S3→S7 từ [ma trận ứng viên](T-012-candidate-evidence-matrix.md), không chọn detector cuối hoặc chấm S4 ai vừa đưa mã.

## Dữ liệu, biến và kiểm soát

- Dùng XQLFW ZIP + `xqlfw_pairs.txt` và `buffalo_sc.zip` đã pin SHA ở E2, cùng YuNet `face_detection_yunet_2026may.onnx` đã pin SHA ở E1. Script dừng khi hash, manifest/pairs hoặc model không khớp. Không thu ảnh/video mới, không lưu ảnh/embedding/prediction theo ảnh vào Git.
- **D0 SCRFD:** `FaceAnalysis` pack `buffalo_sc`, detector SCRFD-500MF CPU, input 640×640, detector threshold 0,5, nhận đúng một face mới lấy embedding MBF như E2. **Cổng tái lập:** trên 7.263 ảnh XQLFW được pair tham chiếu phải khớp E2: 6.064 một mặt, 291 không mặt, 908 nhiều mặt; 4.215/6.000 cặp có score và MBF pair-fold FA/FR `133/125`.
- **D1 YuNet:** cùng ảnh BGR gốc, OpenCV 5.0 `FaceDetectorYN` weight 2026may, input động theo ảnh, score threshold 0,5, NMS 0,3, topK 5.000. Output phải có 15 cột hữu hạn. Theo [OpenCV FaceDetectorYN](https://github.com/opencv/opencv/blob/5.x/doc/tutorials/dnn/dnn_face/dnn_face.markdown), 5 landmark ở cột 4–13 theo thứ tự right eye, left eye, nose, right mouth, left mouth; dùng chính thứ tự này với InsightFace `norm_crop` 112×112 rồi MBF `get_feat`. Nếu không ra đúng 1 mặt, landmark không hợp lệ hoặc embedding không hữu hạn/512 chiều, giữ `unresolved`, không chọn bbox khác. YuNet+MBF là cấu hình thí nghiệm, chưa là pipeline được chọn.
- Giữ cùng MBF ONNX, normalization và cosine. Cùng 6.000 pair protocol/10 fold XQLFW; threshold của mỗi nhánh chọn **chỉ trên 9 fold dev** theo quy tắc E2, rồi chấm fold thứ 10. Không tune detector hay landmark mapping theo điểm test. Không gọi kết quả pair-fold là test tách danh tính hoặc camera cửa phòng.

## Đầu ra và đối chiếu

1. Báo theo từng detector: ảnh một/không/nhiều mặt và ảnh lỗi; 6.000 cặp gốc chia genuine/impostor có score/chưa kết luận. Cặp có score chỉ khi **cả hai ảnh** đúng một mặt với embedding hợp lệ.
2. Báo FMR/FNMR, FA/FR và mẫu số của **từng tập cặp hợp lệ riêng** để thấy kết quả mỗi pipeline. Vì mẫu số có thể khác nhau, không lấy chênh lệch hai tỷ lệ này làm tác động thuần của detector.
3. Tạo **giao cặp hợp lệ** giữa D0 và D1 trước scoring. Trên đúng giao này, dùng cùng 10 fold và mỗi nhánh chọn threshold trên dev của giao, báo FA/FR, genuine/impostor, FMR/FNMR. Đây là phép so có cùng mẫu số, nhưng detector thay cả bbox lẫn landmark/align. Không so threshold số học giữa hai encoder/detector như business policy.
4. Đối chiếu `valid + unresolved = 6.000` cho từng nhánh, `intersection ≤ valid` mỗi nhánh, genuine/impostor và tổng fold. Nếu SCRFD không tái lập E2, model/ảnh sai hash, landmark mapping lỗi, hoặc lớp pair vắng ở fold thì dừng và báo failure; không âm thầm sửa protocol theo kết quả.

**Cách đọc:** nếu YuNet có coverage khác SCRFD, chỉ kết luận về rule một mặt trên ảnh XQLFW. Ảnh nhiều detection **không có nhãn** mặt nào thuộc người vừa khai báo, nên không thử từng mặt và không tính false accept/reject trên cặp unresolved. Chất lượng E1 WIDER, interface XQLFW và proxy LTFT vẫn là ba loại evidence khác miền/đơn vị. Một quyết định triển khai cần S4 có nhãn, thiết bị và giới hạn nghiệp vụ riêng.
