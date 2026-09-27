# T-012 X-012-F — YuNet/SCRFD trước cùng MobileFaceNet trên XQLFW

**Ngày:** 27/09/2026. **Câu hỏi:** khi giữ cùng encoder MBF, ảnh và protocol cặp XQLFW, đổi detector+landmark YuNet/SCRFD ảnh hưởng coverage và lỗi xác minh 1:1 thế nào? Đây là phép thử **interface S3→S7** của [ma trận ứng viên](../T-012-candidate-evidence-matrix.md), không chấm S4 chọn đúng người đưa mã.

## Protocol và cổng kiểm

- [Protocol X-012-F](../T-012-X-012-F-detector-encoder-interface-protocol.md) commit `8ea8567` **trước run**; script/test/workflow commit `e1c6a06`. [GitHub Actions run 36332073757](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36332073757) thành công sau 8m25s; thời gian job **không** là latency theo lượt.
- Cùng XQLFW ZIP SHA-256 `1af459679fba23a12f4d83c82a81523eb930a4aec759eebefcbdde69a678962c`, pairs `636852f90b886f3f56c73b13c9775f7ffcd37662dbb189c694f6a0a605b63b84`, `buffalo_sc.zip` `57d31b56b6ffa911c8a73cfc1707c73cab76efe7f13b675a05223bf42de47c72` và YuNet ONNX `ebafce4e3c118d6554634be5c27ab333b4c047a9a8c3faf1d7cf93101c22f0f0`; script kiểm hash trước khi chấm. Ubuntu GitHub runner, Python 3.12, OpenCV 5.0.0.93, InsightFace 0.7.3, ONNX Runtime 1.20.1, NumPy 2.2.6; CPU và ba biến thread OMP/OPENBLAS/MKL = 1.
- SCRFD-500MF dùng `FaceAnalysis` E2 input 640×640, threshold 0,5. YuNet 2026may dùng ảnh gốc/input động, threshold 0,5, NMS 0,3, topK 5.000; landmark 5 điểm theo schema OpenCV đưa vào `norm_crop` 112×112. **Cùng MBF weight, L2/cosine**. Rule chỉ cấp score khi cả hai ảnh cặp đều đúng một face có embedding; 0 hoặc nhiều detection là chưa kết luận. Threshold pair-fold được chọn trên 9 fold dev cho từng nhánh, không chỉnh theo fold test.
- Cổng SCRFD tái lập đúng [E2](T-011-E2-xqlfw-mbf-vs-r50.md): 7.263 ảnh tham chiếu → `6.064/291/908` ảnh một/không/nhiều mặt; **4.215** cặp có score; FA/FR MBF `133/125`. Cổng và tổng `valid + outside = 6.000` đều qua. File ảnh, model, embedding và JSON chi tiết chỉ ở `RUNNER_TEMP`, được xóa cuối job; repo/log giữ số tổng hợp.

## Coverage

| Detector trước MBF | Ảnh một / không / nhiều detection (mẫu số 7.263) | Cặp có score / 6.000 | Genuine có score / 3.000 | Impostor có score / 3.000 |
|---|---:|---:|---:|---:|
| SCRFD | 6.064 / 291 / 908 | **4.215** (70,25%) | 2.046 | 2.169 |
| YuNet | 5.943 / 2 / 1.318 | **4.055** (67,58%) | 1.992 | 2.063 |

SCRFD có thêm **160 cặp có score** trên protocol này. YuNet có ít ảnh không detection hơn nhưng nhiều ảnh **nhiều detection** hơn; XQLFW không có nhãn bbox/target ở mức cần để kết luận những box thêm là người thật, false positive hay người đã đưa mã. Các cặp ngoài tập có score lần lượt SCRFD `954 genuine + 831 impostor`, YuNet `1.008 + 937`; chúng là **unresolved của rule thử**, không là false reject hay thí sinh vắng.

## Lỗi trên cặp được chấm — hai cách đọc khác nhau

| Tập cặp | Detector | Genuine / impostor có score | FR / genuine (FNMR) | FA / impostor (FMR) |
|---|---|---:|---:|---:|
| Tập riêng của detector | SCRFD | 2.046 / 2.169 | 125/2.046 (6,11%) | 133/2.169 (6,13%) |
| Tập riêng của detector | YuNet | 1.992 / 2.063 | 176/1.992 (8,84%) | 183/2.063 (8,87%) |
| **Giao cùng 3.666 cặp** | SCRFD | **1.779 / 1.887** | **108/1.779 (6,07%)** | **114/1.887 (6,04%)** |
| **Giao cùng 3.666 cặp** | YuNet | **1.779 / 1.887** | **116/1.779 (6,52%)** | **121/1.887 (6,41%)** |

Tập riêng khác nhau: có **549 cặp chỉ SCRFD** và **389 cặp chỉ YuNet** qua rule một mặt. Vì vậy không lấy chênh lệch `8,87% − 6,13%` của hai tập riêng làm tác động thuần của detector. Trong **giao 3.666 cặp** với cùng mẫu số và MBF, YuNet có thêm 8 FR và 7 FA so SCRFD theo threshold pair-fold được chọn riêng trên dev của giao. Đây là chênh lệch mô tả nhỏ trên cặp web phụ thuộc theo ảnh/người; chưa có kiểm bất định theo danh tính hoặc miền cửa phòng. Nó cũng không tách riêng ảnh hưởng bbox khỏi landmark/alignment vì detector thay cả hai.

## Diễn giải và quyết định ở mức nghiên cứu

**Observed:** ở XQLFW với rule đúng một mặt và detection threshold 0,5, YuNet tạo ít ảnh zero detection hơn nhưng nhiều ảnh multi detection hơn, dẫn đến ít cặp có score hơn SCRFD. Trên phần giao cặp hợp lệ, SCRFD+MBF ít FA/FR hơn YuNet+MBF một lượng nhỏ. Điều này bổ sung cho [WIDER S3](T-012-S4-widerface-size-strata.md): YuNet dẫn ở mặt rất nhỏ nhiều người trên WIDER, nhưng ưu thế phát hiện đó **không tự chuyển thành coverage xác minh tốt hơn** khi dùng rule một mặt trên XQLFW.

**Giới hạn:** XQLFW là ảnh web/crop, nhiều detection không chứng minh nhiều người trước cửa phòng. Pair-fold chia cặp, không là kiểm độc lập danh tính/pretrain; threshold 0,5 của detector là cấu hình thí nghiệm, không phải ngưỡng nghiệp vụ. Không có nhãn người đưa mã để thử chọn một mặt từ ảnh nhiều detection; chưa đo thời gian pipeline cùng runner/thiết bị đích hoặc policy. Không sửa YuNet threshold theo điểm này rồi báo lại trên chính XQLFW như locked test.

**Quyết định T-012:** tiếp tục giữ **cả YuNet và SCRFD** là ứng viên S3 vì bằng chứng WIDER/XQLFW khác điều kiện và cùng có trade-off. Rule A0 một mặt để unresolved khi mơ hồ tiếp tục là đối chứng an toàn trong nghiên cứu. Câu hỏi S4 chọn đúng người theo lượt vẫn mở; phép này không cấp quyền chọn YuNet, SCRFD, MBF hay threshold cuối cho app.
