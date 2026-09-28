# Logic triển khai giai đoạn 06

- **Bài toán:** hỗ trợ tiếp nhận tại cửa phòng thi và ghi nhận các kết quả riêng biệt của lượt kiểm tra, check-in, quyền vào phòng và attendance. [T-008](../01-problem/T-008-requirements.md) và [D-003](../00-project/decisions/T-008-D-003-chap-nhan-baseline-nghien-cuu.md) không cho phép điểm AI tự quyết định quyền vào.
- **Yêu cầu của T-018:** app tham chiếu phải ghi attempt trước tra cứu, giữ các trường hợp không tìm thấy/nhiều hồ sơ/sai phòng, kiểm quyền theo ca/phòng và chống ghi trùng. Kết quả `unresolved` theo A0 đi vào thử lại/review. [Luồng T-018](T-018-app-reference.md).
- **Lựa chọn kỹ thuật đã ghi:** [D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md) chọn Flutter, Django REST Framework, PostgreSQL và B0 của Quốc An làm pipeline AI tham chiếu. Nơi chạy AI, ngưỡng và policy vận hành còn mở.
- **Bước lõi hiện tại:** tách dữ liệu/nghiệp vụ/API/UI; lưu tham chiếu roster và policy có người xác nhận/phê duyệt; chỉ mở context khi đủ tham chiếu; tạo attempt có khóa chống retry; tra cứu roster và mở review. Chưa triển khai xác minh AI hoặc ghi check-in vì chưa có profile policy đã duyệt.
- **Kiểm chứng:** test API/quyền/ràng buộc trên SQLite trong bộ nhớ và test giao diện Flutter; PostgreSQL, camera, AI và thiết bị đích chưa được kiểm tích hợp. [Hướng dẫn backend](../../backend/README.md), [hướng dẫn Flutter](../../mobile/README.md).
- **Bước kế tiếp:** thống nhất profile nghiệp vụ, nguồn roster/thiết bị/quyền; kiểm PostgreSQL thật; thêm đăng nhập và chọn context; định nghĩa hợp đồng xác minh 1:1 và đường review trước khi mở hành động check-in.

Đây là bản đồ lập luận của giai đoạn, không thay thế quyết định chính thức hoặc phê duyệt vận hành thật.
