# T-012 — Chẩn đoán đường đi P1 trên proxy bbox LTFT

**Ngày:** 27/09/2026. **Mục đích:** kiểm liệu [báo cáo P0/P1 ở frame cuối](T-012-S4-ltft-box-proxy.md) có che các lần P1 tạm chọn sai ID ở frame giữa. Đây là **chẩn đoán hậu nghiệm trên đúng dữ liệu đã xem**, không là thí nghiệm xác nhận mới, không thay rule P1 và không chọn rule ứng dụng.

## Nguồn và gate

[Định nghĩa D1](../T-012-S4-box-only-proxy-protocol.md) được commit `7b5aac7` trước khi chạy chẩn đoán; [script phát lại](../../../scripts/t012_ltft_box_path_diagnostics.py) commit `9e4839e`. Hai file LTFT `choke1.txt`/`choke2.txt` cùng SHA-256 đã khóa trong [báo cáo chính](T-012-S4-ltft-box-proxy.md); parser kiểm hash/cấu trúc. Script phát lại outcome endpoint P1, yêu cầu khớp `384/17/94` ở Choke1 và `374/21/134` ở Choke2 trước khi thống kê đường đi. Gate đã qua. Không tải ảnh/video; file nhãn và JSON mức run chỉ ở thư mục tạm, không commit.

Với từng cửa sổ–ID, `ever-wrong` nghĩa là P1 **đã chọn box có ID khác target ít nhất một frame** sau frame khởi tạo. Chỉ ở lần sai đầu tiên, kiểm xem nhãn LTFT còn box `face=1` của target trong frame đó không. `Không có box` là thuộc tính của **annotation đã lọc**, không xác nhận người đã ra khỏi khung.

## Kết quả với mẫu số

| Nhóm | Cửa sổ–ID | Từng sai ID | Sai ở endpoint | Từng sai rồi unresolved | Từng sai rồi đúng lại | Lần sai đầu khi target còn box `face=1` | Lần sai đầu khi target không còn box `face=1` |
|---|---:|---:|---:|---:|---:|---:|---:|
| Choke1 | 495 | 18 | 17 | 1 | 0 | 0 | 18 |
| Choke2 | 529 | 23 | 21 | 2 | 0 | 0 | 23 |
| **Tổng** | **1.024** | **41** | **38** | **3** | **0** | **0** | **41** |

Số endpoint `38` khớp báo cáo chính; nếu chỉ đọc endpoint thì bỏ qua **3** trường hợp đã chọn sai ID rồi kết thúc `unresolved`. Không có trường hợp đã sai rồi trở lại `correct-track` ở endpoint trong protocol này. Trong **41/41** lần sai đầu, target không có box `face=1` tại frame sai đầu. Khi target có box lại về cuối, P1 vẫn có thể đang bám ID khác: trong báo cáo chính, **11/38** cửa sổ sai endpoint vẫn có box target ở frame cuối.

## Ý nghĩa và giới hạn

Kết quả hỗ trợ một uncertainty cụ thể: rule chỉ dựa vào overlap có thể **trôi sang người khác lúc box target bị mất trong annotation**, và sai lựa chọn có thể tồn tại sau khi target được ghi nhận trở lại. Đây là lý do phải đo lỗi dọc theo cửa sổ, không chỉ chấm một frame cuối. Tuy nhiên candidate **không biết ID ground truth**, nên không thể dùng nhãn “target đang thiếu” như một điều kiện runtime để né lỗi; cần một cơ chế quan sát/abstain có thể kiểm độc lập nếu tiếp tục nghiên cứu.

Bộ nhãn LTFT xuất phát từ detector rồi được kiểm/gán ID; thiếu box `face=1` có thể do che khuất, điều kiện ảnh, detection bỏ sót hoặc quy tắc loại box. Không có video khớp nhãn để phân xử nguyên nhân. Cùng ID có thể lặp trong nhiều cửa sổ; đây không phải mẫu độc lập, cũng không có claim–actor, camera phòng thi hoặc quyền vào phòng. Vì D1 được đặt **sau khi xem kết quả P0/P1**, không dùng phát hiện này để tuyên bố P1 đạt/không đạt yêu cầu nghiệp vụ hay chọn threshold/model cuối.

**Câu hỏi tiếp theo nếu có dữ liệu phù hợp:** khi bằng chứng liên kết track suy yếu hoặc mất trong vài frame, cách nào giữ `unresolved` thay vì âm thầm bám distractor, và đo trade-off wrong-target/coverage trên cùng lượt có nhãn người mục tiêu độc lập? Với nguồn hiện tại, chỉ chấm được proxy bbox, chưa chấm X-012-A nghiệp vụ.
