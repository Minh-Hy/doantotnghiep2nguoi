# T-012 — Proxy LTFT theo số mặt ở frame đầu

**Ngày:** 27/09/2026. **Câu hỏi:** trên cùng cửa sổ–ID được cấp sẵn box mục tiêu, P1 liên kết box qua từng frame so với P0 so box cuối với box đầu như thế nào khi frame đầu có 1, 2 hoặc ≥3 mặt được gán nhãn?

## Nguồn và phép đo

- [Kế hoạch phân nhóm](../T-012-S4-one-vs-multi-comparison-plan.md) commit `7547a9c` **trước khi xem bảng dưới**; [scorer và test](../../../scripts/t012_ltft_box_proxy.py) commit `d30fdbc`. Đây là phân tích bổ sung sau khi đã xem [kết quả P0/P1 tổng](T-012-S4-ltft-box-proxy.md), không phải test độc lập.
- Hai file `choke1.txt` và `choke2.txt` từ [LTFT commit của tác giả](https://github.com/hertasecurity/LTFT/tree/2c481e807be5cae53c5a056f39e1f1107628f1f6/annotations_IJCB) qua kiểm SHA-256 và cấu trúc theo [protocol gốc](../T-012-S4-box-only-proxy-protocol.md). Chỉ dùng box `face=1`, cửa sổ 16 frame không chồng lặp; mỗi target ID có box ở đầu tạo một trường hợp. Cùng box target **oracle** và cùng rule P0/P1 cho cả ba nhóm. Python 3.13.5 cục bộ; không seed do thuật toán tất định; không dùng ảnh/video hoặc thiết bị đích.
- Outcome: `correct-track / wrong-track / unresolved` ở frame cuối. Nhóm theo **số box hợp lệ ở frame đầu**, không theo dự đoán của P0/P1. File nhãn và JSON mức run ở thư mục tạm, không đưa vào Git.

## Số đếm

| File và số mặt đầu | Cửa sổ–ID | P0 đúng / sai / chưa kết luận | P1 đúng / sai / chưa kết luận |
|---|---:|---:|---:|
| Choke1 — 1 | 13 | 3 / 1 / 9 | 10 / 0 / 3 |
| Choke1 — 2 | 28 | 8 / 6 / 14 | 23 / 2 / 3 |
| Choke1 — ≥3 | 454 | 151 / 61 / 242 | 351 / 15 / 88 |
| Choke2 — 1 | 8 | 3 / 0 / 5 | 3 / 0 / 5 |
| Choke2 — 2 | 18 | 10 / 1 / 7 | 12 / 1 / 5 |
| Choke2 — ≥3 | 503 | 271 / 74 / 158 | 359 / 20 / 124 |
| **Gộp — 1** | **21** | **6 / 1 / 14** | **13 / 0 / 8** |
| **Gộp — 2** | **46** | **18 / 7 / 21** | **35 / 3 / 8** |
| **Gộp — ≥3** | **957** | **422 / 135 / 400** | **710 / 35 / 212** |

**Đối chiếu:** ba nhóm gộp `21 + 46 + 957 = 1.024` trường hợp. P0 cộng thành `446 / 143 / 435`, P1 `758 / 38 / 228`, khớp [run gốc](T-012-S4-ltft-box-proxy.md). Riêng nhóm ≥3 chiếm **957/1.024** trường hợp; P1 đúng **710/957** so P0 **422/957**, sai track **35/957** so **135/957**, chưa kết luận **212/957** so **400/957**. Nhóm 2 mặt có P1 đúng **35/46** so P0 **18/46**. Nhóm 1 mặt chỉ **21** trường hợp nên chỉ nêu số đếm, không xếp hạng bằng tỷ lệ.

## Diễn giải và quyết định

**Observed:** trong proxy hình học này, P1 cải thiện cả ba outcome so P0 ở nhóm ≥3 mặt, là nhóm chi phối mẫu LTFT. Kết quả tổng P0/P1 không chỉ do nhóm ít mặt tạo ra. Nhóm đúng 2 mặt nhỏ hơn nhiều (46 trường hợp) nên dùng để nhận diện khuynh hướng, không ngoại suy tỷ lệ. Không so chênh lệch *giữa* các nhóm như tác động của số người: cỡ mặt, che khuất, chuyển động, camera và thời điểm target biến mất chưa được kiểm soát.

**Giới hạn quyết định:** target box ở đầu do nhãn cấp, không phải người vừa đưa mã được hệ thống chọn. P0/P1 chỉ nối các bbox đã annotation; không có ảnh khớp frame để chạy detector, không đo xác minh 1:1, không có lượt check-in hay thiết bị đích. Cùng ID có thể xuất hiện ở nhiều cửa sổ và nguồn không có split độc lập theo người; không dùng các tỷ lệ như xác suất lỗi ở cửa phòng. Không chọn P1 làm rule cuối từ bảng này.

**Bước suy ra:** T-012 đã có bằng chứng thành phần rằng liên kết theo thời gian đáng đưa vào danh sách ứng viên S4 khi cảnh nhiều mặt. Uncertainty còn lại là **xác định box khởi đầu của người vừa khai báo hồ sơ** và kiểm pipeline có ảnh/transaction; nhãn LTFT hiện tại không trả lời được. Giữ `unresolved` khi thiếu liên kết đáng tin. Không chạy lại so 1 mặt/nhiều mặt LTFT như một benchmark cân bằng vì chỉ có 21 trường hợp 1 mặt.
