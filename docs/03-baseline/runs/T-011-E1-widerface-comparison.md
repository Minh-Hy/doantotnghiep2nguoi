# T-011 — E1: đối chiếu ba candidate detection trên WIDER FACE validation

**Ngày đối chiếu:** 2026-09-27. **Phạm vi:** detection S3; chưa chọn detector/model cuối.

## Câu hỏi được kiểm

Ba candidate được T-009 giữ để thử và T-010 đặt cấu hình/giao thức trước khi đo có khác nhau thế nào về **phát hiện bbox mặt** trên cùng 3.226 ảnh WIDER validation? E1 chưa kiểm chọn người mục tiêu S4, xác minh 1:1, quyền vào phòng hoặc attendance của T-008.

## Điều kiện chung và nguồn bằng chứng

Cả ba run dùng `WIDER_val.zip` và `wider_face_split.zip` cùng hash ở [data gate](../T-011-E1-widerface-data-gate.md): 3.226 ảnh, 39.112 valid GT, 585 ignored GT, không GT ngoài biên; cùng [evaluator AP nội bộ](../../../scripts/t011_widerface_evaluate.py), IoU > 0,5 và quy tắc ignore/duplicate của [T-010](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md). Config/weight/runtime của từng candidate nằm ở [YuNet](T-011-E1-widerface-yunet.md), [BlazeFace](T-011-E1-widerface-blazeface.md), [SCRFD](T-011-E1-widerface-scrfd.md). Prediction thô không được commit; số tổng hợp có thể đối chiếu ở các GitHub Actions run được dẫn trong từng báo cáo.

| Candidate / run | Project AP IoU > 0,5 | Recall cực đại | TP | FP | Prediction rows | Box rỗng sau clip |
|---|---:|---:|---:|---:|---:|---:|
| YuNet [run 36294898744](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294898744) | **0,648304** | **0,739466** | 28.922 | 1.166.280 | 1.195.480 | 182 |
| SCRFD-500MF [run 36296357372](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36296357372/job/108555827946) | 0,547370 | 0,634179 | 24.804 | 4.238.731 | 4.858.820 | 595.274 |
| BlazeFace full-range [run 36296108522](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36296108522/job/108555142384) | 0,136009 | 0,180584 | 7.063 | 467.368 | 477.622 | 3.191 |

**Diễn giải:** Với đúng cấu hình v1 và AP nội bộ này, YuNet đứng đầu về AP/recall, SCRFD thứ hai, BlazeFace thứ ba. Đây là kết quả **theo dữ liệu và điều kiện đã đo**, không phải thứ hạng phổ quát hoặc quyết định kỹ thuật cuối. AP là tích phân đường precision–recall; FP ở ngưỡng output thấp không tương đương số ca cho vào nhầm. Cần xem lý do SCRFD có nhiều box rỗng/clipped; không chỉnh adapter hay protocol sau khi thấy điểm mà không mở revision và chạy lại cả candidate liên quan.

## Điều chưa được kiểm và quyết định tiếp

- Không có official WIDER Easy/Medium/Hard benchmark; evaluator dùng validation TXT và quy tắc project đã đặt trước.
- Ảnh WIDER không đại diện đầy đủ cho camera cửa phòng thi; chưa có domain-specific detection evaluation, kiểm S4 chọn một người trong khung, hoặc tác động đến verification E2 và nghiệp vụ E3.
- Các số median/p95 trên GitHub CPU runner thuộc lượt riêng, tải máy không kiểm soát và chưa cùng thiết bị đích; **không dùng để xếp hạng latency/compute**. M1 vẫn mở.
- Không có acceptance target nghiệp vụ được xác nhận hoặc policy kỳ thi cụ thể; không thể tuyên bố candidate nào đủ triển khai.

**Quyết định ở mức T-011:** E1 đã có bằng chứng thực nghiệm cho cả ba candidate theo protocol v1. Chuyển các sai khác AP/recall, box clipped/rỗng và domain gap sang T-012 để đặt câu hỏi thí nghiệm tiếp. Giữ cả ba run và cấu hình để truy vết; chưa chốt detector, threshold hay architecture.
