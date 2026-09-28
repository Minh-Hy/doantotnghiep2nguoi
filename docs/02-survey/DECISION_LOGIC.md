# Logic quyết định — 02: Khảo sát kỹ thuật

File này là **xương sống suy luận** của bộ T-005: vì sao một stage, yêu cầu dữ liệu, family, candidate và thí nghiệm xuất hiện. Chi tiết cùng nguồn gốc nằm ở [phân rã task](T-005-quoc-an-task-decomposition.md), [dataset](T-005-quoc-an-datasets.md), [model/phương pháp](T-005-quoc-an-models.md) và [thiết kế thí nghiệm](T-005-quoc-an-experiments.md). T-005 là khảo sát cá nhân của Quốc An; T-006 độc lập. [D-002](../00-project/decisions/T-007-D-002-chon-huong-khao-sat-t005.md) ghi T-007 chọn T-005 làm hướng nghiên cứu của nhóm, nhưng các candidate kỹ thuật vẫn chờ thí nghiệm.

## 1. Business problem → stage requirements

Đầu vào là BP-01 và UC-01–UC-03 trong [logic phase 01](../01-problem/DECISION_LOGIC.md): một người khai báo mã ở cửa, thiết bị cần kiểm tra người này có khớp hồ sơ và được vào đúng phòng/ca/giờ không, rồi ghi nhận hoặc chuyển ngoại lệ. Vì **mã chỉ chọn hồ sơ**, S7–S8a cần tạo và so bằng chứng khuôn mặt 1:1; 1:N không phải luồng T-002 đang khảo sát.

- **S0–S1, dữ liệu đầu vào:** danh sách/ảnh/mã/phiên → kiểm tra rồi lấy đúng một hồ sơ hoặc báo lỗi. S8a cần ảnh tham chiếu; S9 cần phòng/ca/giờ. Đây là validation/query, không cần model nhận diện thí sinh.
- **S2–S4, đúng người trước camera:** camera → frame → mọi bbox/landmark → mặt của người vừa khai báo hoặc trạng thái ambiguous. S5–S8a chỉ có ý nghĩa nếu crop thuộc đúng người; vì hành lang có người nền, không mặc định chọn mặt to/rõ nhất. S2 là camera API; S3 là detection/localization có thể cần model; S4 ưu tiên ROI/rule/track bảo thủ và chỉ khảo sát model tracking nếu có dữ liệu cùng lỗi thực tế.
- **S5–S6, ảnh dùng được:** mặt mục tiêu → kiểm tra chất lượng, landmark và phép căn chỉnh → crop phù hợp encoder hoặc retry. Lỗi đầu vào có thể gây false reject ở S8b, nên cần đo ảnh hưởng đầu-cuối trước khi thêm quality model/landmark model.
- **S7–S8b, bằng chứng rồi quyết định:** hai crop → embedding → điểm tương đồng → match, non-match hoặc uncertain. Encoder có thể là ML; phép so điểm và threshold/policy không tự là model mới. False accept và false reject có hậu quả khác nhau; threshold cần hiệu chỉnh trên dev và kiểm chứng trên test.
- **S9–S10, quyết định nghiệp vụ:** kết quả mặt + roster/ca/giờ/trạng thái trước → hợp lệ, sai phòng, muộn, trùng, retry/manual và audit. Đây là rule/database/transaction; không dùng model để suy ra quy định. “Chưa đến” phát sinh ở bước đối soát sau ca.
- **S11, PAD tùy chọn:** nghi ảnh/video giả là bài toán khác verification; chỉ thêm protocol, dữ liệu và model riêng nếu phạm vi/rủi ro yêu cầu. Không suy “người thật” từ similarity cao.

**Requirement chung chưa định lượng:** độ trễ mỗi lượt, thiết bị đích, compute/RAM, mức FMR/FNMR, tỷ lệ retry/manual, điều kiện ánh sáng/góc/khoảng cách và mức tự động hóa theo quy chế. Chúng phải được đo/chốt với nguồn; chưa dùng số tự đặt để loại candidate.

## 2. Stage requirements → data requirements → dataset survey

**Vì sao dữ liệu khác nhau theo stage:** S3 cần ảnh nguyên khung với bbox/landmark; S4 cần nhãn người **đã khai báo mã** giữa nhiều mặt; S5–S6 cần nhãn chất lượng/landmark hoặc phép đo tác động lên verification; S7 cần identity đa dạng nếu train/fine-tune; S8a–S8b cần ảnh reference/probe khác lần thu cùng genuine/impostor claims; S9–S10 chỉ cần fixture nghiệp vụ và expected state. Annotation của stage này không tự chứng minh stage khác.

[Khảo sát dataset](T-005-quoc-an-datasets.md) đi theo thứ tự **task → annotation/identity/split/domain/license criteria → candidate → so sánh vai trò → shortlist để kiểm tra khả dụng**. WIDER FACE phục vụ câu hỏi detection; LFW chỉ smoke verification; XQLFW, YouTube Faces và ChokePoint kiểm tra các điều kiện khác nhau. Các tên này là candidate khảo sát, **chưa là final dataset**. Dataset ảnh đã crop không đo S3/S4; dataset nhiều bbox không cho biết người nào vừa khai báo mã. T-005 chưa tìm được tập công khai đủ claim + target label cho cảnh nhiều mặt ở cửa, nên phần đó chỉ có thể kiểm thử rule bằng fixture và ghi giới hạn, không tuyên bố đã giải quyết hành lang đông.

**Ranh giới dữ liệu hiện tại của T-002/T-005:** nghiên cứu thị giác bằng dataset công khai; logic phòng thi bằng hồ sơ giả lập. Nếu domain gap ảnh hưởng kết luận, phải báo rõ và đề xuất phép đánh giá domain-specific khi có quyền/dữ liệu về sau; không mặc nhiên thu ảnh thí sinh thật hoặc gọi demo là pilot.

## 3. Problem type → model requirements → family → candidate to experiment

[Khảo sát model](T-005-quoc-an-models.md) dùng hard gate về đầu ra đúng stage, trọng số/nguồn/quyền, preprocessing và khả năng chạy; sau đó so chất lượng, độ trễ, kích thước, compute và khả năng triển khai. Không lấy benchmark ở protocol khác để chọn model thắng cho dự án.

- **S3 face detection:** cần bbox mọi mặt và landmark tương thích S6. Do đó survey các family face-specific có keypoint, từ mobile-native/nhẹ tới mức compute cao hơn. MediaPipe, YuNet và SCRFD nhẹ là **đại diện có điều kiện để benchmark**; chưa quyết định detector triển khai.
- **S4/S5/S6:** vì rule ROI, kiểm tra ảnh và geometric alignment có thể đáp ứng output, chúng là đối chứng đầu tiên. Learned tracking/quality/landmark chỉ đáng thử nếu có nhãn phù hợp và lỗi baseline cho thấy lợi ích đáng giá.
- **S7 embedding:** cần biểu diễn vẫn so được identity chưa thấy khi train, không phải classifier cố định cho từng thí sinh. MobileFaceNet, EdgeFace, AdaFace R18 và R50 face encoder là candidate khác vai trò về tài nguyên/chất lượng để lọc tiếp; tên architecture/loss chưa đủ, phải pin weight, dữ liệu train, preprocessing và quyền.
- **S8a/S8b:** similarity và ngưỡng trên development set là đối chứng. Một hay hai ngưỡng là candidate policy; phải đo cả lỗi lẫn tỷ lệ retry/manual. S9/S10 không có model candidate.

**Survey decision hiện có:** T-007 chọn hướng T-005 vì khớp bài toán cửa phòng thi 1:1 ([bản so sánh](T-007-selection.md)). Shortlist trong T-005 là candidate *đáng thử*, có điều kiện kiểm tra file/weight, license, schema, protocol và runtime; chưa chốt dataset/model/pipeline cuối và không được biện minh ngược bằng kết quả thí nghiệm tương lai.

**T-009 kiểm tra bước kế tiếp vì shortlist chưa đủ để chạy:** [audit nguồn, dữ liệu và trọng số](T-009-candidate-audit.md) đối chiếu nguồn chính thức và chạy thử một số weight trên đầu vào tổng hợp. YuNet, BlazeFace, SCRFD-500MF và MobileFaceNet trong `buffalo_sc` đã qua kiểm tra file/runtime tối thiểu trên máy hiện tại; các dataset ảnh chưa kiểm đầy đủ file/nhãn; quyền đã đối chiếu được một phần theo từng nguồn, XQLFW được tác giả công bố để đánh giá học thuật, còn điều khoản phân phối lại ảnh chưa rõ. T-010/PR #6 kiểm thêm archive/path XQLFW nhưng chưa xác nhận quyền phân phối lại ảnh hoặc chọn main test. Vì vậy quyết định T-009 chỉ là **ứng viên đủ cơ sở để chuẩn bị phép thử có điều kiện**. Nó không thay quyết định chọn main test, protocol, model thắng hoặc configuration triển khai. T-008 ở [PR riêng đang review](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3); nếu baseline nghiệp vụ đổi, đối chiếu lại mapping trước khi khóa thí nghiệm.

## 4. Survey uncertainty → experiment → final technical decision

[Thiết kế thí nghiệm](T-005-quoc-an-experiments.md) phát sinh từ những điểm còn chưa chắc:

1. **B0, khả dụng:** candidate có nguồn, quyền, input/output và runtime thật không? Bước này lọc trước benchmark, không dựa test score.
2. **B1, detection:** detector nào tạo bbox/landmark đủ tốt ở chi phí chấp nhận được, và lỗi của nó tác động ra sao tới verification khi giữ encoder cố định?
3. **B2, embedding:** encoder nào phân tách genuine/impostor tốt trên cùng cặp reference/probe và crop phù hợp, khi giữ detector/điều kiện đo tương đương?
4. **B3, policy:** threshold, vùng uncertain hoặc quality rule thay đổi FMR/FNMR, retry/manual và thời gian ra sao khi pipeline khác giữ cố định?
5. **B4, đầu-cuối có điều kiện:** vài tổ hợp có lý do từ B1–B3 xử lý lượt kiểm tra thế nào; dataset nào đủ nhãn để đo từng stage hoặc toàn giao dịch?

Với mỗi phép thử phải có **question/hypothesis → variables → controlled conditions → dataset/split → metrics và lý do → acceptance criteria trước test → result → interpretation → decision**. Cùng dữ liệu/split/protocol/thiết bị cho so sánh trực tiếp; dev chọn cấu hình, locked test để kết luận. Nếu thiếu nhãn, chỉ báo metric của stage đo được. Sau baseline và error analysis mới chọn bottleneck, search space/objective/thuật toán tối ưu; ablation tách tác động khi đổi nhiều thứ. **Chưa có run nên final technical decision vẫn mở.**

**Vì sao bước sau tồn tại:** 03/04 chỉ mở khi candidate, protocol và câu hỏi kiểm chứng đã đủ cụ thể; 05 tổng hợp kết quả để chốt kỹ thuật trong điều kiện project; 06 triển khai cấu hình đã kiểm chứng. Khi bắt đầu từng phase, tạo DECISION_LOGIC.md tại đó và nối lại ID/nguồn/run tương ứng, không tạo trước file rỗng.
