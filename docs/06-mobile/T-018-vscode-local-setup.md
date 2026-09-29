# T-018 — Chạy mốc hiện tại trong VS Code trên Windows

**Ngày kiểm:** 2026-09-29. **Mốc hiện có:** API Django + schema PostgreSQL + Flutter kiểm kết nối/đăng nhập/xem ca. Có thể chạy giao diện bằng Edge trên máy yếu; Android vẫn là đích chính của sản phẩm. Profile giả lập M0 vẫn là bản nháp; chưa có camera/AI/check-in. Chỉ dùng fixture giả, không đưa ảnh mặt, mật khẩu hoặc file `.env` vào Git.

## 1. Chuẩn bị VS Code

Máy Minh Hy đã có `uv 0.11.15`, Python 3.12 qua uv, Flutter 3.44.0, Android SDK 36.1.0 và PostgreSQL 18. Trong VS Code, cài extension **Flutter** của Dart Code ở `Ctrl+Shift+X` (Dart sẽ được cài kèm). Extension Python đã có. Cảnh báo Visual Studio C++ trong `flutter doctor` chỉ liên quan bản Windows desktop.

Mở `D:\WorkSpace\doantotnghiep2nguoi` bằng **File → Open Folder**. Mở hai PowerShell terminal trong VS Code (**Terminal → New Terminal**). Các lệnh dưới đây chạy từ thư mục gốc này.

**Bạn có thể thử ngay trên Edge, không cần Android Emulator.** `flutter devices` phải hiển thị `Edge (web)`; nếu chưa thấy, cài/mở Microsoft Edge và kiểm lại. Muốn thử Android về sau thì dùng **một** trong hai lựa chọn:

- Android Emulator: trong Android Studio mở **Device Manager → Create Virtual Device**, tạo/chạy một máy ảo rồi xác nhận `flutter devices` có dòng `android`.
- Điện thoại thật: bật Developer options và USB debugging, cắm USB, chấp nhận hộp thoại tin cậy máy tính, rồi xác nhận `flutter devices` có dòng `android`. Nếu dùng Wi-Fi để gọi backend, điện thoại và máy Windows cần cùng mạng.

Trước khi thêm web preview, `flutter devices` trên máy này liệt kê Windows/Chrome/Edge và `flutter emulators` chưa có máy ảo. Edge đủ để xem luồng hiện tại; để kiểm camera/AI trên thiết bị Android về sau cần một lựa chọn trên.

## 2. Terminal A — backend

```powershell
Set-Location D:\WorkSpace\doantotnghiep2nguoi\backend
uv sync --locked
uv run --env-file .env python manage.py migrate
```

Nếu chưa có tài khoản Django trên schema mới, tạo **một lần** trong terminal A:

```powershell
uv run --env-file .env python manage.py createsuperuser
```

Lệnh hỏi **username Django bạn tự chọn**, email (có thể để trống) và mật khẩu. Khi gõ mật khẩu, terminal không hiện ký tự; đây là bình thường. Đây là tài khoản của app, **khác** tài khoản PostgreSQL. Chưa có tài khoản thì phải hoàn thành lệnh này trước khi đăng nhập Flutter. Sau đó thay `TEN_DANG_NHAP` bằng đúng username vừa chọn:

```powershell
uv run --env-file .env python manage.py seed_demo --operator TEN_DANG_NHAP
```

Nếu đã có user Django, bỏ qua `createsuperuser` và chỉ chạy seed. Lệnh seed tạo ca/phòng giả và hai mã `SIM001`, `SIM002`, gán operator, nhưng **không** duyệt policy hoặc mở tiếp nhận. Sau đó chạy server:

```powershell
uv run --env-file .env python manage.py runserver 0.0.0.0:8000
```

`backend/.env` đã có trên **máy này**, bị Git ignore; không sao chép nội dung vào chat/ảnh. Schema `exam_entry_app` đã được tạo và migration chạy; `public` cũ vẫn giữ nguyên. Giữ terminal A mở trong lúc thử Flutter. Khi thấy dòng server chạy, dùng browser trên máy Windows mở:

- [Kiểm API](http://127.0.0.1:8000/api/v1/health/) → JSON có `"status": "ok"`.
- [Kiểm database](http://127.0.0.1:8000/api/v1/ready/) → JSON có `"status": "ready"`.

Nếu `/ready/` trả 503, kiểm PostgreSQL đang chạy, tên schema trong `.env`, rồi chạy lại `migrate`. Nhấn `Ctrl+C` ở terminal A để dừng server.

## 3. Terminal B — Flutter trên Edge (khuyên dùng cho máy này)

```powershell
Set-Location D:\WorkSpace\doantotnghiep2nguoi\mobile
flutter pub get
flutter devices
flutter run -d edge --web-hostname 127.0.0.1 --web-port 7357
```

Flutter sẽ mở Edge tại `http://127.0.0.1:7357` và mặc định gọi Django tại `http://127.0.0.1:8000`. **Giữ cả hai terminal mở.** Màn hình đầu phải hiện **Máy chủ: Đã kết nối** và **Cơ sở dữ liệu: Sẵn sàng**. Bấm **Đăng nhập nhân sự**, nhập username/mật khẩu Django vừa tạo; màn hình sau phải hiện `CTX-SIM-01` và **Đang chuẩn bị — chưa tiếp nhận**. Nếu bạn chưa chạy `seed_demo`, đăng nhập sẽ thành công nhưng danh sách ca trống. Nút tiếp nhận vẫn khóa vì policy chưa được duyệt.

Nếu Edge báo không kết nối, kiểm hai URL health/ready ở mục 2, chắc chắn backend còn chạy và Flutter dùng đúng cổng `7357`. Chế độ Edge chỉ để thử giao diện/API; các bước camera, AI chạy trên điện thoại Android sau này không được xác nhận bằng Edge.

## 4. Tùy chọn: Flutter trên Android

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

## 5. Kiểm thử không cần Android

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
flutter build web
flutter build apk --debug
```

Ngày 2026-09-29: backend có 12 test đạt, Django check đạt, migration PostgreSQL `0002`–`0007` và backfill dữ liệu cũ đạt; Flutter analyze, 3 widget test và 1 test HTTP đạt, web/APK debug build thành công ở mốc trước. `flutter run -d edge` đã khởi động, trang web/API/CORS local phản hồi đúng. Truy vấn DB hiện thấy 1 tài khoản Django và fixture ca giả; nếu đó là tài khoản bạn đã tạo, **bỏ qua** `createsuperuser`, dùng đúng username khi cần chạy lại `seed_demo` và đăng nhập. Chưa thử đăng nhập thật vì không có mật khẩu tài khoản hiện có. Chưa có Android device/emulator trên máy để thử trực tiếp. Đây là bằng chứng cho **mốc kết nối/schema**, không phải kiểm thử camera/AI/check-in.

## 6. Xem DB trong pgAdmin

Backend kết nối database `exam_entry` trên `127.0.0.1:5432`, schema `exam_entry_app`. Trong pgAdmin, nhấp phải **Databases → Refresh**; mở **exam_entry → Schemas → exam_entry_app → Tables**. Nếu vẫn chỉ thấy `postgres`, mở **Properties → Connection** của server đã đăng ký, đối chiếu host/port với `127.0.0.1:5432`. [Thiết kế DB](T-018-thiet-ke-co-so-du-lieu.md) liệt kê 24 bảng nghiệp vụ và các bảng chưa bật chức năng.
