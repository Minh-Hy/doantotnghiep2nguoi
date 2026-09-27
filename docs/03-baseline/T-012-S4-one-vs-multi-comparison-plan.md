# T-012 — Kế hoạch so sánh một mặt và nhiều mặt theo từng stage

**Ngày đặt kế hoạch:** 2026-09-27, sau các run T-011 và chẩn đoán T-012 đã công bố. **Trạng thái lúc đặt kế hoạch:** câu hỏi, dữ liệu và cách đo được ghi trước khi có điểm nhóm. **Run sau đó:** [36322220681](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36322220681) thành công; [báo cáo](runs/T-012-S4-widerface-one-multi.md). Chưa chọn model từ kết quả này. Chỉ dùng dữ liệu có sẵn, không thu ảnh/video mới.

## Vì sao phép so sánh này tồn tại

[D-001](../00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md) xác định mỗi thí sinh đưa mã để chọn hồ sơ, rồi hệ thống kiểm người đứng thực hiện lượt bằng xác minh 1:1. Trước cửa phòng có thể có nhiều người lọt vào khung hình. Vì thế [T-005/T-009](../02-survey/T-005-quoc-an-models.md) đặt S3 phát hiện mặt và S4 chọn/giữ đúng người trước S7–S8 xác minh. [T-011 E1](runs/T-011-E1-widerface-comparison.md) đã so ba detector trên toàn WIDER; [E2 coverage](runs/T-011-E2-coverage-diagnosis.md) thấy nhiều detection làm 1.399 cặp XQLFW ngoài rule một mặt. Hai kết quả chưa so ứng viên theo **điều kiện một mặt so với nhiều mặt có nhãn thật**. Đó là uncertainty dẫn tới kế hoạch này.

Câu hỏi chính: **thứ hạng và kiểu lỗi của các ứng viên thay đổi thế nào giữa ảnh một mặt và nhiều mặt, và phần nào của pipeline chịu trách nhiệm cho phần chưa kết luận?** Kết quả phải giải thích ưu/nhược của từng ứng viên theo stage, không cộng thành một accuracy hệ thống.

## So sánh khả thi với nguồn hiện có

| Nhánh | Dữ liệu và nhãn có thật | Giữ cố định / thay đổi | Đơn vị và số đo | Kết luận được phép |
|---|---|---|---|---|
| S3 detection | WIDER FACE validation và nhãn bbox đã kiểm ở T-011; chia ảnh theo **số valid GT**: một mặt (=1), nhiều mặt (≥2), 0 valid GT báo riêng. Ignored GT xử lý đúng evaluator E1. | Cùng archive/manifest, evaluator, IoU, score sweep, weight, wrapper và cấu hình E1; chỉ thay detector YuNet/SCRFD/BlazeFace. Không tune trên validation này. | Số ảnh, valid/ignored GT, project AP và recall cực đại **trong từng nhóm ảnh**; matched/missed GT theo kích cỡ mặt nếu đủ mẫu. Ghi số dự đoán và box bị clip/rỗng theo candidate khi có thể. | So chất lượng detector trên ảnh WIDER một/nhiều mặt. Nhóm theo GT là **phân tầng đánh giá**, không là thông tin cấp cho detector. Không suy chọn đúng thí sinh hoặc hiệu năng cửa phòng. |
| S4 coverage của pipeline E2 | XQLFW 6.000 cặp, nhãn genuine/impostor và số detection đã chẩn đoán ở T-011. | Giữ detector/alignment/rule một mặt và cùng cặp. Không đổi threshold encoder hồi tố. | Cặp dùng được/chưa kết luận theo 0/1/nhiều detection, mẫu số cặp và nguyên nhân giao nhau; FMR/FNMR chỉ trên cặp có score đúng protocol. | Giải thích coverage của pipeline XQLFW; **nhiều detection không đồng nghĩa nhiều người thật** hoặc biết mặt nào là người đưa mã. Không tính cặp chưa chấm thành false reject/check-in lỗi. |
| S4 giữ track — proxy | Nhãn bbox/ID LTFT S5 và [protocol P0/P1](T-012-S4-box-only-proxy-protocol.md) đã chạy. | Cùng 1.024 cửa sổ–ID và box khởi đầu do nhãn cấp; nếu làm phân tầng mới, đặt tiêu chí số box một/nhiều **trước run mới** và dùng cùng cửa sổ cho P0/P1. | Correct/wrong/unresolved, số cửa sổ từng trôi ID, số frame mất target ID; mẫu số theo nhóm nếu nhóm đó có dữ liệu. | Chỉ đo liên kết hình học sau khởi tạo oracle, không so detector/encoder và không chứng minh chọn đúng người khai báo. |
| S4→E2 theo lượt | Nguồn hiện đã rà **chưa kiểm đủ** nhãn nối mã/hồ sơ được khai báo với người mục tiêu trong cảnh. | [X-012-A](T-012-S4-experiment-readiness.md) giữ A0/A1/A2 và yêu cầu nhãn độc lập, split, cùng transaction/window trước locked test. | Correct-target/wrong-target/unresolved theo lượt, rồi FMR/FNMR đầu-cuối nếu reference/claim hợp lệ. | **Chưa chạy được phép chấm theo lượt**. Không tạo claim giả từ ID track/identity của dataset. |

## Runner và cổng kiểm trước khi xem điểm nhóm

[Scorer phân tầng](../../scripts/t012_widerface_one_multi.py) dùng lại `evaluate()` của T-011, chia ảnh theo **số valid GT** trước khi chấm; không dùng số detection của candidate để gán nhóm. [Workflow](../../.github/workflows/t012-e1-error-slices.yml) tải đúng archive/weight đã pin, tạo prediction trong thư mục tạm, kiểm lại E1 tổng, rồi mới chấm từng nhóm bằng cùng prediction đó. Mọi số đếm cộng được (ảnh, GT, TP/FP, neutral, prediction/drop/clip) phải đối chiếu đúng E1 tổng; AP từng nhóm được tính riêng, không cộng/trung bình để thay AP toàn tập. Nhóm 0 valid GT báo ảnh/FP/neutral, AP và recall là không xác định. [Kiểm tra synthetic](../../tests/test_t012_widerface_one_multi.py) kiểm phân nhóm và cổng đối chiếu trước run thật.

Workflow chỉ in số tổng hợp; ảnh, weight, prediction theo ảnh và JSON tạm không đưa lên Git. Run trên GitHub Actions là phép đo chất lượng detector trên WIDER, không là thời gian của thiết bị đích. Chưa điền kết quả trước khi run thành công.

## Thứ tự thực hiện và quy tắc đọc kết quả

1. **Kiểm manifest WIDER theo nhãn gốc** và báo số ảnh/GT của ba nhóm; xác nhận có đủ mẫu một mặt và nhiều mặt. Khóa mã phân tầng, config E1, metric và script trước khi xem điểm theo nhóm.
2. **Chạy lại prediction ba detector trên cùng ảnh** và dùng đúng evaluator T-010/T-011 cho từng nhóm ảnh. Báo AP/recall, mẫu số, điều kiện CPU/weight/commit và lệch tái lập nếu có. Đây là phân tích mới sau E1 tổng thể; không trình bày như đã được đăng ký trước run E1.
3. **Đặt cạnh nhau** coverage XQLFW và proxy LTFT như hai loại bằng chứng riêng. Nếu phân tầng LTFT mới, ghi quy tắc nhóm và mã trước khi xem bảng mới. Không cộng score WIDER, XQLFW, LTFT vào một thước đo.
4. **Diễn giải candidate:** candidate nào giữ recall/AP tốt hơn trong nhóm nhiều mặt, đổi lấy chi phí gì trong M1 tham chiếu; rule nào làm tăng coverage nhưng có nguy cơ chọn sai. Nếu kích cỡ mặt/độ khó khác nhiều giữa hai nhóm WIDER, nêu confounding và báo slice theo cỡ; không gọi chênh lệch là tác động nhân quả của đám đông.
5. Chỉ khi có dữ liệu **claim–actor theo lượt** hợp lệ mới so A0/A1/A2 về chọn đúng người và xác minh 1:1 đầu-cuối. Nếu không có, giữ giới hạn này và tiếp tục quyết định ở cấp component; không lấy proxy thay bằng chứng nghiệp vụ.

**Tiêu chí chấp nhận hiện tại:** phép so sánh phải dùng cùng dữ liệu/split/config trong mỗi nhánh, báo đủ mẫu số và ba outcome khi phù hợp, không tăng coverage bằng cách âm thầm chọn sai người. Mức FMR/FNMR, wrong-target, latency đạt nghiệp vụ chưa có nguồn kỳ thi nên để mở; kết quả nghiên cứu được dùng để giữ/loại candidate cho phép thử sau, chưa là quyết định triển khai.

## Kiểm tiếp sau run nhóm ảnh: giữ cố định cỡ mặt GT

Run 36322220681 cho thấy nhóm ảnh một mặt và nhiều mặt khác mạnh về phân bố cỡ mặt. Trước khi xem kết quả mới, khóa phép đếm chéo **nhóm ảnh theo số valid GT (đúng 1 / từ 2 trở lên) × cỡ bbox valid GT** theo bốn khoảng đã dùng ở T-012: `<16`, `16–<32`, `32–<96`, `≥96` px (căn bậc hai diện tích bbox trên ảnh gốc). Nhóm ảnh được xác định từ nhãn, không từ output của detector.

Trên cùng prediction, IoU `>0,5` và quy tắc matching E1, báo cho từng candidate và từng ô: **valid GT, matched GT, missed GT, recall cực đại = matched/valid**. Đối chiếu tổng từng ô với TP E1 và số GT/TP của hai nhóm ảnh trong báo cáo trước. Không tính AP theo ô vì việc lọc GT theo cỡ có thể đổi cách xử lý prediction trùng/ignored; phép này chỉ so recall trên các GT có cùng khoảng cỡ. Ưu tiên diễn giải `32–<96` và `≥96` vì nhóm một mặt chỉ có 5 GT `<16` và 26 GT `16–<32`; các ô nhỏ vẫn phải báo mẫu số, không coi thứ hạng ở đó là ổn định. Không tune model hoặc threshold từ bảng này.

Đây vẫn là so sánh mô tả S3 trên WIDER: giữ cỡ mặt theo khoảng **không** kiểm soát hết che khuất, góc nhìn, nền hoặc mật độ cảnh; không suy tác động nhân quả của nhiều người hay khả năng chọn đúng người đưa mã. Mã và định nghĩa ô phải được commit trước run chéo mới.
