# Định hướng hiện tại

**Nguồn:** [dinhhuongdatn.docx](../sources/dinhhuongdatn.docx), bản ghi do nhóm cung cấp ngày 2026-09-24 sau buổi gặp đầu tiên. Ngày gặp và câu nào được thầy xác nhận trực tiếp chưa được tách rõ trong nguồn. Vì vậy, tài liệu này là tóm tắt làm việc, không tự gán mọi ý thành yêu cầu chính thức của thầy.

## Mục tiêu nghiên cứu được ghi nhận

Chọn một bài toán ứng dụng nhận dạng khuôn mặt; xây baseline; xác định một điểm cần cải thiện trong pipeline; tích hợp thuật toán optimization có vai trò tìm kiếm/lựa chọn/quyết định rõ ràng; train hoặc fine-tune nếu phù hợp; đánh giá và so sánh định lượng. Mobile app dùng camera để chứng minh hệ thống hoạt động thực tế. Đóng góp nghiên cứu nằm ở optimization và bằng chứng thực nghiệm, không chỉ ở giao diện app.

Chuỗi suy nghĩ: **bài toán → yêu cầu → dữ liệu → model → điểm cần cải thiện → đối tượng và objective function → thuật toán tối ưu → baseline/proposed → đánh giá → mobile**.

## Phạm vi dự kiến

- Nhóm đã chọn **kiểm tra thí sinh tại cửa phòng thi** ở [D-001](decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md), theo xác nhận của Quốc An rằng mình và Minh Hy thống nhất. Quy chế kỳ thi mục tiêu và mức tự động hóa vẫn cần xác định; không suy lựa chọn này từ bản Word gốc.
- Pipeline tham khảo: camera → phát hiện khuôn mặt → crop/alignment → embedding/đặc trưng → nhận dạng → điểm danh hoặc ghi nhận hiện diện. Pipeline cụ thể tùy câu hỏi nghiên cứu.
- Có thể tối ưu hyperparameter, feature, ROI/bounding box, vùng ảnh, cấu trúc model hoặc hiệu năng trên mobile. Đây là **hướng khảo sát**, không phải các hạng mục phải làm hết.
- Jaya, HHO, PSO, GA, Bayesian Optimization và các thuật toán khác là **ứng viên**, chưa chọn. Cần xác định search space và objective function trước.
- Edge device, nhiều thuật toán, robustness và bài báo chỉ là hướng mở rộng khi phần chính đã hoàn thành.

## Điều phải kiểm chứng khi thiết kế thí nghiệm

Baseline và proposed cần dùng cùng dữ liệu, split, metric, giao thức đánh giá và điều kiện thực nghiệm, ngoại trừ thành phần cần nghiên cứu. Chỉ chọn metric có ý nghĩa với bài toán; cải thiện có thể là chất lượng nhận dạng hoặc đánh đổi hợp lý giữa chất lượng, tốc độ và kích thước model. Nếu thay nhiều thành phần, cần tách tác động khi có thể.

## Chưa chốt

Use case cửa phòng thi đã được nhóm chọn; hướng T-005 được ghi ở [D-002](decisions/T-007-D-002-chon-huong-khao-sat-t005.md). [D-004](decisions/T-018-D-004-chon-stack-app-tham-chieu.md) và [D-005](decisions/T-018-D-005-pham-vi-android-ai-tren-may.md) chọn stack app tham chiếu, Android trước và AI trên điện thoại cho ca học phần giả lập. Chưa chốt quy chế kỳ thi thật/mức tự động hóa, dataset/model/cấu hình cuối, optimization target/algorithm, training hay inference, operating point/metric định lượng, thiết bị đích, thời hạn và hình thức demo. Theo dõi câu hỏi ở [questions.md](questions.md) và quyết định chính thức ở [decisions/](decisions/).
