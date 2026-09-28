# T-012 — Chọn B0 để chuyển từ khảo sát sang pipeline gốc

**Ngày:** 28/09/2026. **Loại quyết định:** cấu hình baseline nghiên cứu để tiếp tục làm đồ án; không phải lựa chọn model/ngưỡng cuối cho phòng thi. Quốc An định hướng thứ tự công việc: chọn model và dataset vừa đủ → chạy pipeline gốc → phân tích ưu/nhược → thêm một optimization có mục tiêu → so sánh công bằng và nêu đóng góp. Vì vậy dừng việc mở rộng ma trận tổ hợp model ở bước này.

## B0 được chọn và vì sao

| Vai trò | Chọn cho B0 | Lý do đủ để bắt đầu | Phạm vi chưa chứng minh |
|---|---|---|---|
| Phát hiện và landmark S3 | **SCRFD-500MF** trong `buffalo_sc` | Weight/hash đã kiểm ở T-009; đã chạy trên WIDER và trong pipeline XQLFW. [X-012-F](runs/T-012-X-012-F-detector-encoder-interface.md) tái lập E2, chấm được 4.215/6.000 cặp với MBF, hơn YuNet 160 cặp trong rule một mặt. | YuNet nhanh hơn trong M1 và tốt hơn với mặt rất nhỏ trên nhóm WIDER nhiều mặt. Chưa biết detector nào tốt hơn ở camera cửa phòng. |
| Chọn người S4 | **A0 bảo thủ:** chỉ tiếp tục khi ảnh có đúng một mặt hợp lệ; 0 hoặc nhiều mặt → `unresolved`/retry/manual | Không gán nhầm một mặt bất kỳ cho hồ sơ đã khai. Có outcome rõ để đo điểm yếu trước khi cải thiện. | Không giải quyết chọn đúng người đã đưa mã khi camera thấy nhiều người; XQLFW không có nhãn claim–actor. |
| Căn chỉnh S6 | 5 landmark của detector → `norm_crop` 112×112 | Đúng giao diện weight encoder hiện chạy được, không thêm model khi chưa có lỗi chứng minh cần. | Chưa tách lỗi bbox khỏi lỗi landmark. |
| Embedding và xác minh S7–S8 | **MobileFaceNet (MBF)** trong cùng pack `buffalo_sc`, L2 + cosine; ngưỡng chỉ chọn trên dev fold của thí nghiệm | Pipeline và nguồn đã kiểm, ONNX 13.616.099 byte; [M2](runs/T-012-M2-reference-encoder.md) median `8,35 ms`/crop trên CPU tham chiếu, giúp có mốc gọn để tối ưu. | [R50](runs/T-011-E2-xqlfw-mbf-vs-r50.md) ít lỗi hơn trên cặp XQLFW hợp lệ nhưng lớn/chậm hơn; MBF chưa đạt một tiêu chí nghiệp vụ được chốt. Không dùng ngưỡng pair-fold làm policy cửa phòng. |
| Phòng/ca/trùng lượt | Tra cứu và business rule theo T-008; không dùng model | Các điều kiện này là dữ liệu/quyền quyết định, không phải phân loại ảnh. | App/E3 chưa triển khai, nên B0 hiện là **pipeline thị giác**, chưa là giao dịch check-in đầu-cuối. |

**Dữ liệu được chọn theo vai trò, không gộp thành một dataset hệ thống:** [WIDER FACE validation](runs/T-011-E1-widerface-comparison.md) đo S3 phát hiện mặt; [XQLFW 6.000 cặp](runs/T-011-E2-xqlfw-mbf.md) là tập chính đang dùng để đo **B0 thị giác từ JPG XQLFW chưa căn chỉnh tới score** và ba outcome trên cặp; [LTFT box-only](runs/T-012-S4-ltft-box-proxy.md) chỉ là proxy phụ để hiểu giữ track khi đã được cấp box mục tiêu ban đầu. JPG XQLFW vốn là ảnh web/face-centric, không phải khung hình camera cửa phòng. Không train/fine-tune B0; weight pretrained và nguồn/hash/quyền dùng xem [T-009 PR #5](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/5) và [external assets](../00-project/external-assets.md). Không lấy WIDER, XQLFW hay LTFT làm bằng chứng về cả lượt thí sinh tại cửa phòng.

## Pipeline gốc đã chạy — mốc để so optimization

`Ảnh JPG XQLFW probe + reference theo cặp → SCRFD phát hiện mặt → A0 kiểm đúng một mặt ở mỗi ảnh → căn chỉnh 5 điểm → MBF embedding → L2/cosine → ngưỡng chọn trên dev fold → match / non-match / unresolved`.

[Runner E2 gốc](../../scripts/t011_xqlfw_baseline.py) và [báo cáo B0](runs/T-011-E2-xqlfw-mbf.md) đã chạy chuỗi này trên XQLFW, không chỉ chấm crop đưa thẳng vào encoder. Trong 7.263 ảnh được tham chiếu: 6.064 ảnh một mặt, 291 ảnh không mặt, 908 ảnh nhiều detection. Trong 6.000 cặp: **4.215 có score**, **1.785 unresolved** theo A0; trên cặp có score, **FA 133/2.169 impostor (FMR 6,13%)**, **FR 125/2.046 genuine (FNMR 6,11%)** với pair-fold dev/test. Mốc thời gian decode + detect + embed của run gốc là median/p95 `78/125 ms/ảnh`, nhưng máy có tải khác lúc chạy; chỉ giữ làm tham khảo, không so tốc độ optimization với số này hoặc gọi là latency lượt.

**Ưu điểm B0:** chạy lại được bằng file/hash đã pin; các stage và outcome rõ; không tự xác nhận khi mơ hồ; có mốc lỗi và coverage để so sau này. **Nhược điểm thấy ngay:** 1.785/6.000 cặp không có score theo A0, lỗi FA/FR vẫn tồn tại trên 4.215 cặp còn lại; không có bằng chứng chọn đúng người trong cảnh nhiều mặt, thử app, hay dữ liệu camera cửa phòng. Nhiều detection trên ảnh XQLFW không chứng minh có nhiều người trong một lượt check-in.

## Chuyển sang phần đóng góp

1. **Cố định B0 trên giấy và trong mã/run hiện có.** Không mở thêm tổ hợp YuNet × R50 chỉ để kéo dài chọn model. YuNet và R50 được giữ làm đối chứng thành phần khi một thay đổi cụ thể cần so.
2. **Phân tích lỗi B0 theo đúng mẫu số:** zero/multi detection gây unresolved; FA/FR trên cặp hợp lệ; ảnh/cỡ/chất lượng và điều kiện làm lỗi. [T-012 error analysis](T-012-error-analysis.md) đã có phần đầu; chỉ bổ sung phép đo nếu nó xác định một bottleneck có thể can thiệp.
3. **Chọn một optimization sau khi nêu rõ giả thuyết và nhãn kiểm được.** S4 nhiều mặt là nhu cầu quan trọng, nhưng không dùng proxy LTFT có box oracle để tuyên bố chọn đúng người khai báo. Nếu dữ liệu công khai hiện có chưa chấm được S4 theo lượt, ưu tiên một cải thiện khác có thể kiểm trên B0 và ghi S4 là giới hạn.
4. **Chạy B0 và bản cải thiện trên cùng dữ liệu/split/điều kiện.** Báo coverage/unresolved trên toàn bộ mẫu, FA/FR và mẫu số trên phần được chấm, thời gian/tài nguyên trên cùng runner. So với B0 **và** đối chứng mạnh phù hợp khi cần; nêu rõ thay đổi nào tạo cải thiện, đổi lấy chi phí gì, trường hợp nào vẫn thất bại.

Đây là điểm dừng của bước chọn model/dataset. Quyết định sau baseline là **optimization nào có thể kiểm chứng thành đóng góp**, không phải tìm thêm model có điểm công bố cao nhất.
