# T-012 — Hợp đồng nhãn tối thiểu cho X-012-A

**Trạng thái:** bản chuẩn bị trước dữ liệu, chưa khóa thí nghiệm và chưa có kết quả S4. Tài liệu này cụ thể hóa [câu hỏi X-012-A](T-012-error-analysis.md) và [điều kiện sẵn sàng](T-012-S4-experiment-readiness.md); nó không chọn dataset, cách chọn mặt hay giá trị chấp nhận.

## 1. Đơn vị và sự thật cần biết

- **Capture session:** một buổi/camera/thiết lập ghi hình có nguồn và quyền dùng xác định.
- **Attempt/transaction:** một lần một người đưa claim/hồ sơ để bắt đầu kiểm tra, có mốc bắt đầu–kết thúc quan sát. Đơn vị chấm chính là attempt, không phải frame, bbox hay cặp ảnh XQLFW.
- **Claim:** hồ sơ được chọn bằng thao tác ngoài nhãn ảnh. Claim không chứng minh ai trong frame là người đã khai báo. Muốn chấm X-012-A nghiệp vụ, nguồn dữ liệu có sẵn phải cung cấp bằng chứng độc lập nối actor thực hiện claim với hồ sơ; không suy liên kết này từ model hay track ID.
- **Target:** actor gắn với thao tác claim ở lượt đó, nếu người này xuất hiện trong cửa sổ camera. Nếu target vắng khỏi khung, bị che đến mức không xác định được, hoặc không thể đối chiếu claim với actor, phải ghi riêng; không lấy mặt gần/lớn nhất làm target mặc định.

Một nguồn công khai chỉ có face/track ID mà không có claim và ranh giới attempt **chưa đủ để chấm X-012-A như nghiệp vụ cửa phòng**. Nó có thể dùng cho phép thử proxy tracking, với tên và kết luận riêng.

## 2. Các trường cần ghi ở bộ dữ liệu cục bộ

| Nhóm | Trường logic bắt buộc | Mục đích |
|---|---|---|
| Nguồn và quyền | mã nguồn/quyền dùng, capture-session ID, điều kiện sử dụng và lưu giữ | Xác định lượt được phép dùng và điều kiện bàn giao |
| Attempt | mã attempt phi định danh, thời điểm bắt đầu/kết thúc, camera, claim key cục bộ, actor thực hiện claim | Khóa đơn vị chấm và nối claim với actor bằng chứng độc lập |
| Frame/track | thứ tự frame và timestamp; bbox/track ID của các mặt có liên quan, gồm người nền; vùng quan sát nếu có | Chấm đúng track, sai track hoặc không chọn trong cùng cửa sổ |
| Nhãn target | `visible`, `absent-from-window`, hoặc `undeterminable`; track ID mục tiêu khi `visible`; lý do khi không gán được | Không ép trường hợp thiếu bằng chứng thành đúng/sai |
| Tình huống | một/nhiều mặt, mục tiêu bị che/ngoài khung, người nền, lượt bị ngắt, quay lại | Báo lỗi theo ca, không che rủi ro bằng một tỷ lệ chung |
| Kiểm nhãn | người gán, người kiểm độc lập, kết quả phân xử và revision nhãn | Truy vết sửa nhãn mà không dùng output candidate làm ground truth |

File ảnh/video, mapping claim–actor, bbox/track theo người và nhãn mức attempt ở kho cục bộ được kiểm soát; **không commit vào Git**. Repo chỉ có protocol, nguồn/quyền đã được phép công bố, số đếm tổng hợp và hash/phiên bản manifest nếu không làm lộ danh tính. Theo quyết định phạm vi của Quốc An ngày 27/09/2026, nhóm **chỉ dùng dữ liệu có sẵn, không tổ chức thu ảnh/video mới**. Kiểm điều kiện sử dụng của từng nguồn trước khi tải/chạy.

## 3. Quy tắc nhãn và chấm cần khóa trước test

1. Người gán nhãn nhận thông tin claim–actor từ biên bản lượt hoặc quan sát độc lập, **không nhìn output A0/A1/A2**. Người kiểm thứ hai rà các lượt khó; bất đồng chưa phân xử ghi `undeterminable` và lý do.
2. `visible`: target xác định được trong ít nhất phần cửa sổ quan sát đã định; track/bbox mục tiêu phải được gắn với frame liên quan. `absent-from-window`: biết actor thực hiện claim nhưng người đó không có mặt trong cửa sổ. `undeterminable`: không xác thực được mapping hoặc hình ảnh không cho phép phân xử. Không gộp hai trạng thái cuối.
3. Mỗi candidate xuất một lựa chọn track/face hoặc `unresolved` cho **mỗi attempt**. Nếu chọn track mục tiêu với nhãn `visible` là `correct-target`; chọn track khác, hoặc chọn ai khi target `absent-from-window`, là `wrong-target`; không chọn là `unresolved`. Lượt `undeterminable` không vào mẫu số đúng/sai, nhưng phải báo số lượng và lý do.
4. Báo `wrong-target` trên **mọi attempt có nhãn xác định**; `correct-target` và `unresolved` trên cùng mẫu số đó, rồi tách riêng `visible`/`absent-from-window`. Coverage của lựa chọn đúng chỉ tính trên target `visible`; khả năng từ chối an toàn khi target vắng báo riêng. Không gọi `unresolved` là absent/check-in thất bại.
5. Dev/test tách theo actor; mọi lần xuất hiện cùng actor và frame của cùng attempt nằm một phía. Nếu dữ liệu ít đến mức không thể chia như vậy, ghi `not runnable` cho phép so sánh locked test, không đổi split sau khi xem điểm.

## 4. Cổng chạy và đầu ra

Trước run, kiểm: quyền/consent và nguồn; mapping claim–actor độc lập; frame + mốc attempt đồng bộ; nhãn target và distractor đủ để chấm; kiểm bất đồng nhãn; split theo actor; cấu hình A0/A1/A2 và cửa sổ quan sát cố định; metric và mức chấp nhận do nhóm duyệt. Chỉ A2 khi thực sự có sequence. Thiếu bất cứ điều kiện bắt buộc nào thì ghi đúng nguyên nhân `not runnable`; có thể làm kiểm logic với dữ liệu tổng hợp nhưng không báo performance S4 thực.

Run report cần có số capture session, actor, attempt mỗi split và từng loại nhãn; số `undeterminable`/bị loại và lý do; ba outcome theo candidate trên cùng attempt; metric theo `visible`/`absent-from-window` và tình huống nhiều người; timing và điều kiện máy; sai khác/vi phạm protocol; kết luận chỉ trong miền dữ liệu đã đo. Điều kiện chấp nhận định lượng và policy vào phòng vẫn `TBD`, không lấy từ số XQLFW hoặc WIDER.

## 5. Chỉ dùng dữ liệu có sẵn: ranh giới của phép thử proxy

Nếu dữ liệu công khai có video nhiều người và face/track ID nhưng không có claim–actor theo lượt, chỉ được thiết kế **proxy giữ đúng track đã chỉ định**. Target proxy có thể được chỉ định từ nhãn công bố tại đầu cửa sổ quan sát, nhưng nhãn tương lai và ID ground truth không được đưa vào input của candidate. Kết quả proxy trả lời liệu cách liên kết qua frame có giữ đúng người giữa các distractor; nó **không** trả lời ai là người đã chọn hồ sơ thí sinh, không tính hiệu quả check-in hay quyết định vào phòng.

Nguồn [LTFT](T-012-S4-ltft-label-audit.md) đã có nhãn mặt/ID trên chuỗi ChokePoint S5 để tiếp tục kiểm khả năng này. Trước khi chạy, cần xác nhận quyền dùng của video và annotation, cách ghép frame chính xác, nhãn mục tiêu độc lập với output candidate, cửa sổ/split/metric cố định và số ca đủ nhãn. Thiếu điều kiện nào thì ghi `not runnable` cho phép thử tương ứng; không đổi tên proxy thành X-012-A nghiệp vụ.
