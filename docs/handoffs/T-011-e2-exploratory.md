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
