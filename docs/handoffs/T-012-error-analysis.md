# Bàn giao T-012 — phân tích lỗi baseline có điều kiện

- **Người thực hiện/ngày:** Codex theo yêu cầu Quốc An, 2026-09-27; Minh Hy review theo Sheet.
- **Đầu vào:** T-008 PR #3 làm business baseline tạm theo chỉ đạo Quốc An; T-009 PR #5, T-010 PR #6 và T-011 draft PR #7. Nhánh T-012 bắt đầu từ commit T-011 `b7755ca`, để giữ nguyên bằng chứng E1/E2 và review phần phân tích riêng.
- **Đầu ra:** [T-012 error analysis](../03-baseline/T-012-error-analysis.md) và [Decision Logic phase 03](../03-baseline/DECISION_LOGIC.md). Phân biệt observed/inference/hypothesis; trace về T-008; đề xuất X-012-A về S4 target selection/coverage làm câu hỏi thiết kế thí nghiệm tiếp theo.
- **Cách kiểm:** đối chiếu mọi mẫu số và số liệu với ba [run E1](../03-baseline/runs/T-011-E1-widerface-comparison.md), [đối chứng E2](../03-baseline/runs/T-011-E2-xqlfw-mbf-vs-r50.md) và [coverage diagnosis](../03-baseline/runs/T-011-E2-coverage-diagnosis.md); kiểm link/ID và `git diff --check`. Không tạo metric mới từ dữ liệu thô hoặc sửa protocol đã chấm.
- **Giới hạn:** T-011 chưa hoàn tất E3/M1; không có nhãn người mục tiêu, dữ liệu camera cửa phòng hoặc profile kỳ thi. X-012-A là câu hỏi ưu tiên, **chưa phải thí nghiệm đã chạy**. Đánh giá có thể đổi sau review hoặc evidence mới.
- **File ngoài Git:** không có file mới. Dữ liệu/weight/run đầu vào của T-011 vẫn theo handoff và external-assets của task đó; T-012 không sao chép ảnh, prediction theo ảnh hoặc embedding.
- **Commit/PR:** cập nhật sau khi đẩy nhánh T-012; PR sẽ là draft và phụ thuộc PR #7. Không merge trước khi xác nhận thứ tự review/các dependency.
