# T-012 — Điều kiện chuẩn bị phép thử S4 chọn người mục tiêu

**Trạng thái:** kế hoạch nghiên cứu X-012-A, **chưa chạy experiment** và chưa chọn cách triển khai. Nguồn câu hỏi là [T-012 error analysis](T-012-error-analysis.md): E2 chỉ chấm 4.215/6.000 cặp XQLFW; [phân tích ba nhánh](runs/T-012-E2-three-outcome-analysis.md) giữ 1.785 cặp còn lại ở `unresolved`. Số cặp ảnh web không thay thế số lượt ở cửa phòng.

## 1. Quyết định cần bằng chứng

**Business need:** sau khi hồ sơ thí sinh đã được xác định, hệ thống cần biết người đang đứng kiểm tra có phải đối tượng cần xác minh hay bằng chứng còn mơ hồ. Theo T-008 FR-006/FR-009 và RISK-001/002, không được biến mơ hồ thành xác minh thành công; quyền xử lý ngoại lệ phụ thuộc policy/người có thẩm quyền.

**Câu hỏi thử:** so với A0 (chỉ tiếp tục khi đúng một mặt), A1 (người/track ổn định trong vùng giao dịch, mơ hồ thì unresolved) hoặc A2 (liên kết hình học qua các frame, nếu có sequence) có tạo thêm **kết luận đúng mục tiêu** mà không tăng **kết luận sai mục tiêu** không? A2 chỉ được thử khi dữ liệu có chuỗi thời gian và đồng bộ giao dịch. Chưa coi A1/A2 là giải pháp được chọn.

## 2. Đơn vị dữ liệu và nhãn cần thu

| Thành phần | Cần có để kiểm S4 | Nếu thiếu thì kết luận nào không thể đưa ra |
|---|---|---|
| Transaction/attempt | Một lượt check-in giả lập hoặc được phép ghi nhận, kèm claim/hồ sơ được chọn, phiên/room ngữ cảnh và mốc bắt đầu–kết thúc quan sát | Không tính được tỷ lệ theo lượt hay thời gian chờ |
| Ảnh/sequence | Frame đầy đủ trong cửa sổ quan sát, timestamp, camera/điều kiện; giữ vùng có người xung quanh để kiểm distractor | Không kiểm được chọn người trong cảnh thật; crop một mặt chỉ kiểm E2 |
| Nhãn mục tiêu độc lập | Người mục tiêu nào trong frame/track, hoặc `không có mục tiêu`/`không xác định được` kèm lý do; annotator không dùng output A0–A2 làm ground truth | Không tính được wrong-target; coverage tăng có thể che sai người |
| Loại ca | Một người, nhiều người, mục tiêu ngoài khung/che khuất, đổi vị trí, lượt bị ngắt, không có người; tỷ lệ từng loại ghi riêng | Không biết candidate hoạt động ở trường hợp ngoại lệ nào |
| Điều kiện và quyền | Nguồn, quyền sử dụng/consent phù hợp, hạn lưu giữ và cách xử lý dữ liệu nhạy cảm | Không thể dùng dữ liệu cho phép thử hoặc chia sẻ bằng chứng |

Không đưa ảnh mặt, danh tính, bbox theo người hoặc embedding vào Git. Chỉ commit manifest **phi định danh**/số đếm tổng hợp khi quyền dùng và mức tiết lộ cho phép; dữ liệu thô theo [external-assets](../00-project/external-assets.md). Annotation cần ít nhất hướng dẫn gán nhãn, người kiểm độc lập và cách phân xử trường hợp bất đồng; số lượng/ngưỡng đồng thuận còn phải xác định trước locked test. Không gán “người đứng gần nhất/lớn nhất” làm ground truth.

## 3. Protocol phải khóa trước khi chạy

1. **Manifest và split:** liệt kê transaction có quyền dùng; tách dev/test theo người và, nếu có thể, ca/camera/sequence để tránh frame cùng lượt hoặc identity lọt hai phía. Báo phân bố ca một/nhiều/không có mục tiêu và đặc tính ảnh; không ép XQLFW thành dữ liệu S4 khi nó thiếu nhãn giao dịch.
2. **Đối chứng:** A0, A1 và A2 (nếu khả thi) nhận cùng transaction, frame window, detector output và điều kiện phần cứng. Pin cách xử lý trường hợp detector không cho box, nhiều box hoặc transaction gián đoạn. Không tune vùng, độ ổn định hay timeout trên test.
3. **Đầu ra ba nhánh trên mỗi transaction:** `correct-target`, `wrong-target`, `unresolved`. Với trường hợp ground truth `không có mục tiêu`, một lựa chọn bất kỳ là wrong-target; abstain là unresolved. Với ground truth `không xác định được`, báo riêng và không ép thành đúng/sai. Quy tắc chấm chi tiết phải được duyệt trước test.
4. **Metric và mẫu số:** tỷ lệ correct-target/wrong-target/unresolved trên toàn bộ transaction đủ nhãn và theo từng loại ca; latency p50/p95, số frame/thời gian chờ và tỷ lệ cần xử lý tiếp. Báo mẫu số, khoảng bất định phù hợp nhóm phụ thuộc theo người/sequence, và số ca bị loại cùng lý do. Chỉ khi có reference/claim và nhãn phù hợp mới đo thêm FMR/FNMR đầu-cuối S4→E2 với encoder/threshold khóa từ dev.
5. **Acceptance:** mục tiêu wrong-target, unresolved, thời gian và chi phí review phải xuất phát từ rủi ro nghiệp vụ/policy được nhóm duyệt **trước** test; hiện đều TBD. Nếu không có target, chỉ so sánh mô tả và giữ lựa chọn mở. Không chọn cách có coverage cao hơn nếu lỗi chọn sai chưa được kiểm.

## 4. Quyết định sẵn sàng hiện tại

| Điều kiện | Hiện trạng | Hệ quả |
|---|---|---|
| Nhãn người mục tiêu ở mức transaction | Chưa có trong T-011/XQLFW | **Chưa thể chấm X-012-A** hoặc khẳng định A1/A2 an toàn hơn A0 |
| Dữ liệu chuỗi và quyền dùng phù hợp | Chưa được ghi nhận | A2 chỉ là candidate có điều kiện; không tạo kết quả giả |
| Policy/authority và target chấp nhận | Generic T-008 là mốc tạm; giá trị kỳ thi chưa chốt | Có thể thiết kế protocol, chưa thể tuyên bố đạt yêu cầu triển khai |
| Baseline có thể giữ nguyên | A0/T-011 và số đếm E2 đã có | Có đối chứng để tránh đổi nhiều yếu tố cùng lúc |

**Bước thực hiện khi đủ dữ liệu:** lập manifest và hướng dẫn gán nhãn → kiểm quyền/nhãn và phân bố ca → khóa split/metric/target → chạy A0 trước trên cùng tập → chạy candidate khả thi → báo cả ba nhánh và lỗi theo ca → review evidence trước quyết định kỹ thuật. Nếu dữ liệu S4 không có, ghi rõ `not runnable`; tiếp tục E1/E2/E3/M1 trong đúng phạm vi riêng của chúng.
