# Backend T-018 — mốc M1 có thể chạy

Backend dùng Python 3.12, Django 5.2, Django REST Framework, Psycopg và PostgreSQL 18. Các bảng mới ở schema `exam_entry_app` của database `exam_entry`; schema `public` từ lần thử trước không được dùng bởi mã mới.

## Chạy trên máy Minh Hy

Mở terminal PowerShell tại thư mục `backend/` trong VS Code:

```powershell
uv sync --locked
uv run --env-file .env python manage.py migrate
uv run --env-file .env python manage.py runserver 0.0.0.0:8000
```

File `.env` đã được chuẩn bị cục bộ, bị Git bỏ qua. Không đưa mật khẩu hoặc nội dung file này lên Git/ảnh chụp màn hình. Với máy khác, sao chép `.env.example` thành `.env`, tự điền giá trị rồi tạo schema PostgreSQL `exam_entry_app` bằng tài khoản có quyền `CREATE` trước khi migrate. Không chạy migration vào schema `public` cũ.

Để thử đăng nhập/ca giả lập, dừng server bằng `Ctrl+C` rồi tạo tài khoản **một lần** và seed fixture:

```powershell
uv run --env-file .env python manage.py createsuperuser
uv run --env-file .env python manage.py seed_demo --operator TEN_DANG_NHAP
```

`TEN_DANG_NHAP` là username vừa nhập khi chạy `createsuperuser`, không phải username PostgreSQL. Sau đó chạy lại `runserver`. `seed_demo` tạo `CTX-SIM-01` cùng hai mã `SIM001`, `SIM002` và gán operator; ca vẫn ở `SETUP`, policy chưa được duyệt. Có thể chạy lại lệnh seed mà không nhân đôi fixture.

Sau khi server báo đang chạy, mở:

- `http://127.0.0.1:8000/api/v1/health/` → `status: ok`, xác nhận API sống.
- `http://127.0.0.1:8000/api/v1/ready/` → `status: ready`, xác nhận DB/schema/migration sẵn sàng.

Để dừng server, nhấn `Ctrl+C`. Nếu cổng 8000 đang được dùng, dừng tiến trình cũ trước khi chạy lại để URL trong Flutter không bị lệch.

## API hiện có

| API | Quyền | Công dụng ở M1 |
|---|---|---|
| `GET /api/v1/health/` | Công khai | Kiểm tra API. |
| `GET /api/v1/ready/` | Công khai | Kiểm tra DB và bảng lõi. |
| `POST /api/v1/auth/login/` | Username/password hợp lệ | Lấy token thử nghiệm để gọi API được bảo vệ. |
| `POST /api/v1/auth/logout/` | Token | Thu hồi token của phiên hiện tại. |
| `GET /api/v1/contexts/` | Đăng nhập | Chỉ trả ca/phòng được gán cho user. |
| `GET/POST /api/v1/attempts/` | Đăng nhập, POST cần operator | Tạo attempt trước lookup, chặn khi context/profile chưa sẵn sàng; header `Idempotency-Key` chống gửi trùng. |
| `GET /api/v1/attempts/<uuid>/` | Actor của attempt | Đọc lượt của chính mình. |

Không có API ghi check-in, quyết định cho vào hoặc attendance ở mốc này. Profile giả lập còn ở trạng thái nháp; không tự đánh dấu policy đã duyệt chỉ để mở luồng.

Token ở bản local được Flutter giữ trong bộ nhớ đến khi đăng xuất/đóng app. HTTP local và tài khoản demo chỉ dành cho thử nghiệm; chưa dùng dữ liệu hoặc tài khoản kỳ thi thật.

## Kiểm tra mã

```powershell
uv run --env-file .env python manage.py check
uv run --env-file .env python manage.py test --settings=config.test_settings
uv run --env-file .env python manage.py showmigrations foundation
```

Kiểm thử tự động dùng SQLite trong bộ nhớ để kiểm quyền, precondition và idempotency. Migration/readiness được kiểm riêng với PostgreSQL cục bộ. Đọc [kế hoạch T-018](../docs/06-mobile/T-018-ke-hoach-trien-khai-app.md) để biết phần còn lại.
