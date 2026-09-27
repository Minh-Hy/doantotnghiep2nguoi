# Decision Logic — Phase 03 Baseline

## Chuỗi dẫn tới phép đo

1. [D-001](../00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md) và [T-008 PR #3](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3) xác định nghiệp vụ cửa phòng, capability, quyền và rủi ro. T-008 được dùng làm mốc generic tạm cho nghiên cứu; policy kỳ thi chưa được gán.
2. [T-009 PR #5](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/5) kiểm ứng viên dữ liệu/weight theo đúng stage và giữ/hoãn có điều kiện. Quyết định survey chỉ chọn **candidate đáng thử**.
3. [T-010 PR #6](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6) suy uncertainty thành E1 detection, E2 verification, E3 fixture nghiệp vụ và M1 vận hành; đặt dữ liệu, biến, metric, quy tắc chọn threshold và giới hạn trước khi xem điểm. Bản logic gốc của T-010 ở PR #6 là nguồn; file này được mang sang nhánh T-012 để tiếp tục cùng chuỗi reasoning khi các PR chưa hợp nhất.
4. [T-011 PR #7](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/7) tạo evidence E1 trên WIDER, E2 pair-fold và split tách danh tính custom trên XQLFW, cùng M1 detection timing trên một CPU runner. E3 chưa có profile/implementation; M1 chưa có phép đo cùng thiết bị đích. Mỗi run chỉ trả lời phạm vi của nó.
5. [T-012](T-012-error-analysis.md) phân loại observed error, inference, hypothesis. [Phân tích ba nhánh E2](runs/T-012-E2-three-outcome-analysis.md) cho thấy 1.785 cặp chưa chấm cần ở `unresolved`; đổi encoder không tác động coverage của rule một mặt. Từ đó [X-012-A](T-012-S4-experiment-readiness.md) đặt đơn vị transaction, nhãn mục tiêu và cách chấm `correct-target / wrong-target / unresolved`; chưa chấm thắng/thua vì thiếu dữ liệu.
6. Experiment sau này kiểm uncertainty với split/metric/acceptance có nguồn; **final technical decision** mới dựa trên evidence đó và review. Không đi ngược từ candidate hoặc điểm benchmark để sửa nghiệp vụ.

## Vì sao bước sau tồn tại

T-011 E2 chỉ chấm 4.215/6.000 cặp; 1.399/1.785 cặp bị loại có ảnh nhiều detection. Đây là dấu hiệu coverage của pipeline nghiên cứu, không xác nhận sai người ở cửa phòng. Để cân nhắc thay rule một mặt cần nhãn người mục tiêu và metric lỗi chọn nhầm (T-008 RISK-001/002), vì chỉ tăng số cặp được chấm có thể che giấu sai lựa chọn S4. Do đó X-012-A tồn tại **trước** bất kỳ quyết định chọn rule/model S4 nào.

Quốc An giới hạn nguồn ở dữ liệu có sẵn. [Audit LTFT](T-012-S4-ltft-label-audit.md) thấy nhãn box/ID nhiều người nhưng video S5 không khớp frame, nên câu hỏi **có ảnh** chưa kiểm được. Từ capability giữ đúng người sau khi chọn ban đầu, [protocol box-only](T-012-S4-box-only-proxy-protocol.md) suy ra phép thử hẹp P0/P1 với cùng box khởi đầu do nhãn cấp, không chứa claim. [Kết quả](runs/T-012-S4-ltft-box-proxy.md) P1 `758/38/228` so P0 `446/143/435` đúng/sai/unresolved trên 1.024 cửa sổ–ID cho thấy liên kết liên frame đáng nghiên cứu tiếp **trong proxy**. Bước kế tiếp vẫn tồn tại vì proxy không trả lời ai là người thực hiện claim, không đo detector/camera cửa phòng hay quyền vào phòng; không được lấy điểm proxy để chọn rule cuối.

[Chẩn đoán đường đi D1](runs/T-012-S4-ltft-path-diagnostic.md) được đặt **sau khi xem endpoint P0/P1** để hỏi endpoint có che sai ID giữa cửa sổ không. Kết quả 41 cửa sổ từng sai so với 38 sai endpoint và 3 kết thúc unresolved; tất cả lần sai đầu xảy ra khi box target hợp lệ không còn trong annotation frame đó. Vì vậy câu hỏi tiếp theo phải kiểm **mất dấu/abstain và lỗi xuyên thời gian**, chứ không chỉ tỷ lệ đúng ở frame cuối. D1 không cấp quyền chọn P1 hay biến nhãn target vắng thành tín hiệu runtime.

E2 có 954 genuine và 831 impostor `unresolved` trên toàn bộ 6.000 cặp. Đây không phải false reject hay absence: một cặp ảnh không là transaction và không có quyền ra quyết định vào phòng. Chính sự phân biệt này dẫn đến yêu cầu **nhãn transaction và ba outcome có mẫu số đầy đủ** trong X-012-A. Nếu chỉ đo FMR/FNMR trên cặp còn lại, phần thiếu kết luận và khả năng chọn sai người vẫn không thấy được.

E1 có AP/recall ba detector. [X-012-B run report](runs/T-012-E1-widerface-error-slices.md) cho thấy nhóm bbox `<16` px bị bỏ sót nhiều trên WIDER; phép chẩn đoán không phải cớ tune trên validation đã xem. Cần đo phân bố cỡ mặt/điều kiện tại camera cửa phòng trước khi gọi đây là bottleneck triển khai. [E2 split custom](runs/T-011-E2-xqlfw-identity-disjoint.md) tách identity giữa hai nhóm chọn/chấm threshold và vẫn thấy R50 ít lỗi hơn MBF trên cặp được chấm; 1.484 impostor nối nhóm bị loại và 1.378 cặp trong nhóm không qua rule một mặt, nên chưa là main test gần miền hoặc bằng chứng về unseen pretrain identity. X-012-C tồn tại để kiểm miền/chi phí encoder trên thiết bị đích. [M1 cùng runner](runs/T-011-M1-reference-detection.md) đã đo detection component, nhưng không thay phép đo thiết bị đích/attempt/hàng chờ X-012-E. E3 chờ policy profile và app; không dùng điểm E1/E2/M1 để điền kết quả.

## Quy tắc giữ nhất quán

- Không gộp AP E1, FMR/FNMR E2, coverage S4 và pass/fail E3 thành một accuracy hệ thống.
- Không chọn model, threshold, dataset cuối hoặc thuật toán tối ưu từ kết quả học thuật hiện có.
- Không biến timing GitHub runner thành claim về latency thiết bị đích hay giảm nhân sự.
- Không tạo pass/fail E3 khi thiếu profile policy được duyệt hoặc implementation; `not-runnable` không là `pass`.
- Nếu T-008/T-010 đổi capability/protocol sau review, rà lại trace và run/fixture bị ảnh hưởng trước khi gọi baseline locked.
