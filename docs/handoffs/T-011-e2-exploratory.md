# Bàn giao T-011 — run E2 thăm dò, các nhánh khác còn mở

- **Người thực hiện/ngày:** Codex theo yêu cầu Quốc An, 2026-09-26; Minh Hy là người review theo Sheet.
- **Nguồn đầu vào:** Quốc An cho phép dùng T-008 làm baseline tạm để tiếp tục; PR #3 thực tế vẫn có review CHANGES_REQUESTED của Hy. Xem [rà soát đầu vào](../03-baseline/T-011-readiness-review.md). T-009 PR #5 và T-010 PR #6 chưa merge vào main.
- **Đầu ra:** [run E2 XQLFW/MobileFaceNet](../03-baseline/runs/T-011-E2-xqlfw-mbf.md), mã scripts/t011_xqlfw_baseline.py và ba unit test trong tests/test_t011_protocol.py. T-011 chưa hoàn tất toàn bộ E1/E2/E3/M1.
- **Cách kiểm:** dùng Python 3.12.2 với InsightFace 0.7.3, OpenCV runtime 5.0.0, ONNX Runtime 1.20.1 CPU, NumPy 2.2.6 và scikit-learn 1.7.1. Chạy unittest discover trên tests/test_t011_protocol.py (3 test qua); chạy script với XQLFW ZIP, pairs TXT và buffalo_sc ZIP có hash trong run doc. Script xuất JSON tổng hợp vào artifacts, không xuất tên/ảnh/embedding.
- **Kết quả:** 7.263 ảnh được tham chiếu, 6.064 ảnh tạo embedding đúng một mặt; 4.215/6.000 cặp hợp lệ; FMR 133/2.169 = 6,13%, FNMR 125/2.046 = 6,11% tại threshold chọn trên 9 fold khác. Đây là phép thử pair-fold học thuật, không có identity-disjoint hoặc kết quả cửa phòng thi.
- **Việc tiếp theo:** T-012 phân tích 908 ảnh detector báo nhiều mặt và 291 ảnh không phát hiện để đặt giả thuyết coverage; kiểm một encoder khác trên cùng protocol; tìm main test phù hợp hơn. E1 cần archive/nhãn detection; E3 cần giải quyết ý review T-008 và implementation; M1 cần điều kiện đo kiểm soát. Không chốt model/threshold cuối từ run này.
- **File ngoài Git:** XQLFW ZIP/pairs, buffalo_sc ZIP, ONNX giải nén và JSON run ở máy chạy; nguồn và hash trong [external-assets](../00-project/external-assets.md). Chưa gửi trực tiếp cho Minh Hy; tải lại từ nguồn công khai và đối chiếu hash.
- **Commit/PR:** [commit mã run 03c68d6](https://github.com/quocanwyf/doantotnghiep2nguoi/commit/03c68d6d358aa09d4bfbd30a5c0641ad9358a0b2); [draft PR #7](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/7). Không merge khi các giới hạn trên chưa được nhóm hiểu rõ.

## Bổ sung chẩn đoán coverage (2026-09-26)

[Phân tích hậu nghiệm](../03-baseline/runs/T-011-E2-coverage-diagnosis.md) và script scripts/t011_xqlfw_coverage.py xác nhận 1.399/1.785 cặp bị loại có ít nhất một ảnh nhiều mặt. Chạy cùng ZIP/hash và cấu hình detector; JSON tổng hợp nằm ngoài Git ở artifacts/t011-xqlfw-coverage.json. Chưa có nhãn để biết box nào là người mục tiêu, nên chưa đổi rule chọn mặt hoặc kết quả E2 gốc.

## Bổ sung đối chứng R50 (2026-09-27)

[Run E2 đối chứng](../03-baseline/runs/T-011-E2-xqlfw-mbf-vs-r50.md) dùng cùng 4.215 cặp hợp lệ, detector và pair-fold: MobileFaceNet tái lập đúng run gốc (FMR 133/2.169; FNMR 125/2.046), R50 có FMR 76/2.169 và FNMR 74/2.046. R50 được giữ làm ứng viên cho phép đo tiếp, chưa là model cuối do dữ liệu khác miền, coverage 70,25%, fold trùng identity và chưa đo chi phí trên thiết bị đích. Runner chunked ở scripts/t011_xqlfw_r50_comparison.py; buffalo_l.zip ngoài Git có hash trong external-assets. JSON aggregate cục bộ ở artifacts; checkpoint embedding tạm đã xóa sau kiểm tra.

## Bổ sung cổng dữ liệu E1 (2026-09-27)

[WIDER FACE validation data gate](../03-baseline/T-011-E1-widerface-data-gate.md) kiểm archive CUHK-CSE và annotation: 3.226 ảnh/nhãn khớp, 39.708 bbox, 0 ảnh lỗi giải mã; 585 nhãn invalid và 11 bbox kích thước không dương cần quy tắc ignore/chấm được khóa. Nguồn, byte, hash ở external-assets A-004. Chưa có AP/recall hoặc quyết định detector; E1 cần evaluator/adapter cùng manifest trước run.

## Bổ sung đối chiếu và chuẩn bị run (2026-09-27)

[Bảng trace T-008→T-011](../03-baseline/T-011-T008-T009-T010-trace-review.md) dùng nội dung T-008 PR #3 commit `c235b80` làm mốc theo chỉ đạo Quốc An, không sửa T-008. T-010 đã thêm [quy tắc chấm E1](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E1-scoring-protocol.md) và [catalog fixture E3](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-010-experiment-protocol/docs/03-baseline/T-010-E3-fixture-contract.md). T-011 chưa có AP/recall detector hay pass/fail workflow E3. Môi trường tiến trình cục bộ đang trả lỗi `helper_unknown_error: setup refresh had errors`, nên chưa thể preflight evaluator/wrapper hoặc chạy run E1; ghi giới hạn này thay vì tự điền kết quả.

## Bổ sung mã E1 và kiểm thử tổng hợp (2026-09-27)

- [Evaluator](../03-baseline/T-011-E1-widerface-data-gate.md) tại scripts/t011_widerface_evaluate.py kiểm SHA/ZIP/manifest/GT, có `--preflight-only`, chấm AP nội bộ đúng T-010 và chỉ xuất summary tổng hợp. [Prediction runner](../../scripts/t011_widerface_predict.py) có adapter YuNet, BlazeFace, SCRFD với config v1; file raw prediction phải nằm trong `artifacts/` hoặc ngoài Git.
- Test mới: tests/test_t011_widerface_evaluator.py và tests/test_t011_widerface_predict_adapter.py (box tổng hợp). [GitHub Actions run 36293858671](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36293858671) chạy Python 3.12: **10/10 test đạt**. Chúng kiểm logic synthetic, không load WIDER ảnh thật hoặc weight. Môi trường cục bộ vẫn không mở được tiến trình, nên chưa có GT/model preflight, AP, recall hay latency detector. [Run 36293972494](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36293972494) xác nhận workflow checkout/setup-python v7 vẫn đạt **10/10 test**.
- Khi môi trường phục hồi: GT preflight → từng adapter preflight → full prediction cho cả 3 candidate → cùng evaluator → report run có hash/config/thiết bị/giới hạn. Nếu GT ngoài biên hoặc adapter lỗi, dừng và sửa protocol bằng revision trước khi xem AP.

## Bổ sung GT/image preflight trên WIDER thật (2026-09-27)

[GitHub Actions run 36294105147](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294105147) tải WIDER validation và annotation đúng SHA-256 vào bộ nhớ tạm, chạy evaluator `--preflight-only` với Python 3.12.14, NumPy 2.2.6 và OpenCV headless 5.0.0.93. Kết quả: 3.226 ảnh, 39.708 dòng box, 39.112 valid GT, 585 ignored GT, 11 dòng box không dương, **0 GT ngoài biên ảnh**; hash/CRC/manifest/giải mã qua. Workflow không lưu ảnh hoặc nhãn thô thành artifact. Đây chỉ là cổng dữ liệu; preflight của YuNet/BlazeFace/SCRFD và AP/recall/latency E1 chưa chạy.

## Bổ sung preflight ba detector (2026-09-27)

[Run 36294608464](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294608464) chạy qua GT/image gate và API/coordinate preflight trên cùng 8 ảnh đầu manifest: YuNet 10.419 box, BlazeFace full-range 2.126 box, SCRFD-500MF 20.866 box ở cấu hình score thấp đã đặt trước. Tất cả weight được đối chiếu SHA-256; số box chỉ xác nhận adapter chạy và cảnh báo dung lượng output, **không phải AP/recall hay căn cứ chọn model**. Run 36294478001 đã phát hiện hash nội bộ `det_500m.onnx` bị chép sai một ký tự dù `buffalo_sc.zip` đúng hash; T-010 và T-011 đã đính chính trước khi chấm. Chưa chạy full 3.226 ảnh; cần thống nhất một gói OpenCV, kiểm chi phí lưu/chấm prediction lớn và report điều kiện đo.

## Bổ sung run YuNet toàn WIDER và việc tiếp theo (2026-09-27)

Các mục trên ghi trạng thái tại thời điểm viết; mốc mới nhất là [run E1 YuNet 36294898744](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294898744), được phân tích trong [run report](../03-baseline/runs/T-011-E1-widerface-yunet.md). Trên 3.226 ảnh, project AP tại IoU > 0,5 = 0,6483041468, recall cực đại = 0,7394661485 (39.112 valid GT). Prediction và summary chỉ ở bộ nhớ tạm GitHub runner, đã xóa cuối job. Đây chưa là điểm WIDER chính thức hay quyết định detector. Đã chuẩn bị workflow riêng để chạy BlazeFace và SCRFD trên cùng manifest/evaluator; hai kết quả này chưa có. Giữ PR #7 ở draft đến khi so sánh có đủ phạm vi và giới hạn.

## Bổ sung E1 ba detector toàn WIDER (2026-09-27)

Mục trước là trạng thái lịch sử. [Báo cáo đối chiếu E1](../03-baseline/runs/T-011-E1-widerface-comparison.md) hiện ghi đủ ba run theo cùng 3.226 ảnh, 39.112 valid GT và evaluator đã pin: YuNet AP 0,648304/recall 0,739466; SCRFD-500MF AP 0,547370/recall 0,634179; BlazeFace full-range AP 0,136009/recall 0,180584. [Run YuNet](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36294898744), [BlazeFace](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36296108522/job/108555142384), [SCRFD](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36296357372/job/108555827946) là nguồn log tổng hợp. Workflow đầu tiên cho SCRFD lỗi tên file ONNX trước inference; workflow sau sửa tên file, giữ nguyên hash weight/config/evaluator và chạy thành công. Prediction/summary thô chỉ ở `RUNNER_TEMP`, được xóa sau job.

**Giới hạn và bước tiếp:** AP là metric detection nội bộ, không phải WIDER benchmark chính thức; WIDER khác miền camera cửa phòng. Các thời gian trên GitHub runner không đủ điều kiện so latency hoặc chi phí thiết bị đích. T-012 cần phân tích lỗi box clipped/rỗng, khác biệt theo điều kiện ảnh, ảnh hưởng S4/E2 và đặt thí nghiệm domain-specific; E3 còn phụ thuộc policy/authority từ T-008, M1 còn cần profile thiết bị. T-011/PR #7 vẫn draft, chưa có final model/threshold.

## Bổ sung M1 tham chiếu trên cùng runner (2026-09-27)

Quốc An xác nhận T-009/T-010 đã hoàn tất phạm vi audit/protocol để T-011 tiếp tục; góp ý nghiệp vụ chi tiết của T-008 được để cho giai đoạn xây app, không chặn phép đo component hiện tại. [Protocol M1 tham chiếu](../03-baseline/T-011-M1-reference-protocol.md), script `scripts/t011_m1_reference_detection.py` và workflow `.github/workflows/t011-m1-reference.yml` đo ba detector trên cùng 60 ảnh WIDER đã giải mã, ba vòng/mỗi candidate, trong một CPU runner. Cách chọn ảnh, warm-up, phạm vi thời gian và điều kiện diễn giải được ghi **trước khi chạy**. Kiểm Python compile, chọn mẫu 60 vị trí duy nhất và `git diff --check` đã qua.

[Run M1 36305640667](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36305640667) thành công; [báo cáo](../03-baseline/runs/T-011-M1-reference-detection.md) ghi median/p95 `adapter.detect`: YuNet 25,72/48,81 ms, BlazeFace 13,26/33,95 ms, SCRFD 83,24/165,81 ms trong cùng job CPU với 180 calls/candidate. Đây là số tham chiếu component, chưa đo target device, RAM riêng từng model, S4/E2/E3 đầu-cuối hoặc công sức check-in. Lần `workflow_dispatch` đầu tiên trả 404 vì workflow mới chưa ở default branch; thêm trigger `push` trên nhánh T-011 rồi chạy thành công. Không thay protocol sau khi xem số.

## Bổ sung kiểm split tách danh tính E2 (2026-09-27)

[Audit trước scoring](../03-baseline/T-011-E2-identity-split-feasibility.md) dùng đúng pairs XQLFW/hash của T-011: 3.743 identity; 10 pair-fold chính thức mỗi fold có 635–659 identity xuất hiện ở dev. Quy tắc hash hai nhóm cố định trước khi dùng score giữ 4.516/6.000 cặp (3.000 genuine, 1.516 impostor) trước detection, loại 1.484 impostor nối hai nhóm. Hai nhóm có đủ cả hai nhãn; chưa biết bao nhiêu cặp qua rule một mặt. Script audit không xuất identity. Workflow `.github/workflows/t011-e2-identity-split.yml` dùng lại detector/alignment và encoder hiện có để thử threshold chọn trên nhóm danh tính còn lại; kết quả phải được báo riêng với protocol 10-fold của tác giả. Chưa có kết quả model cho split mới tại thời điểm ghi mục này.

[Run preflight 36306309908](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36306309908) dừng **trước khi tải/đọc ảnh** vì test tổng hợp đã kỳ vọng sai `false_reject=0`: threshold 0,9 chọn từ group 0 làm genuine score 0,8 ở group 1 bị từ chối, nên giá trị đúng là 1. Chỉnh assertion để kiểm đúng hai threshold 0,8/0,9 và lỗi 1; không đổi hàm chọn threshold, split hay dữ liệu.

[Run ảnh thật 36306431440](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36306431440) thành công tại commit `766b02e`; [báo cáo](../03-baseline/runs/T-011-E2-xqlfw-identity-disjoint.md) đối chiếu 4.215 cặp pair-fold cũ khớp lại, rồi chấm split custom trên 3.138/4.516 cặp đủ điều kiện. MobileFaceNet FA 68/1.092, FR 121/2.046; R50 FA 44/1.092, FR 75/2.046. Có 1.484 impostor bị loại do cắt qua hai nhóm và 1.378 cặp trong nhóm không qua rule một mặt; hai lý do không được gộp. Vẫn chưa là main test hoặc quyết định model/threshold.

## Bàn giao mốc nghiên cứu cho T-012

[T-011 baseline summary](../03-baseline/T-011-baseline-summary.md) là trang đọc nhanh E1/E2/M1 và giới hạn. Phạm vi baseline thăm dò hiện tại đã có mã, protocol, nguồn/hash, run, mẫu số và báo cáo; PR #7 có thể chuyển sang review/merge khi nhóm muốn đưa mốc này vào main. E3 pass/fail cần app và policy profile ở giai đoạn sau theo phạm vi Quốc An đã chốt, M1 target hardware/domain test cũng chưa có; không trình bày chúng là đã đạt. T-012 nhận các khoảng trống đó làm câu hỏi nghiên cứu, không dùng T-011 để chọn model cuối.
