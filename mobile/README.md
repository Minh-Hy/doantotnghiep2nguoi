# Flutter app T-018

Đây là vỏ ứng dụng tham chiếu Android. Màn hình đầu kiểm tra API và DB, cho nhân sự đăng nhập rồi xem ca/phòng được cấp. Nút tiếp nhận vẫn khóa cho đến khi profile, luồng tạo lượt và camera/AI trên điện thoại được tích hợp. Không dùng màn hình này để xác nhận thí sinh.

```powershell
flutter pub get
flutter test
flutter build apk --debug
flutter run --dart-define=EXAM_API_BASE_URL=http://10.0.2.2:8000
```

`10.0.2.2` truy cập máy host từ Android emulator. Với thiết bị khác, truyền URL phù hợp qua `EXAM_API_BASE_URL`; bản phát hành cần HTTPS. Chỉ bản debug Android cho phép HTTP để kết nối máy phát triển. Không truyền token, mật khẩu hoặc dữ liệu thí sinh qua `--dart-define`.

Tài khoản nhân sự và ca giả lập tạo theo [backend/README.md](../backend/README.md). Token đăng nhập hiện chỉ ở bộ nhớ ứng dụng; chưa có hàng đợi offline hoặc lưu phiên an toàn qua lần khởi động lại. Theo [D-005](../docs/00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md), AI sẽ chạy trên Android và check-in chỉ có hiệu lực sau khi đồng bộ với backend và được nhân sự xác nhận; các phần đó chưa được triển khai ở mốc này.
