# Giai đoạn 02 — khảo sát kỹ thuật

Hai thành viên đã khảo sát độc lập. Nhóm chọn bối cảnh cửa phòng thi của T-002 ở [D-001](../00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md); T-007 chọn bộ khảo sát T-005 của Quốc An làm hướng nghiên cứu theo [D-002](../00-project/decisions/T-007-D-002-chon-huong-khao-sat-t005.md). [Bản so sánh](T-007-selection.md) giải thích vì sao hướng T-006 của Minh Hy không được dùng nguyên dạng cho bài toán 1:1. Việc chọn hướng khảo sát chưa chốt dataset/model/cấu hình cuối.

[Logic quyết định của phase 02](DECISION_LOGIC.md) nối yêu cầu nghiệp vụ, stage, candidate và câu hỏi thí nghiệm; các file dưới đây chứa khảo sát chi tiết.

## Bộ tài liệu T-005 của Quốc An

Đọc theo thứ tự suy luận, không bắt đầu bằng tên dataset/model:

1. [Phân rã bài toán và phân loại task](T-005-quoc-an-task-decomposition.md): nghiệp vụ, xác minh 1:1, product/runtime pipeline, ML so với rule/database, giao diện và trường hợp lỗi.
2. [Yêu cầu và khảo sát dataset theo task](T-005-quoc-an-datasets.md): annotation, vai trò train/dev/test/external, candidate space, quyền và khoảng trống nhãn người mục tiêu.
3. [Yêu cầu và khảo sát phương pháp/model theo task](T-005-quoc-an-models.md): family → candidate → lọc → shortlist có điều kiện, phân biệt architecture/loss/weight/pipeline.
4. [Thiết kế benchmark và cổng quyết định tối ưu](T-005-quoc-an-experiments.md): metric từng task, baseline plan, phân tích lỗi/bottleneck, quyết định optimization sau baseline, ablation và điều kiện chọn pipeline cuối.

Các tài liệu trên **thay cho** bản khảo sát một file trước đây. Chúng là thiết kế nghiên cứu: chưa có final dataset/model/pipeline/optimization, chưa tải/kiểm tra trọn bộ dữ liệu, chưa chạy benchmark. Candidate shortlist giúp tạo phép thử; không phải kết quả đánh giá. PAD là task bổ trợ riêng; nghiệp vụ phòng/ca/giờ và ghi nhận là phần mềm có test riêng.

## T-009 — Audit khả dụng trước thí nghiệm

[T-009: kiểm tra dataset và trọng số ứng viên](T-009-candidate-audit.md) ghi nguồn, quyền được công bố, mức kiểm file/runtime thực tế và khoảng trống còn lại. Một số weight đã mở/chạy với đầu vào tổng hợp; dataset ảnh chưa được tải/parse đầy đủ. [Sổ nguồn T-009](T-009-source-register.md) ghi link, mục/trang nguồn và lý do giữ, hoãn hoặc cần điều kiện để tái sử dụng khi viết báo cáo. Tài liệu audit lọc **candidate để chuẩn bị thí nghiệm**, chưa chọn dataset/model cuối hoặc báo performance. T-008 đang được review ở [PR riêng](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3), nên mapping nghiệp vụ cần kiểm lại khi baseline ổn định.

## Cổng chuyển sang thực nghiệm sau T-007

Trước khi chạy, xác minh quyền dùng và phiên bản file/weight; chốt protocol, manifest cặp/lượt, tách dev/test theo identity hoặc phiên phù hợp, thiết bị đo, metric chính và operating point. Chạy baseline trước, phân tích lỗi có nhãn rồi mới chọn bottleneck và phương pháp tối ưu. Nếu làm nhiều can thiệp, có ablation đơn lẻ và kết hợp; so với chính baseline gốc lẫn pipeline mạnh khác. Chỉ chốt pipeline cuối khi có bằng chứng trên cùng dữ liệu/split/điều kiện đo.

Bộ khảo sát T-006 của Minh Hy vẫn là nguồn đối chiếu độc lập. T-007 đã chọn **hướng T-005** làm cơ sở thử nghiệm, nhưng shortlist trong T-005 vẫn chỉ là candidate có điều kiện; quyết định kỹ thuật cuối đợi kết quả baseline và experiment.
