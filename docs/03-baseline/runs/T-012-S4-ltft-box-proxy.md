# T-012 — Kết quả thăm dò proxy hình học chỉ dùng bbox LTFT

**Ngày:** 27/09/2026. **Câu hỏi:** khi được cấp box mục tiêu ở frame đầu cùng các box mặt mỗi frame, liên kết qua từng frame có giữ đúng ID ở frame cuối tốt hơn so với chỉ so với vị trí ban đầu không? **Phạm vi:** annotation-only, không có ảnh/video, không đo chọn người khai báo hồ sơ hoặc check-in.

## Protocol, nguồn và cách chạy

- [Protocol P0/P1](../T-012-S4-box-only-proxy-protocol.md) đã được commit **`0540452` trước khi chạy**; evaluator [script T-012](../../../scripts/t012_ltft_box_proxy.py) được commit `869dda7` trước khi đọc kết quả. Không tune tham số theo điểm.
- Hai file công khai [LTFT IJCB annotations](https://github.com/hertasecurity/LTFT/tree/master/annotations_IJCB) ở commit tác giả `2c481e807be5cae53c5a056f39e1f1107628f1f6`. SHA-256 `choke1.txt`: `e79b7eccd835a449505d6998112b5104a480abec0b5f6cd0d69162b846222274`; `choke2.txt`: `0b91483182869ba513164c23b587f3078fa7810966aec1858c61fc446b40d3d2`. Script dừng nếu hash/cấu trúc/ID/box không qua gate; cả hai file đã qua.
- Đơn vị: cửa sổ 16 frame **không chồng lặp** bắt đầu ở 0,16,32,…; mỗi ID có box `face=1` ở frame đầu là một trường hợp. P0 chọn box ở frame cuối có IoU duy nhất >0 với box ban đầu. P1 chọn IoU duy nhất >0 từng frame với box vừa chọn, dừng nếu không chọn được. Cả hai nhận **cùng box khởi đầu từ nhãn**; ID chỉ dùng chấm. Không có seed vì phép chọn mẫu và rule tất định.
- Có 157 cửa sổ đầy đủ ở Choke1 và 133 ở Choke2; 14 và 11 frame cuối không đủ 16 frame nên nằm ngoài mẫu số. Một cửa sổ có thể sinh nhiều trường hợp nếu nhiều ID hiện ở frame đầu.
- Chạy Python 3.13.5 cục bộ trên hai file `.txt` tạm; không đo latency/thiết bị đích. Tổng hợp JSON chỉ ở thư mục tạm trong lúc đối chiếu; repo lưu số đếm, hash, protocol và mã, **không lưu file nhãn, bbox theo người, ảnh hay embedding**.

## Số đếm chính

| File | Cửa sổ–ID | P0 đúng | P0 sai | P0 unresolved | P1 đúng | P1 sai | P1 unresolved |
|---|---:|---:|---:|---:|---:|---:|---:|
| Choke1 | 495 | 162 | 68 | 265 | 384 | 17 | 94 |
| Choke2 | 529 | 284 | 75 | 170 | 374 | 21 | 134 |
| **Tổng** | **1.024** | **446** | **143** | **435** | **758** | **38** | **228** |

Mẫu số của mỗi candidate đều là **1.024 cửa sổ–ID**: P0 `446 + 143 + 435`, P1 `758 + 38 + 228`. Theo proxy này, tỷ lệ đúng lần lượt **43,55% và 74,02%**; sai track **13,96% và 3,71%**; unresolved **42,48% và 22,27%**. Đây là số mô tả trên chính hai file đã kiểm, **không phải estimate độc lập cho camera cửa phòng**.

| Nhóm endpoint | Mẫu số | P0 đúng / sai / unresolved | P1 đúng / sai / unresolved |
|---|---:|---:|---:|
| ID target còn box ở frame cuối | 806 | 446 / 90 / 270 | 758 / 11 / 37 |
| ID target **không được annotation ghi nhận** ở frame cuối | 218 | 0 / 53 / 165 | 0 / 27 / 191 |
| Có ≥2 box ở frame đầu | 1.003 | 440 / 142 / 421 | 745 / 38 / 220 |

Nhóm 218 **không** được gọi là người vắng mặt: bộ nhãn bắt đầu bằng face detector, có thể thiếu mặt do che khuất/chất lượng hoặc do người đã ra khỏi khung. Việc P1 vẫn chọn sai ID ở 27 cửa sổ nhóm này cho thấy một rule nối box không được tự động biến thành quyền xác minh/cho vào.

## Diễn giải và giới hạn quyết định

**Observed:** trên box annotation có sẵn và khởi tạo bằng box target do nhãn cấp, `P1-sequential` cho nhiều `correct-track` hơn và ít `wrong-track`/`unresolved` hơn `P0-static` ở cả Choke1 lẫn Choke2. Đây là bằng chứng rằng chuyển động giữa frame là một biến đáng nghiên cứu tiếp trong proxy hình học; **không chốt P1 làm rule triển khai**.

**Không được suy ra:** (1) app biết box nào là người vừa chọn hồ sơ — ở phép thử, box đó là **oracle**; (2) detector trên video thật cho box đầy đủ/đúng; (3) khả năng face verification, chống sai danh tính, check-in hoặc attendance; (4) throughput/latency thiết bị; (5) an toàn khi target không được annotation ghi nhận; (6) hiệu quả trên kỳ thi/phòng/camera đích. [Audit video S5](../T-012-S4-ltft-label-audit.md) đã phát hiện archive Zenodo không khớp frame LTFT, nên không ghép ảnh hoặc báo kết quả video.

**Thiết kế chỉ là exploratory:** không có dev/test hay split danh tính; cửa sổ không chồng lặp nhưng cùng ID có thể xuất hiện nhiều lần, và người ở Choke1/Choke2 có thể trùng. Không tính khoảng tin cậy kiểu các cửa sổ độc lập, không tối ưu IoU/timeout hoặc chọn winner cuối từ bảng này. Repository LTFT công khai annotation nhưng chưa thấy license rõ cho tái phân phối; chỉ dẫn nguồn và giữ số tổng hợp trong báo cáo.

**Quyết định T-012:** giữ câu hỏi S4 về chọn đúng người mục tiêu ở trạng thái chưa được giải quyết. Nếu nghiên cứu tiếp bằng dữ liệu có sẵn, phải tách (a) chọn box khởi đầu từ hành động/claim và (b) giữ track sau khi đã chọn; proxy hiện tại chỉ cung cấp evidence cho (b). X-012-A nghiệp vụ vẫn `not runnable` khi không có claim–actor và nhãn transaction độc lập.
