# T-012 — Kiểm nhãn gốc ChokePoint cho câu hỏi S4

**Ngày:** 2026-09-27. **Loại bằng chứng:** kiểm archive nhãn công khai; không tải ảnh/video, không chạy detector hoặc X-012-A. **Câu hỏi:** gói ground truth gốc có nhãn nhiều người và người mục tiêu theo lượt để chấm S4 không?

## Nguồn và cách kiểm

- [Zenodo record của tác giả](https://zenodo.org/records/815657) công bố `groundtruth.tar.xz` v1, 456.396 byte, MD5 `5c9d4d38a1c614905fe48da48ecdf06c`; [trang tác giả](https://arma.sourceforge.net/chokepoint/) nêu license nghiên cứu phi thương mại. SHA-256 file đã tải vào thư mục tạm: `2BA86BF1EBD3DBE14D170A8FEDE5D0911AB383FEAE1AB30CA2E779AE7671DC1D`. Đã đối chiếu MD5 trước khi đọc XML.
- Liệt kê file trong archive, parse mọi XML, đếm phần tử `frame` và số `person` trực tiếp dưới từng frame; chỉ xuất schema/tổng hợp, không xuất ID hay nhãn theo ảnh. Archive không đưa vào Git.

## Kết quả

| Kiểm | Số đếm / cấu trúc |
|---|---|
| File XML ground truth | 72 |
| File tên chứa sequence đông `_S5_` | 0 |
| Phần tử `frame` qua 72 XML | 176.916 |
| Phần tử `person` | 72.291 |
| Frame có hơn một `person` trong XML | 0 |
| Trường trong `person` | `id`, `leftEye(x,y)`, `rightEye(x,y)`; không có bbox mặt hoặc claim/attempt trong phần tử này |

Các số frame/person là **dòng annotation qua camera và sequence**, không phải số lượt độc lập hay số người khác nhau. [Zenodo](https://zenodo.org/records/815657) mô tả các sequence thường có một người trong ảnh và hai sequence đông `P2E_S5`/`P2L_S5`; gói ground truth gốc được kiểm ở đây **không chứa S5**. [WaveLab](https://www.wavelab.at/sources/plusfiaq/) mô tả nhãn bổ sung cho sáu sequence ChokePoint S5, nhưng đó là nguồn khác và trang hiện chưa cung cấp mẫu thỏa thuận tải PLUSFiaQ/annotation bổ sung để kiểm file/quyền.

## Quyết định phạm vi

Gói ground truth gốc **không đủ để chạy X-012-A nhiều người**: không có frame nhiều `person` được gán nhãn, không có nhãn mục tiêu theo claim hoặc ranh giới attempt. Có thể nghiên cứu cảnh cổng/verification đơn người trong một protocol riêng, nhưng không đổi tên thành bằng chứng chọn đúng thí sinh giữa người nền. Không dựng target từ `person id` hoặc giả định người duy nhất là người đã khai báo mã. X-012-A vẫn `not runnable` với nguồn này; nếu nhận được nhãn S5 bổ sung hợp lệ, phải audit lại nội dung và quyền trước khi thiết kế proxy, rồi vẫn cần liên kết claim–actor độc lập cho phép thử nghiệp vụ.
