# T-012 — E2: kết quả ba nhánh trên toàn bộ cặp XQLFW

**Ngày phân tích:** 2026-09-27. **Loại bằng chứng:** tính lại từ số đếm tổng hợp đã công bố trong [run E2](T-011-E2-xqlfw-mbf-vs-r50.md) và [coverage diagnosis](T-011-E2-coverage-diagnosis.md); không chạy lại ảnh, detector hoặc encoder. **Đơn vị:** cặp ảnh trong phép thử 1:1, không phải một lượt thí sinh đến cửa phòng.

## Câu hỏi

Nếu giữ quy tắc E2 hiện tại (mỗi ảnh trong cặp phải có đúng một detection), bao nhiêu cặp đi đến `match`, `non-match` hoặc `unresolved`? Việc chỉ báo FMR/FNMR trên cặp hợp lệ đã che phần nào của pipeline?

Quy ước trong bảng dưới đây: `match`/`non-match` là kết quả nhị phân theo threshold được chọn ngoài fold của **từng encoder** trong T-011; `unresolved` là cặp không thể chấm vì ít nhất một ảnh không thỏa quy tắc một mặt. Đây là cách **mô tả output của protocol**, chưa phải ba trạng thái attendance hoặc một chính sách cho vào phòng.

## Đối chiếu số đếm

XQLFW có 3.000 cặp genuine và 3.000 cặp impostor. Nguồn T-011 có 2.046 genuine + 2.169 impostor hợp lệ = 4.215 cặp; phần còn lại là 954 genuine + 831 impostor = 1.785 cặp unresolved. Tỷ lệ hợp lệ toàn tập là 4.215/6.000 = **70,25%**; unresolved là **29,75%**. Mẫu số FMR/FNMR bên dưới vẫn là cặp hợp lệ của từng loại.

| Encoder | Nhãn cặp | Match | Non-match | Unresolved | Tổng | Lỗi có điều kiện trên cặp hợp lệ |
|---|---|---:|---:|---:|---:|---|
| MobileFaceNet | Genuine | 1.921 | 125 | 954 | 3.000 | FNMR = 125/2.046 = 6,11% |
| MobileFaceNet | Impostor | 133 | 2.036 | 831 | 3.000 | FMR = 133/2.169 = 6,13% |
| R50 | Genuine | 1.972 | 74 | 954 | 3.000 | FNMR = 74/2.046 = 3,62% |
| R50 | Impostor | 76 | 2.093 | 831 | 3.000 | FMR = 76/2.169 = 3,50% |

Phép tính kiểm: `match(genuine) = 2.046 − false reject`; `non-match(impostor) = 2.169 − false accept`. Mỗi dòng có tổng đúng 3.000; unresolved giống nhau giữa hai encoder vì detector, alignment và rule lọc cặp được giữ cố định. Genuine unresolved = 954/3.000 = **31,80%**; impostor unresolved = 831/3.000 = **27,70%**. Chênh lệch này mô tả **coverage theo nhãn cặp trong XQLFW**, không chứng minh cơ chế gây thiếu mặt hay bias tại phòng thi.

Trong 1.785 cặp unresolved, [chẩn đoán T-011](T-011-E2-coverage-diagnosis.md) cho biết 1.399 cặp có ít nhất một ảnh nhiều detection và 448 cặp có ít nhất một ảnh không detection; hai nhóm giao nhau 62 cặp. Không được cộng 1.399 và 448 thành tổng. Nhiều detection không có nghĩa đã xác định được người mục tiêu; không detection cũng chưa chứng minh thí sinh vắng mặt.

## Ý nghĩa đối với nghiệp vụ và thí nghiệm

- **OBSERVED:** R50 có ít lỗi match/non-match hơn MobileFaceNet trên cùng 4.215 cặp đã chấm. Cả hai để lại đúng 1.785 cặp chưa chấm; thay encoder trong phép đối chứng này không cải thiện coverage do quy tắc S4/S3.
- **INFERENCE:** nếu hệ thống tương lai giữ nhánh `unresolved`, nó phải có luồng tiếp tục quan sát, thử lại hoặc review theo policy; không được tự đổi cặp chưa chấm thành `non-match`, `check-in thất bại` hoặc `absent`. Điều này truy về T-008 FR-006/FR-009 và phân biệt attempt với check-in/attendance.
- **CHƯA ĐO:** tỷ lệ lượt phải chuyển người, thời gian hàng chờ, sai chọn người, false acceptance nghiệp vụ và hiệu quả giảm nhân sự. Một cặp ảnh không tương đương một transaction; ảnh và identity có thể lặp giữa cặp. Không thể lấy 29,75% làm tỷ lệ review ở cửa phòng hoặc lấy 6,13% làm tỷ lệ cho nhầm người vào phòng.
- **CÂU HỎI KẾ TIẾP:** với transaction có nhãn người mục tiêu (hoặc nhãn không có mục tiêu), cách xử lý S4 nào tăng tỷ lệ kết luận mà không tăng chọn sai người? Cần đo `correct-target`, `wrong-target`, `unresolved` trên **cùng mẫu số transaction**, rồi mới đo tác động S4→E2 trên cùng dữ liệu và threshold khóa từ dev.

Phân tích này là cầu nối giữa [X-012-A](../T-012-error-analysis.md) và [kế hoạch chuẩn bị phép thử S4](../T-012-S4-experiment-readiness.md). Nó không thay kết quả hay threshold T-011 và không quyết định model/dataset triển khai.
