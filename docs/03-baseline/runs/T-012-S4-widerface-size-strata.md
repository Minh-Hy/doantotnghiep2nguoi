# T-012 — WIDER: một/nhiều mặt trong cùng khoảng cỡ GT

**Run:** [GitHub Actions 36328357593](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36328357593), ba job thành công ngày 2026-09-27. **Định nghĩa và mã trước run:** commit `fbc968a`, [kế hoạch](../T-012-S4-one-vs-multi-comparison-plan.md). Đây là phép phân tích tiếp sau [bảng một/nhiều mặt](T-012-S4-widerface-one-multi.md), không phải một protocol đã đặt trước T-011 E1.

## Câu hỏi và phép đo

Bảng trước cho YuNet dẫn khi gộp mọi mặt trong ảnh nhiều người, còn SCRFD dẫn ở ảnh đúng một mặt. Nhưng 47,13% GT trong nhóm ảnh nhiều mặt nhỏ hơn 16 px, so với 0,45% ở nhóm một mặt. Vì vậy, phép này hỏi: **trong cùng khoảng cỡ mặt GT, thứ hạng recall của ba detector còn như bảng gộp không?**

Giữ nguyên 3.226 ảnh WIDER FACE validation, 39.112 valid GT, archive/hash, weight, wrapper, quy trình tạo prediction và evaluator T-011. Trong mỗi job, cùng prediction tạm được dùng cho các lát cắt và nhóm ảnh rồi xóa. Nhóm ảnh xác định bằng **số valid GT trong ảnh** (`one_valid` = 1; `multi_valid` ≥ 2), không dùng số mặt detector trả về. Cỡ mặt là căn bậc hai diện tích bbox GT trên ảnh gốc: `<16`, `16–<32`, `32–<96`, `≥96` px. Mỗi ô báo **matched GT / valid GT** và recall cực đại theo matching IoU `>0,5` của E1. Không tính AP theo ô vì lọc GT theo cỡ có thể thay đổi cách tính prediction trùng hoặc ignored. Không chỉnh threshold hay cấu hình theo kết quả này.

## Kết quả

| Nhóm ảnh | Cỡ GT (px) | Valid GT | YuNet matched/GT (recall) | SCRFD-500MF matched/GT (recall) | BlazeFace matched/GT (recall) |
|---|---:|---:|---:|---:|---:|
| 1 mặt | <16 | 5 | 5/5 (100,00%) | 3/5 (60,00%) | 0/5 (0,00%) |
| 1 mặt | 16–<32 | 26 | 23/26 (88,46%) | 24/26 (92,31%) | 1/26 (3,85%) |
| 1 mặt | 32–<96 | 248 | 222/248 (89,52%) | **243/248 (97,98%)** | 161/248 (64,92%) |
| 1 mặt | ≥96 | 840 | 796/840 (94,76%) | **834/840 (99,29%)** | 750/840 (89,29%) |
| ≥2 mặt | <16 | 17.906 | **9.590/17.906 (53,56%)** | 5.323/17.906 (29,73%) | 0/17.906 (0,00%) |
| ≥2 mặt | 16–<32 | 10.242 | **8.965/10.242 (87,53%)** | 8.768/10.242 (85,61%) | 129/10.242 (1,26%) |
| ≥2 mặt | 32–<96 | 8.358 | 7.878/8.358 (94,26%) | **8.133/8.358 (97,31%)** | 4.800/8.358 (57,43%) |
| ≥2 mặt | ≥96 | 1.487 | 1.443/1.487 (97,04%) | **1.476/1.487 (99,26%)** | 1.222/1.487 (82,18%) |

**Đối chiếu:** bốn ô nhóm một mặt cộng thành 1.119 GT; bốn ô nhóm nhiều mặt cộng thành 37.993 GT. Matched GT cộng lần lượt YuNet **28.922** = 1.046 + 27.876, SCRFD **24.804** = 1.104 + 23.700, BlazeFace **7.063** = 912 + 6.151; khớp E1 và [run nhóm ảnh trước](T-012-S4-widerface-one-multi.md). Ba job cũng tái lập project AP tổng làm tròn sáu chữ số: 0,648304 / 0,547370 / 0,136009. Clip box ở run này khớp số T-011 của cả ba candidate; run nhóm ảnh trước từng có SCRFD lệch 2 box clip, nên vẫn giữ ghi chú độ nhạy tái lập ở báo cáo đó.

## Diễn giải và ranh giới quyết định

- **Quan sát:** trong cả hai nhóm ảnh, SCRFD có recall cao hơn YuNet ở hai khoảng `32–<96` và `≥96` px. YuNet hơn SCRFD rõ ở nhóm `<16` px nhiều mặt và nhỉnh hơn ở `16–<32` px nhiều mặt. Vì nhóm nhiều mặt chứa rất nhiều GT nhỏ, recall gộp **73,37% YuNet so với 62,38% SCRFD** che khuất việc SCRFD dẫn trong hai khoảng cỡ lớn hơn. Không dùng recall gộp để tuyên bố một candidate tốt hơn cho mọi cỡ mặt.
- **Mẫu số yếu:** nhóm một mặt chỉ có 5 GT `<16` và 26 GT `16–<32`; các tỷ lệ ở hai ô đó chỉ là mô tả, không là thứ hạng ổn định. Các khoảng cỡ cũng không giữ cố định chính xác kích cỡ, che khuất, pose, nền hay mật độ; bảng không chứng minh tác động nhân quả của nhiều người lên detection.
- **Quyết định ở mức nghiên cứu:** tiếp tục giữ YuNet và SCRFD để nghiên cứu theo phân bố cỡ mặt dự kiến và chi phí vận hành; BlazeFace cấu hình đã pin là đối chứng nhưng recall thấp hơn trong các ô đủ mẫu trên WIDER. Chưa chọn detector/model cuối, threshold hoặc dataset triển khai.
- **Giới hạn nghiệp vụ:** đây là **S3 phát hiện mặt** trên WIDER. Dataset không có nhãn ai đưa mã/hồ sơ ở lượt check-in, nên bảng không đo S4 chọn đúng người, xác minh 1:1 đầu-cuối, latency thiết bị cửa phòng hay hiệu quả giảm nhân sự. Câu hỏi X-012-A vẫn cần nhãn claim–actor độc lập nếu sau này được chấm; không suy nhãn đó từ bbox WIDER.

Prediction theo ảnh, weight và archive chỉ nằm tạm trên runner; không upload artifact hoặc đưa ảnh/identity vào Git. Mỗi job in crosstab tổng hợp và xóa file tạm sau khi chấm.
