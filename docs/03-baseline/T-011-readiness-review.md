# T-011 — Rà soát đầu vào và quyết định chạy E2

**Ngày:** 2026-09-26. **Người rà soát:** Codex theo yêu cầu Quốc An. **Trạng thái:** cho phép phép thử học thuật thăm dò E2; chưa duyệt baseline so sánh đầy đủ hoặc quyết định kỹ thuật cuối.

## Phạm vi giả định T-008

Quốc An cho phép tiếp tục với T-008 như **business baseline tạm chấp nhận** để chuẩn bị T-011. Điều này không phải bằng chứng Minh Hy đã duyệt PR #3: review hiện tại của Hy là CHANGES_REQUESTED với 6 ý P1 và 2 ý P2. Không sửa hay merge PR #3 trong T-011.

Đối với E2, nhu cầu xác minh người hiện tại với record đã chọn vẫn xuất phát từ TQ-002/003 và FR-006/009 của T-008; các góp ý trên không đổi định nghĩa phép đo genuine/impostor 1:1. Đối với E3, các góp ý ảnh hưởng trực tiếp tới expected outcome và quyền xử lý, nên chưa khóa fixture hoặc kết luận pass/fail:

- kết quả check-in cũ không được lộ/chuyển thành quyền vào trước bước xác minh hoặc xác nhận của người có quyền;
- case chưa gắn được một registration cần lifecycle độc lập;
- roster/policy thay đổi trong lúc attempt phải có hiệu lực và bản ghi quyết định rõ;
- override không được tự bỏ qua điều kiện xác định hồ sơ duy nhất và bằng chứng danh tính;
- arrival trước mở hoặc sau đóng intake vẫn phải có đường ghi nhận/đối soát;
- correction phải rà soát entry authorization và report đã phát hành;
- nhiều discrepancy cùng lúc không được biến thành success vì nhánh đầu tiên đã xong;
- khóa nghiệp vụ check-in duy nhất cần là registration trong exam/session, không chỉ chuỗi mã.

Nguồn: [review của Minh Hy trên PR #3](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3). T-011 không tự đưa các đáp án nghiệp vụ này vào T-008; người phụ trách T-008 xử lý trong PR đó.

## Rà soát T-009 và T-010

- [T-009 PR #5](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/5) gắn XQLFW với xác minh cặp 1:1 và pack buffalo_sc với detector SCRFD-500MF/encoder MobileFaceNet. Dataset này không đo S4 chọn người mục tiêu, điều kiện ca/phòng hoặc hiệu quả vận hành. Nguồn tác giả cho phép tải và hướng dẫn đánh giá học thuật; quyền phân phối lại ảnh/weight không được suy từ license của mã.
- [T-010 PR #6](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6) đã đặt trước quy tắc pair-fold: mỗi fold đánh giá dùng threshold chọn từ 9 fold khác, không tune trên fold đang chấm. Đây là phép đo thăm dò; các fold có identity overlap nên không có claim unseen-identity. Ngưỡng cân bằng FMR/FNMR trên dev là **ngưỡng báo cáo thí nghiệm**, không là chính sách cho vào phòng.
- T-010 chưa chọn main verification test, target FMR/FNMR theo nghiệp vụ hoặc thiết bị triển khai. E1 thiếu ảnh/nhãn được kiểm, E3 thiếu profile đã giải quyết review, M1 thiếu tải/thiết bị. Không lấy run E2 làm kết quả thay thế.

## Quyết định và ranh giới T-011

**Cho phép:** chạy một baseline học thuật E2 với XQLFW và buffalo_sc sau khi pin hash input, pipeline và máy. Ghi coverage ảnh/cặp, FMR/FNMR cùng denominator, thời gian trên PC tham chiếu, confidence interval và giới hạn.

**Chưa cho phép kết luận:** model tốt nhất, threshold triển khai, kết quả identity-disjoint, đáp ứng nghiệp vụ kỳ thi, giảm nhân sự hoặc pass/fail E3. Muốn so encoder khác phải vượt gate weight/runtime/preprocessing và dùng cùng protocol; muốn chốt kỹ thuật cuối phải có test phù hợp hơn và evidence T-012/experiment sau đó.

Chuỗi: **T-008 TQ-002/003 (tạm chấp nhận) → T-009 candidate B0 → T-010 E2 pair-fold → T-011 phép đo thăm dò → T-012 phân tích lỗi/đặt câu hỏi tiếp**.

## Cập nhật E1 sau review ban đầu — 2026-09-27

[Cổng dữ liệu WIDER FACE validation](T-011-E1-widerface-data-gate.md) đã kiểm file thật từ CUHK-CSE: 3.226 ảnh khớp annotation, 39.708 bbox, hash/CRC và giải mã đạt. Vì có cờ invalid và bbox không dương, E1 vẫn cần khóa evaluator, quy tắc ignore/match và wrapper từng detector trước khi chấm AP/recall. Kết luận review ban đầu “thiếu archive/nhãn” được thay bằng **“data gate cơ bản đạt; benchmark E1 chưa khóa”**. Không có điểm detector trong cập nhật này.
