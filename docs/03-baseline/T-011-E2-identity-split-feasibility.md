# T-011 — Kiểm khả năng tách danh tính khi chọn ngưỡng E2

**Ngày kiểm:** 2026-09-27. **Trạng thái:** chỉ kiểm cấu trúc [file pairs XQLFW của tác giả](https://martlgap.github.io/xqlfw/pages/download.html) (SHA-256 `636852F90B886F3F56C73B13C9775F7FFCD37662DBB189C694F6A0A605B63B84`); **chưa chạy detector/encoder** cho split mới. Đây là protocol **tự thiết kế để kiểm độ nhạy**, không phải 10-fold chính thức của XQLFW và không là main test miền cửa phòng.

## Câu hỏi

Run E2 hiện tại chọn threshold trên 9 pair-fold và chấm fold còn lại, nhưng cùng identity có thể xuất hiện cả hai phía. Nếu yêu cầu danh tính dùng để chọn threshold tách khỏi danh tính chấm, file pairs còn đủ genuine và impostor để làm phép kiểm mô tả không?

## Quy tắc đặt trước khi dùng score

Script [`t011_xqlfw_identity_split_audit.py`](../../scripts/t011_xqlfw_identity_split_audit.py) gán mỗi identity vào nhóm 0 hoặc 1 bằng parity byte đầu của SHA-256 trên chuỗi cố định `T-011-XQLFW-identity-disjoint-v1` + identity. Với mỗi nhóm làm test, nhóm kia là dev chọn threshold theo đúng quy tắc cân bằng FMR/FNMR của T-010. Cặp impostor nối hai nhóm bị **loại khỏi cả hai tập**; genuine cùng identity luôn ở một nhóm. Quy tắc chỉ dùng tên identity từ file pairs, không xem ảnh, detection, embedding hoặc score. Không chọn lại cách chia sau khi thấy kết quả model.

## Kết quả audit trước detection

File chính thức có 6.000 cặp, 3.743 identity. Với mỗi fold pair chính thức, có **635–659 identity** cũng xuất hiện ở chín fold còn lại; vì vậy pair-fold T-011 không phải phép thử tách identity khi chọn ngưỡng.

| Nhóm identity | Identity | Genuine pairs | Impostor pairs | Tổng cặp |
|---|---:|---:|---:|---:|
| 0 | 1.849 | 1.490 | 743 | 2.233 |
| 1 | 1.894 | 1.510 | 773 | 2.283 |

Hai nhóm không chung identity. Giữ **4.516/6.000 cặp (75,27%)** trước detection; loại 1.484 impostor nối hai nhóm, không loại genuine. Mỗi phía đều có cả hai nhãn, nên có thể thử chọn threshold trên nhóm kia và chấm nhóm này. Đây chỉ là **khả thi về cấu trúc pairs**: quy tắc một mặt có thể tiếp tục làm mất cặp và thay đổi phân bố, cần kiểm số hợp lệ trước khi tính metric.

## Phép thử tiếp theo và giới hạn

Nếu chạy, giữ đúng ảnh XQLFW/weight/hash, SCRFD-500MF + alignment của E2 và **cùng cặp hợp lệ cho MobileFaceNet/R50**. Trên mỗi test group, dùng chỉ cặp hợp lệ của group kia để chọn threshold; báo riêng số identity/cặp genuine/impostor hợp lệ và bị loại theo group, FMR/FNMR với tử số/mẫu số, và threshold của từng encoder. Không trộn kết quả custom split với bảng 10-fold chính thức hoặc đổi threshold theo test.

Tách identity giữa dev/test **không chứng minh model chưa thấy các identity khi huấn luyện**; overlap với dữ liệu train của weight chưa kiểm. XQLFW vẫn là ảnh web/crop khác cảnh cửa phòng, và việc loại gần nửa impostor làm tập chấm khác phân bố 6.000 cặp gốc. Nếu còn quá ít impostor hợp lệ để ước lượng FMR mục tiêu, chỉ báo kết quả mô tả/độ bất định; không chọn model hoặc threshold triển khai từ phép thử này.
