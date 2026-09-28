# T-012 X-012-H — Kết quả gate IoU cho proxy liên kết mặt S4

**Ngày chạy:** 28/09/2026. **Phạm vi:** chỉ bbox/ID annotation LTFT với box mục tiêu ban đầu do nhãn cấp; không có ảnh/video, SCRFD/MBF, claim hồ sơ hoặc lượt check-in. [Protocol](../T-012-X-012-H-s4-overlap-gate-protocol.md) commit `7085022` được push **trước khi chạy P2**; [script và test](../../../scripts/t012_ltft_overlap_gate.py) commit `2589cf7`. P2 chỉ thêm gate `IoU >= 0,3` vào P1 sequential; giá trị 0,3 lấy từ [mã SORT tác giả](https://github.com/abewley/sort/blob/master/sort.py) làm điểm tham chiếu trước kết quả, không tune trên LTFT và không gọi P2 là SORT.

## Nguồn và kiểm tái lập

- Hai file nhãn từ [LTFT tác giả, commit `2c481e8`](https://github.com/hertasecurity/LTFT/tree/2c481e807be5cae53c5a056f39e1f1107628f1f6/annotations_IJCB), tải tạm và qua SHA-256: `choke1.txt` = `e79b7eccd835a449505d6998112b5104a480abec0b5f6cd0d69162b846222274`; `choke2.txt` = `0b91483182869ba513164c23b587f3078fa7810966aec1858c61fc446b40d3d2`. Chỉ box `face=1`; cùng cửa sổ 16 frame không chồng lặp và 1.024 trường hợp như [P1 gốc](T-012-S4-ltft-box-proxy.md).
- Chạy cục bộ Windows, Python 3.12.2; không đo latency và không có seed vì parser, cửa sổ và rule đều tất định. Lệnh: `python scripts/t012_ltft_overlap_gate.py --choke1 <đường-dẫn-choke1.txt> --choke2 <đường-dẫn-choke2.txt> --output <summary.json>`. Test `python -m unittest tests.test_t012_ltft_box_proxy tests.test_t012_ltft_overlap_gate` đạt 3/3. Script chặn diễn giải nếu số P1 không tái lập. Kết quả P1 **khớp chính xác**: Choke1 `384/17/94`, Choke2 `374/21/134` (đúng/sai/chưa kết luận), tổng `758/38/228`; `ever-wrong` P1 tổng **41** khớp [D1](T-012-S4-ltft-path-diagnostic.md). Summary JSON và hai file nhãn chỉ ở thư mục tạm, không đưa lên Git.

## Kết quả trên cùng mẫu số

| Nguồn | Số cửa sổ–ID | P1 đúng / sai / chưa kết luận | P2 đúng / sai / chưa kết luận | P1 / P2 từng sai ở bất kỳ frame nào |
|---|---:|---:|---:|---:|
| Choke1 | 495 | 384 / 17 / 94 | **382 / 0 / 113** | 18 / 0 |
| Choke2 | 529 | 374 / 21 / 134 | **373 / 3 / 153** | 23 / 3 |
| **Tổng** | **1.024** | **758 / 38 / 228** | **755 / 3 / 266** | **41 / 3** |

Theo đơn vị proxy này, gate P2 đổi **35 sai → chưa kết luận**, đồng thời đổi **3 đúng → chưa kết luận**; không có cặp outcome nào khác đổi. Sai endpoint giảm `38/1.024 → 3/1.024` (3,71% → 0,29%), đúng giảm `758/1.024 → 755/1.024` (74,02% → 73,73%), chưa kết luận tăng `228/1.024 → 266/1.024` (22,27% → 25,98%). Đây là **đánh đổi giảm chọn sai bằng từ chối liên kết yếu**, không là tăng tỷ lệ nhận diện đúng.

| Nhóm audit | Mẫu số | P1 đúng / sai / chưa kết luận | P2 đúng / sai / chưa kết luận |
|---|---:|---:|---:|
| Target còn được annotation ghi ở endpoint | 806 | 758 / 11 / 37 | 755 / 0 / 51 |
| Target không được annotation ghi ở endpoint | 218 | 0 / 27 / 191 | 0 / 3 / 215 |
| Có ≥3 box ở frame đầu | 957 | 710 / 35 / 212 | 707 / 2 / 248 |

Các nhóm target ở endpoint là **kiểm hậu nghiệm bằng nhãn**, không là tín hiệu P2 được phép đọc. `Không có record` không chứng minh người thật đã rời camera. Nhóm ≥3 chiếm phần lớn mẫu; nhóm một mặt chỉ có 21 trường hợp và không thích hợp để tuyên bố hiệu năng một-vs-nhiều cân bằng.

## Diễn giải và quyết định nghiên cứu

**Observed:** gate IoU 0,3 giữ gần như toàn bộ correct-track P1 trong proxy (`755/758`) và loại phần lớn wrong-track (`35/38`), kể cả `ever-wrong` từ 41 còn 3. Sự đánh đổi là 38 trường hợp thêm vào `unresolved`. Điều này **ủng hộ giữ ý tưởng gating/abstention làm candidate S4 tiếp theo** hơn là nối mọi overlap dương khi có nhiều box.

**Không được suy:** P2 chưa chứng minh chọn đúng người đã đưa mã, giảm false accept danh tính, giảm hàng chờ hoặc cải thiện B0 trên XQLFW/camera cửa phòng. Box đầu và box mỗi frame là annotation; không có detector thực và video LTFT hiện chưa ghép frame–nhãn đáng tin. Cả hai file đã được dùng phân tích P1/D1/D2 trước đó, cùng người có thể lặp giữa các cửa sổ; đây là thăm dò trên nguồn đã xem, không phải locked independent test. Giá trị `0,3` là tham số nghiên cứu, không là policy ứng dụng.

**Bước tiếp có căn cứ:** giữ B0 thị giác không đổi và giữ P2 làm **ứng viên component S4**. Để gọi là optimization của pipeline B0, phải có frame/video công khai khớp nhãn, đầu vào chọn người ban đầu độc lập và phép so B0/proposed trên cùng transaction/điều kiện; hiện chưa có. Nếu chỉ có dữ liệu box-only, kết quả đóng góp giới hạn ở association sau khởi tạo oracle. Không chọn model, threshold triển khai hay tuyên bố hiệu quả cửa phòng từ run này.
