# T-011 — E2 XQLFW: kiểm ngưỡng với nhóm danh tính tách rời

**Run:** [GitHub Actions 36306431440](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36306431440), hoàn tất 2026-09-27, commit `766b02e514abb7a9a55041751bbee208d4c4845b`. **Phạm vi:** phép kiểm độ nhạy của E2 trên XQLFW, không phải 10-fold chính thức hoặc test camera cửa phòng. [Quy tắc chia và audit pairs](../T-011-E2-identity-split-feasibility.md) được ghi trước khi chấm ảnh.

## Câu hỏi và điều kiện giữ cố định

Kết quả đối chứng [pair-fold gốc](T-011-E2-xqlfw-mbf-vs-r50.md) có còn cùng chiều khi **danh tính dùng chọn ngưỡng và danh tính dùng chấm không giao nhau**? Hai encoder vẫn nhận cùng ảnh, SCRFD-500MF/landmark, `norm_crop` 112×112, L2 và cosine của run gốc. XQLFW ZIP/pairs, buffalo_sc/buffalo_l và ONNX được kiểm bằng đúng SHA-256 trong [external-assets](../../00-project/external-assets.md); detector threshold 0,5, input 640×640. Runtime GitHub Actions `ubuntu-latest` CPU, Python 3.12, OpenCV 5.0.0.93, InsightFace 0.7.3, ONNX Runtime 1.20.1, NumPy 2.2.6, scikit-learn 1.7.1. Split xác định bằng hash cố định, không dùng random seed hay score.

Mỗi identity thuộc nhóm 0 hoặc 1. Khi chấm nhóm 0, threshold của **từng encoder** lấy từ cặp hợp lệ nhóm 1 theo quy tắc cân bằng |FMR − FNMR| T-010; rồi đổi vai nhóm. Cặp impostor nối hai nhóm bị loại để không đưa identity của test vào dev. Cặp phải có đúng một detection ở cả hai ảnh; không tự chọn mặt cho cặp mơ hồ. Không tune ngưỡng trên nhóm đang chấm.

## Cổng tái lập và coverage

Chạy lại nhánh 10 pair-fold cũ trong cùng job cho **4.215 cặp hợp lệ** và thu đúng các số tổng hợp đã công bố: MobileFaceNet FA 133/2.169, FR 125/2.046; R50 FA 76/2.169, FR 74/2.046, cùng ROC AUC/EER. Cổng này giảm rủi ro cấu hình mới vô tình đổi protocol gốc; nó không chứng minh mọi prediction theo ảnh giống bit-for-bit.

| Tập custom | Genuine trước lọc mặt | Impostor trước lọc mặt | Genuine hợp lệ | Impostor hợp lệ | Hợp lệ/tổng trước lọc |
|---|---:|---:|---:|---:|---:|
| Nhóm 0 | 1.490 | 743 | 1.029 | 534 | 1.563/2.233 = 70,00% |
| Nhóm 1 | 1.510 | 773 | 1.017 | 558 | 1.575/2.283 = 68,99% |
| Cả hai nhóm | 3.000 | 1.516 | 2.046 | 1.092 | **3.138/4.516 = 69,49%** |

Trước bước mặt, split loại 1.484 impostor nối hai nhóm. Trong số đó, **1.077 cặp vốn qua rule một mặt** nhưng bị loại chỉ vì protocol tách danh tính. Trong 4.516 cặp đủ điều kiện split, 1.378 cặp không qua rule một mặt (954 genuine, 424 impostor). Vì vậy 3.138/6.000 = 52,30% của toàn bộ pairs gốc được đưa vào phép chấm custom; phần còn lại gồm cả **loại theo thiết kế split** và **unresolved do pipeline mặt**, không được gộp thành một loại lỗi hay suy tỷ lệ review tại cửa phòng.

## Kết quả tại threshold chọn ngoài nhóm chấm

| Encoder | Nhóm test | Genuine | Impostor | False reject | False accept | Threshold từ nhóm dev |
|---|---:|---:|---:|---:|---:|---:|
| MobileFaceNet | 0 | 1.029 | 534 | 60 | 37 | 0,117016 |
| MobileFaceNet | 1 | 1.017 | 558 | 61 | 31 | 0,120677 |
| R50 | 0 | 1.029 | 534 | 40 | 30 | 0,114648 |
| R50 | 1 | 1.017 | 558 | 35 | 14 | 0,123886 |

Tổng hợp trên **chính 3.138 cặp hợp lệ chung**:

| Encoder | FMR | FNMR |
|---|---:|---:|
| MobileFaceNet | 68/1.092 = **6,23%** | 121/2.046 = **5,91%** |
| R50 | 44/1.092 = **4,03%** | 75/2.046 = **3,67%** |

**Quan sát trong phạm vi này:** R50 ít hơn 24 false accept và 46 false reject so với MobileFaceNet. Hai nhóm có FMR khác nhau, đặc biệt R50: 30/534 ở nhóm 0 và 14/558 ở nhóm 1; vì vậy không chỉ nhìn một tỷ lệ gộp. So trực tiếp các tỷ lệ custom này với pair-fold gốc **không cô lập riêng tác động identity split**, vì gần nửa impostor bị loại theo thiết kế và threshold được chọn lại. Kết quả chỉ cho thấy chiều chênh lệch MBF/R50 vẫn tồn tại trên tập custom đã định trước.

## Giới hạn và tác động đến bước sau

Identity chỉ tách giữa **dev chọn threshold và test của phép đo này**; chưa kiểm identity trong tập pretrain WebFace600K. Cặp/ảnh có thể phụ thuộc lẫn nhau theo người; không diễn giải tỷ lệ như 3.138 lượt thí sinh độc lập. XQLFW là ảnh web/crop, không có target selection S4 hoặc policy check-in; 1.378 cặp đủ điều kiện split vẫn bị rule một mặt giữ `unresolved`. 1.092 impostor hợp lệ chỉ hỗ trợ kết luận mô tả, không xác nhận operating point FMR thấp theo yêu cầu nghiệp vụ chưa đặt. Không đo latency/RAM encoder trên thiết bị đích.

**Quyết định ở mức T-011:** giữ MobileFaceNet làm đối chứng nhẹ và R50 làm candidate có lỗi xác minh thấp hơn trong cả hai phép thử XQLFW, nhưng **không chọn model/threshold cuối**. Chuyển coverage S4, domain gap và đánh đổi chất lượng–chi phí sang [T-012](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/8). Nếu muốn kết luận triển khai, cần dữ liệu/nhãn gần cửa phòng, test không dùng tuning, thiết bị đo và mục tiêu rủi ro có nguồn.
