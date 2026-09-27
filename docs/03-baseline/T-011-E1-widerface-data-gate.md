# T-011 — Cổng dữ liệu E1 cho WIDER FACE validation

**Ngày kiểm:** 2026-09-27. **Trạng thái:** file/annotation gate đạt; quy tắc chấm/ignore đã được đặt trước ở T-010; evaluator và adapter đã viết; **10 kiểm thử tổng hợp đạt**, GT/image preflight trên toàn bộ WIDER validation và API preflight của cả ba detector trên 8 ảnh đạt; detector benchmark chưa chạy.

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

1. Dùng annotation/evaluator đã khóa ở [T-010 E1 scoring protocol](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md); kiểm preflight GT trước khi tính điểm. Nếu báo AP theo WIDER chuẩn phải có đúng ground truth/protocol của từng mức khó. Không tự coi mọi dòng TXT là bbox hợp lệ.
2. Pin manifest validation, kích thước ảnh/tọa độ, preprocessing và output adapter riêng cho YuNet, BlazeFace full-range, SCRFD-500MF; so trên **cùng ảnh và cùng evaluator**.
3. Ghi nguồn/hash weight, runtime, warm-up và thiết bị; nếu thiếu một wrapper hoặc dữ liệu cho candidate thì không tạo bảng so sánh giả.
4. Giới hạn kết luận ở detection S3: WIDER FACE là ảnh sự kiện, không có claim thí sinh/người mục tiêu S4 hoặc nghiệp vụ ca/phòng. Nó không kiểm được xác minh 1:1 hay hiệu quả cửa phòng.

**Quyết định cổng:** WIDER FACE validation qua kiểm file/nhãn cơ bản và GT/image preflight cho E1. Protocol evaluation/ignore và config ba wrapper đã được đặt trước; phép đo AP/recall vẫn chờ inference đầy đủ trên cùng 3.226 ảnh.

## Protocol chấm được đặt trước — 2026-09-27

[T-010 E1 scoring protocol](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md) đã định nghĩa AP **nội bộ** trên 3.226 ảnh validation từ TXT, xử lý `invalid`/bbox không dương, ignored region, ghép prediction–GT và các ca preflight. Không gọi kết quả sau này là WIDER Easy/Medium/Hard chính thức. **Benchmark E1 vẫn chưa chạy**: evaluator code, wrapper ba detector và điều kiện đo phải được pin, kiểm bằng fixture trước khi xem điểm; mốc dữ liệu ở tài liệu này không tự hoàn thành các gate đó.

## Mã chạy và thứ tự kiểm bắt buộc — 2026-09-27

- [Evaluator E1](../../scripts/t011_widerface_evaluate.py) nhận validation ZIP/annotation ZIP đã pin, kiểm manifest/ảnh/GT và tính AP nội bộ theo [T-010 E1 protocol](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md). [Test evaluator](../../tests/test_t011_widerface_evaluator.py) dùng box tổng hợp để bắt lỗi ignore, duplicate, IoU boundary, AP, ảnh rỗng và manifest.
- [Prediction adapter](../../scripts/t011_widerface_predict.py) có ba nhánh YuNet/BlazeFace/SCRFD với hash/config v1 đặt trước, xuất bbox/score theo tọa độ ảnh gốc vào JSON **ngoài Git**. [Test adapter](../../tests/test_t011_widerface_predict_adapter.py) kiểm chuyển tọa độ và giá trị không hữu hạn.
- Thứ tự thực hiện khi môi trường chạy trở lại: (1) evaluator `--preflight-only` để kiểm GT/ảnh, số box ngoài biên; (2) mỗi adapter `--preflight-only` để kiểm API/tọa độ; (3) chạy prediction đầy đủ trên cùng 3.226 ảnh; (4) evaluator chấm từng JSON bằng cùng code và ghi summary; (5) so AP và thời gian với phạm vi đo rõ. Nếu một gate lỗi, dừng và ghi revision, **không chọn cấu hình bằng điểm validation**.
- [GitHub Actions run 36293858671](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36293858671) chạy Python 3.12, **10/10 unit test tổng hợp đạt** cho logic AP/ignore/duplicate/IoU/manifest và chuyển tọa độ adapter. Đây là test synthetic của code; không đọc WIDER thật và không load weight/model. [Run 36293972494](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36293972494) trên workflow `actions/checkout@v7` và `actions/setup-python@v7` cũng đạt **10/10 test**; job và log đã được kiểm.
- [GT/image preflight run 36294105147](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294105147) tải hai ZIP vào bộ nhớ tạm của GitHub runner, kiểm SHA-256/CRC, 3.226 ảnh giải mã và manifest; `gt_outside_image = 0`, `valid_gt = 39.112`, `ignored_gt = 585`, `nonpositive_rows = 11`. Chỉ log số tổng hợp, không lưu ảnh/nhãn thô vào Git hoặc artifact. Python 3.12.14, NumPy 2.2.6, OpenCV headless 5.0.0.93. Đây là cổng dữ liệu, **không có detector score**.
- [Run 36294608464](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294608464) qua GT/image gate và API/coordinate preflight trên **cùng 8 ảnh đầu theo manifest** cho YuNet, BlazeFace full-range, SCRFD-500MF. Đúng hash weight: YuNet `EBAFCE4E...`, BlazeFace `3698B18F...`, SCRFD `5E4447F5...BD6C0...`; lần đầu SCRFD thất bại do chép nhầm một ký tự hash nội bộ, đã sửa ở [T-010 protocol](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md) và runner **trước khi có AP**. Số row lần lượt 10.419, 2.126, 20.866; chỉ kiểm output shape/tọa độ/score và nhận diện rủi ro dung lượng prediction, không dùng chúng để chọn model hoặc threshold. Thời gian 8 ảnh trong log là quan sát không kiểm soát, không dùng làm so sánh latency.
- Chưa có run E1 đầy đủ: công cụ khởi tạo tiến trình cục bộ trả lỗi `helper_unknown_error: setup refresh had errors`; GitHub runner mới thực hiện preflight. Vì vậy chưa có AP/recall/latency detector hay model thắng. Trước benchmark cần chuẩn hóa môi trường OpenCV: `mediapipe` kéo `opencv-contrib-python`, `insightface` kéo thêm `opencv-python-headless`; [hướng dẫn gói OpenCV](https://pypi.org/project/opencv-python-headless/) khuyên chỉ cài một gói cung cấp `cv2`. Cần xử lý xung đột này và kiểm tài nguyên cho JSON prediction lớn trước phép đo toàn bộ.
