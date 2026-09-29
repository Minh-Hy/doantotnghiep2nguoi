# T-018 — Profile ca thi học phần giả lập

**Phiên bản tài liệu:** `0.2-dev`, ngày 2026-09-29. **Trạng thái:** Minh Hy đã chọn phương án này làm fixture phát triển theo [D-006](../00-project/decisions/T-018-D-006-profile-gia-lap-cho-phat-trien.md); Quốc An còn review. **Chưa được phê duyệt để chấm E3 hoặc vận hành/check-in.** **Task:** T-018 trên [Sheet chung](https://docs.google.com/spreadsheets/d/14BQCQ_LbGkZS15Grfi4AZNWBX15h479XjoyQvP9jHcU/edit?gid=0#gid=0), Minh Hy phụ trách, Quốc An review. **Người/ngày chọn fixture phát triển:** Minh Hy, 2026-09-29. **Người/ngày phê duyệt profile cho E3:** `TBD`.

## 1. Nguồn, phạm vi và cách đọc

- [T-008](../01-problem/T-008-requirements.md) là **baseline nghiệp vụ generic**: tạo attempt trước tra cứu, kiểm context và quyền, tách attempt/check-in/entry/attendance, giữ ngoại lệ/audit/correction. Các giá trị policy trong T-008 là ví dụ, không tự trở thành quy chế.
- [E3](../03-baseline/T-010-E3-fixture-contract.md) yêu cầu pin profile và expected outcome **trước khi chạy** fixture F01–F12; bốn outcome AI chỉ là bằng chứng kỹ thuật, không phải quyết định nghiệp vụ.
- [D-005](../00-project/decisions/T-018-D-005-pham-vi-android-ai-tren-may.md) đã chọn Android trước, B0 trên điện thoại, một ca học phần giả lập, check-in sau đồng bộ và xác nhận của nhân sự. Không thấy mặt, nhiều mặt hoặc AI lỗi được thử lại một lần rồi chuyển người xử lý.
- [Câu hỏi mở](../00-project/questions.md) và OQ-001–OQ-023 của T-008 vẫn giữ nguyên. Tài liệu này chỉ đề xuất **fixture mô phỏng** để nhóm duyệt; không mô tả một trường, môn, kỳ thi hay quy chế thật.

Quy ước: **ĐÃ CHỌN** là nội dung của D-005; các dòng **ĐỀ XUẤT** đã được Minh Hy chọn để xây fixture theo D-006 nhưng còn chờ Quốc An review trước E3; **TBD** là phần chưa thể coi là policy. Thiếu policy/quyền cần thiết thì giữ `unresolved`/review, không tự điền giá trị mặc định. Chỉ khi hai thành viên ghi người, ngày và phiên bản đồng ý ở mục 8 mới được dùng profile này để chấm E3.

## 2. Context và roster mô phỏng

| Trường | Giá trị của fixture | Trạng thái |
|---|---|---|
| `exam_key` | `EXAM-SIM-01` — kỳ thi học phần giả lập, không gán tên trường/môn thật | ĐỀ XUẤT |
| `session_key` | `SESSION-SIM-01` — một ca giả lập | ĐỀ XUẤT |
| `room_key` | `ROOM-SIM-01` — một phòng giả lập | ĐỀ XUẤT |
| Trạng thái tiếp nhận | `SETUP` trước khi role có quyền mở; `OPEN` chỉ khi readiness đạt | ĐỀ XUẤT theo T-008 P-003 |
| `roster_version` | `R-SIM-001-draft`; nguồn là fixture do nhóm tạo, chưa là roster chính thức | ĐỀ XUẤT |
| `policy_version` | `P-SIM-001-draft`; **chưa có hiệu lực** trước review/phê duyệt | ĐỀ XUẤT |
| Mốc giờ ca/arrival window | `TBD` — không tự đánh dấu đúng giờ/muộn hoặc mở check-in khi cần rule này | Câu hỏi mở OQ-002 |

Roster bình thường để thử tra cứu, không chứa tên/ảnh/danh tính người thật:

| `registration_key` | Mã khai báo giả | Phân công trong fixture | Mục đích |
|---|---|---|---|
| `REG-SIM-001` | `SIM001` | `SESSION-SIM-01` / `ROOM-SIM-01` | Nhánh hợp lệ |
| `REG-SIM-002` | `SIM002` | `SESSION-SIM-01` / `ROOM-SIM-01` | Nhánh lượt lặp/check-in trùng |

Các biến thể kiểm lỗi là **bản fixture riêng**, không âm thầm sửa roster bình thường: `SIM404` không có record; `SIMDUP` ánh xạ tới hai `registration_key` khác nhau; `SIMROOM` thuộc `ROOM-SIM-OTHER`; `SIMSESSION` thuộc `SESSION-SIM-OTHER`. Mỗi biến thể phải ghi version và nguồn roster của chính nó trước khi chạy. Registration key là khóa nguồn ổn định; mã khai báo có thể trùng, nên không dùng mã khai báo làm khóa duy nhất. Roster cũ/đã đổi không được viết lại lịch sử attempt (T-008 BR-001/016; E3-F02/F03/F09).

## 3. Phạm vi kết quả và vai trò

| Đối tượng | Ý nghĩa trong profile bản đầu |
|---|---|
| **Attempt** | Một lượt tiếp nhận có `attempt_id`, context, version roster/policy, thời điểm và actor; tạo **trước khi** lookup, kể cả khi không tìm thấy hồ sơ. |
| **Check-in có hiệu lực** | Chỉ có sau khi backend đã nhận/kiểm điều kiện, nhân sự tại cửa được cấp quyền bấm xác nhận và DB ghi thành công. Tối đa một kết quả hiệu lực cho một registration/ca. |
| **Entry authorization** | `not_applicable` trong bản đầu theo D-005; không suy từ check-in là đã được phép/đã qua cửa. |
| **Attendance** | Không tự kết luận ở bản đầu; để `UNFINALIZED`. Đối soát/định nghĩa nguồn đủ căn cứ thuộc mốc sau, nên thiếu check-in không là `ABSENT_CONFIRMED`. |

| Vai trò mô phỏng | Quyền đã có nguồn | Phần còn chờ review |
|---|---|---|
| **Nhân sự tại cửa / operator** | Theo D-005: xem kết quả và **xác nhận** check-in khi đủ điều kiện, sau đồng bộ; thao tác chỉ trong context được cấp. | Ai cấp quyền mở/đóng ca, xem những trường dữ liệu nào, có được ghi fallback không: `TBD`. |
| **Người nhận case / reviewer** | Theo D-005: nhận các trường hợp thiếu/trùng mã, sai phòng, xác minh không đạt/không rõ sau retry. | Mapping người trực, loại case được quyết, quyền kết luận/override và tuyến thay thế: `TBD`. Không mặc định reviewer được override. |
| **Roster owner / profile approver** | T-008 tách trách nhiệm xác nhận roster và phê duyệt policy. | Người thật được giao quyền, hiệu lực phiên bản và quyền cập nhật: `TBD`. Hai thành viên review profile **thử nghiệm** không thay thẩm quyền của trường. |
| **Hệ thống/AI** | Tạo attempt, áp rule đã duyệt, ghi trạng thái/bằng chứng và cảnh báo. | Không tự cấp quyền vào, tự kết luận attendance, tự override hoặc tự ghi check-in từ điểm AI. |

Trước khi gọi context là `OPEN`, cần roster có nguồn/phiên bản, policy cần cho scope được duyệt, operator và người nhận review có phạm vi quyền rõ, audit hoạt động và đường fallback được xác định. Thiếu bất kỳ điều kiện bắt buộc nào thì giữ `SETUP`/`unresolved` (T-008 P-001–P-003; E3-F09).

## 4. Trạng thái và bằng chứng AI

**Attempt** dùng lifecycle nghiệp vụ T-008: `STARTED → IN_PROGRESS → CONCLUDED` hoặc `INTERRUPTED`. Attempt `CONCLUDED` có thể là check-in, chuyển review hoặc chưa hoàn tất; bản thân trạng thái đó không chứng minh check-in. Khi người quay lại sau `INTERRUPTED`, tạo lượt mới liên kết lượt cũ.

**Check-in** giữ riêng `UNRECORDED`, `REVIEW_PENDING`, `RECORDED`, `DISPUTED`. `RECORDED` là kết quả đã được backend ghi và xác nhận; nếu có mâu thuẫn sau đó, mở case/correction và giữ bản gốc. Các cờ `WRONG_ROOM`, `WRONG_SESSION`, `LATE`, `CLOCK_UNTRUSTED` độc lập với trạng thái chính.

| `identity_evidence_outcome` | Ý nghĩa / ví dụ trong fixture | Bước tiếp dự kiến |
|---|---|---|
| `satisfied` | Kiểm tra 1:1 đáp ứng điều kiện **đã được profile/thiết bị duyệt**. Không tự có check-in. | Backend kiểm context, policy, version, quyền và trùng; operator xem rồi xác nhận nếu đủ. |
| `unmet` | Kiểm tra chạy được nhưng không đáp ứng điều kiện được duyệt. Không kết luận gian lận. | Tạo review; cách kiểm bổ sung do người có quyền quyết, không tự cho check-in. |
| `unavailable` | Không có đầu vào dùng được hoặc AI/camera không chạy. **ĐỀ XUẤT ánh xạ:** không thấy mặt hoặc lỗi kỹ thuật. | Cho thử lại một lần; còn lỗi thì chuyển review/fallback. |
| `inconclusive` | Có đầu vào nhưng không xác định được kết quả đáng tin. **ĐỀ XUẤT ánh xạ:** nhiều mặt theo A0. | Cho thử lại một lần; còn mơ hồ thì chuyển review. |

Ánh xạ `không mặt → unavailable`, `nhiều mặt → inconclusive`, `AI lỗi → unavailable` là **đề xuất cần Quốc An/Minh Hy review trước E3**, không là kết luận model cuối. B0 chỉ chạy tiếp khi đúng một mặt; không tự chọn một người trong ảnh nhiều mặt. Threshold, thiết bị đích, quyền dùng weight/ảnh và dữ liệu face test còn `TBD`; không đưa ảnh, embedding, weight hoặc danh tính thật vào Git.

**Đếm retry theo đề xuất để review:** `verification_try_no=1` cho lần kiểm tra đầu. Chỉ với không thấy mặt/nhiều mặt/AI lỗi, operator có thể kích hoạt **một** lần kiểm tra lại ngay (`verification_try_no=2`) trong cùng attempt; ghi actor, thời điểm, loại lỗi và outcome từng lần. Nếu lần thứ hai vẫn không có kết quả dùng được, kết thúc attempt theo nhánh review. `unmet` đi review ngay, không tự retry. Nếu attempt bị gián đoạn rồi mở attempt mới, cách tính hạn mức xuyên lượt là `TBD`; test E3 có liên quan phải chờ chốt để tránh reset hạn mức bằng cách tạo lượt mới. Đây là cách cụ thể hóa D-005, chưa là policy được duyệt.

## 5. Mất mạng và chống ghi trùng

AI B0 có thể chạy trên Android khi không có mạng; điều đó **không** làm check-in offline có hiệu lực. Thiết bị hiển thị `PENDING_SYNC`, giữ attempt/outcome/phiên bản nguồn và khóa idempotency trong hàng đợi cục bộ theo thiết kế bảo vệ dữ liệu còn `TBD`. Khi kết nối lại: hỏi backend kết quả đã có → gửi/tiếp tục cùng khóa nếu chưa có → backend kiểm context/roster/policy/quyền/trùng → operator xem kết quả server và bấm xác nhận → chỉ sau phản hồi ghi thành công mới hiển thị `RECORDED`. Nếu không biết request trước đã commit hay chưa, không tạo khóa mới và không hiện thành công giả (T-008 BR-007/010; E3-F06/F07).

Nếu phiên bản roster/policy đã đổi hoặc bản cache không đủ tin cậy, chuyển `REVIEW_PENDING` hoặc giữ chờ; không tự dùng bản mới để viết lại attempt cũ. Thiết kế mã hóa, thời hạn hàng đợi, ảnh/embedding có được giữ trên máy hay không, khôi phục khi app bị xóa và quy tắc giờ thiết bị không đáng tin đều là `TBD` trước M4/M5.

## 6. Bảng nhánh xử lý mô phỏng

Các `error_code` dưới đây là **mã đề xuất cho contract v1**, chưa là API đã tồn tại. Mọi nhánh phải lưu tối thiểu: `attempt_id`, context, roster/policy version, nguồn/mã khai báo giả hoặc registration key nếu xác định được, actor/role, thời điểm sự kiện và thời điểm ghi, trạng thái trước/sau, loại bằng chứng/lỗi, idempotency key hoặc tham chiếu request, case/decision liên kết. Không lưu ảnh mặt mặc định. Quyền xem audit và thời hạn lưu còn `TBD`.

| Nhánh / trace E3 | Đầu vào | Actor có quyền và kết quả dự kiến | Mã / bước tiếp cho UI | Audit bổ sung |
|---|---|---|---|---|
| Bình thường — F01 | `SIM001`, đúng context, AI `satisfied`, chưa có check-in, online hoặc đã sync | Operator được cấp context xác nhận **sau khi** backend kiểm đủ policy; ghi tối đa một `RECORDED`. **Chưa chạy F01 đến khi arrival/authority được duyệt.** | `READY_TO_CONFIRM` → nút xác nhận → `CHECKIN_RECORDED` khi server trả thành công | Bằng chứng AI + phiên bản pipeline, quyền và thao tác xác nhận |
| Không có hồ sơ / mã trùng — F02 | `SIM404` / `SIMDUP` | Hệ thống giữ attempt chưa gắn registration, tạo case cho reviewer; không tạo hồ sơ/check-in giả | `ROSTER_NOT_FOUND` / `ROSTER_AMBIGUOUS` → chuyển bàn hỗ trợ | Mã nhập, số record tìm thấy, người nhận case |
| Sai phòng/ca — F03 | `SIMROOM` / `SIMSESSION` | Operator chỉ ghi sai lệch; reviewer được phân quyền xử lý, **quyền cho ngoại lệ TBD**; không tự ghi ở context sai | `WRONG_ROOM` / `WRONG_SESSION` → hướng dẫn kiểm phân phòng | Context nguồn/điểm, roster version, quyết định sau review |
| Thời gian/đồng hồ không rõ — F04 | Arrival ngoài mốc hoặc đồng hồ không tin cậy | Chưa phân loại late hay cho tiếp tục khi ArrivalWindow/LatePolicy `TBD`; giữ review | `ARRIVAL_POLICY_UNSET` / `CLOCK_UNTRUSTED` → người có quyền kiểm | `observed_at`, `recorded_at`, nguồn đồng hồ/độ tin cậy |
| AI `unmet` — F05 | Kết quả chạy được nhưng không đạt | Không ghi check-in; reviewer nhận case, quyết định bổ sung `TBD` | `IDENTITY_UNMET` → kiểm tra theo người có quyền | Outcome, pipeline version, reason được phép lưu |
| Không mặt/nhiều mặt/AI lỗi — F05 | `unavailable`/`inconclusive` theo bảng mục 4 | Operator thử lại một lần; nếu vẫn không dùng được thì case cho reviewer, không ghi check-in | `IDENTITY_UNAVAILABLE` / `IDENTITY_INCONCLUSIVE` → thử lại hoặc `RETRY_EXHAUSTED` → review | Cả hai lần thử, actor, nguyên nhân, attempt liên kết |
| Lượt lặp / đã ghi — F06 | Cùng registration/ca đã `RECORDED`, hoặc client không rõ lần gửi trước | Backend trả kết quả đã có; operator không tạo check-in mới, mâu thuẫn thì mở case | `ALREADY_RECORDED` / `RESULT_UNKNOWN` → tra server trước khi gửi lại | ID kết quả cũ, khóa idempotency, các attempt liên kết |
| Mất mạng/thiết bị lỗi — F07 | AI tại máy có outcome nhưng chưa sync hoặc không có nguồn tin cậy | Giữ `PENDING_SYNC`/`INTERRUPTED`; fallback chỉ theo quyền/policy sau này; không hiện `RECORDED` | `SYNC_PENDING` / `SOURCE_UNAVAILABLE` → chờ đồng bộ hoặc chuyển người trực | Khoảng gián đoạn, nguồn cục bộ, thời điểm xảy ra/ghi |
| Yêu cầu override trái quyền — F08 | Actor không có quyền hoặc chưa tìm được người duyệt | Không áp dụng; giữ case pending và tuyến escalation `TBD` | `FORBIDDEN` / `REVIEWER_UNAVAILABLE` → liên hệ người được giao | Actor, quyền đã kiểm, yêu cầu/lý do, người được chuyển |
| Roster/policy đổi — F09 | Version tại attempt khác bản hiện hành | Giữ snapshot version cũ, đánh dấu cần review ảnh hưởng; không sửa kết quả cũ | `VERSION_STALE` → đối chiếu nguồn/hiệu lực | Version cũ/mới, thời điểm hiệu lực, quyết định review |
| Đóng ca/đối soát — F10 | Thiếu check-in, còn case hoặc nguồn thủ công | Người đối soát `TBD`; không tự xác nhận absent; attendance `UNFINALIZED`/`UNDETERMINED` theo scope sau | `RECONCILIATION_PENDING` → danh sách case cần xử lý | Nguồn đã xét, khoảng mất dữ liệu, version báo cáo |
| Correction — F11 | Bằng chứng mới mâu thuẫn bản ghi | Chỉ người có CorrectionAuthority `TBD`; giữ bản gốc, trước/sau và ảnh hưởng | `CORRECTION_REQUIRES_AUTHORITY` → chuyển người được cấp quyền | Bản gốc, actor/lý do/bằng chứng, báo cáo/hồ sơ bị ảnh hưởng |
| Bỏ dở/quay lại — F12 | Attempt `INTERRUPTED` rồi quay lại | Tạo attempt mới liên kết; không tạo check-in/attendance thứ hai; re-entry ngoài scope bản đầu | `ATTEMPT_INTERRUPTED` → bắt đầu lượt có liên kết hoặc review | Lý do ngắt, lượt trước/mới, kết quả hiệu lực trước |

`REVIEW_PENDING` phải có vai trò nhận và bước tiếp; nếu chưa gán được người trực, vẫn giữ pending và ghi tuyến escalation `TBD`, không tự từ chối vì chờ lâu. Các mã lỗi/expected outcome phụ thuộc policy chỉ trở thành test oracle sau khi profile được duyệt (T-008 BR-008; E3-F08).

## 7. Điều kiện được chấm E3 và phần chưa chốt

E3-F02/F03/F05/F06/F07/F08/F09/F12 có invariant generic để thiết kế test ngay, nhưng **chưa báo pass** khi chưa có app. F01/F04 cần ArrivalWindow, điều kiện bằng chứng và authority được duyệt. F10/F11 cần AttendanceDefinition/CorrectionAuthority hoặc phải báo `not-runnable` đúng phạm vi D-005. Mỗi fixture pin version, trạng thái trước, input/event time, expected state/audit và actor; kết quả sau này là `pass/fail/not-runnable`, không là accuracy AI.

| Vấn đề cần chốt | Nguồn câu hỏi | Ảnh hưởng trước khi triển khai/chấm |
|---|---|---|
| Mốc ca, arrival/late, đồng hồ nào tin cậy | T-008 OQ-002; questions.md #8 | Chặn nhánh check-in/late và F01/F04 phụ thuộc thời gian. |
| Người phê duyệt profile mô phỏng; operator/reviewer trực và quyền từng loại case | OQ-007/009/011; D-005 | Chặn mở context và kết luận case theo quyền. |
| Nguồn roster, bản có hiệu lực và cách cập nhật | OQ-013/014; E3-F09 | Chặn readiness và xử lý version đổi. |
| Tiêu chí AI/thiết bị/weight/ảnh được phép; ánh xạ outcome và retry xuyên attempt | D-005; OQ-003/004/016; questions.md #5–6 | Chặn M4/E3 có AI, không tự chọn threshold hoặc lưu ảnh. |
| Hàng đợi offline, dữ liệu cục bộ, fallback và bảo vệ dữ liệu | D-005; OQ-018/021/023 | Chặn công bố check-in offline hoặc hoàn tất M5. |
| Quyền override/correction, retention, AttendanceDefinition/nguồn hiện diện | OQ-001/009/012/015/016; questions.md #8 | Chặn F08/F10/F11 và mọi kết luận attendance. |
| Thiết bị Android đích và điều kiện thử | D-005; questions.md #6 | Chặn khẳng định B0 đạt trên máy và E3/app end-to-end. |
| Kỳ thi/quy chế/trường thật | questions.md #1 | Ngoài profile giả lập; không suy ra từ fixture này. |

## 8. Duyệt profile và quản lý thay đổi

Trước run E3, Minh Hy và Quốc An cần ghi: phiên bản profile được duyệt, ngày, người và phạm vi duyệt; version roster/policy fixture, điều kiện/thiết bị/nguồn dữ liệu, các nhánh không áp dụng, expected outcome cụ thể cho từng case. Mọi thay đổi sau đó tạo revision mới, nêu fixture bị ảnh hưởng và chạy lại; không sửa expected outcome sau khi xem kết quả để biến fail thành pass. Minh Hy đã chọn phương án để phát triển theo D-006; tài liệu này hiện **chưa** có xác nhận của Quốc An cho E3 và không là policy của một cơ sở đào tạo.
