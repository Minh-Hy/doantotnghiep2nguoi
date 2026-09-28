# T-018 — API lõi tiếp nhận

API Django REST Framework lưu dữ liệu trên PostgreSQL. Phần này quản lý ca/phòng, phiên bản roster và policy, quyền theo context, lượt kiểm tra, case ngoại lệ, check-in và audit. Hiện chỉ mở API tạo/đọc attempt; chưa có API xác minh AI hay ghi check-in.

## Chạy ở máy phát triển

Yêu cầu Python 3.12 qua `uv` và một PostgreSQL đang chạy. Trên Windows, dùng **pgAdmin → Query Tool** với tài khoản quản trị PostgreSQL để tạo database/tài khoản ứng dụng bằng mật khẩu tự chọn (không gửi mật khẩu vào chat hoặc Git). **Chạy từng câu SQL riêng**, vì `CREATE DATABASE` không chạy trong transaction:

```sql
CREATE USER exam_entry WITH PASSWORD 'mat-khau-rieng-cua-ban';
CREATE DATABASE exam_entry OWNER exam_entry;
```

Sau đó từ thư mục `backend`:

```powershell
uv sync --frozen
Copy-Item .env.example .env
# Sửa .env bằng secret ngẫu nhiên và mật khẩu PostgreSQL vừa tạo; file này bị Git bỏ qua.
uv run --env-file .env python manage.py migrate
uv run --env-file .env python manage.py createsuperuser
uv run --env-file .env python manage.py runserver 0.0.0.0:8000
```

`APP_SECRET_KEY` là bắt buộc. Không dùng `APP_DEBUG=1`, HTTP thuần hoặc token thử nghiệm khi triển khai thật. Cần cấu hình HTTPS, host, xác thực, sao lưu và quyền truy cập theo môi trường trước khi vận hành.

Có thể tạo secret ngẫu nhiên bằng `uv run python -c "import secrets; print(secrets.token_urlsafe(48))"` rồi dán vào `APP_SECRET_KEY` trong `.env`. Nếu PostgreSQL dùng port khác 5432, sửa `APP_DB_PORT`. `APP_ALLOWED_HOSTS` mẫu đã có `10.0.2.2` cho Android emulator; với điện thoại thật, thêm IP LAN của máy chạy BE và dùng mạng phát triển được tin cậy. Không dùng HTTP/mật khẩu thật trên mạng công cộng.

Tạo dữ liệu giả lập qua Django admin: kỳ thi, phòng, context, roster, quyền operator. Context chỉ được `OPEN` khi đã có phiên bản roster, người/thời điểm xác nhận roster, phiên bản policy, người/thời điểm phê duyệt policy và vai trò xử lý ngoại lệ. Các trường này là chốt kỹ thuật để tránh mở nhầm; chúng **không thay thế** phê duyệt chính sách nghiệp vụ. Chưa nhập dữ liệu cá nhân hoặc ảnh thật vào bản thử.

Sau khi đã tạo tài khoản bằng `createsuperuser` hoặc admin, có thể chuẩn bị **ca thi học phần giả lập** và cấp quyền operator cho tài khoản đó:

```powershell
uv run --env-file .env python manage.py seed_demo --operator TEN_DANG_NHAP
```

Lệnh có thể chạy lại, tạo hai mã giả `DEMO-001`/`DEMO-002` và giữ context ở `SETUP`. Nó không tự duyệt policy, mở ca hay tạo check-in. Mở Flutter, đăng nhập tài khoản này để xem `DEMO-T018-HOC-PHAN / DEMO-P101`. Khi chưa có profile kiểm thử được nhóm duyệt, nút tiếp nhận vẫn khóa.

## API v1 hiện có

| Phương thức | Đường dẫn | Ý nghĩa |
|---|---|---|
| `GET` | `/api/v1/health/` | Kiểm tra tiến trình API, không kiểm tra kết nối DB. |
| `GET` | `/api/v1/ready/` | Kiểm tra API kết nối được DB. |
| `POST` | `/api/v1/auth/login/` | Đăng nhập bằng `username`/`password`, trả token cho phiên ứng dụng. |
| `POST` | `/api/v1/auth/logout/` | Thu hồi token hiện tại. |
| `GET` | `/api/v1/contexts/` | Context mà tài khoản có quyền. |
| `POST` | `/api/v1/attempts/` | Tạo lượt bằng `context_id`, `candidate_code`, `idempotency_key` UUID. |
| `GET` | `/api/v1/attempts/{id}/` | Xem lượt trong context được phép truy cập. |

Các đường dẫn ngoài health, ready và login yêu cầu `Authorization: Token <token>` hoặc phiên admin có session. Token chỉ giữ trong bộ nhớ Flutter ở mốc hiện tại; khi mở lại app cần đăng nhập lại. Đăng xuất thu hồi token nếu có kết nối; nếu mất mạng, app xóa phiên cục bộ nhưng token phía server chỉ được thu hồi khi kết nối lại hoặc quản trị viên can thiệp. Đây chưa là phiên xác thực offline. Operator của context mới được tạo attempt. Cùng `idempotency_key` và mã trong một context trả lại attempt cũ; dùng key đó với mã khác trả 409.

Tra cứu roster chỉ phân biệt một hồ sơ đúng phòng, không tìm thấy, nhiều hồ sơ, hoặc sai phòng. Ba trường hợp sau mở review case. Một hồ sơ đúng phòng chỉ chuyển attempt sang `IN_PROGRESS` và `VERIFY_IDENTITY`; **không** tạo check-in hay quyết định cho vào phòng. API không nhận ảnh hoặc embedding. Dữ liệu trả về tránh tên/danh tính; admin và database vẫn cần quyền truy cập phù hợp.

## Kiểm tra

```powershell
uv run python manage.py test entry --settings=config.test_settings
uv run python manage.py makemigrations --check --dry-run --settings=config.test_settings
```

`config.test_settings` chỉ dành cho test, dùng SQLite trong bộ nhớ để chạy nhanh; không xác nhận tương thích PostgreSQL. Khi có PostgreSQL tại máy/CI, chạy `migrate` và kiểm thử tích hợp trên PostgreSQL trước khi gọi là hoàn tất backend.
