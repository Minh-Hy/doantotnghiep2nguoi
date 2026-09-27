# Decision Logic — Phase 03 Baseline

## Chuỗi dẫn tới phép đo

1. [D-001](../00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md) và [T-008 PR #3](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3) xác định nghiệp vụ cửa phòng, capability, quyền và rủi ro. T-008 được dùng làm mốc generic tạm cho nghiên cứu; policy kỳ thi chưa được gán.
2. [T-009 PR #5](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/5) kiểm ứng viên dữ liệu/weight theo đúng stage và giữ/hoãn có điều kiện. Quyết định survey chỉ chọn **candidate đáng thử**.
3. [T-010 PR #6](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6) suy uncertainty thành E1 detection, E2 verification, E3 fixture nghiệp vụ và M1 vận hành; đặt dữ liệu, biến, metric, quy tắc chọn threshold và giới hạn trước khi xem điểm. Bản logic gốc của T-010 ở PR #6 là nguồn; file này được mang sang nhánh T-012 để tiếp tục cùng chuỗi reasoning khi các PR chưa hợp nhất.
4. [T-011 draft PR #7](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/7) tạo evidence E1 trên WIDER và E2 trên XQLFW. E3 chưa có profile được duyệt/implementation; M1 chưa có phép đo cùng thiết bị đích. Mỗi run chỉ trả lời phạm vi của nó.
5. [T-012](T-012-error-analysis.md) phân loại observed error, inference, hypothesis và chọn câu hỏi X-012-A về S4 target selection/coverage; vì thiếu nhãn mục tiêu, bước kế là thiết kế data gate và phép thử, chưa chấm thắng/thua.
6. Experiment sau này kiểm uncertainty với split/metric/acceptance có nguồn; **final technical decision** mới dựa trên evidence đó và review. Không đi ngược từ candidate hoặc điểm benchmark để sửa nghiệp vụ.

## Vì sao bước sau tồn tại

T-011 E2 chỉ chấm 4.215/6.000 cặp; 1.399/1.785 cặp bị loại có ảnh nhiều detection. Đây là dấu hiệu coverage của pipeline nghiên cứu, không xác nhận sai người ở cửa phòng. Để cân nhắc thay rule một mặt cần nhãn người mục tiêu và metric lỗi chọn nhầm (T-008 RISK-001/002), vì chỉ tăng số cặp được chấm có thể che giấu sai lựa chọn S4. Do đó X-012-A tồn tại **trước** bất kỳ quyết định chọn rule/model S4 nào.

E1 có AP/recall ba detector. [X-012-B run report](runs/T-012-E1-widerface-error-slices.md) cho thấy nhóm bbox `<16` px bị bỏ sót nhiều trên WIDER; phép chẩn đoán không phải cớ tune trên validation đã xem. Cần đo phân bố cỡ mặt/điều kiện tại camera cửa phòng trước khi gọi đây là bottleneck triển khai. E2 chưa chứng minh unseen identity; X-012-C cần split/test phù hợp và phép đo chi phí cùng điều kiện. E3/M1 phải chờ dependency nghiệp vụ/thiết bị thực, không dùng điểm E1/E2 để điền kết quả.

## Quy tắc giữ nhất quán

- Không gộp AP E1, FMR/FNMR E2, coverage S4 và pass/fail E3 thành một accuracy hệ thống.
- Không chọn model, threshold, dataset cuối hoặc thuật toán tối ưu từ kết quả học thuật hiện có.
- Không biến timing GitHub runner thành claim về latency thiết bị đích hay giảm nhân sự.
- Không tạo pass/fail E3 khi thiếu profile policy được duyệt hoặc implementation; `not-runnable` không là `pass`.
- Nếu T-008/T-010 đổi capability/protocol sau review, rà lại trace và run/fixture bị ảnh hưởng trước khi gọi baseline locked.
