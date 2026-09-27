# T-009 — Kiểm tra khả dụng của dữ liệu và trọng số ứng viên

**Ngày kiểm tra:** 2026-09-26. **Người thực hiện:** Quốc An. **Trạng thái:** bàn giao để Minh Hy review; chưa chọn dataset, model, cấu hình hoặc giao thức đánh giá cuối cùng.

Nguồn và vị trí dùng lại khi viết báo cáo được ghi trong [sổ nguồn T-009](T-009-source-register.md).

## 1. Câu hỏi và ranh giới

[T-007](T-007-selection.md) chọn **hướng nghiên cứu T-005** cho bài toán cửa phòng thi, chứ không chọn các tên dataset/model trong T-005 làm giải pháp cuối. T-009 kiểm tra cổng **B0 — khả dụng**: nguồn, quyền dùng được công bố, file/annotation, trọng số, input/output, preprocessing và khả năng mở/chạy thử. B0 chỉ xác định candidate nào có thể tiếp tục chuẩn bị thí nghiệm; kết quả chạy trên dữ liệu thật thuộc task sau.

[T-008 đang được review riêng ở PR #3](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/3) mô tả generic business baseline. Vì chưa nằm trong `main`, các câu hỏi kỹ thuật TQ của bản đó chỉ là đầu vào **tạm thời**; nếu T-008 thay đổi, phải đối chiếu lại T-009 trước khi khóa protocol. Không sửa yêu cầu nghiệp vụ để làm một candidate kỹ thuật trở nên phù hợp. T-009 không chứng minh giảm nhân lực, không đánh giá độ chính xác, không đặt ngưỡng xác minh, không lựa chọn công nghệ triển khai.

| Nhu cầu từ T-005/T-008 dự thảo | Loại bằng chứng cần | Điều B0 có thể kết luận |
|---|---|---|
| S3 tìm mọi mặt trong ảnh cửa phòng | Ảnh nguyên khung, bbox/landmark, detector có đầu ra phù hợp | Dataset/weight có đường truy cập và schema phù hợp; chưa biết detector nào tốt hơn |
| S4 xác định người đang làm thủ tục | Claim + nhãn người mục tiêu giữa nhiều mặt | Các tập hiện khảo sát **chưa đủ** nhãn để chứng minh S4 trong cảnh đông |
| S7–S8 xác minh người với hồ sơ đã chọn | Identity, cặp genuine/impostor, reference/probe, encoder có weight và preprocessing rõ | Có thể chuẩn bị protocol 1:1; chưa biết FMR/FNMR hoặc threshold |
| S9–S10 kiểm tra ca/phòng/trùng lượt, ghi nhận và review | Fixture hồ sơ, policy, trạng thái mong đợi | Kiểm thử rule/app riêng; không cần dataset/model mặt |

**Mức bằng chứng dùng trong tài liệu:** `N` = tên/công bố được nêu trong survey; `S` = đã đối chiếu nguồn chính thức, quyền hoặc định dạng được công bố; `F` = đã kiểm tra byte/cấu trúc file thật; `R` = đã mở và chạy inference tối thiểu trên đầu vào tổng hợp. Mức cao hơn **không** có nghĩa là đã có benchmark hay được phép dùng trong mọi mục đích. Với dataset ảnh mặt, ở lượt B0 ban đầu T-009 chủ yếu đạt `S`; riêng file protocol cặp XQLFW đạt `F`, nhưng lúc đó chưa tải archive ảnh. Bằng chứng kiểm thêm trong T-010 được ghi riêng ở mục 4.1, không thay đổi mức bằng chứng của lượt B0. Với vài weight, đạt `F/R` trên máy hiện tại.

## 2. Audit dataset theo vai trò, không theo độ phổ biến

Quyền của **ảnh**, **annotation**, **mã đánh giá** và **trọng số** là các câu hỏi khác nhau. Một repo mã có license mở không tự cấp quyền dùng ảnh mặt hoặc checkpoint. Số lượng dưới đây là số do nguồn công bố, **chưa là số mẫu hợp lệ sau lọc**. `Cần xác minh` nghĩa là chưa khóa vai trò main/locked test; không tự động cấm phép thử học thuật thăm dò nếu tác giả công bố dữ liệu/weight để đánh giá. Quyền phân phối file hoặc triển khai thực tế được xét riêng.

| Candidate / stage và vai trò có thể | Nguồn, annotation/protocol đã xác nhận ở mức công bố | Quyền, file thực và domain gap | Kết quả B0 / việc kế tiếp |
|---|---|---|---|
| **WIDER FACE — S3 component** | [Trang tác giả](https://shuoyang1213.me/WIDERFACE/) là nguồn gốc; [Open Model Zoo](https://github.com/openvinotoolkit/open_model_zoo/blob/master/data/datasets.md) mô tả ảnh validation và `wider_face_val_bbx_gt.txt` | [Trang tác giả](https://shuoyang1213.me/WIDERFACE/) ghi CC BY-NC-ND; chưa kiểm archive và annotation thực. Ảnh sự kiện không đại diện đầy đủ camera cửa phòng. Không có claim/target S4 | `S` một phần; **cần xác minh** archive/nhãn và giữ đúng điều kiện CC BY-NC-ND trước benchmark detection |
| **FDDB — S3 external** | [Bài báo gốc](https://people.cs.umass.edu/~elm/papers/fddb.pdf) nêu ellipse annotation và 10 folds | Ellipse cần quy tắc chuyển/đánh giá riêng nếu so bbox. Archive và điều khoản ảnh chưa kiểm tra; không có claim 1:1 | `S` về protocol; **dự phòng**, chưa đưa vào run |
| **LFW — S8 smoke** | [Nguồn gốc UMass](http://vis-www.cs.umass.edu/lfw/) và protocol cặp ảnh 1:1 đã được T-005 xác định | Trang/ảnh và quyền dùng chưa kiểm tra được bằng file thật; ảnh web đã crop, không đo cửa phòng, detection hoặc S4 | `S` một phần; **chỉ smoke có điều kiện**, không làm bằng chứng triển khai |
| **XQLFW — S8 stress chất lượng** | [Trang tác giả](https://martlgap.github.io/xqlfw/) công bố 6.000 cặp, 3.743 identity, 7.263 ảnh; [protocol pairs](https://github.com/Martlgap/xqlfw/releases/download/1.0/xqlfw_pairs.txt) tải thật có header `10 300`, 6.000 dòng cặp: 3.000 genuine (3 trường) và 3.000 impostor (4 trường) | Ở lượt B0 của T-009 chưa tải ảnh/đối chiếu path pairs; điều khoản phân phối lại ảnh chưa rõ. Ảnh cặp không đo S3/S4; ảnh suy giảm khác miền camera thi | `F` **chỉ với file pairs**; ứng viên thử nghiệm 1:1 học thuật; kiểm ảnh/path ở T-010, ghi rõ protocol và giới hạn trước khi chạy |
| **YouTube Faces — S8 video 1:1** | [Trang tác giả](https://www.cs.tau.ac.il/~wolf/ytfaces/) công bố 3.425 video/1.595 người, 5.000 cặp và 10 splits, có errata | Tải qua biểu mẫu/credential; gói lớn. Chưa có byte, xác nhận quyền hoặc cách tái lập split đã sửa. Video chủ yếu person-centric, không có claim tại cửa | `S`; **hoãn**, không phụ thuộc vào tập này cho protocol gần hạn |
| **ChokePoint — S3/video/portal external** | [Trang tác giả](https://arma.sourceforge.net/chokepoint/) công bố 48 sequence, 64.204 ảnh mặt, raw frame/crop/ground truth và G1/G2; [README archive](https://zenodo.org/records/815657/files/README.txt) đã đọc | Nguồn ghi nghiên cứu phi thương mại và yêu cầu trích dẫn. Archive khoảng 12 GB **chưa tải**; cần kiểm mapping nhãn/reference–probe. Đa số frame một người; 2 sequence đông không đủ claim + target label của S4 | `S`; **ứng viên external có điều kiện**, không gọi là full end-to-end test |
| **DigiFace-1M — S7 nếu phải train/fine-tune** | [Repo tác giả](https://github.com/microsoft/DigiFace1M) nêu cấu trúc identity và nhiều phần tải | [R-UDA license](https://github.com/microsoft/DigiFace1M/blob/main/LICENSE) giới hạn nghiên cứu phi thương mại; synthetic → real gap, chi phí lưu trữ/train. Chưa tải | `S`; **chỉ mở nhánh train nếu experiment cho thấy cần**, không phải dataset mặc định |
| **WFLW / 300-W — S6 nếu landmark thành bottleneck** | [WFLW](https://wywu.github.io/projects/LAB/WFLW.html), [300-W](https://ibug.doc.ic.ac.uk/resources/300-W/) có nhãn landmark theo protocol riêng | Chưa tải/kiểm quyền/đổi schema. Landmark score riêng không tự chứng minh verification tốt hơn | `S`; **defer** cho đến khi S6 có câu hỏi đo rõ |
| **VGGFace2 — S7 nếu train** | [Repo tác giả](https://github.com/ox-vgg/vgg_face2) công bố 3,31 triệu ảnh/9.131 người và split | Đường tải/điều khoản dữ liệu hiện chưa xác minh; chi phí lớn và có thể trùng identity với benchmark | `S`; **không làm dependency** của baseline |
| **SCface / IJB-C** | [SCface](https://www.scface.org/) yêu cầu thỏa thuận/công văn có người đủ thẩm quyền ký; [NIST](https://www.nist.gov/itl/tted/btg/ijb-c-dataset-request-form) đã ngừng phân phối IJB-C từ 2023 | Không có đường truy cập độc lập phù hợp cho đồ án ở thời điểm audit | `S`; **loại khỏi kế hoạch phụ thuộc hiện tại** |

**Khoảng trống chung:** chưa có dataset public trong shortlist vừa có **claim đã chọn**, nhiều mặt cùng khung, nhãn **target của giao dịch**, roster/ca/phòng và kết quả được người có thẩm quyền xử lý. Các tập ảnh/video công khai chỉ đo stage có nhãn tương ứng. S4 cần fixture rule/ambiguous để kiểm logic, rồi đánh giá có nhãn domain-specific nếu nhóm có dữ liệu và quyền. Không được suy ra hiệu quả vận hành phòng thi từ điểm trên LFW/XQLFW/ChokePoint.

### 2.1. Kết quả tự kiểm quyền dữ liệu cho shortlist (2026-09-26)

Đây là đối chiếu điều kiện **được nguồn phát hành công bố**. `CONFIRMED` theo Quốc An ngày 2026-09-26: mục đích hiện tại là đồ án tốt nghiệp để học/nghiên cứu; nhóm chưa xác nhận việc dùng app trong một kỳ thi vận hành thật. Không suy rằng dữ liệu được phép đưa vào sản phẩm vận hành hoặc công bố lại ảnh. Quyền truy cập, quyền dùng ảnh, quyền dùng annotation và quyền phân phối là các câu hỏi riêng.

| Dữ liệu | Điều khoản/nguồn đã tìm được | Kết luận cấp candidate |
|---|---|---|
| WIDER FACE (S3) | [Trang tác giả](https://shuoyang1213.me/WIDERFACE/) ghi CC BY-NC-ND. | **Giữ để chuẩn bị benchmark detection phi thương mại**, kèm ghi nguồn; vẫn phải kiểm archive/nhãn. Không chia sẻ ảnh đã biến đổi hoặc dùng cho mục đích thương mại theo giấy phép này. |
| XQLFW (S8) | [Trang tải tác giả](https://martlgap.github.io/xqlfw/pages/download.html) cho tải ảnh và protocol; [MIT trong repo](https://github.com/Martlgap/xqlfw/blob/main/LICENSE) là nguồn mã, không thấy tuyên bố rõ áp dụng cho ảnh dẫn xuất LFW. | **Có thể thử benchmark xác minh 1:1 trong đồ án học thuật**: tác giả công bố archive/protocol và hướng dẫn đánh giá. File/path đã được kiểm thêm ở T-010. Chưa khẳng định quyền phân phối lại ảnh; chưa chọn làm main test vì split chính thức trùng identity và khác miền phòng thi. |
| ChokePoint (portal external) | [License tác giả](https://arma.sourceforge.net/chokepoint/) cho nghiên cứu phi thương mại, yêu cầu trích dẫn, giữ notice và đánh dấu bản dẫn xuất. | **Giữ external có điều kiện** cho đồ án phi thương mại; cần tải/kiểm nhãn và giữ notice. Không dùng như bằng chứng toàn quy trình. |
| DigiFace-1M (chỉ nếu train) | [R-UDA](https://github.com/microsoft/DigiFace1M/blob/main/LICENSE) giới hạn computational use cho nghiên cứu phi thương mại; không dùng dữ liệu/kết quả trong commercial offering. | **Hoãn** vì chưa có câu hỏi train; nếu mở nhánh train phải tuân điều khoản và kiểm dữ liệu thực. |
| FDDB, LFW, YTF, WFLW/300-W, VGGFace2 | Nguồn được khảo sát về task/protocol; quyền ảnh và đường tải dùng cho lần chạy cụ thể chưa được xác minh đủ ở T-009. | **Dự phòng/hoãn** theo vai trò đã ghi ở bảng trên; không âm thầm thay vào main test chỉ vì có tên trong survey. |

## 3. Audit trọng số theo vai trò và file cụ thể

`OpenCV 5.0.0`, `onnxruntime 1.20.1`, `mediapipe 1.0.0` có trên **máy kiểm tra hiện tại**; chưa có PyTorch. Máy này không phải thiết bị đích. Mọi phép chạy `R` dùng ảnh/tensor toàn số 0, chỉ chứng minh file mở được và đầu ra đúng kiểu, **không** chứng minh mặt thật được phát hiện hay xác minh.

| Candidate / vai trò | File, nguồn và preprocessing cần pin | Kiểm tra thực tế / quyền / quyết định B0 |
|---|---|---|
| **OpenCV YuNet — S3** | [OpenCV Zoo](https://github.com/opencv/opencv_zoo/blob/main/models/face_detection_yunet/README.md) có nhiều phiên bản; audit file `face_detection_yunet_2026may.onnx` từ [nguồn raw của repo](https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2026may.onnx). Không dùng Git LFS pointer 131 byte thay model. | `F/R`: 229.738 byte, SHA-256 `EBAFCE4E3C118D6554634BE5C27AB333B4C047A9A8C3FAF1D7CF93101C22F0F0`; `cv2.FaceDetectorYN` mở được, blank 320×320 không có detection. [Thư mục model](https://github.com/opencv/opencv_zoo/blob/main/models/face_detection_yunet/README.md) ghi mọi file trong thư mục theo MIT; giữ notice khi phân phối. **Giữ để benchmark S3 có điều kiện.** |
| **MediaPipe BlazeFace full-range — S3** | [Tài liệu Face Detector](https://developers.google.com/edge/mediapipe/solutions/vision/face_detector) nêu bbox + 6 keypoints; [model card](https://storage.googleapis.com/mediapipe-assets/MediaPipe%20BlazeFace%20Model%20Card%20(Full%20Range).pdf) nêu đầu vào/giới hạn/license Apache-2.0. File audit là bản `blaze_face_full_range/float16/latest` từ [nguồn phát hành](https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_full_range/float16/latest/blaze_face_full_range.tflite). | `F/R`: 1.083.786 byte, SHA-256 `3698B18F063835BC609069EF052228FBE86D9C9A6DC8DCB7C7C2D69AED2B181B`; MediaPipe Tasks mở được, blank 320×320 cho 0 detection. 6 keypoints **chưa được kiểm tra** khả năng map sang template encoder; model card chỉ mô tả face detection, không xác minh danh tính. **Giữ để benchmark S3 có điều kiện.** |
| **SCRFD-500MF + MobileFaceNet — S3/S7, tách hai component** | [InsightFace model zoo](https://github.com/deepinsight/insightface/blob/master/model_zoo/README.md) công bố pack `buffalo_sc`: detector SCRFD-500MF + encoder MBF@WebFace600K; [release](https://github.com/deepinsight/insightface/releases/tag/model-zoo) chứa zip. Encoder cần alignment 112×112 và pipeline màu/normalization đúng implementation phát hành, **chưa khóa ở T-009**. | `F/R`: zip 14.969.382 byte, SHA-256 `57D31B56B6FFA911C8A73CFC1707C73CAB76EFE7F13B675A05223BF42DE47C72`; `det_500m.onnx` 2.524.817 byte và `w600k_mbf.onnx` 13.616.099 byte mở/chạy tensor 0 bằng ONNX Runtime CPU; encoder xuất 512 chiều. Zoo ghi **non-commercial research only** cho models, kể cả pack này. **Giữ hai component như candidate có điều kiện**, không coi pack là pipeline đã chọn. |
| **EdgeFace XS — S7 compact khác họ** | [Repo tác giả](https://github.com/otroshi/edgeface) phát hành `edgeface_xs_gamma_06.pt` khoảng 7,17 MB, mô tả RGB aligned/normalization. | `S`: xác nhận file qua metadata repo, **chưa tải/chạy/export**; PyTorch chưa có. [BSD-3 của repo mã](https://github.com/otroshi/edgeface/blob/main/LICENSE) không thay thế [CC BY-NC-SA 4.0 của bản weight XS-GAMMA do Idiap phát hành](https://huggingface.co/Idiap/EdgeFace-XS-GAMMA); chưa đối chiếu hash giữa nguồn GitHub/Hugging Face. **Giữ trong pool, chưa qua runtime gate.** |
| **AdaFace R18 — S7 chất lượng ảnh** | [Repo tác giả](https://github.com/mk-minchul/AdaFace) có nhiều weight R18 theo training set, yêu cầu BGR 112×112/alignment. Phải chọn **một weight ID cụ thể** trước so sánh. | `S`: link weight qua Google Drive, **chưa xác minh tải hoặc chạy; điều khoản phân phối lại weight chưa rõ**. MIT của repo mã không xác nhận riêng quyền của weight trên Google Drive. **Cho phép chuẩn bị thử nghiệm học thuật**, nhưng chưa ghi kết quả vì chưa tải/pin đúng weight và chạy runtime. |
| **R50 trong `buffalo_l` — S7 reference** | [InsightFace zoo/release](https://github.com/deepinsight/insightface/blob/master/model_zoo/README.md) mô tả R50@WebFace600K trong pack lớn, kèm detector khác. | `S`: metadata release khoảng 289 MB; **chưa tải/chạy**, quyền non-commercial research theo zoo. Chỉ làm đối chứng nếu tài nguyên/protocol cho phép; không mặc định mạnh hơn trên domain này. |
| **RetinaFace mobile — S3 fallback** | [InsightFace zoo](https://github.com/deepinsight/insightface/blob/master/model_zoo/README.md) có hướng truy cập qua nguồn ngoài | `S` một phần; chưa pin weight, byte, runtime/quyền riêng. Chỉ mở nếu một detector chính không khả dụng hoặc B1 có câu hỏi mới. |

**Giới hạn so sánh:** YuNet, BlazeFace, SCRFD đều có đầu ra mặt/landmark nhưng schema và preprocessing khác nhau. MBF, EdgeFace, AdaFace và R50 không được so qua một crop tùy tiện; T-010 phải ghi rõ align/color/normalization/score theo từng weight. Kết quả blank-frame chỉ là kiểm khả dụng, không phải so detector hay encoder. Quyền của pack nghiên cứu phi thương mại phải được kiểm lại nếu phạm vi sử dụng thay đổi.

### 3.1. Kết quả tự kiểm quyền trọng số cho shortlist (2026-09-26)

- **YuNet:** [README riêng của model](https://github.com/opencv/opencv_zoo/blob/main/models/face_detection_yunet/README.md) ghi mọi file trong thư mục theo MIT. File ONNX đã pin ở bảng trên có thể tiếp tục thử S3 theo điều kiện license.
- **BlazeFace full-range:** [model card của Google](https://storage.googleapis.com/mediapipe-assets/MediaPipe%20BlazeFace%20Model%20Card%20(Full%20Range).pdf) ghi Apache-2.0 cho model, dùng để phát hiện mặt; nhận dạng danh tính nằm ngoài chức năng model này. Giữ cho S3, không quảng diễn thành verification.
- **SCRFD-500MF, MBF và R50 từ InsightFace:** [model zoo](https://github.com/deepinsight/insightface/blob/master/model_zoo/README.md) ghi **chỉ nghiên cứu phi thương mại** cho tất cả model. Có thể tiếp tục đánh giá trong đồ án theo phạm vi này, nhưng phải đánh giá lại quyền trước khi đóng gói/triển khai ngoài phạm vi nghiên cứu.
- **EdgeFace XS-GAMMA:** [Idiap phát hành đúng biến thể XS-GAMMA-06](https://huggingface.co/Idiap/EdgeFace-XS-GAMMA) với CC BY-NC-SA 4.0. Repo GitHub ghi BSD-3 cho mã; không dùng BSD-3 để mô tả quyền weight. Giữ candidate nghiên cứu phi thương mại, ưu tiên pin file từ bản phát hành có license rõ và kiểm checksum/runtime trước khi so sánh.
- **AdaFace R18:** [repo mã MIT](https://github.com/mk-minchul/AdaFace/blob/master/LICENSE) và [README link các weight R18](https://github.com/mk-minchul/AdaFace/blob/master/README.md), nhưng chưa tìm được tuyên bố riêng xác nhận điều khoản cho đúng file weight Google Drive sẽ dùng. Có thể tải đúng R18 từ link tác giả để thử nội bộ cho đồ án; pin weight/preprocessing/checksum trước khi báo kết quả. Quyền đóng gói hoặc phân phối lại weight vẫn cần xét riêng.
- **RetinaFace mobile fallback:** chưa pin file nên chưa có đối tượng để kết luận quyền. Không đưa vào run.

Quyền dùng không chứng minh model phù hợp nghiệp vụ, accuracy hay khả năng chạy trên thiết bị đích. Quyền dùng ảnh thí sinh thực tế, nếu nhóm thu thập sau này, là một quy trình riêng.

## 4. Manifest kiểm tra B0 ngoài Git

Các file nhị phân được tải **chỉ vào thư mục tạm trên máy kiểm tra**, không commit; đường dẫn tạm không phải cách bàn giao artifact. Cần tải lại từ link nguồn và đối chiếu hash khi chạy T-010. Không dùng ảnh mặt hoặc dữ liệu thí sinh thật ở lượt kiểm tra này.

| File / runtime | Kiểm tra đã làm | Kết quả và giới hạn |
|---|---|---|
| XQLFW pairs TXT / file protocol | Tải từ [release tác giả](https://github.com/Martlgap/xqlfw/releases/download/1.0/xqlfw_pairs.txt), đếm dòng và số trường mà không xuất tên người | 160.795 byte; SHA-256 `636852F90B886F3F56C73B13C9775F7FFCD37662DBB189C694F6A0A605B63B84`; header `10 300`, 6.000 cặp cân bằng 3.000/3.000; **chưa đối chiếu với archive ảnh** |
| YuNet ONNX / OpenCV 5.0.0 | Mở `FaceDetectorYN`, suy luận ảnh đen 320×320 | Mở thành công, không trả mặt; chưa kiểm accuracy/landmark trên ảnh thật |
| BlazeFace TFLite / MediaPipe 1.0.0 | Mở Tasks `FaceDetector`, suy luận ảnh đen 320×320 | Mở thành công, 0 mặt; chưa kiểm camera range, landmark mapping |
| `buffalo_sc.zip` / ONNX Runtime 1.20.1 CPU | Kiểm tên/size ONNX trong zip; mở detector và encoder, suy luận tensor 0 | Detector có score/box/landmark output; encoder `[1, 512]`, giá trị hữu hạn; chưa kiểm preprocess hoặc similarity thật |

### 4.1. Bằng chứng bổ sung từ T-010, không hồi tố kết luận B0

Ngày 2026-09-26, [T-010 (PR #6)](https://github.com/quocanwyf/doantotnghiep2nguoi/pull/6) kiểm thêm archive XQLFW ngoài Git: ZIP mở và kiểm CRC được; 6.000 cặp trong file protocol đều tham chiếu tới ảnh có trong archive. Đây là `F` cho **file ảnh và path của riêng XQLFW**, không phải runtime benchmark, xác nhận quyền dùng ảnh hay bằng chứng cho S3/S4/toàn bộ quy trình cửa phòng. T-010 cũng phát hiện 10 fold chính thức có identity trùng giữa các fold; vì vậy không được gọi chúng là split kiểm tra người chưa thấy. Chi tiết manifest, hash và phạm vi kết luận nằm ở T-010. XQLFW **có thể dùng cho phép thử học thuật pair-fold/stress** theo hướng dẫn tác giả; chưa được chọn làm main verification test vì official folds trùng identity và ảnh web/crop khác miền phòng thi. Việc tác giả cho tải để đánh giá không được diễn giải thành quyền phân phối lại ảnh hoặc dùng trong sản phẩm.

## 5. Quyết định T-009 và câu hỏi chuyển tiếp

**Kết luận cấp survey/B0 để nhóm review:**

1. **Đề xuất đưa vào chuẩn bị B1/B2 nếu phạm vi là nghiên cứu phi thương mại:** YuNet, BlazeFace full-range, SCRFD-500MF và MBF từ `buffalo_sc` vì đã qua `F/R` trên máy kiểm tra và đã có điều khoản weight công bố. Đây là đề xuất **cho thử**, không phải chọn cấu hình cuối. Mỗi component phải có wrapper/preprocessing được kiểm trên ảnh phù hợp; nếu phạm vi dùng khác nghiên cứu phi thương mại, rà lại điều kiện weight.
2. **Chuẩn bị thêm candidate B2:** EdgeFace XS đã có điều khoản bản Idiap nhưng chưa kiểm file/runtime; AdaFace R18 được tác giả hướng dẫn tải/inference và có thể thử học thuật sau khi pin file/runtime; R50 chưa tải/chạy và chỉ cho nghiên cứu phi thương mại; không đưa các tên này vào bảng điểm như thể đã chạy. RetinaFace mobile là fallback, không mở rộng benchmark vô lý.
3. **Dữ liệu:** WIDER FACE có điều khoản CC BY-NC-ND và là candidate detection cần kiểm file; ChokePoint có điều khoản nghiên cứu phi thương mại, giữ external có điều kiện. XQLFW có thể thử xác minh 1:1 trong đồ án học thuật theo protocol công bố. **Chưa chọn main verification test**: T-010 đã kiểm file/path XQLFW, nhưng official folds trùng identity và ảnh khác miền phòng thi; vai trò main/external và protocol cần chốt theo câu hỏi E2. LFW chỉ có thể là smoke; YTF tạm hoãn vì access. Không lấy một dataset làm đại diện tất cả stage.
4. **Không chọn dữ liệu train** khi chưa có kết quả baseline cho thấy cần train/fine-tune. SCface/IJB-C không là dependency. Stage rule/roster có fixture giả lập riêng.

| Câu hỏi phát sinh từ B0 | Việc phải có trước khi trả lời bằng experiment | Chủ trì task tiếp theo |
|---|---|---|
| B1: detector nào phù hợp ảnh nguyên khung và chi phí thực? | Tải/parse WIDER hoặc nguồn detection hợp lệ; pin output/landmark, cùng ảnh, cùng thiết bị và metric | T-010 thiết kế protocol; task thực nghiệm theo Sheet chạy |
| B2: encoder nào phân tách claim 1:1 ở cùng điều kiện? | Tải/parse cặp + quyền; tách dev/test, pin weight/preprocess/align; kiểm train/test identity overlap khi có thể | T-010 thiết kế protocol; thực nghiệm sau đó |
| S4: có thể chọn đúng người giữa nhiều mặt? | Claim + nhãn target theo giao dịch, không chỉ bbox; nếu thiếu chỉ kiểm logic ambiguous/review | T-010 ghi giới hạn; nghiên cứu dữ liệu riêng nếu cần |
| S9–S10: lỗi/uncertain dẫn tới outcome nào? | Baseline T-008 đã review, policy nào generic/configurable, fixture trạng thái và authority | Đối chiếu lại sau khi PR T-008 ổn định |
| Thiết bị và quyền dùng có phù hợp triển khai? | Thiết bị/compute mục tiêu và phạm vi sử dụng do nhóm xác nhận; kiểm license của từng artifact | Trước final technical decision/implementation |

Trace quyết định: [T-004 business scope](../00-project/decisions/T-004-D-001-chon-bai-toan-cua-phong-thi.md) → [T-005 stage/data/model requirements](T-005-quoc-an-task-decomposition.md) → [T-007 chọn hướng survey](T-007-selection.md) → **T-009 kiểm khả dụng** → T-010 đặt câu hỏi/split/metric/điều kiện thử → kết quả experiment → quyết định kỹ thuật cuối. Nếu T-008 generic baseline sau review đổi cách xác định candidate record hoặc yêu cầu verification, phải cập nhật mapping trước T-010; không sửa T-008 để hợp với weight đã tải.

## 6. Review cần thiết

- Đối chiếu lại phần quyền/shortlist đã được tự kiểm ở mục 2.1 và 3.1 nếu phạm vi sử dụng hoặc file candidate thay đổi; WIDER/LFW/ChokePoint chưa có archive ảnh được kiểm ở T-009; XQLFW có pairs và archive được T-010 kiểm, có thể dùng thử học thuật nhưng không được tuyên bố identity-disjoint hoặc đại diện phòng thi.
- Nhóm đối chiếu candidate với protocol T-010 đang được review riêng, rồi xác định dữ liệu và phương tiện thực sự có thể dùng cho thí nghiệm. Không lấy bảng này làm tuyên bố đã qua đủ B0 của dataset.
- Khi T-008 được review xong, đối chiếu lại ranh giới claim/record resolution, human authority và outcome trước khi khóa thí nghiệm.

## 7. Đối chiếu với mốc nghiệp vụ T-008 cho bước sau (2026-09-27)

Theo chỉ đạo trực tiếp của Quốc An ngày 2026-09-27, dùng T-008 PR #3 commit `c235b80` làm mốc nghiệp vụ cho T-009/T-010/T-011 trong lượt đối chiếu; không sửa T-008. Việc PR #3 chưa merge/review xong trên GitHub là trạng thái riêng, không đổi phạm vi quyết định **candidate để thử** của T-009. [Bảng đối chiếu đầy đủ ở T-011 PR #7](https://github.com/quocanwyf/doantotnghiep2nguoi/blob/codex/T-011-exploratory-baseline/docs/03-baseline/T-011-T008-T009-T010-trace-review.md).

- TQ-002/FR-006 dẫn đến S3 detection và S7–S8 verification 1:1 trong hướng nghiên cứu D-001/D-002. WIDER FACE chỉ có nhãn detection; XQLFW chỉ có nhãn cặp. Hai tập không chứng minh S4 chọn người mục tiêu, tra cứu hồ sơ, quyền vào hoặc attendance. TQ-003 về unavailable/inconclusive tạo yêu cầu báo coverage và nhánh review; không được biến cặp không chấm thành match/non-match.
- TQ-001 và TQ-004–007 là lookup, context/policy, duplicate, fallback, audit/attendance/correction. T-009 chỉ chỉ ra nhu cầu dữ liệu/fixture của chúng; **chưa audit nguồn roster hoặc triển khai các capability đó**. Không chọn model cho rule/database.
- TQ-008 cần đo vận hành thực; smoke runtime B0 không trả lời throughput hoặc công sức tại cửa. Các policy value/authority của kỳ thi cụ thể vẫn chưa có dù cấu trúc T-008 được dùng làm mốc.
- Evidence đến sau T-009 được giữ đúng thời điểm: T-011 đã kiểm file/nhãn WIDER FACE và chạy R50 trên XQLFW, nhưng đó không hồi tố biến shortlist B0 thành lựa chọn cuối. T-009 **giữ nguyên candidate**, chuyển các khoảng trống sang protocol/run tiếp theo.
