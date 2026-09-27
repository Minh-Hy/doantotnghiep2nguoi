# T-012 — WIDER E1: so detector trên ảnh một mặt và nhiều mặt

**Run:** [GitHub Actions 36322220681](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36322220681), 2026-09-27, ba job thành công. **Mã đặt trước run:** commit `b424cd3`; [kế hoạch và cổng đọc kết quả](../T-012-S4-one-vs-multi-comparison-plan.md). Đây là phân tích **sau E1 tổng thể T-011**, với nhóm ảnh và metric đã ghi trước khi xem điểm nhóm; không phải benchmark WIDER Easy/Medium/Hard chính thức.

## Câu hỏi và điều kiện đo

So YuNet, SCRFD-500MF và BlazeFace full-range trên cùng WIDER FACE validation, phân ảnh bằng **số bbox mặt hợp lệ trong GT**, không bằng output của detector: 0, đúng 1, hoặc từ 2 mặt trở lên. Dùng lại archive, weight, cấu hình, prediction wrapper, IoU > 0,5, ignored-GT logic và project AP của [E1 T-011](T-011-E1-widerface-comparison.md). [Workflow](../../../.github/workflows/t012-e1-error-slices.yml) chạy Ubuntu GitHub Actions/Python 3.12, mỗi candidate một job; prediction theo ảnh và weight chỉ nằm trong thư mục tạm rồi được xóa. Không dùng số thời gian job để so latency detector hay thiết bị đích.

Hash archive ảnh `f9efbd09f28c5d2d884be8c0eaef3967158c866a593fc36ab0413e4b2a58a17a`; hash archive nhãn `c7561e4f5e7a118c249e0a5c5c902b0de90bbf120d7da9fa28d99041f68a8a5c`. [Scorer](../../../scripts/t012_widerface_one_multi.py) gọi lại đúng evaluator E1 cho từng tập ảnh rời nhau. Số ảnh, valid GT, prediction, TP/FP, neutral, drop và clip của ba nhóm phải cộng khớp E1 tổng; cả ba job đã qua cổng này. AP từng nhóm được tính độc lập, **không** cộng hoặc lấy trung bình để tạo AP toàn tập.

## Mẫu số và phân bố mặt

| Nhóm ảnh theo valid GT | Ảnh | Valid GT | Ignored GT | GT <16 px | GT 16–<32 px | GT 32–<96 px | GT ≥96 px |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 mặt hợp lệ | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| Đúng 1 mặt | 1.119 | 1.119 | 1 | 5 | 26 | 248 | 840 |
| ≥2 mặt | 2.103 | 37.993 | 584 | 17.906 | 10.242 | 8.358 | 1.487 |
| **Tổng** | **3.226** | **39.112** | **585** | **17.911** | **10.268** | **8.606** | **2.327** |

Cỡ mặt là căn bậc hai diện tích bbox GT trên ảnh gốc, theo bins T-012 đã dùng. Trong nhóm một mặt, **75,07% GT ≥96 px** và chỉ **0,45% GT <16 px**. Trong nhóm nhiều mặt, **47,13% GT <16 px** và chỉ **3,91% GT ≥96 px**. Do vậy hai nhóm khác mạnh về cỡ mặt; chênh lệch AP/recall **không được diễn giải là tác động nhân quả riêng của việc có nhiều người**.

## Kết quả detector

| Candidate | E1 toàn tập project AP | 1 mặt: TP/GT | 1 mặt: AP | 1 mặt: recall cực đại | ≥2 mặt: TP/GT | ≥2 mặt: AP | ≥2 mặt: recall cực đại |
|---|---:|---:|---:|---:|---:|---:|---:|
| YuNet | 0,648304 | 1.046/1.119 | 0,898846 | 93,48% | 27.876/37.993 | **0,642116** | **73,37%** |
| SCRFD-500MF | 0,547370 | 1.104/1.119 | **0,946234** | **98,66%** | 23.700/37.993 | 0,535381 | 62,38% |
| BlazeFace full-range | 0,136009 | 912/1.119 | 0,758517 | 81,50% | 6.151/37.993 | 0,116751 | 16,19% |

Nhóm 0 valid GT không có mẫu số để tính AP/recall; scorer ghi `null`, không ghi 0 như một điểm hiệu năng. Tổng TP theo nhóm lần lượt YuNet 28.922, SCRFD 24.804, BlazeFace 7.063, khớp cổng replay T-011. Prediction rows/drop cũng khớp. Clip box của YuNet và BlazeFace khớp chính xác; SCRFD có **534.289** box clip ở run này so **534.287** ở T-011 (lệch 2), đã được workflow ghi riêng; TP/rows/drop khớp và AP tổng làm tròn 6 chữ số không đổi. Không gọi SCRFD là tái lập bit-for-bit.

## Diễn giải và quyết định ở mức nghiên cứu

- **Quan sát:** SCRFD có AP/recall cao nhất trong nhóm ảnh đúng một mặt; YuNet cao nhất trong nhóm ảnh ≥2 mặt và toàn tập. BlazeFace thấp hơn hai candidate còn lại ở cả hai nhóm trong cấu hình đã pin.
- **Giới hạn giải thích:** nhóm ≥2 mặt đồng thời chứa nhiều mặt rất nhỏ. Bảng này chưa tách được ảnh hưởng cỡ mặt, độ che khuất, góc nhìn và mật độ cảnh. [Phân tích theo cỡ mặt trước đó](T-012-E1-widerface-error-slices.md) đã cho thấy nhóm <16 px khó cho cả ba detector; cần kết hợp hai lát cắt khi giải thích khác biệt. Rất nhiều prediction ở ngưỡng output thấp phục vụ đường precision–recall; FP bbox của E1 **không** là false acceptance của thí sinh.
- **Đánh đổi vận hành chưa chốt:** [M1 CPU runner tham chiếu](T-011-M1-reference-detection.md) đã đo median detection YuNet 25,72 ms, SCRFD 83,24 ms, BlazeFace 13,26 ms trên 60 ảnh khác điều kiện run này. Đây là bằng chứng chi phí riêng, không phải latency theo nhóm ảnh hay thời gian check-in. Không chọn detector cuối chỉ từ bảng AP.
- **S4 nghiệp vụ chưa được chấm:** GT WIDER đánh dấu mặt, không đánh dấu ai đã đưa mã/hồ sơ. Kết quả này so **S3 detection** ở hai loại ảnh; nó không đo chọn đúng người mục tiêu, giữ track, xác minh 1:1 trong cảnh đông hoặc hiệu quả cửa phòng thi. Kết quả LTFT box-only và XQLFW coverage vẫn là hai bằng chứng proxy khác đơn vị, không gộp vào AP.

**Kết luận T-012:** giữ YuNet và SCRFD là candidate đáng kiểm tiếp vì thứ hạng đổi theo loại ảnh và có đánh đổi chất lượng/chi phí; BlazeFace là mốc nhanh trong M1 tham chiếu nhưng cấu hình hiện tại có recall thấp trên WIDER nhiều mặt. Quyết định này chỉ là **candidate cho phép thử sau**, chưa chọn model/dataset/threshold triển khai. Câu hỏi kế tiếp từ dữ liệu hiện có là liệu thứ hạng S3 còn đổi khi **giữ cố định cỡ mặt GT** giữa hai nhóm; phép chấm chọn đúng người khai báo theo lượt vẫn cần nhãn claim–actor độc lập.
