# T-011 — Cổng dữ liệu E1 cho WIDER FACE validation

**Ngày kiểm:** 2026-09-27. **Trạng thái:** file/annotation gate đạt để thiết kế run E1; **chưa chạy detector benchmark** và chưa khóa quy tắc chấm/ignore.

## Vì sao kiểm

T-008/T-005 tạo nhu cầu phát hiện mặt ở S3 trên ảnh nguyên khung. [T-009 PR #5](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/5) giữ WIDER FACE làm ứng viên detection nhưng chưa kiểm archive và nhãn thực; [T-010 PR #6](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6) yêu cầu đúng file, split, bbox và quy tắc match/ignore trước khi so YuNet, BlazeFace, SCRFD. Bước này trả lời phần **dữ liệu có mở/chấm được không**, không trả lời detector nào tốt hơn.

## Nguồn và file đã kiểm

Nguồn phát hành: [CUHK-CSE/wider_face](https://huggingface.co/datasets/CUHK-CSE/wider_face), trang của The Chinese University of Hong Kong; card ghi giấy phép CC BY-NC-ND 4.0 và validation gồm 3.226 ảnh. Tải hai asset từ mục Files của repo đó vào thư mục tạm ngoài Git:

| Asset | Dung lượng byte | SHA-256 |
|---|---:|---|
| WIDER_val.zip | 362.752.168 | F9EFBD09F28C5D2D884BE8C0EAEF3967158C866A593FC36AB0413E4B2A58A17A |
| wider_face_split.zip | 3.591.642 | C7561E4F5E7A118C249E0A5C5C902B0DE90BBF120D7DA9FA28D99041F68A8A5C |

Cách tái lập: [script audit ở commit 250a157](https://github.com/quocanwyf/doantotnghiep2nguoi/commit/250a157) nhận --images, --annotations và --output; kiểm SHA-256/CRC, parse toàn bộ nhãn và giải mã từng ảnh. JSON chỉ chứa số tổng hợp, nằm cục bộ trong artifacts/t011-widerface-data-gate.json, không đưa ảnh/nhãn thô vào Git. Runtime kiểm: Python 3.12.2, OpenCV 5.0.0, NumPy 2.2.6.

Cả hai ZIP qua kiểm CRC. File nhãn được parse là wider_face_split/wider_face_val_bbx_gt.txt; mỗi nhóm gồm đường dẫn ảnh, số bbox và các dòng 10 trường (x, y, width, height, blur, expression, illumination, invalid, occlusion, pose). Không giải nén hoặc commit ảnh.

## Kết quả kiểm cấu trúc

- 3.226 JPG trong archive ảnh; 3.226 mục ảnh trong annotation, không path thiếu hoặc trùng. Giải mã bằng OpenCV 5.0.0: **0 lỗi**.
- 39.708 dòng bbox; **0 dòng sai 10 trường**; parse hết 46.160 dòng TXT.
- 585 bbox có cờ invalid = 1; 11 bbox có width hoặc height không dương. Các nhóm này có thể trùng nhau, không cộng thành số bbox bị bỏ.
- Archive còn có wider_face_val.mat. Kiểm hiện tại xác nhận TXT khớp ảnh; chưa xác nhận protocol easy/medium/hard hoặc quy tắc ignore/chấm AP chính thức.

## Điều kiện trước khi chạy E1

1. Khóa annotation và evaluator: bbox nào được tính/ignore, xử lý invalid/nonpositive và cách match prediction–ground truth; nếu báo AP theo WIDER chuẩn phải có đúng ground truth/protocol của từng mức khó. Không tự coi mọi dòng TXT là bbox hợp lệ.
2. Pin manifest validation, kích thước ảnh/tọa độ, preprocessing và output adapter riêng cho YuNet, BlazeFace full-range, SCRFD-500MF; so trên **cùng ảnh và cùng evaluator**.
3. Ghi nguồn/hash weight, runtime, warm-up và thiết bị; nếu thiếu một wrapper hoặc dữ liệu cho candidate thì không tạo bảng so sánh giả.
4. Giới hạn kết luận ở detection S3: WIDER FACE là ảnh sự kiện, không có claim thí sinh/người mục tiêu S4 hoặc nghiệp vụ ca/phòng. Nó không kiểm được xác minh 1:1 hay hiệu quả cửa phòng.

**Quyết định cổng:** WIDER FACE validation qua kiểm file/nhãn cơ bản cho E1. Phép đo AP/recall vẫn chờ quy tắc evaluation/ignore và các wrapper detector được khóa trước khi chấm.

## Protocol chấm được đặt trước — 2026-09-27

[T-010 E1 scoring protocol](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md) đã định nghĩa AP **nội bộ** trên 3.226 ảnh validation từ TXT, xử lý `invalid`/bbox không dương, ignored region, ghép prediction–GT và các ca preflight. Không gọi kết quả sau này là WIDER Easy/Medium/Hard chính thức. **Benchmark E1 vẫn chưa chạy**: evaluator code, wrapper ba detector và điều kiện đo phải được pin, kiểm bằng fixture trước khi xem điểm; mốc dữ liệu ở tài liệu này không tự hoàn thành các gate đó.
