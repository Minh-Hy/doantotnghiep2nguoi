# T-012 X-012-I — Chỉ tạo embedding sau khi A0 xác nhận đúng một mặt

**Khóa trước run:** 28/09/2026. **Loại:** tối ưu chi phí tính toán của B0, không sửa quyết định danh tính hay giải quyết S4 nhiều mặt.

## Câu hỏi xuất phát từ B0

B0 gọi `FaceAnalysis.get`, nên recognition chạy cho **mọi** mặt được phát hiện rồi A0 mới loại ảnh có 0 hoặc nhiều mặt. [Mã nguồn InsightFace](https://github.com/deepinsight/insightface/blob/master/python-package/insightface/app/face_analysis.py) cho thấy thứ tự này. Trong E2, 908/7.263 ảnh có nhiều detection; embedding tạo cho các box ấy không được dùng. Câu hỏi: **đưa A0 lên trước recognition có giảm thời gian xử lý ảnh, trong khi giữ nguyên số ảnh/cặp có score và kết quả xác minh không?**

Đây là thay đổi thứ tự xử lý, không là model mới, không chọn đại một box trong ảnh nhiều mặt. Khi S4 sau này giải được việc chọn người mục tiêu, quy tắc A0 này cần được thay bằng lựa chọn S4 đã kiểm.

## Hai nhánh và điều kiện đo

- **B0 đối chứng:** cùng `buffalo_sc`, SCRFD-500MF 640×640/0,5 và MobileFaceNet; `FaceAnalysis.get(image)` chạy detection và recognition, sau đó A0 chỉ giữ ảnh đúng một mặt.
- **I can thiệp:** gọi đúng detector đã nạp trong B0; nếu có đúng một box thì tạo `Face` từ bbox, score, landmark và gọi đúng recognition model của B0 một lần; nếu 0 hoặc nhiều box thì trả `unresolved` trước recognition. Không đổi ảnh, weight, tiền xử lý, landmark, embedding, cosine, threshold fold hay chính sách chọn người.
- **Dữ liệu:** XQLFW 7.263 JPG / 6.000 cặp và ba SHA-256 đã khóa ở E2. Cùng ảnh được giải mã **một lần**, rồi chạy hai nhánh liên tiếp; thứ tự B0→I và I→B0 xen kẽ theo vị trí ảnh. Warm-up hai nhánh trước khi đo. Một runner CPU, cùng phiên bản thư viện, một luồng CPU theo workflow; thời gian chỉ bao `get` hoặc `detect + recognition.get`, không gồm tải/giải mã, tạo app hay ghi summary.
- **Gate đúng chức năng:** hai nhánh phải có cùng số detection cho từng ảnh; với đúng một mặt, bbox/landmark và embedding phải bằng nhau trong sai số số học nhỏ; cùng 4.215 cặp có score, 1.785 chưa kết luận, cùng FA 133/FR 125 của B0. Nếu không tái lập, dừng diễn giải tốc độ.
- **Chỉ số:** median/p95 thời gian trên **cùng ảnh** cho toàn bộ, nhóm một mặt và nhóm nhiều mặt; tổng thời gian inference trên 7.263 ảnh; số lần recognition bỏ qua; chênh lệch theo từng ảnh. Báo mẫu số, máy/runner, commit và phiên bản. Không gọi thời gian này là latency lượt check-in; ảnh trong ZIP không đại diện phân bố camera cửa phòng.

## Diễn giải trước kết quả

Nếu I giữ nguyên outcome và giảm thời gian nhóm nhiều mặt, nó chứng minh tránh tính embedding thừa trong **B0 A0** trên nguồn này. Nếu toàn bộ không nhanh hơn hoặc biến thiên thứ tự lớn, không tuyên bố cải thiện vận hành. Dù nhanh hơn, I vẫn trả `unresolved` khi nhiều mặt, nên **không** giải quyết mục tiêu S4 chọn đúng người khai báo. XQLFW đã được xem trong quá trình chọn baseline, vì vậy đây là phép thử phát triển, không là kiểm định độc lập hoặc kết quả thiết bị đích.
