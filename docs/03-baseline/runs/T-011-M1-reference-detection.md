# T-011 — M1 tham chiếu: thời gian ba detector trên cùng runner

**Run:** [GitHub Actions 36305640667](https://github.com/quocanwyf/doantotnghiep2nguoi/actions/runs/36305640667), ngày 2026-09-27, commit `1eeed269bbee6cfb935708667e112c7d01cdb8c5`. **Trạng thái:** run hoàn tất; phép đo chi phí component tham chiếu, chưa phải hiệu năng thiết bị triển khai. Câu hỏi, mẫu và phạm vi thời gian được ghi [trước khi chạy](../T-011-M1-reference-protocol.md).

## Điều kiện thực tế

- Cùng một job `ubuntu-latest`, Linux 6.17.0-1022-azure x86_64, 4 logical CPU; Python 3.12. Runtime: OpenCV 5.0.0 CPU (YuNet), MediaPipe 1.0.0 Tasks IMAGE CPU (BlazeFace), InsightFace 0.7.3 + ONNX Runtime 1.20.1 CPU (SCRFD); NumPy 2.2.6. `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS` đặt 1; mỗi runtime vẫn dùng cơ chế threading nội bộ của chính nó.
- Ảnh từ `WIDER_val.zip` đúng hash E1 `F9EFBD09F28C5D2D884BE8C0EAEF3967158C866A593FC36AB0413E4B2A58A17A`. Manifest có 3.226 ảnh; lấy **60 vị trí cách đều** sau khi sắp xếp tên path. Kích thước ảnh được chọn: rộng 1.024 px; cao 426–1.623 px. Giải mã trước đo; cùng frame BGR cho ba adapter. Không dùng nhãn/điểm E1 để chọn ảnh.
- Model hash được script kiểm trước chạy: YuNet `EBAFCE4E3C118D6554634BE5C27AB333B4C047A9A8C3FAF1D7CF93101C22F0F0`; BlazeFace `3698B18F063835BC609069EF052228FBE86D9C9A6DC8DCB7C7C2D69AED2B181B`; SCRFD `5E4447F50245BBD7966BDC6C0FA52938C61474A04EC7DEF48753668A9D8B4EA3A`.
- Khởi tạo model và giải mã ảnh ngoài timer; warm-up 8 frame/candidate; 3 vòng × 60 frame = **180 lần gọi `adapter.detect`/candidate**, xoay thứ tự candidate qua mỗi vòng. Thời gian gồm preprocessing/postprocessing trong adapter, không gồm ZIP, decode, load model, xác minh/check-in hoặc ghi dữ liệu. JSON tạm chỉ ở `RUNNER_TEMP`, in thống kê tổng hợp trong log rồi xóa, không upload ảnh/weight/prediction.

## Kết quả quan sát

| Candidate | Calls | Median ms | P95 ms | Min–max ms | Tổng bbox từ 180 calls |
|---|---:|---:|---:|---:|---:|
| YuNet | 180 | 25,72 | 48,81 | 13,80–58,57 | 56.526 |
| BlazeFace full-range | 180 | 13,26 | 33,95 | 5,65–64,71 | 28.275 |
| SCRFD-500MF | 180 | 83,24 | 165,81 | 42,61–203,19 | 272.217 |

Trong **job và mẫu này**, BlazeFace có median thấp nhất, SCRFD cao nhất. Các cấu hình E1 dùng score output thấp để vẽ AP, nên chi phí postprocessing và số bbox phản ánh cấu hình nghiên cứu v1; không suy latency của một threshold triển khai chưa chọn. [E1 quality](T-011-E1-widerface-comparison.md) đo AP/recall trên **toàn bộ 3.226 ảnh**, còn M1 đo thời gian trên 60 ảnh; không gộp hai mẫu số thành một điểm tổng hợp hoặc phán quyết model.

## Giới hạn và quyết định tiếp

Một run trên runner chia sẻ tài nguyên không bảo đảm xếp hạng tốc độ ổn định; chưa có lặp độc lập theo job, RAM đỉnh riêng từng model, thời gian 1:1 verification, S4, E3, thiết bị đích, tải/queue hoặc công sức nhân sự. Vì thế M1 này **giải quyết khoảng trống so thời gian giữa các run E1 rời rạc ở mức tham chiếu**, nhưng chưa trả lời candidate nào đáp ứng cửa phòng thi. Khi có thiết bị/khối lượng công việc mục tiêu, đo lại cùng manifest/procedure và thêm end-to-end attempt, review/fallback tách riêng; target chấp nhận phải có nguồn nghiệp vụ trước kết luận đạt/không đạt.
