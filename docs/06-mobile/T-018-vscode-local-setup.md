# T-018 — Chạy mốc hiện tại trong VS Code trên Windows

**Ngày kiểm:** 2026-09-29. **Mốc hiện có:** API Django + schema PostgreSQL + Flutter kiểm kết nối/đăng nhập/xem ca. Profile giả lập M0 vẫn là bản nháp; chưa có camera/AI/check-in. Chỉ dùng fixture giả, không đưa ảnh mặt, mật khẩu hoặc file `.env` vào Git.

## 1. Chuẩn bị VS Code và Android

Máy Minh Hy đã có `uv 0.11.15`, Python 3.12 qua uv, Flutter 3.44.0, Android SDK 36.1.0 và PostgreSQL 18. Trong VS Code, cài extension **Flutter** của Dart Code ở `Ctrl+Shift+X` (Dart sẽ được cài kèm). Extension Python đã có. Cảnh báo Visual Studio C++ trong `flutter doctor` chỉ liên quan bản Windows desktop.

Mở `D:\WorkSpace\doantotnghiep2nguoi` bằng **File → Open Folder**. Mở hai PowerShell terminal trong VS Code (**Terminal → New Terminal**). Các lệnh dưới đây chạy từ thư mục gốc này.

Để chạy Android, phải có **một** trong hai lựa chọn:

- Android Emulator: trong Android Studio mở **Device Manager → Create Virtual Device**, tạo/chạy một máy ảo rồi xác nhận `flutter devices` có dòng `android`.
- Điện thoại thật: bật Developer options và USB debugging, cắm USB, chấp nhận hộp thoại tin cậy máy tính, rồi xác nhận `flutter devices` có dòng `android`. Nếu dùng Wi-Fi để gọi backend, điện thoại và máy Windows cần cùng mạng.

Hiện `flutter devices` trên máy này chỉ liệt kê Windows/Chrome/Edge và `flutter emulators` chưa có máy ảo. Bạn có thể chạy test/build mã trước; để **nhìn app trên Android** cần hoàn tất một lựa chọn trên.

## 2. Terminal A — backend

```powershell
Set-Location D:\WorkSpace\doantotnghiep2nguoi\backend
uv sync --locked
uv run --env-file .env python manage.py migrate
```

Nếu chưa có tài khoản Django trên schema mới, tạo **một lần** trong terminal A:

```powershell
uv run --env-file .env python manage.py createsuperuser
uv run --env-file .env python manage.py seed_demo --operator TEN_DANG_NHAP
```

Thay `TEN_DANG_NHAP` bằng **username vừa nhập ở bước createsuperuser**, không phải tên đăng nhập PostgreSQL. Nhập mật khẩu khi terminal hỏi; không dán mật khẩu vào chat hoặc tài liệu. Nếu đã có user, bỏ qua `createsuperuser` và chỉ chạy seed. Lệnh seed tạo ca/phòng giả và hai mã `SIM001`, `SIM002`, gán operator, nhưng **không** duyệt policy hoặc mở tiếp nhận. Sau đó chạy server:

```powershell
uv run --env-file .env python manage.py runserver 0.0.0.0:8000
```

`backend/.env` đã có trên **máy này**, bị Git ignore; không sao chép nội dung vào chat/ảnh. Schema `exam_entry_app` đã được tạo và migration chạy; `public` cũ vẫn giữ nguyên. Giữ terminal A mở trong lúc thử Flutter. Khi thấy dòng server chạy, dùng browser trên máy Windows mở:

- [Kiểm API](http://127.0.0.1:8000/api/v1/health/) → JSON có `"status": "ok"`.
- [Kiểm database](http://127.0.0.1:8000/api/v1/ready/) → JSON có `"status": "ready"`.

Nếu `/ready/` trả 503, kiểm PostgreSQL đang chạy, tên schema trong `.env`, rồi chạy lại `migrate`. Nhấn `Ctrl+C` ở terminal A để dừng server.

## 3. Terminal B — Flutter

**Android Emulator:**

```powershell
Set-Location D:\WorkSpace\doantotnghiep2nguoi\mobile
flutter pub get
flutter devices
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

`10.0.2.2` là địa chỉ từ Android Emulator về máy Windows. Trên màn hình app, **Máy chủ: Đã kết nối** và **Cơ sở dữ liệu: Sẵn sàng** là kết quả mong đợi. Bấm **Đăng nhập nhân sự**, dùng username/mật khẩu Django vừa tạo; màn hình sau phải hiện `CTX-SIM-01` và **Đang chuẩn bị — chưa tiếp nhận**. Nút tiếp nhận vẫn khóa vì policy chưa được duyệt. Tắt backend rồi bấm **Kiểm tra lại** ở màn hình đầu: app phải báo không kết nối; mở backend và bấm lại để phục hồi.

**Điện thoại thật:** tìm IPv4 LAN của máy Windows bằng `ipconfig`, dùng `flutter run --dart-define=API_BASE_URL=http://<IP-LAN>:8000`. Thêm chính IP này vào `APP_ALLOWED_HOSTS` trong `backend/.env`, khởi động lại backend và cho phép cổng 8000 qua Windows Firewall nếu bị chặn. Không dùng `127.0.0.1` trên điện thoại vì đó là chính điện thoại.

Nếu muốn bấm **F5** trong VS Code, mở riêng thư mục `mobile/` bằng **File → New Window → Open Folder**, chọn Android ở thanh trạng thái và chạy Debug. Lệnh `flutter run` trong terminal vẫn là cách trực tiếp nhất để xác nhận đường kết nối.

## 4. Kiểm thử không cần Android

Trong terminal backend (sau khi đã dừng `runserver` hoặc mở terminal mới):

```powershell
uv run --env-file .env python manage.py check
uv run --env-file .env python manage.py test --settings=config.test_settings
uv run --env-file .env python manage.py showmigrations foundation
```

Trong terminal `mobile/`:

```powershell
flutter analyze
flutter test
flutter build apk --debug
```

Ngày 2026-09-29: backend có 7 test đạt, Django check đạt, migration PostgreSQL thật đạt; Flutter analyze, 3 widget test và 1 test HTTP đạt, APK debug build thành công. Chưa có Android device/emulator trên máy để thử trực tiếp. Đây là bằng chứng cho **mốc kết nối/đăng nhập/ca**, không phải kiểm thử camera/AI/check-in.
