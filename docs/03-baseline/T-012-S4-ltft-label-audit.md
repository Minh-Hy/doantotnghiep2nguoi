# T-012 — Audit nhãn LTFT cho phép thử proxy S4

**Ngày kiểm:** 27/09/2026. **Trạng thái:** đã kiểm file nhãn và cấu trúc archive video S5 công khai; **chưa xác lập được mapping frame–nhãn, nên proxy chưa chạy được**. Chưa trích xuất/kiểm nội dung ảnh, chưa chạy candidate và chưa có kết quả S4. Đây là audit khả năng dùng **dữ liệu có sẵn**, không phải quyết định chọn dataset/model cuối.

## Vì sao kiểm nguồn này

T-008 yêu cầu phân biệt người đang kiểm tra với người nền, và T-012 phát hiện XQLFW chỉ có cặp ảnh nên không chấm được chọn người trong cảnh nhiều mặt. [Bài báo LTFT](https://arxiv.org/pdf/2010.08675) công bố ground truth track trên video đông người; [repository của tác giả](https://github.com/hertasecurity/LTFT) dẫn tới hai chuỗi ChokePoint S5 ghi ở lối đi. Vì vậy LTFT là ứng viên **proxy liên kết/chọn một track đã chỉ định giữa nhiều người**. Nó không cung cấp claim/hồ sơ thí sinh hay ranh giới lượt check-in.

## Bằng chứng kiểm file

Đọc trực tiếp `annotations_IJCB/choke1.txt` và `choke2.txt` tại commit LTFT `2c481e807be5cae53c5a056f39e1f1107628f1f6`. Mỗi dòng sau header chứa frame index, số detection, rồi các bộ `ID, x, y, width, height, face flag, confidence` theo README. Parser kiểm số trường `2 + 7 × số detection`; không lưu file nhãn hoặc ảnh trong Git. `face=1` được tính là box mặt hợp lệ cho bảng dưới; `face=0` không được tính là mặt mục tiêu. Đây chỉ là kiểm **nhãn**, chưa phải kiểm frame/video.

| Nguồn | SHA-256 file nhãn | Frame / khai báo | Frame ≥2 face=1 | Frame 1 face=1 | Frame 0 face=1 | Box face=1 | ID có face=1 |
|---|---|---:|---:|---:|---:|---:|---:|
| Choke1 | `e79b7eccd835a449505d6998112b5104a480abec0b5f6cd0d69162b846222274` | 2.526 / 2.526 | 1.768 | 224 | 534 | 7.881 | 24 |
| Choke2 | `0b91483182869ba513164c23b587f3078fa7810966aec1858c61fc446b40d3d2` | 2.139 / 2.139 | 1.678 | 139 | 322 | 8.509 | 26 |

Hai file đều có **0 dòng sai số trường**. Số ID có `face=1` khớp số subject 24/26 trong README; ID của box `face=0` được loại khỏi phép đếm subject. Bài báo cho biết box ban đầu do detector tạo ở confidence >0,50, sau đó được kiểm thủ công và gán track/ID. Do đó đây là nhãn đã kiểm/gán ID, nhưng **không phải toàn bộ mặt xuất hiện trong video**: lỗi bỏ sót ở bước detector nguồn có thể không được gán nhãn. Không dùng nó để ước lượng recall detector trên mọi mặt, hoặc mặc định box ngoài annotation là false positive.

## Quyền dùng và giới hạn

- [ChokePoint của tác giả gốc](https://arma.sourceforge.net/chokepoint/) cho phép dùng/copy/phân phối cho nghiên cứu phi thương mại, yêu cầu dẫn NICTA và bài báo gốc, giữ thông báo giấy phép và đánh dấu bản dẫn xuất. Trang này liệt kê P2E_S5/P2L_S5; chỉ tải lần lượt từng archive theo hướng dẫn nguồn. Không commit ảnh/video lên repo.
- Repository LTFT công bố file nhãn và hướng dẫn dựng Choke1/Choke2 từ các camera S5, nhưng API GitHub trả `license: null` và repo không có file LICENSE ở root tại lần kiểm này. Vì vậy **quyền tái phân phối/biến đổi file nhãn LTFT chưa rõ**. Chỉ dẫn link/metadata tổng hợp trong repo; trước khi chia sẻ file nhãn hoặc sản phẩm dẫn xuất cần xác minh điều khoản với chủ sở hữu. Việc file có thể tải công khai không tự tạo một giấy phép mở.
- Choke1/Choke2 nối ba camera/đoạn theo thứ tự riêng của LTFT. Phải xác minh khớp số frame, thứ tự và kích thước bbox trên video gốc trước khi chấm; không gán ID bằng vị trí gần nhất từ bản XML ChokePoint cũ vì archive đó không có S5.
- LTFT không có claim–actor, người mục tiêu theo transaction, attendance hay quyền vào phòng. Số nhiều mặt nói trên chỉ chứng minh **khả năng xây proxy**, chưa chứng minh A1/A2 hoạt động hoặc cải thiện nghiệp vụ. Trường hợp `face=0`/không box không tự động là “target vắng”; đó có thể là giới hạn của annotation.

## Kiểm cấu trúc video Zenodo: hiện không khớp hướng dẫn LTFT

Tải tuần tự hai archive S5 đúng [record Zenodo](https://zenodo.org/records/815657) về thư mục tạm, xác nhận MD5 gốc rồi chỉ đọc **tên file** trong tar lồng nhau, không trích xuất ảnh:

| Archive | Kích thước / MD5 đã kiểm | Cấu trúc thực thấy | Số frame từ tên file | Nhãn LTFT tương ứng |
|---|---|---|---:|---:|
| `P2E_S5.tar.xz` | 180.516.452 byte / `e6bca312e40ebebdfb709f2315eebf80` | `C1.1`, `C2.1`, `C3.1`, mỗi thư mục 808 JPG | 2.424 nếu nối ba camera | Choke1: 2.526 |
| `P2L_S5.tar.xz` | 143.729.848 byte / `14b28f3d83a75b62d3aa6ad5ee117843` | `C1.1`, `C2.1`, `C3.1`, mỗi thư mục 757 JPG | 2.271 nếu nối ba camera | Choke2: 2.139 |

[README LTFT](https://github.com/hertasecurity/LTFT) yêu cầu ghép `C1.2 → C1.1 → C1.3` cho từng video, nhưng archive Zenodo mà chính README trỏ tới chỉ chứa `.1` của ba camera. Mặt khác, tổng frame từ tên file cũng lệch 102 (Choke1) và 132 (Choke2) so với header nhãn. **Chưa biết** đây là lỗi hướng dẫn, bản archive khác, cắt/nhân frame hay quy ước tên riêng; không tự đoán phép đổi chỉ số. Vì vậy **không thể ghép bbox/ID LTFT lên frame Zenodo một cách có căn cứ ở hiện trạng**. Không chạy proxy hoặc báo wrong-track/coverage từ hai nguồn này trước khi tìm được mapping có thể kiểm độc lập.

## Bước tiếp có thể làm bằng dữ liệu sẵn có

1. Tìm bản frame/video hoặc hướng dẫn dựng Choke1/Choke2 đúng 2.526/2.139 frame từ nguồn tác giả, hoặc bằng chứng độc lập cho mapping từng frame; kiểm vài mốc đầu/giữa/cuối, camera order, fps và bbox alignment trước khi khóa manifest. Nếu không giải được sai khác ở trên, LTFT `not runnable` cho proxy có ảnh.
2. Định nghĩa proxy trước khi xem output: chọn target ID từ nhãn tại đầu một cửa sổ, chỉ truyền **vị trí quan sát ban đầu** cho candidate; chấm việc giữ đúng track ở frame sau, `wrong-track` và `unresolved` trên cùng cửa sổ. Không đưa ID nhãn hoặc tọa độ tương lai vào candidate.
3. Tách cửa sổ dev/test theo video hoặc ID nếu khả thi; kiểm ID có thể xuất hiện giữa Choke1/Choke2 và frame chồng lặp trước khi nói split độc lập. Khóa cách lấy mẫu, mẫu số và điều kiện chấp nhận trước test.
4. Nếu chỉ có nhãn mà không có frame đúng hoặc không rõ quyền chạy/chia sẻ, dừng ở audit. Nếu proxy chạy được, tên/report phải ghi **LTFT tracking proxy**, không gọi là X-012-A nghiệp vụ hay hiệu quả cửa phòng.
