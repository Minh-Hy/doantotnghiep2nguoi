# T-012 X-012-I — Đưa A0 lên trước bước tạo embedding

**Ngày:** 28/09/2026. **Run:** [GitHub Actions 36390331459](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36390331459), thành công. **Protocol khóa trước run:** [X-012-I](../T-012-X-012-I-conditional-embedding-protocol.md), commit `d44e334`; mã/workflow commit `68adc61`. Đây là phép đo tối ưu **chi phí xử lý B0**, không đổi model hay giải bài toán chọn đúng người ở S4.

## Vì sao thử

B0 gọi `FaceAnalysis.get` nên tạo embedding cho tất cả detection rồi mới áp dụng A0 `đúng một mặt`. Ở XQLFW, B0 gặp 908/7.263 ảnh nhiều detection và không dùng embedding nào của các ảnh này. Bản I giữ SCRFD/MBF và A0, nhưng chỉ gọi recognition khi detector trả đúng một box. Giả thuyết là giảm công việc thừa, giữ nguyên outcome xác minh; phép thử **không** giả định box lớn nhất hay box khớp nhất là người khai báo.

## Input, đối chứng và gate

- XQLFW: 7.263 JPG từ 6.000 cặp; SHA-256 ZIP `1af459679fba23a12f4d83c82a81523eb930a4aec759eebefcbdde69a678962c`, pairs `636852f90b886f3f56c73b13c9775f7ffcd37662dbb189c694f6a0a605b63b84`. `buffalo_sc.zip` SHA-256 `57d31b56b6ffa911c8a73cfc1707c73cab76efe7f13b675a05223bf42de47c72`; hai ONNX hash được kiểm và in trong [run log](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36390331459).
- B0 và I xử lý **cùng một ảnh đã giải mã** liên tiếp, xen kẽ thứ tự chạy theo vị trí ảnh; hai nhánh warm-up trước đo. Runner Linux Azure 4 logical CPU, Python 3.12.14, OpenCV 5.0.0, ONNX Runtime 1.20.1, InsightFace 0.7.3, CPUExecutionProvider; SCRFD 640×640, detection threshold 0,5. Workflow đặt ba biến môi trường BLAS/OpenMP bằng 1; chưa xác nhận số luồng nội bộ ONNX Runtime.
- Mỗi ảnh có cùng số detection giữa hai nhánh. Trên ảnh một mặt, bbox/landmark và embedding khớp trong dung sai `rtol=atol=10⁻⁶`; nếu sai, run dừng. E2 pair-fold gốc được dùng lại. Không lưu embedding/ảnh/weight ở Git; file tạm được xóa ở bước cuối workflow.

## Kết quả chức năng: không đổi

| Chỉ số | B0 và I |
|---|---:|
| Ảnh một / không / nhiều detection | 6.064 / 291 / 908 |
| Cặp có score / toàn bộ | 4.215 / 6.000 |
| Cặp `unresolved` genuine / impostor | 954 / 831 |
| FA / impostor có score | 133 / 2.169 = 6,13% |
| FR / genuine có score | 125 / 2.046 = 6,11% |

B0 gọi recognition **8.057 lần** trên 7.263 ảnh; I gọi **6.064 lần**. I bỏ 1.993 lần vốn dành cho 908 ảnh nhiều detection. Cả hai vẫn để ảnh nhiều mặt `unresolved`; đây là hành vi B0 hiện tại, không phải giải pháp S4.

## Thời gian inference trên cùng runner

Timer chỉ bao `FaceAnalysis.get` hoặc `detector.detect + recognizer.get` tương ứng; **không** bao giải mã ảnh, nạp model, truy vấn hồ sơ, review hay toàn bộ lượt check-in. Tổng giây là tổng thời gian inference riêng từng nhánh trên cùng bộ ảnh, không phải wall time job.

| Nhóm ảnh | n | B0 median / p95 | I median / p95 | Tổng B0 → I |
|---|---:|---:|---:|---:|
| Toàn bộ | 7.263 | 52,74 / 73,79 ms | 49,65 / 65,75 ms | 394,72 → 358,95 s (−9,06%) |
| Một mặt | 6.064 | 51,98 / 66,11 ms | 52,03 / 66,02 ms | 319,72 → 320,00 s |
| Nhiều mặt | 908 | 70,65 / 97,19 ms | 32,23 / 41,84 ms | 66,02 → 29,71 s (−55,00%) |
| Không mặt | 291 | 31,23 / 40,68 ms | 31,82 / 40,37 ms | 8,98 → 9,24 s |

Thứ tự xen kẽ không đảo dấu ở mức tổng nhóm: với B0 chạy trước, tổng riêng 3.632 ảnh là B0/I `198,35/180,45 s`; với I chạy trước, 3.631 ảnh là `196,37/178,50 s`. Đây là kiểm nhiễu thứ tự đơn giản, chưa phải lặp nhiều runner hoặc khoảng tin cậy hiệu năng.

## Diễn giải và bước tiếp

**Kết luận trong phạm vi B0/XQLFW:** đưa A0 lên trước recognition loại công việc thừa trên ảnh nhiều detection mà không đổi tập ảnh/cặp được chấm, embedding một mặt hoặc FA/FR. Lợi thời gian tập trung ở nhóm nhiều detection; nhóm một mặt không có cải thiện có ý nghĩa thực dụng trong run này. Vì XQLFW là ảnh web đã dùng để phát triển baseline và tỷ lệ nhiều detection không phản ánh camera cửa phòng, **không** suy ra giảm 9,06% latency của lượt check-in hoặc throughput vận hành.

X-012-I là tối ưu cách thực thi **rule A0**, không phải đóng góp giải quyết nhiều mặt. S4 vẫn cần chọn/giữ đúng người đã khai báo hồ sơ khi camera thấy người khác. [X-012-H](T-012-X-012-H-s4-overlap-gate.md) mới chứng minh một gate giảm sai track trong proxy với box đầu oracle; LTFT frame–nhãn chưa ghép được để nối S3→S4→verification. Bước nghiên cứu tiếp theo chỉ nên chạy khi một nguồn ảnh/nhãn sẵn có cho phép chấm mục tiêu độc lập, hoặc tiếp tục tối ưu stage khác với cùng nguyên tắc B0→lỗi quan sát→can thiệp→đối chứng. Chưa chọn model/ngưỡng triển khai.
