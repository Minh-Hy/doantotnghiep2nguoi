# T-012 — Điều kiện chuẩn bị phép thử S4 chọn người mục tiêu

**Trạng thái:** kế hoạch nghiên cứu X-012-A, **chưa chạy experiment** và chưa chọn cách triển khai. Nguồn câu hỏi là [T-012 error analysis](T-012-error-analysis.md): E2 pair-fold chỉ chấm 4.215/6.000 cặp XQLFW; [phân tích ba nhánh](runs/T-012-E2-three-outcome-analysis.md) giữ 1.785 cặp còn lại ở `unresolved`. [Split danh tính custom](runs/T-011-E2-xqlfw-identity-disjoint.md) chấm 3.138 cặp trong 4.516 cặp đủ điều kiện chia nhóm trước detection; 1.484 impostor nối nhóm bị loại bởi thiết kế split, không thuộc unresolved của detector. Số cặp ảnh web không thay thế số lượt ở cửa phòng.

**Phạm vi được làm rõ:** luồng chính là một thí sinh khai báo hồ sơ rồi quét chính người đó để xác minh 1:1. Nhiều mặt trong vùng camera là ngoại lệ cần quét lại hoặc chuyển xử lý nếu không rõ người thực hiện lượt; không phải mục tiêu mặc định phải tự chọn người từ đám đông. X-012-A chỉ cần mở lại khi nhóm quyết định tự động kết luận trong ngoại lệ nhiều mặt. Thiếu dữ liệu cho X-012-A **không chặn** nghiên cứu E1/E2 hoặc xây nhánh `unresolved`/fallback của app.

## 1. Quyết định cần bằng chứng

**Business need:** sau khi hồ sơ thí sinh đã được xác định, hệ thống cần biết người đang đứng kiểm tra có phải đối tượng cần xác minh hay bằng chứng còn mơ hồ. Theo T-008 FR-006/FR-009 và RISK-001/002, không được biến mơ hồ thành xác minh thành công; quyền xử lý ngoại lệ phụ thuộc policy/người có thẩm quyền.

**Câu hỏi thử có điều kiện:** nếu nhóm muốn tăng tự động hóa ở cảnh nhiều mặt, so với A0 (chỉ tiếp tục khi đúng một mặt), A1 (người/track ổn định trong vùng giao dịch, mơ hồ thì unresolved) hoặc A2 (liên kết hình học qua các frame, nếu có sequence) có tạo thêm **kết luận đúng mục tiêu** mà không tăng **kết luận sai mục tiêu** không? A2 chỉ được thử khi dữ liệu có chuỗi thời gian và đồng bộ giao dịch. Chưa coi A1/A2 là giải pháp được chọn.

## 2. Đơn vị dữ liệu và nhãn cần có từ nguồn sẵn có

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
| Baseline có thể giữ nguyên | A0/T-011 và số đếm E2 pair-fold/custom split đã có, nhưng chưa có nhãn target ở mức transaction | Có đối chứng kỹ thuật để chuẩn bị; vẫn phải chạy A0 trên cùng tập transaction mới để so A1/A2 |

### Rà nguồn dữ liệu công khai cho S4 (27/09/2026)

[PLUSFiaQ, trang nhóm tác giả](https://www.wavelab.at/sources/plusfiaq/) mô tả 7 sequence, 12 người đi nhiều lượt qua một cổng, với bbox mặt, tracking ID và cờ `target class`. Đây là **ứng viên proxy cho tracking/chọn mặt trong hàng chờ**, gần hình học cửa vào hơn cặp ảnh XQLFW. Nhưng cờ `next at gate` được tác giả nói là chưa chỉnh/kiểm đầy đủ; trang tải yêu cầu thỏa thuận cấp quyền và hiện phần mẫu thỏa thuận ghi “coming soon”. Chưa có file, giấy phép cụ thể, mapping claim/hồ sơ sang từng lượt hoặc manifest transaction đã kiểm. **Không đưa PLUSFiaQ vào locked X-012-A ở trạng thái hiện tại.** Nếu sau này có quyền truy cập, phải kiểm annotation thực và định nghĩa lại đơn vị attempt cùng nhãn mục tiêu độc lập trước khi chấm.

[ChokePoint, trang tác giả](https://arma.sourceforge.net/chokepoint/) có raw frames, ground truth và license nghiên cứu phi thương mại; camera trên cổng cho phép kiểm miền hình ảnh. [Trang PLUSFiaQ](https://www.wavelab.at/sources/plusfiaq/) còn mô tả annotation bổ sung cho 6 sequence ChokePoint, gồm reflection được đánh dấu non-target. Tuy nhiên ChokePoint gốc là protocol face verification qua cổng; không có claim/roster gắn với từng attempt X-012-A. Chỉ dùng làm proxy S4 sau khi xác nhận có quyền dùng annotation bổ sung, map được target theo frame/track và dựng/kiểm nhãn transaction độc lập. Không lấy GT identity hoặc một người vừa qua cổng làm mặc định “người đã khai báo mã”.

[Audit nhãn gốc ChokePoint](T-012-S4-chokepoint-label-audit.md) đã kiểm archive thật: 72 XML, **không có S5**, và 0/176.916 frame XML có hơn một `person`. Vì vậy ngay cả phép thử proxy S4 nhiều người cũng chưa thể chạy bằng **gói nhãn gốc này**; nhãn S5 bổ sung là dependency riêng cần xác minh quyền và file.

**Nguồn mới đã kiểm:** [LTFT và audit file nhãn/video](T-012-S4-ltft-label-audit.md) công bố track/ID trên hai chuỗi ChokePoint S5 đông người. Hai file nhãn có 1.768/2.526 và 1.678/2.139 frame với ít nhất hai box `face=1`; bài báo nói box được tạo bằng detector rồi kiểm thủ công/gán ID. Tuy nhiên archive Zenodo mà LTFT dẫn tới chỉ có các đoạn `.1` của ba camera, tổng tên file 2.424/2.271 frame, không khớp hướng dẫn ghép `.2 → .1 → .3` hay header nhãn 2.526/2.139. **Chưa có mapping frame–nhãn có thể kiểm, nên chưa chạy proxy có ảnh.** Nguồn cũng không có claim–actor hoặc lượt check-in. File nhãn công khai nhưng không có giấy phép rõ để tái phân phối.

[Protocol box-only LTFT](T-012-S4-box-only-proxy-protocol.md) chỉ dùng chuỗi bbox/ID annotation để kiểm association hình học, không cần video đang lệch. [Run thăm dò](runs/T-012-S4-ltft-box-proxy.md) trên 495/529 cửa sổ–ID của Choke1/Choke2 ghi P0 đúng/sai/unresolved `446/143/435`, P1 `758/38/228` trên cùng 1.024 trường hợp. Đây là kết quả **box oracle**, không chấm A1 dựa trên vùng giao dịch, detector hay nghiệp vụ claim–actor, và không chọn P1 làm rule app.

[D1 đường đi P1](runs/T-012-S4-ltft-path-diagnostic.md) bổ sung rằng 41 cửa sổ từng chọn sai ID ở frame giữa, so với 38 sai endpoint. Lần sai đầu luôn trùng với frame không có box target `face=1` trong annotation, **không đồng nghĩa target rời khung**. Đây là câu hỏi về giữ `unresolved` khi mất dấu cần chấm trên nguồn có nhãn phù hợp hơn; không lấy ground truth ID làm tín hiệu runtime.

[D2 audit nhãn thô](runs/T-012-S4-ltft-faceflag-audit.md) thấy cả 41 frame sai đầu đều không có target ID trong dòng gốc; không ca nào chỉ bị loại do `face=0`. Audit này không bổ sung claim–actor, video ghép frame hay tín hiệu runtime để chạy X-012-A.

**Nguồn đối chiếu bị hoãn cho S4:** [MEVID của Kitware](https://github.com/Kitware/MEVID) có ảnh `actor check-in` và ID cho các tracklet, nhưng theo README đây là dataset **person re-identification**: các bbox phát hành là ảnh chip người theo tracklet, metadata công bố gồm vị trí track, person/outfit/camera ID; ảnh check-in phục vụ liên kết actor với ID. Không có nhãn face box của mọi người trong cùng frame hoặc sự kiện một thí sinh chọn hồ sơ tại cửa phòng. Tên `check-in photos` **không được đọc thành attempt/check-in nghiệp vụ T-008**. Kho video 127 GB và ảnh tham chiếu 600 MB cũng cần chuẩn bị riêng; không tải nguồn này cho X-012-A khi chưa có protocol chứng minh nhãn cần thiết. Có thể nghiên cứu MEVID riêng cho person ReID, nhưng không lấy nó để lấp nhãn claim–actor S4.

**Sàng lọc thêm IJB-S (27/09, chỉ đọc nguồn):** [bài báo của nhóm tạo bộ dữ liệu](https://biometrics.cse.msu.edu/Publications/Face/Kalkaetal_IJBSIARPPAJanusSurveillanceVideoBenchmark_BTAS2018.pdf) mô tả video giám sát của 202 danh tính, nhãn bbox/identity và các giao thức detection, nhận dạng open-set 1:N từ video sang gallery. Đây có thể là nguồn cho câu hỏi detection/identification trong miền giám sát, nhưng giao thức công bố **không định nghĩa một lượt người tự khai báo hồ sơ và nhãn độc lập chỉ ai trong cảnh là người khai báo**. Chưa kiểm file thực tế, quyền truy cập/điều khoản, độ phủ cảnh nhiều mặt hoặc mapping theo attempt. Vì vậy **không đưa IJB-S vào X-012-A ở thời điểm này** và không chuyển gallery identity thành claim giả để tạo nhãn đúng người.

Các nguồn trên **chưa giải quyết điều kiện chạy X-012-A nghiệp vụ**. Tập cuối cần có claim theo transaction, người mục tiêu/không có mục tiêu trong khung, distractor, thời gian quan sát và quyền sử dụng rõ. Quốc An đã chốt **chỉ dùng dữ liệu có sẵn, không thu mới**; nếu nguồn hiện có chỉ cung cấp tracking/face ID thì chỉ chạy proxy với protocol/nhãn độc lập phù hợp, báo riêng và không suy hiệu năng tại phòng thi. Nếu không tìm được nguồn có claim–actor, X-012-A nghiệp vụ giữ `not runnable` trong phạm vi này.

**Điểm dừng nghiên cứu hiện tại (27/09):** trong các nguồn đã rà — XQLFW, ChokePoint gốc/S5, LTFT, PLUSFiaQ và MEVID — chưa có bộ **đã kiểm được** đồng thời cung cấp claim–actor theo lượt và nhãn nhiều người phù hợp để chấm X-012-A. Đây không phải tuyên bố rằng mọi dataset công khai đều thiếu; chỉ là giới hạn evidence hiện có. Phần độc lập khả thi bằng annotation LTFT đã hoàn tất ở [proxy box-only](runs/T-012-S4-ltft-box-proxy.md). Không lặp phép thử proxy để thay thế câu hỏi nghiệp vụ; mở lại X-012-A chỉ khi tìm được nguồn sẵn có đáp ứng [hợp đồng nhãn](T-012-X-012-A-label-contract.md) và quyền dùng.

**Bước thực hiện khi đủ dữ liệu:** lập manifest và hướng dẫn gán nhãn → kiểm quyền/nhãn và phân bố ca → khóa split/metric/target → chạy A0 trước trên cùng tập → chạy candidate khả thi → báo cả ba nhánh và lỗi theo ca → review evidence trước quyết định kỹ thuật. Nếu dữ liệu S4 không có, ghi rõ `not runnable`; tiếp tục E1/E2/E3/M1 trong đúng phạm vi riêng của chúng.

[Hợp đồng nhãn X-012-A](T-012-X-012-A-label-contract.md) định nghĩa tối thiểu claim–actor–target, các trạng thái `visible / absent-from-window / undeterminable`, đơn vị attempt, mẫu số và cổng chạy; phần cuối tách phép thử proxy LTFT. Đây là chuẩn bị để nhóm kiểm dữ liệu trước thí nghiệm, không phải manifest đã có hoặc run S4.
