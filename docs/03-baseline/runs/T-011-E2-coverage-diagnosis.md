# T-011 — Chẩn đoán coverage của E2 XQLFW

**Ngày:** 2026-09-26. **Trạng thái:** phân tích hậu nghiệm, tách khỏi [run E2 gốc](T-011-E2-xqlfw-mbf.md). Kết quả và quy tắc loại cặp của run gốc không thay đổi.

## Câu hỏi và phương pháp

Vì sao chỉ 4.215/6.000 cặp được chấm trong E2, và nhóm lỗi nào cần khảo sát tiếp? Chạy lại **chỉ detector** SCRFD-500MF trên đúng 7.263 ảnh được tham chiếu, cùng ZIP/hash, input 640×640 và detection threshold 0,5. [Script chẩn đoán](../../../scripts/t011_xqlfw_coverage.py) đếm số mặt mỗi ảnh, phân loại lý do loại cặp và tổng hợp diện tích bounding box/điểm detector; chỉ ghi thống kê tổng hợp vào JSON ngoài Git. Không đổi ngưỡng, chọn mặt, tạo embedding hay chấm lại cặp.

## Kết quả

Số ảnh theo quy tắc một mặt khớp **chính xác** với run gốc: 6.064 một mặt, 291 không mặt, 908 nhiều mặt, 0 lỗi giải mã. Trong 908 ảnh nhiều mặt, 765 ảnh có hai detection, 114 có ba, 25 có bốn và 4 có từ năm trở lên.

| Loại cặp | Genuine | Impostor | Tổng |
|---|---:|---:|---:|
| Hợp lệ: cả hai ảnh đúng một mặt | 2.046 | 2.169 | 4.215 |
| Bị loại: chỉ có ảnh nhiều mặt | 712 | 625 | 1.337 |
| Bị loại: chỉ có ảnh không mặt | 211 | 175 | 386 |
| Bị loại: vừa có ảnh nhiều mặt vừa có ảnh không mặt | 31 | 31 | 62 |

Như vậy **1.399/1.785 cặp bị loại (78,4%)** có ít nhất một ảnh nhiều mặt. 448 cặp (25,1%) có ít nhất một ảnh không mặt, gồm 62 cặp cũng có ảnh nhiều mặt. Các nhóm này không được cộng chồng để suy tổng.

Ở 908 ảnh nhiều mặt, bounding box lớn thứ hai có diện tích **ít nhất 25%** box lớn nhất trong 743 ảnh (81,8%); chỉ 51 ảnh (5,6%) có box thứ hai dưới 10% box lớn nhất. Điểm detector của box lớn thứ hai theo diện tích dưới 0,7 trong 543 ảnh (59,8%). Các con số này không cho biết box nào là người mục tiêu, cũng không xác nhận detection nào là thật/giả.

## Diễn giải và bước kiểm chứng

Quy tắc **tự chọn box lớn nhất** có thể tăng coverage, nhưng số liệu hình học trên không đủ để xác nhận chọn đúng người. Đặc biệt, nhiều box thứ hai có kích thước đáng kể. Do đó chưa thay quy tắc trong E2 gốc và chưa cộng các cặp bị loại vào mẫu chấm FMR/FNMR.

Ưu tiên kế tiếp là kiểm tra mẫu ảnh nhiều mặt/không mặt với **nhãn người mục tiêu hoặc review thủ công có quy trình**, rồi đặt trước một phép thử riêng cho quy tắc chọn mặt/detector: tỷ lệ chọn đúng mục tiêu, coverage, FMR/FNMR trên cùng protocol và lỗi khi không xác định được mục tiêu. Nếu không có nhãn mục tiêu, chỉ báo cáo thay đổi coverage và giữ kết luận về lỗi nhận diện có điều kiện. Phép thử mới phải giữ run gốc làm đối chứng và tránh chọn rule theo chính fold chấm.

**Giới hạn:** XQLFW là ảnh web/crop, không đại diện ảnh cửa phòng thi. Thống kê hậu nghiệm mô tả output của một detector và một ngưỡng; không chứng minh nguyên nhân detector sai, cũng không cho phép suy hiệu quả vận hành hoặc chọn cấu hình cuối.
