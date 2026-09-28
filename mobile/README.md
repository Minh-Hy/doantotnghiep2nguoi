# Flutter app T-018

Đây là vỏ ứng dụng tham chiếu. Màn hình đầu kiểm tra kết nối API; nút bắt đầu lượt giữ khóa cho đến khi có đăng nhập, context được duyệt và camera/AI được tích hợp. Không dùng màn hình này để xác nhận thí sinh.

```powershell
flutter pub get
flutter test
flutter build apk --debug
flutter run --dart-define=EXAM_API_BASE_URL=http://10.0.2.2:8000
```

`10.0.2.2` truy cập máy host từ Android emulator. Với thiết bị khác, truyền URL phù hợp qua `EXAM_API_BASE_URL`; bản phát hành cần HTTPS. Chỉ bản debug Android cho phép HTTP để kết nối máy phát triển. Không truyền token, mật khẩu hoặc dữ liệu thí sinh qua `--dart-define`.
