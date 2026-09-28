# Giai đoạn 06 — ứng dụng mobile

[D-004](../00-project/decisions/T-018-D-004-chon-stack-app-tham-chieu.md) ghi lựa chọn Flutter + Django REST Framework + PostgreSQL và B0 của Quốc An cho app tham chiếu. [T-018](T-018-app-reference.md) ghi luồng, ranh giới AI/nghiệp vụ và các điều kiện còn mở. Nơi chạy AI (on-device/server) vẫn phải được quyết định theo thiết bị và yêu cầu vận hành, không suy từ stack backend.

**Kiểm thử tối thiểu dự kiến:** mở app → camera hoạt động → xác minh 1:1 → ghi attempt/check-in hoặc chuyển review → xem kết quả. Khi có mã, bổ sung hướng dẫn build, thiết bị đã thử và giới hạn thực tế.
