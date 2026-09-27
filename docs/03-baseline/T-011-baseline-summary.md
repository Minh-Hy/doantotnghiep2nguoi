# T-011 — Mốc baseline nghiên cứu cửa phòng thi

**Ngày tổng kết:** 2026-09-27. **Phạm vi T-011 hoàn tất ở lượt này:** phép đo component detection E1, xác minh 1:1 E2 và timing detection tham chiếu M1, theo các protocol đã ghi trước từng run. Đây là **baseline nghiên cứu để T-012 phân tích lỗi**, chưa là pipeline triển khai hoặc bằng chứng giảm người ở cửa phòng.

## Bài toán → phép đo → bằng chứng

| Nhu cầu từ T-008/T-005 | Phép đo T-011 | Bằng chứng có thể dùng | Giới hạn của bằng chứng |
|---|---|---|---|
| Cần thấy mặt trong camera (S3) trước khi xác minh | E1 ba detector trên WIDER validation | [YuNet, SCRFD, BlazeFace](runs/T-011-E1-widerface-comparison.md): project AP lần lượt 0,648304 / 0,547370 / 0,136009, cùng 3.226 ảnh và 39.112 valid GT | Chỉ bbox detection, ảnh WIDER khác miền; không đo S4 chọn người |
| Cần xác minh 1:1 (S7–S8), đồng thời không che cặp chưa kết luận | E2 hai encoder trên cặp XQLFW | [Pair-fold gốc](runs/T-011-E2-xqlfw-mbf-vs-r50.md) có 4.215/6.000 cặp hợp lệ; [kiểm split danh tính](runs/T-011-E2-xqlfw-identity-disjoint.md) giữ 3.138/4.516 cặp đủ điều kiện split, R50 ít FA/FR hơn MBF trên cùng cặp | Không có target S4, domain cửa phòng hay identity pretrain audit; không chọn threshold triển khai |
| Cần biết đánh đổi chất lượng–chi phí | M1 CPU tham chiếu cùng job | [Thời gian ba detector](runs/T-011-M1-reference-detection.md) trên 60 frame: median YuNet 25,72 ms, BlazeFace 13,26 ms, SCRFD 83,24 ms | Chưa đo encoder, end-to-end attempt, RAM riêng, target hardware hoặc hàng chờ |

Các con số có **đơn vị và mẫu số khác nhau**, không gộp thành accuracy hoặc điểm tổng. Score threshold của E1 dùng để dựng đường precision–recall; threshold E2 được chọn trên dev của từng protocol để báo kết quả, không quyết định cho thí sinh vào phòng.

## E3 và phần cần thiết bị thật

[T-010 E3 fixture catalog](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E3-fixture-contract.md) đã định nghĩa nhóm ca để kiểm logic nhưng **chưa có app/policy profile được duyệt để chấm pass/fail**. Theo phạm vi Quốc An xác nhận ngày 2026-09-27, các chi tiết case, quyền override, hiệu lực roster/policy, correction và fallback của T-008 sẽ đi vào giai đoạn xây app; không dựng một implementation giả chỉ để đánh dấu E3 đạt. M1 trên thiết bị đích và phép đo queue/công sức cũng chưa có bối cảnh, thiết bị và baseline thực địa. Đây là việc cần làm **trước kết luận triển khai**, không phải kết quả đã có của T-011.

## Quyết định chuyển T-012

T-011 đã tạo đủ mốc **thăm dò có thể truy lại** để T-012 hỏi lỗi/uncertainty ở đúng stage: E1 miss theo cỡ/điều kiện, S4 mất coverage và nguy cơ chọn nhầm target, E2 khác biệt MBF/R50 và domain/identity gap, M1 chi phí tham chiếu. [T-012 PR #8](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/8) phải diễn giải các bằng chứng này, rồi đặt phép thử tiếp theo. T-011 **không quyết định model/dataset/threshold cuối**; những quyết định đó cần test phù hợp domain, metric/acceptance có nguồn và đánh đổi trên thiết bị đích.
