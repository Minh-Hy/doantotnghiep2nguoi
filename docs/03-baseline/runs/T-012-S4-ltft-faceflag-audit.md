# T-012 — D2: kiểm ID mục tiêu trong nhãn thô tại lần P1 chọn sai đầu tiên

**Ngày:** 27/09/2026. **Phạm vi:** audit hậu nghiệm trên cùng 1.024 cửa sổ–ID LTFT của [proxy bbox](T-012-S4-ltft-box-proxy.md) và [chẩn đoán D1](T-012-S4-ltft-path-diagnostic.md). D2 chỉ phân biệt hai dạng thiếu box trong annotation; không phải phép thử độc lập hoặc đo lượt check-in.

## Câu hỏi, nguồn và cách kiểm

[Định nghĩa D2](../T-012-S4-box-only-proxy-protocol.md) được ghi tại commit `b8f1afb` trước khi đọc hai nhóm kết quả; [script audit](../../../scripts/t012_ltft_faceflag_audit.py) ở commit `3d5930c`. Script phát lại P1 đến **frame đầu tiên chọn ID khác target** trong từng cửa sổ, rồi đọc dòng nhãn thô của chính frame đó: còn detection mang target ID với `face=0`, hay không có detection mang target ID. Hai nhóm phải cộng đúng số D1: Choke1 `18`, Choke2 `23`.

Nguồn: `annotations_IJCB/choke1.txt` và `choke2.txt` tại [LTFT commit `2c481e8`](https://github.com/hertasecurity/LTFT/tree/2c481e807be5cae53c5a056f39e1f1107628f1f6/annotations_IJCB). SHA-256 lần lượt `e79b7eccd835a449505d6998112b5104a480abec0b5f6cd0d69162b846222274` và `0b91483182869ba513164c23b587f3078fa7810966aec1858c61fc446b40d3d2`. Parser kiểm hash, số frame và cấu trúc dòng trước khi audit; tổng first-wrong khớp D1. Hai file nhãn chỉ được đọc trong thư mục tạm; Git chỉ chứa số tổng hợp.

## Kết quả

| Chuỗi | Cửa sổ–ID D1 | Lần sai ID đầu | Có target ID với `face=0` | Không có target ID trong dòng thô |
|---|---:|---:|---:|---:|
| Choke1 | 495 | 18 | 0 | 18 |
| Choke2 | 529 | 23 | 0 | 23 |
| **Tổng** | **1.024** | **41** | **0** | **41** |

Trong **41/41 lần sai đầu**, target ID vắng khỏi **dòng nhãn thô** của frame tương ứng; không chỉ bị loại bởi bộ lọc `face=1`. Đây là phân nhóm của 41 ca D1, **không** là 41 người hay 41 lượt vào phòng. P1 vẫn nhận box/IoU mà không nhận ID ground truth; script chỉ dùng ID để chấm sau đó.

## Diễn giải và giới hạn

Kết quả loại trừ một cách giải thích hẹp: không có ca nào trong 41 ca mà target ID vẫn được ghi trong dòng nhãn nhưng bị bỏ đi chỉ vì cờ `face=0`. Nó **không xác định** người thật có ở trong khung hay không, detector bỏ sót, bị che khuất, lỗi gán ID, hoặc nguyên nhân khác. LTFT tạo nhãn từ detection và kiểm/gán ID thủ công; video Zenodo hiện chưa ghép đáng tin với từng frame nhãn để quan sát nguyên nhân. `face=0` cũng không mặc nhiên là một mặt target hợp lệ theo [README LTFT](https://github.com/hertasecurity/LTFT).

D2 được đặt sau khi đã thấy D1; cùng cửa sổ, cùng nhãn, không split xác nhận độc lập. Vì proxy dùng box mục tiêu khởi đầu do nhãn cấp, thiếu claim–actor và camera phòng thi, D2 không chọn P1, model hay ngưỡng cho ứng dụng. Câu hỏi tiếp theo có giá trị là cách một candidate **không biết ID ground truth** phát hiện bằng chứng liên kết suy yếu để trả `unresolved`; muốn chấm quyết định nghiệp vụ X-012-A cần nguồn có claim và nhãn người mục tiêu độc lập theo [hợp đồng dữ liệu](../T-012-X-012-A-label-contract.md).
