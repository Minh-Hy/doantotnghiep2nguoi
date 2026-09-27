# T-011 — E2 đối chứng MobileFaceNet và R50 trên XQLFW

**Ngày chạy:** 2026-09-26–27. **Người chạy:** Codex theo yêu cầu Quốc An. **Trạng thái:** phép thử 1:1 học thuật thăm dò, chưa là main test hay quyết định model cuối. Kết quả [run MobileFaceNet đầu tiên](T-011-E2-xqlfw-mbf.md) được giữ nguyên.

## Câu hỏi và phương pháp

Sau khi MobileFaceNet chạy được trên XQLFW nhưng còn lỗi xác minh, encoder R50 trong shortlist T-009 có giảm FMR/FNMR trên **chính các cặp hợp lệ đó** khi giữ detector/alignment không? Đây là câu hỏi E2 từ [T-010 PR #6](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6), không phải phép đo toàn bộ nghiệp vụ cửa phòng.

- **Biến thay đổi:** encoder MobileFaceNet@WebFace600K trong buffalo_sc hoặc R50@WebFace600K trong buffalo_l. Chỉ lấy w600k_r50.onnx từ buffalo_l; không dùng detector SCRFD-10GF của pack này.
- **Giữ cố định:** cùng XQLFW ZIP/pairs, SCRFD-500MF của buffalo_sc (input 640×640, detection threshold 0,5), cùng khuôn mặt và 5 landmarks do detector trả, InsightFace norm_crop 112×112, L2 normalization, cosine similarity. Chỉ ảnh có đúng một mặt được dùng; hai encoder nhận đúng **cùng 4.215 cặp**. R50 và MobileFaceNet đều được runtime InsightFace nhận input mean/std 127,5/127,5.
- **Split/ngưỡng:** 10 pair-fold chính thức. Với mỗi fold chấm, chọn threshold của **từng encoder** trên 9 fold còn lại bằng quy tắc cân bằng |FMR − FNMR| của T-010; fold chấm không tham gia chọn. Threshold chỉ là ngưỡng báo cáo experiment, không là policy cho vào phòng.
- **Metric:** FMR/FNMR ngoài fold với mẫu số, ROC AUC/EER mô tả, coverage ảnh/cặp. Không có target chấp nhận nghiệp vụ đã chốt, nên kết quả chỉ so theo điều kiện đo hiện tại.

## Nguồn và tái lập

[XQLFW và pairs từ tác giả](https://martlgap.github.io/xqlfw/pages/download.html) dùng đúng file/hash của run gốc. [InsightFace Model Zoo](https://github.com/deepinsight/insightface/blob/master/model_zoo/README.md) nêu buffalo_sc dùng MobileFaceNet@WebFace600K, buffalo_l dùng R50@WebFace600K và giới hạn model cho nghiên cứu phi thương mại; hai pack được tải từ [release chính thức](https://github.com/deepinsight/insightface/releases/tag/model-zoo). Sổ [external-assets](../../00-project/external-assets.md) ghi byte/hash từng archive và ONNX. buffalo_l.zip: 288.621.354 byte, SHA-256 80FFE37D8A5940D59A7384C201A2A38D4741F2F3C51EEF46EBB28218A7B0CA2F; w600k_r50.onnx: SHA-256 4C06341C33C2CA1F86781DAB0E829F88AD5B64BE9FBA56E56BC9EBDEFC619E43. ZIP CRC đã qua; smoke 20 ảnh thật tạo 16 embedding.

Runner: [commit 9d7a0ac](https://github.com/quocanwyf/doantotnghiep2nguoi/commit/9d7a0ac), scripts/t011_xqlfw_r50_comparison.py. Chạy với các đối số --images, --pairs, --sc-model, --r50-model, --cache, --checkpoint-dir, --output và --chunk-size 100. Checkpoint chứa embedding/tên path **chỉ ở thư mục tạm ngoài Git**, được kiểm lại bằng hash đầu vào và thứ tự ảnh; JSON cuối chỉ có thống kê tổng hợp. Lần chạy liên tục đầu tiên bị lỗi thiếu bộ nhớ khi máy có ứng dụng khác; bản chunked hoàn tất, nên **không dùng thời gian run này để so latency**. Checkpoint trung gian đã xóa sau khi kiểm kết quả.

Máy: AMD Ryzen 5 5600H, RAM 16,48 GB, Windows build 26200; Python 3.12.2, InsightFace 0.7.3, ONNX Runtime 1.20.1 CPU, OpenCV 5.0.0, NumPy 2.2.6, scikit-learn 1.7.1. Không có seed ngẫu nhiên trong protocol hoặc runner.

## Kết quả

Ảnh được tham chiếu: 7.263; đúng một mặt: **6.064**, không mặt: 291, nhiều mặt: 908. Cặp hợp lệ: **4.215/6.000** gồm 2.046 genuine và 2.169 impostor. Coverage và toàn bộ kết quả MobileFaceNet chạy lại **khớp chính xác** run gốc, kể cả ROC AUC/EER.

| Encoder | False accept / impostor | FMR | False reject / genuine | FNMR | ROC AUC mô tả | EER lưới mô tả |
|---|---:|---:|---:|---:|---:|---:|
| MobileFaceNet | 133/2.169 | 6,13% | 125/2.046 | 6,11% | 0,9807 | 6,07% |
| R50 | 76/2.169 | 3,50% | 74/2.046 | 3,62% | 0,9908 | 3,54% |

Trên các cặp hợp lệ này, R50 có ít hơn **57 false accept** và **51 false reject**; FMR thấp hơn 2,63 điểm phần trăm, FNMR thấp hơn 2,49 điểm phần trăm. Các khoảng Wilson 95% nếu giả sử cặp độc lập là R50 FMR [2,81%; 4,36%] và FNMR [2,89%; 4,52%]. Cặp chia sẻ ảnh/identity, nên các khoảng này **không phản ánh đầy đủ bất định theo người/domain**.

| Fold | Genuine / impostor hợp lệ | MBF: FR / FA | R50: FR / FA |
|---:|---:|---:|---:|
| 1 | 207 / 227 | 10 / 16 | 8 / 12 |
| 2 | 204 / 228 | 12 / 15 | 5 / 6 |
| 3 | 208 / 215 | 12 / 11 | 9 / 3 |
| 4 | 195 / 210 | 13 / 13 | 4 / 13 |
| 5 | 197 / 223 | 15 / 12 | 7 / 4 |
| 6 | 195 / 215 | 6 / 12 | 5 / 9 |
| 7 | 208 / 199 | 14 / 13 | 9 / 6 |
| 8 | 215 / 224 | 13 / 11 | 12 / 9 |
| 9 | 204 / 209 | 11 / 15 | 8 / 9 |
| 10 | 213 / 219 | 19 / 15 | 7 / 5 |

## Diễn giải và quyết định tiếp theo

**Evidence trong phạm vi hẹp:** R50 tách genuine/impostor tốt hơn MobileFaceNet trên tập **cặp XQLFW dùng được** với detector/alignment cố định và threshold được chọn ngoài fold. Đây là lý do giữ R50 làm ứng viên trong các phép đo tiếp theo; MobileFaceNet tiếp tục là mốc nhẹ. File ONNX R50 174.383.860 byte, khoảng 12,8 lần file MobileFaceNet 13.616.099 byte; chưa đo latency, RAM đỉnh hoặc khả năng chạy trên thiết bị đích trong điều kiện kiểm soát, nên chưa biết đánh đổi chất lượng–chi phí có phù hợp không.

Không chọn model cuối hoặc threshold triển khai từ run này. XQLFW là ảnh web/crop khác miền cửa phòng; 1.785 cặp bị loại có thể làm metric trên cặp hợp lệ bị lệch; pair-fold trùng identity, overlap với dữ liệu train chưa kiểm; không có nhãn chọn người mục tiêu giữa nhiều mặt, profile policy kỳ thi, E1/E3/M1 hay main test. Bước sau cần main test/split phù hợp hơn, kiểm coverage S4 và đo tài nguyên có kiểm soát trên thiết bị mục tiêu trước final technical decision.
