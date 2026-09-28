# T-012 X-012-G — kiểm đúng một tổ hợp còn thiếu trước khi dừng chọn B0

**Khóa trước run:** 28/09/2026. [B0](T-012-B0-pipeline-choice.md) đã chọn SCRFD-500MF + A0 + MobileFaceNet (MBF) để đi tiếp. Câu hỏi còn có thể ảnh hưởng lập luận khi báo cáo: **YuNet + R50** có đổi đánh đổi chất lượng của ba tổ hợp đã đo không? Chỉ chạy một lần để hoàn thành ma trận 2 detector × 2 encoder, rồi dừng bước chọn; không mở thêm model/dataset.

## Thiết kế

- **Bốn nhánh:** SCRFD+MBF (B0), SCRFD+R50 (đối chứng chất lượng), YuNet+MBF (đối chứng detector nhanh), **YuNet+R50 (ô mới)**. Mỗi detector xuất bbox/5 landmark, ảnh đúng một face mới được căn chỉnh 112×112 và đưa vào encoder; ảnh 0/nhiều face vẫn `unresolved`. Cùng L2/cosine. Không chọn face theo score/box lớn nhất.
- **Nguồn:** cùng XQLFW ZIP 7.263 ảnh tham chiếu/6.000 cặp và pair-fold của [E2](runs/T-011-E2-xqlfw-mbf-vs-r50.md), `buffalo_sc.zip`, `buffalo_l.zip` R50 và YuNet 2026may với SHA-256 đã pin trong T-011/X-012-F; script dừng nếu hash sai. Chỉ dùng nguồn sẵn có, không thu ảnh mới. Weight và ảnh lưu tạm trong GitHub runner, không commit/upload.
- **Cấu hình detector:** SCRFD `buffalo_sc` input 640×640, threshold 0,5; YuNet dynamic image input, score 0,5, NMS 0,3, topK 5.000. R50 ONNX `w600k_r50.onnx` từ `buffalo_l` với preprocessing của InsightFace; MBF từ `buffalo_sc`. Giữ đúng giao diện landmark/alignment của [X-012-F](T-012-X-012-F-detector-encoder-interface-protocol.md).
- **Chấm:** 10 pair-fold. Với mỗi nhánh, chọn ngưỡng trên 9 fold dev bằng evaluator E2, chấm fold còn lại. Báo ảnh một/không/nhiều detection; `valid/unresolved` trên **6.000 cặp** theo nhánh; FA/FR và FMR/FNMR trên tập valid riêng. Lấy **giao cặp valid của cả bốn nhánh** rồi chọn/chấm ngưỡng lại trong cùng giao để so trên đúng mẫu số. Không so tỷ lệ trên hai tập valid khác nhau như tác động thuần của model.

## Cổng tái lập và cách kết luận

- SCRFD image outcomes phải là `6.064/291/908` một/không/nhiều detection; YuNet là `5.943/2/1.318`. Tập valid SCRFD phải `4.215`, YuNet `4.055`; giao phải `3.666` cặp. Nếu lệch, dừng trước diễn giải ô mới.
- Trên valid riêng, cổng pair-fold: SCRFD+MBF FA/FR `133/125`; SCRFD+R50 `76/74`; YuNet+MBF `183/176`. Kiểm `valid + unresolved = 6.000`, genuine/impostor tổng đúng 3.000 mỗi loại. Đây là cổng hồi quy của E2/X-012-F, không là acceptance nghiệp vụ.
- Báo kết quả YuNet+R50 và so bốn nhánh trên giao 3.666 cặp, cùng các mẫu số. Nêu rõ nếu R50 cải thiện lỗi nhưng tốn thêm chi phí encoder theo M2; M1/M2 là run khác nhau, **không cộng** median thành latency pipeline. Không chọn cấu hình cửa phòng, không suy từ multi detection của XQLFW ra số người trong lượt, không đo S4 người đưa mã.

**Quyết định sau run:** giữ B0 làm mốc gốc trừ khi phát hiện lỗi tái lập/cấu hình nghiêm trọng; ghi ô YuNet+R50 là đối chứng nếu có giá trị. Sau đó chuyển sang phân tích B0 và optimization trên cùng protocol, không chạy thêm tổ hợp chọn model trong T-012.
