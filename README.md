# Đồ án tốt nghiệp AI của nhóm hai người

Dự án nghiên cứu ứng dụng nhận dạng khuôn mặt với một thành phần được tối ưu có thể kiểm chứng bằng số liệu, sau đó triển khai bản phù hợp lên mobile. Đây là **định hướng sau buổi gặp đầu tiên**. Nhóm đã chọn bài toán cửa phòng thi ở [D-001](docs/00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md) và hướng khảo sát T-005 ở [D-002](docs/00-project/decisions/T-007-D-002-chon-huong-khao-sat-t005.md); dataset/model/cấu hình cuối vẫn chờ thí nghiệm.

## Hai nơi làm việc chung

- **GitHub:** mã nguồn, tài liệu và note bàn giao cho AI của cả hai: [quocanwyf/doantotnghiep2nguoi](https://github.com/quocanwyf/doantotnghiep2nguoi).
- **Google Sheet:** task, người phụ trách, người review và trạng thái: [bảng task](https://docs.google.com/spreadsheets/d/14BQCQ_LbGkZS15Grfi4AZNWBX15h479XjoyQvP9jHcU/edit?gid=0#gid=0).

Sau khi pull, đọc [AGENTS.md](AGENTS.md), [trạng thái hiện tại](docs/00-project/status.md), [định hướng](docs/00-project/brief.md) và [quy trình làm việc](docs/00-project/workflow.md). Task lấy từ Sheet; không duy trì bản sao task trong Git.

## Bản đồ tài liệu

```text
docs/00-project/       Thông tin chung, quyết định, câu hỏi, trạng thái, quy trình
docs/01-problem/       Chọn một nghiệp vụ và định nghĩa bài toán
docs/02-survey/        Khảo sát dataset, model, điểm và thuật toán tối ưu
docs/03-baseline/      Baseline và giao thức chạy có thể tái lập
docs/04-optimization/  Phương pháp tối ưu và phiên bản đề xuất
docs/05-evaluation/    So sánh, ablation và giới hạn kết luận
docs/06-mobile/        Tích hợp ứng dụng mobile và kiểm thử thực tế
docs/07-report/        Bản thảo báo cáo và đầu ra nộp
docs/meetings/         Một file mỗi buổi gặp
docs/progress/         Một file mỗi tuần cho cả hai
docs/handoffs/         Một file bàn giao cho mỗi task hoàn thành
docs/sources/          Bản Word gốc để hai thành viên đối chiếu
backend/               Django REST Framework: API và schema PostgreSQL T-018
mobile/                Flutter Android và bản xem thử Edge: trạng thái, đăng nhập, ca T-018
data/                  Dữ liệu cục bộ; nội dung nhạy cảm không lên Git
artifacts/             Checkpoint, log và đầu ra lớn cục bộ
```

Giai đoạn 01 và 02 đang làm có DECISION_LOGIC.md để ghi vì sao bước tiếp theo tồn tại và được suy ra từ bước trước. Khi bắt đầu giai đoạn sau, tạo và cập nhật file tương tự song song với công việc thực tế; không tạo trước tài liệu rỗng hoặc chốt kỹ thuật quá sớm.

Lộ trình T-018 và giới hạn hiện tại được ghi tại [giai đoạn 06](docs/06-mobile/README.md); [hướng dẫn chạy trong VS Code](docs/06-mobile/T-018-vscode-local-setup.md) cho phép thử mốc kết nối hiện có.
