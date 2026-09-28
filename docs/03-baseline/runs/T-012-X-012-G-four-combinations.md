# T-012 X-012-G — bốn tổ hợp detector × encoder trên XQLFW

**Ngày:** 28/09/2026. **Mục tiêu hẹp:** điền đúng ô YuNet + R50 còn thiếu để trình bày lựa chọn B0 và các đối chứng có logic; sau phép này dừng mở rộng tổ hợp model ở bước chọn. [Protocol](../T-012-X-012-G-four-combination-protocol.md) commit `4d5d466` trước code/run; script/workflow commit `5e896e5`; [GitHub Actions run 36377073461](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36377073461) thành công. Thời gian job 38m18s **không** là latency model hoặc lượt check-in.

## Điều kiện và cổng tái lập

- Cùng 7.263 JPG XQLFW được 6.000 cặp tham chiếu, cùng pair-fold, weight SCRFD/MBF `buffalo_sc`, R50 `buffalo_l` và YuNet 2026may với hash đã pin ở E2/X-012-F. CPU Ubuntu runner, Python 3.12, NumPy 2.2.6, OpenCV package 5.0.0.93, InsightFace 0.7.3, ONNX Runtime 1.20.1, scikit-learn 1.7.1; OMP/OPENBLAS/MKL mỗi loại một thread. File ảnh, weight, embedding và JSON chi tiết chỉ ở `RUNNER_TEMP`, xóa cuối job.
- SCRFD: 6.064 ảnh đúng một mặt, 291 không mặt, 908 nhiều detection; YuNet: 5.943 / 2 / 1.318. Cổng valid pair SCRFD 4.215, YuNet 4.055, giao 3.666 cặp đều qua. Ba nhánh cũ tái lập đúng FA/FR trên tập valid riêng: SCRFD+MBF `133/125`, SCRFD+R50 `76/74`, YuNet+MBF `183/176`.
- Mỗi nhánh chọn threshold trên 9 fold dev, chấm fold còn lại; ảnh 0/nhiều detection không có score. Không dùng threshold số học làm policy thi. Chênh lệch error giữa hai **tập valid riêng** không phải hiệu ứng thuần của detector; vì vậy bảng giao cặp bên dưới là so sánh chính.

## Kết quả

| Tổ hợp | Cặp có score / 6.000 | Genuine / impostor có score | FA / impostor riêng | FR / genuine riêng |
|---|---:|---:|---:|---:|
| SCRFD + MBF **B0** | 4.215 (70,25%) | 2.046 / 2.169 | 133/2.169 (6,13%) | 125/2.046 (6,11%) |
| SCRFD + R50 | 4.215 (70,25%) | 2.046 / 2.169 | 76/2.169 (3,50%) | 74/2.046 (3,62%) |
| YuNet + MBF | 4.055 (67,58%) | 1.992 / 2.063 | 183/2.063 (8,87%) | 176/1.992 (8,84%) |
| **YuNet + R50 mới** | **4.055 (67,58%)** | **1.992 / 2.063** | **110/2.063 (5,33%)** | **107/1.992 (5,37%)** |

Ngoài tập có score: mỗi nhánh SCRFD có `954 genuine + 831 impostor = 1.785` cặp; mỗi nhánh YuNet có `1.008 + 937 = 1.945` cặp. Đây là **unresolved theo rule A0**, không cộng vào false reject. Encoder không thay coverage vì cùng output detector và rule một mặt.

**Giao đúng 3.666 cặp cả bốn nhánh có score**, gồm 1.779 genuine và 1.887 impostor; mỗi nhánh chọn threshold trên dev fold của chính giao này:

| Tổ hợp | FA / 1.887 impostor (FMR) | FR / 1.779 genuine (FNMR) |
|---|---:|---:|
| SCRFD + MBF | 114 (6,04%) | 108 (6,07%) |
| SCRFD + R50 | **61 (3,23%)** | **59 (3,32%)** |
| YuNet + MBF | 121 (6,41%) | 116 (6,52%) |
| YuNet + R50 | 67 (3,55%) | 63 (3,54%) |

Trên **cùng giao cặp**, R50 giảm FA/FR so MBF ở cả hai detector: SCRFD giảm `53/49`, YuNet giảm `54/53`. Giữ encoder cố định, SCRFD ít lỗi hơn YuNet: với MBF ít `7 FA/8 FR`, với R50 ít `6 FA/4 FR`. YuNet có ít ảnh zero detection hơn nhưng nhiều ảnh multi detection hơn trong XQLFW, khiến rule A0 chấm ít hơn 160 cặp. Không biết các box thêm là người nền hay false positive vì nguồn không có nhãn mặt mục tiêu theo lượt.

## Quyết định vừa đủ cho báo cáo và bước sau

- **Giữ SCRFD + MBF là B0**: cấu hình gọn, đã chạy pipeline thị giác từ JPG chưa căn chỉnh tới score, có mốc lỗi/coverage để đo cải thiện. Đây không phải nhánh có lỗi thấp nhất.
- **Giữ SCRFD + R50 làm đối chứng chất lượng**: ít FA/FR nhất trong bốn nhánh trên giao cặp, nhưng weight R50 lớn hơn và [M2](T-012-M2-reference-encoder.md) chậm hơn MBF trên CPU tham chiếu.
- **Giữ YuNet + MBF làm đối chứng detector nhẹ/nhanh** theo M1; **YuNet + R50 là ứng viên đánh đổi đáng nhắc đến**, vì R50 giảm lỗi của nhánh YuNet nhưng chi phí encoder tăng. Chưa xếp tốc độ pipeline bốn nhánh: M1/M2 khác run và job 38 phút chia sẻ tải giữa các nhánh.
- **Dừng chọn thêm model/dataset cho B0 ở T-012.** Tiếp theo phân tích điểm yếu B0, chọn một optimization có dữ liệu/nhãn và metric kiểm được, rồi so trước–sau trên cùng protocol. Không lấy điểm XQLFW đã dùng để thiết kế/so ứng viên làm chứng cứ độc lập về hiệu quả cửa phòng.

**Giới hạn:** XQLFW là ảnh web/face-centric, pair-fold có thể chia sẻ người/ảnh giữa dev và test; chưa kiểm overlap danh tính với dữ liệu pretrain, chưa có nhãn claim–actor S4, camera phòng thi, thiết bị đích hoặc policy. Phép thử không xác nhận cả quy trình check-in, quyền vào hay giảm nhân sự.
