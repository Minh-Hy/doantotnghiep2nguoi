# T-018 — Tự dựng lại ứng dụng từng bước

**Ngày:** 2026-09-29. **Người làm:** Minh Hy; Quốc An review theo task T-018 trên Sheet. Đây là hướng dẫn thao tác cho Minh Hy, đi cùng [kế hoạch M0–M8](T-018-ke-hoach-trien-khai-app.md), [D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md) và [D-005](../00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md). Mã `backend/` và `mobile/` thử nghiệm đã gỡ theo yêu cầu; các commit cũ trong PR #9 vẫn có thể xem lại. Không coi test của mã cũ là kết quả của mã tự dựng.

## Trước khi bắt đầu

1. Mở thư mục gốc `D:\WorkSpace\doantotnghiep2nguoi` trong VS Code, mở **Terminal → New Terminal** và chọn PowerShell. Mọi lệnh dưới đây bắt đầu từ thư mục gốc, trừ khi có `Set-Location`.
2. Đóng cửa sổ Notepad đang mở `backend/README.md` và mọi terminal đứng trong `backend/`. Thư mục `backend/` rỗng có thể còn bị Windows khóa; sau khi đóng, xóa thư mục rỗng đó trong Explorer hoặc PowerShell: `Remove-Item -LiteralPath .\backend`. Không dùng `-Recurse` cho bước này.
3. Kiểm tra công cụ: `uv --version`, `flutter --version`, `flutter doctor`, `flutter devices`. Nếu `flutter doctor` còn lỗi Android SDK/license, xử lý theo dòng báo lỗi trước khi build app.
4. PostgreSQL 18 cục bộ, role/database `exam_entry` và schema từ lần thử trước **vẫn còn**. Chưa chạy migration của mã mới lên database này. File `.env.t018-backup` ở thư mục gốc là bản sao cấu hình cũ, bị Git bỏ qua; giữ kín, không gửi lên Git hoặc chụp màn hình nội dung. Khi đến M2, tạo database phát triển mới hoặc đối chiếu migration cũ rồi mới dùng lại database cũ.

## Bước 1 — M0: ghi hợp đồng giả lập trước khi viết luồng nghiệp vụ

Đọc [T-008](../01-problem/T-008-requirements.md), [E3](../03-baseline/T-010-E3-fixture-contract.md), [D-005](../00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md) và [câu hỏi mở](../00-project/questions.md). Tự tạo tài liệu task `docs/06-mobile/T-018-profile-ca-thi-gia-lap.md`, ghi rõ:

- Một ca học phần giả lập, một phòng, roster và mã giả; version của roster/policy, vai trò nhân sự tại cửa và người review.
- Các trạng thái attempt, bốn outcome AI, trường hợp không có/nhiều mặt, một lần thử lại rồi chuyển review.
- Khi mất mạng: máy giữ **chờ đồng bộ**; backend kiểm lại và nhân sự xác nhận thì check-in mới có hiệu lực. Attempt, check-in, quyền vào phòng và attendance là bốn kết quả riêng.
- Với mỗi nhánh: đầu vào, người có quyền, kết quả, mã lỗi/bước tiếp, dữ liệu cần audit. Đánh dấu `TBD` cho quy tắc giờ đến, override, retention, thiết bị Android và policy thật chưa được quyết định.

Đưa bản profile cho Quốc An review. Chỉ gọi M0 xong khi hai người thống nhất phiên bản profile và ghi nguồn/ngày; chưa cần chờ kỳ thi thật để dựng khung M1.

## Bước 2 — M1a: tự tạo khung backend

Từ terminal ở thư mục gốc, gõ từng lệnh và xem kết quả sau mỗi lệnh:

```powershell
uv init --bare --no-workspace backend
Set-Location backend
uv add django djangorestframework "psycopg[binary]"
uv run django-admin startproject config .
uv run python manage.py startapp entry
uv run python manage.py check
Set-Location ..
```

`backend/` cần có `pyproject.toml`, `uv.lock`, `manage.py`, `config/` và `entry/`. Chưa chạy `migrate` hoặc `createsuperuser`: cấu hình database của project mới chưa được nối với PostgreSQL. Trong VS Code, tự đọc `config/settings.py`, `config/urls.py` và `entry/apps.py` để biết chức năng từng file.

Sau khung chạy được, tự chia backend theo thứ tự: **settings từ biến môi trường → health/readiness → model và migration → service nghiệp vụ → serializer/API → quyền và test**. Trước mỗi API, ghi request/response, mã lỗi, quyền, idempotency và trạng thái trong profile; không để view tự quyết định nghiệp vụ. Chỉ dùng dữ liệu giả. Bằng chứng M1a: `manage.py check` thành công và bạn giải thích được vai trò của 3 file trên.

## Bước 3 — M1b: tự tạo khung Flutter Android

Trở lại terminal ở thư mục gốc:

```powershell
flutter create --platforms=android --project-name exam_entry mobile
Set-Location mobile
flutter analyze
flutter test
flutter devices
Set-Location ..
```

`mobile/` cần có `pubspec.yaml`, `lib/main.dart`, `android/` và `test/`. Mở một emulator Android hoặc cắm điện thoại có USB debugging; khi `flutter devices` nhìn thấy máy, chạy `flutter run` từ `mobile/` để xem ứng dụng mặc định. Sau đó tự thay màn hình mẫu bằng Material 3 và chia `lib/` thành `app/`, `core/` và `features/`; bước đầu chỉ cần trạng thái kết nối và màn hình đăng nhập/chọn ca. Không đưa mật khẩu vào `--dart-define` hoặc mã nguồn.

## Bước 4 — M2 đến M7: mỗi lần chỉ qua một cổng

| Mốc | Bạn tự làm | Bằng chứng trước khi sang mốc sau |
|---|---|---|
| M2 | Tạo database phát triển sạch trong pgAdmin, cấu hình `.env` bị Git bỏ qua, chạy migration; tạo user và fixture ca/phòng/roster giả; nối đăng nhập và context Flutter. | Đăng nhập đúng/sai, quyền theo ca/phòng, readiness và migration trên PostgreSQL thật. |
| M3 | Nhập mã, tạo attempt trước lookup, nhánh sai/thiếu/trùng phòng, idempotency và audit. | Chạy fixture hợp lệ và ngoại lệ; lookup không tự ghi check-in. |
| M4 | Đo B0 trên Android đích, rồi tích hợp camera và adapter AI 1:1 trên máy. | Không mặt, nhiều mặt, lỗi camera/AI và một lần thử lại đều vào nhánh đã ghi; không commit ảnh/weight. |
| M5 | Backend đánh giá policy, nhân sự xác nhận check-in, reviewer xử lý ngoại lệ. | Test quyền, retry, mạng lỗi, hai request đồng thời; không tạo hai check-in. |
| M6 | Đối soát và correction có audit, không suy attendance từ việc thiếu check-in. | Fixture E3-F07 và F09–F12 theo profile đã duyệt. |
| M7 | Kiểm E3-F01–F12 và chuỗi trên emulator/thiết bị Android được nêu tên. | Ghi pass/fail/not-runnable, cấu hình, phiên bản, dữ liệu và giới hạn; Quốc An review. |

Khi hoàn thành một phần, lưu commit nhỏ cùng tài liệu và ghi cách kiểm. Nếu gặp lỗi ở bất kỳ lệnh nào, giữ nguyên thông báo lỗi, ghi lệnh vừa chạy và đường dẫn terminal hiện tại để cùng xử lý trước khi sang bước sau.
