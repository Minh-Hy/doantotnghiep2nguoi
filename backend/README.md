# T-018 — API lõi tiếp nhận

API Django REST Framework lưu dữ liệu trên PostgreSQL. Phần này quản lý ca/phòng, phiên bản roster và policy, quyền theo context, lượt kiểm tra, case ngoại lệ, check-in và audit. Hiện chỉ mở API tạo/đọc attempt; chưa có API xác minh AI hay ghi check-in.

## Chạy ở máy phát triển

Yêu cầu Python 3.12 qua `uv` và một PostgreSQL đang chạy. Tạo database và tài khoản PostgreSQL riêng cho ứng dụng, rồi từ thư mục `backend`:

```powershell
uv sync --frozen
Copy-Item .env.example .env
# Sửa .env bằng secret ngẫu nhiên và thông tin PostgreSQL tại máy; file này bị Git bỏ qua.
uv run --env-file .env python manage.py migrate
uv run --env-file .env python manage.py createsuperuser
uv run --env-file .env python manage.py runserver 0.0.0.0:8000
```

`APP_SECRET_KEY` là bắt buộc. Không dùng `APP_DEBUG=1`, HTTP thuần hoặc token thử nghiệm khi triển khai thật. Cần cấu hình HTTPS, host, xác thực, sao lưu và quyền truy cập theo môi trường trước khi vận hành.

Tạo dữ liệu giả lập qua Django admin: kỳ thi, phòng, context, roster, quyền operator. Context chỉ được `OPEN` khi đã có phiên bản roster, người/thời điểm xác nhận roster, phiên bản policy, người/thời điểm phê duyệt policy và vai trò xử lý ngoại lệ. Các trường này là chốt kỹ thuật để tránh mở nhầm; chúng **không thay thế** phê duyệt chính sách nghiệp vụ. Chưa nhập dữ liệu cá nhân hoặc ảnh thật vào bản thử.

## API v1 hiện có

| Phương thức | Đường dẫn | Ý nghĩa |
|---|---|---|
| `GET` | `/api/v1/health/` | Kiểm tra tiến trình API, không kiểm tra kết nối DB. |
| `GET` | `/api/v1/contexts/` | Context mà tài khoản có quyền. |
| `POST` | `/api/v1/attempts/` | Tạo lượt bằng `context_id`, `candidate_code`, `idempotency_key` UUID. |
| `GET` | `/api/v1/attempts/{id}/` | Xem lượt trong context được phép truy cập. |

Các đường dẫn ngoài health yêu cầu `Authorization: Token <token>` hoặc phiên admin có session. Chưa có màn hình cấp token/đăng nhập Flutter; token thử có thể tạo trong Django admin, phải giữ ngoài Git. Operator của context mới được tạo attempt. Cùng `idempotency_key` và mã trong một context trả lại attempt cũ; dùng key đó với mã khác trả 409.

Tra cứu roster chỉ phân biệt một hồ sơ đúng phòng, không tìm thấy, nhiều hồ sơ, hoặc sai phòng. Ba trường hợp sau mở review case. Một hồ sơ đúng phòng chỉ chuyển attempt sang `IN_PROGRESS` và `VERIFY_IDENTITY`; **không** tạo check-in hay quyết định cho vào phòng. API không nhận ảnh hoặc embedding. Dữ liệu trả về tránh tên/danh tính; admin và database vẫn cần quyền truy cập phù hợp.

## Kiểm tra

```powershell
uv run python manage.py test entry --settings=config.test_settings
uv run python manage.py makemigrations --check --dry-run --settings=config.test_settings
```

`config.test_settings` chỉ dành cho test, dùng SQLite trong bộ nhớ để chạy nhanh; không xác nhận tương thích PostgreSQL. Khi có PostgreSQL tại máy/CI, chạy `migrate` và kiểm thử tích hợp trên PostgreSQL trước khi gọi là hoàn tất backend.
