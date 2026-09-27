# T-012 — X-012-B: slice lỗi detection E1 trên WIDER FACE validation

**Ngày chạy:** 2026-09-27. **Trạng thái:** chẩn đoán hậu nghiệm hoàn tất; không thay đổi cấu hình E1 và không tạo quyết định detector cuối.

## Câu hỏi và điều kiện

[T-011 E1](T-011-E1-widerface-comparison.md) cho AP/recall tổng hợp của ba detector. Run này hỏi **GT nào còn bị bỏ sót trong từng cấu hình** theo kích thước mặt và mã annotation, để xác định phép thử dữ liệu/miền tiếp theo. [Thiết kế slice và deviation v1→v2](../T-012-error-analysis.md) được ghi trước khi xem slice SCRFD. Cùng WIDER validation 3.226 ảnh, 39.112 valid GT, 585 ignored GT, cùng weight/config E1 v1 và evaluator `IoU > 0,5`; xem [GitHub Actions run v2](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36298776083), commit `3baad2676eff54a864d8926a732412a72e0b2252`.

`size` = căn bậc hai diện tích bbox GT trên ảnh gốc; bốn nhóm `<16`, `16–<32`, `32–<96`, `≥96` pixel. Mỗi GT hợp lệ nằm đúng một nhóm size. Mã blur/illumination/occlusion/pose là **mã số nguyên gốc** của TXT; báo theo mã, chưa giải thích mức độ. `Matched GT`/`missed GT` dùng cùng ghép score giảm dần và mỗi GT tối đa một match; `max recall` của slice là matched/valid GT trong slice, không phải AP hoặc operating point triển khai.

## Cổng phát lại T-011

| Candidate | Rows | Box rỗng | TP/39.112 | AP chấm lại | AP T-011 | Box clip v2 so T-011 |
|---|---:|---:|---:|---:|---:|---:|
| YuNet | 1.195.480 | 182 | 28.922 | 0,6483041468333666 | 0,6483041468333666 | 56.316 so 56.316 |
| SCRFD-500MF | 4.858.820 | 595.274 | 24.804 | 0,5473701625535704 | 0,5473701658877327 | 534.289 so 534.287 |
| BlazeFace full-range | 477.622 | 3.191 | 7.063 | 0,1360090960544673 | 0,1360090960544673 | 14.206 so 14.206 |

Rows, box rỗng và TP khớp **chính xác** T-011 cho cả ba. YuNet/BlazeFace AP và clip khớp chính xác. SCRFD AP lệch `−0,0000000033341623` (khoảng 3,3×10⁻⁹), clip tăng 2 box trên 4.858.820 rows; chưa biết nguyên nhân, không gọi run này tái lập bit-for-bit. Chênh AP rất nhỏ về số, nhưng vẫn là deviation được giữ để audit. [Run v1](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36298113886) dừng SCRFD trước khi in slice do cổng clip exact; revision v2 báo clip riêng và chấm lại AP gốc. Không thay weight, score threshold, NMS, dataset hoặc quy tắc match.

## Slice theo kích thước GT

| Căn bậc hai diện tích bbox | Valid GT | YuNet matched / recall | SCRFD matched / recall | BlazeFace matched / recall |
|---|---:|---:|---:|---:|
| `<16` px | 17.911 | 9.595 / 53,57% | 5.326 / 29,74% | 0 / 0,00% |
| `16–<32` px | 10.268 | 8.988 / 87,53% | 8.792 / 85,63% | 130 / 1,27% |
| `32–<96` px | 8.606 | 8.100 / 94,12% | 8.376 / 97,33% | 4.961 / 57,65% |
| `≥96` px | 2.327 | 2.239 / 96,22% | 2.310 / 99,27% | 1.972 / 84,74% |

Tổng theo size khớp 39.112 valid GT và TP từng detector. Với YuNet, 8.316/10.190 missed GT nằm trong nhóm `<16` px; SCRFD 12.585/14.308; BlazeFace 17.911/32.049. Đây là **phân bố lỗi trên WIDER**, không phải tỷ lệ mặt nhỏ ở cửa phòng thi. SCRFD có recall nhóm `32–<96` và `≥96` cao hơn YuNet, nhưng AP tổng thấp hơn; AP còn phụ thuộc score ranking và FP, không suy nguyên nhân từ recall slice.

## Slice theo mã annotation

| Mã gốc / valid GT | YuNet matched / recall | SCRFD matched / recall | BlazeFace matched / recall |
|---|---:|---:|---:|
| blur `0` / 5.365 | 5.010 / 93,38% | 5.021 / 93,59% | 3.675 / 68,50% |
| blur `1` / 10.378 | 9.471 / 91,26% | 9.255 / 89,18% | 2.974 / 28,66% |
| blur `2` / 23.369 | 14.441 / 61,80% | 10.528 / 45,05% | 414 / 1,77% |
| occlusion `0` / 23.428 | 20.200 / 86,22% | 18.203 / 77,70% | 6.143 / 26,22% |
| occlusion `1` / 7.097 | 4.465 / 62,91% | 3.229 / 45,50% | 441 / 6,21% |
| occlusion `2` / 8.587 | 4.257 / 49,57% | 3.372 / 39,27% | 479 / 5,58% |

Các nhóm mã chồng lấn với size và nhau; **không diễn giải chúng là nguyên nhân độc lập**. Script còn xuất tổng hợp `illumination_code` và `pose_code` trong log cùng run để tái kiểm khi cần, không đặt ra claim vì chưa khảo sát phân bố giao nhau và ý nghĩa mã.

## Diễn giải và quyết định tiếp

**OBSERVED:** trên WIDER E1 v1, recall của nhóm bbox `<16` px thấp hơn nhiều so với nhóm lớn hơn ở cả ba candidate; nhóm mã blur/occlusion trong bảng cũng có recall khác nhau. **INFERENCE có giới hạn:** nếu camera cửa phòng tạo nhiều mặt nhỏ, đây có thể là rủi ro cho detection; hiện chưa có dữ liệu để biết tần suất hay tác động nghiệp vụ. **HYPOTHESIS cần kiểm:** khoảng cách/cỡ mặt/độ mờ của camera cửa phòng làm thay đổi coverage S3 và S4. Phép thử sau phải ghi nhận phân bố kích cỡ/điều kiện ảnh thực tế hoặc dữ liệu gần miền, có nhãn target nếu muốn đo S4, rồi chọn acceptance theo rủi ro T-008 trước locked test.

Không chỉnh resize/threshold trên WIDER validation đã xem rồi trình bày điểm mới là test độc lập. Kết quả này bổ sung điều kiện dữ liệu cần kiểm cho S3; nó không quyết định có cần tự động xử lý ngoại lệ nhiều mặt X-012-A hay không. [T-012 main analysis](../T-012-error-analysis.md) giữ ranh giới giữa component, nghiệp vụ và final technical decision.
