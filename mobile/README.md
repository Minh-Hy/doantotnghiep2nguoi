# Flutter T-018 — Android và bản xem thử trên Edge

Ứng dụng hiện có màn hình kiểm tra API/PostgreSQL, đăng nhập nhân sự và danh sách ca/phòng được phân công. Ca giả lập vẫn ở `SETUP`; nút tiếp nhận bị khóa. Chưa có camera, AI hoặc check-in.

## Chạy trên Edge từ VS Code (không cần máy ảo)

Sau khi khởi động backend ở terminal khác, mở terminal PowerShell tại `mobile/`:

```powershell
flutter pub get
flutter run -d edge --web-hostname 127.0.0.1 --web-port 7357
```

Edge mở app tại `http://127.0.0.1:7357` và app tự gọi Django local ở cổng 8000. Cần tạo username Django và chạy `seed_demo` trước khi có thể đăng nhập/xem ca; xem [hướng dẫn VS Code](../docs/06-mobile/T-018-vscode-local-setup.md). Edge chỉ dùng để thử giao diện/API mốc này; Android vẫn là đích chính cho camera/AI.

## Chạy Android từ VS Code

Mở thư mục gốc repository trong VS Code, cài extension **Flutter** của Dart Code, mở terminal PowerShell tại `mobile/`. Khởi động backend ở terminal khác trước.

```powershell
flutter pub get
flutter devices
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Địa chỉ `10.0.2.2` dành cho Android Emulator truy cập server đang chạy trên máy Windows. Nếu dùng điện thoại thật cùng Wi-Fi, thay bằng IP LAN của máy Windows, ví dụ `http://192.168.x.x:8000`; đồng thời thêm IP đó vào `APP_ALLOWED_HOSTS` trong `backend/.env` và cho phép cổng 8000 qua Windows Firewall nếu cần. URL không chứa mật khẩu.

Để thấy `CTX-SIM-01` sau đăng nhập, trước đó hãy tạo username Django và chạy `seed_demo --operator TEN_DANG_NHAP` trong backend như [hướng dẫn VS Code](../docs/06-mobile/T-018-vscode-local-setup.md). Username này khác role PostgreSQL `exam_entry`. Token chỉ ở bộ nhớ app và bị thu hồi khi đăng xuất thành công.

Ngày 2026-09-29 chưa có emulator hoặc điện thoại Android kết nối trên máy Minh Hy. Bạn có thể tạo máy ảo trong Android Studio Device Manager hoặc bật USB debugging trên điện thoại rồi kiểm `flutter devices`. Cảnh báo Visual Studio C++ của `flutter doctor` chỉ dành cho bản Windows desktop, không chặn Android.

## Kiểm tra mã

```powershell
flutter analyze
flutter test
flutter build web
flutter build apk --debug
```

APK debug nằm ở `mobile/build/app/outputs/flutter-apk/app-debug.apk` và không được commit. Xem [hướng dẫn setup VS Code](../docs/06-mobile/T-018-vscode-local-setup.md) để kiểm từng bước trên máy.
