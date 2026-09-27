# T-011 — E2 exploratory XQLFW / buffalo_sc MobileFaceNet

**Ngày chạy:** 2026-09-26. **Người chạy:** Codex theo yêu cầu Quốc An. **Loại bằng chứng:** phép thử học thuật thăm dò, không là locked main test hay final technical decision. Xem [review đầu vào T-011](../T-011-readiness-review.md).

## Câu hỏi và thiết kế

Trên cặp ảnh xác minh 1:1 có chênh lệch chất lượng của XQLFW, pipeline SCRFD-500MF → căn chỉnh chính thức InsightFace → MobileFaceNet trong buffalo_sc tạo được bao nhiêu cặp dùng được, và FMR/FNMR mô tả là bao nhiêu? Câu hỏi xuất phát từ T-008 TQ-002/003, candidate T-009 và protocol E2 ở [T-010 PR #6](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6).

- **Đầu vào:** một pack buffalo_sc, không so model khác trong run này; 6.000 pairs của [XQLFW tác giả](https://martlgap.github.io/xqlfw/pages/download.html).
- **Split:** 10 fold theo thứ tự file pairs. Với mỗi fold, threshold chọn trên 9 fold còn lại bằng |FMR − FNMR| nhỏ nhất; hòa thì chọn FMR thấp hơn rồi threshold cao hơn. Fold đang chấm không tham gia chọn ngưỡng. Identity trùng giữa các fold: đây là pair-fold evaluation, không là unseen-identity test.
- **Pipeline cố định:** InsightFace 0.7.3 FaceAnalysis với CPUExecutionProvider; SCRFD input 640×640, detection threshold 0,5; yêu cầu đúng một mặt trên mỗi ảnh; alignment 112×112 của InsightFace; MobileFaceNet embedding 512 chiều, chuẩn L2 và cosine similarity. Không tuning trên score của run này.
- **Ảnh/cặp không dùng được:** ảnh decode lỗi, không có mặt hoặc có nhiều mặt không tạo embedding; cặp chứa một ảnh như vậy bị loại khỏi FMR/FNMR và được tính vào coverage. Đây là quy tắc đặt trước khi chạy toàn bộ, không sửa sau khi xem kết quả.

## Nguồn, phiên bản và tái lập

- **Commit mã chạy:** [03c68d6](https://github.com/quocanwyf/doantotnghiep2nguoi/commit/03c68d6d358aa09d4bfbd30a5c0641ad9358a0b2), file scripts/t011_xqlfw_baseline.py; ba unit test protocol đã qua.
- **XQLFW ZIP:** 195.229.543 byte, SHA-256 1AF459679FBA23A12F4D83C82A81523EB930A4AEC759EEBEFCBDDE69A678962C; pairs TXT 160.795 byte, SHA-256 636852F90B886F3F56C73B13C9775F7FFCD37662DBB189C694F6A0A605B63B84. 6.000 path cặp có ảnh trong archive, kiểm CRC trước T-011.
- **Model ZIP:** [InsightFace buffalo_sc](https://github.com/deepinsight/insightface/blob/master/model_zoo/README.md), 14.969.382 byte, SHA-256 57D31B56B6FFA911C8A73CFC1707C73CAB76EFE7F13B675A05223BF42DE47C72. Bên trong: det_500m.onnx SHA-256 5E4447F50245BBD7966BDC0FA52938C61474A04EC7DEF48753668A9D8B4EA3A; w600k_mbf.onnx SHA-256 9CC6E4A75F0E2BF0B1AED94578F144D15175F357BDC05E815E5C4A02B319EB4F.
- **Máy tham chiếu:** AMD Ryzen 5 5600H, 6 core/12 logical CPU, RAM 16,48 GB; Windows build 26200. Python 3.12.2, OpenCV runtime 5.0.0 từ opencv-contrib-python 5.0.0.93, ONNX Runtime 1.20.1 CPU, InsightFace 0.7.3, NumPy 2.2.6, scikit-learn 1.7.1. Không đo trên thiết bị đích.
- **Cách chạy:** tạo môi trường có các phiên bản trên; cung cấp ba file tải từ nguồn tác giả, lưu ngoài Git. Dùng script scripts/t011_xqlfw_baseline.py với các đối số --images (XQLFW ZIP), --pairs (TXT), --model (buffalo_sc ZIP), --cache (thư mục ngoài Git) và --output (artifacts/t011-xqlfw-mbf-summary.json). Script kiểm ba SHA-256 đầu vào, không ghi ảnh/tên/embedding vào output.

## Kết quả quan sát

- **Ảnh được tham chiếu:** 7.263; đúng một mặt và embedding: **6.064 (83,49%)**; không thấy mặt: 291; nhiều mặt: 908; decode lỗi: 0.
- **Cặp:** 4.215/6.000 dùng được (**70,25%**). Loại 1.785 cặp, gồm 954 genuine và 831 impostor. Các tỷ lệ lỗi bên dưới **có điều kiện trên cặp dùng được**, không đại diện tất cả lượt.
- **FMR:** 133 false accept / 2.169 impostor cặp dùng được = **6,13%**. **FNMR:** 125 false reject / 2.046 genuine cặp dùng được = **6,11%**. Đây là tổng dự đoán ngoài fold, mỗi fold dùng threshold riêng chọn từ 9 fold còn lại.
- **ROC AUC mô tả trên cặp hợp lệ:** 0,9807; EER xấp xỉ trên lưới ROC: 6,07%. Hai metric này xem nhãn toàn tập để mô tả separation, không dùng chọn ngưỡng cho fold chấm.
- **Khoảng Wilson 95% nếu giả sử các cặp độc lập:** FMR [5,20%; 7,22%], FNMR [5,15%; 7,23%]. Nhiều cặp chia sẻ ảnh/identity, nên khoảng này **không phản ánh đầy đủ bất định theo người hoặc domain**.
- **Thời gian decode + detection + embedding:** tổng 586,2 giây; median 78 ms/ảnh, p95 125 ms/ảnh. Máy có hoạt động khác trong lúc chạy, nên đây chỉ là số tham khảo để tìm chi phí, **không là benchmark latency so sánh công bằng** và không gồm giao dịch cửa phòng.

### Kiểm từng fold

| Fold | Genuine dùng được | Impostor dùng được | False reject | False accept | FMR | FNMR |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 207 | 227 | 10 | 16 | 7,05% | 4,83% |
| 2 | 204 | 228 | 12 | 15 | 6,58% | 5,88% |
| 3 | 208 | 215 | 12 | 11 | 5,12% | 5,77% |
| 4 | 195 | 210 | 13 | 13 | 6,19% | 6,67% |
| 5 | 197 | 223 | 15 | 12 | 5,38% | 7,61% |
| 6 | 195 | 215 | 6 | 12 | 5,58% | 3,08% |
| 7 | 208 | 199 | 14 | 13 | 6,53% | 6,73% |
| 8 | 215 | 224 | 13 | 11 | 4,91% | 6,05% |
| 9 | 204 | 209 | 11 | 15 | 7,18% | 5,39% |
| 10 | 213 | 219 | 19 | 15 | 6,85% | 8,92% |

## Diễn giải và quyết định

Kết quả cho thấy pipeline **chạy được trên ảnh thật**, nhưng 1.785/6.000 cặp không qua được quy tắc một mặt. Tỷ lệ nhiều mặt do detector báo trên ảnh crop đáng điều tra; run này không có nhãn cho từng detection để kết luận nguyên nhân hoặc tùy tiện chọn mặt điểm cao nhất. Không được diễn giải FMR/FNMR trên 4.215 cặp như lỗi của toàn bộ 6.000 cặp hay của cửa phòng thi.

**Quyết định T-011:** giữ kết quả làm mốc thăm dò E2 và đầu vào phân tích lỗi T-012. Câu hỏi kế tiếp là vì sao coverage thấp và liệu quy tắc chọn/loại mặt hoặc một detector khác cải thiện coverage mà không tăng false accept. Cần một encoder khác vượt gate T-009 để so chất lượng dưới cùng protocol; cần main test có split/domain phù hợp trước quyết định kỹ thuật cuối. Chưa chọn model hoặc threshold triển khai.

## Giới hạn và dữ liệu ngoài Git

XQLFW là ảnh web/crop, không có claim phòng thi, roster, camera/ánh sáng cửa phòng, target giữa nhiều người, chính sách vào hoặc attendance. Fold chính thức trùng identity, overlap với dữ liệu train WebFace600K của pretrained weight chưa kiểm chứng. Việc loại cặp không ngẫu nhiên có thể làm số liệu lỗi bị lệch. Không có E1 detector benchmark trên ảnh nguyên khung, E3 workflow implementation hay M1 vận hành ở run này.

JSON tổng hợp nằm cục bộ trong thư mục artifacts bị ignore; không đưa archive ảnh, tên identity, embedding, checkpoint hoặc raw prediction vào Git. Nguồn và hash file ngoài Git ghi trong [external-assets](../../00-project/external-assets.md).

## Chẩn đoán coverage hậu nghiệm

[Phân tích T-011](T-011-E2-coverage-diagnosis.md) phân tách lý do loại 1.785 cặp trên đúng input/detector của run này. Đây là quan sát sau khi xem kết quả; không sửa quy tắc hoặc số đo E2 gốc.

## Đối chứng encoder tiếp theo

[Run T-011 MobileFaceNet so R50](T-011-E2-xqlfw-mbf-vs-r50.md) dùng đúng các cặp hợp lệ và cùng detector/alignment; run gốc ở trên vẫn là mốc bất biến. Kết quả so sánh chỉ có điều kiện trên cặp dùng được.
