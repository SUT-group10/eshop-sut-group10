# E-02 — Protocol thí nghiệm flaky test

Phiên bản 1.1 — cập nhật ngày 21/10/2026. Người phụ trách: Trần Quốc Vỹ; Dương hỗ trợ thao tác CI khi cần.

## 1. Mục tiêu và căn cứ

Chốt cách chạy và thu dữ liệu trước E-03 để quan sát một test có cả pass và fail trên cùng phiên bản mã, rồi cung cấp dữ liệu nhất quán cho phân tích log. Protocol không yêu cầu mọi lượt pass hoặc đúng tỷ lệ 5 pass/5 fail.

| Nguồn | Yêu cầu áp dụng |
| --- | --- |
| [Brief T07, mục 2 và 6](../requirements/T07_CI-CD_and_Test-Harness_Engineering.docx.md) | Tạo sleep-based flake, quan sát qua 10 lượt; phân tích log và retry history, so sánh người với AI. |
| [Checklist E-02](../tasks/checklist.md) | Định nghĩa trước cách chạy, thành công/thất bại và dữ liệu cần thu; không sửa test giữa các lần đo. |
| Checklist E-03 | Ít nhất 10 lượt độc lập; lưu SHA, thời gian, kết quả, URL, raw log và retry history. |
| [Proposal nhóm, phần ChatGPT](../proposal/Tool_Survey_Proposal.md) | Chạy trên pipeline; người phân tích thủ công trước, người và AI nhận cùng dữ liệu. |
| Quyết định của protocol này | Một đợt gồm đúng 10 dispatch mới, chạy tuần tự, chế độ `sampled`, không retry. Các quy tắc phân loại và dừng bên dưới là lựa chọn triển khai, không phải câu chữ bổ sung của đề. |

Đầu ra của E-02 là tài liệu này. E-03 mới tạo bảng run và dữ liệu thực nghiệm; không dùng các lượt chẩn đoán E-01 làm dữ liệu thu trước theo protocol này.

## 2. Đối tượng và phiên bản được đo

- Test: [`cart-timing.flaky.js`](../../backend/tests/experiments/cart-timing.flaky.js), chạy qua [`jest.flaky.config.cjs`](../../backend/jest.flaky.config.cjs).
- Test E-01 đã có trong commit `bb969986fc0c67868f28eaa06d6eaf5780256c96`. A chờ trực tiếp 60 hoặc 160 ms rồi thêm sản phẩm; B chờ 100 ms rồi đọc giỏ. Thiết kế và nguyên nhân đã biết nằm trong [hướng dẫn E-01](../../backend/tests/experiments/README.md).
- Mỗi lượt dùng `sampled`; lựa chọn fast/slow độc lập, xác suất bằng nhau. Không ép số lượt mỗi case, không đổi assertion theo case. `selectedCase` là case được chọn, không thay cho kết quả Jest.
- Mỗi lượt tạo app và SQLite trong bộ nhớ mới bằng fixture hiện có; cleanup chờ thao tác thêm kết thúc rồi đóng database. Không mở server hay database dùng chung, không cần Internet để gọi API qua Supertest; CI vẫn cần mạng để tải dependency/actions.
- Trước lượt đầu, ghi **SHA đầy đủ của phiên bản thực sự sẽ chạy** và revision chứa protocol vào hồ sơ đợt đo. Giữ nguyên test, fixture, SUT, lockfile, Jest config, workflow và lệnh trong cả đợt. Không push thêm vào ref đang được đo cho đến khi xong.
- Mọi run phải có `head_sha` và SHA trong bước ghi runtime khớp SHA đã chốt. Nếu code/cấu hình/điều kiện chạy cần đổi, dừng đợt, giữ dữ liệu cũ và lập đợt mới với lý do, SHA và phiên bản protocol tương ứng trước khi chạy lại.

## 3. Môi trường và điều kiện bắt đầu

Đợt đo chính dùng **GitHub Actions**, workflow [`flaky-experiment.yml`](../../.github/workflows/flaky-experiment.yml), job `cart-timing`:

| Thuộc tính | Điều kiện |
| --- | --- |
| Runner | GitHub-hosted `ubuntu-22.04`; ghi image version thực tế từ log Set up job cho từng run. |
| Node | `24.14.0`, như workflow hiện có. |
| Runtime của action | [checkout@v6](https://github.com/actions/checkout/releases/tag/v6.0.0), [setup-node@v6](https://github.com/actions/setup-node/releases/tag/v6.0.0), [upload-artifact@v6](https://github.com/actions/upload-artifact/releases/tag/v6.0.0) dùng Node 24; đây là runtime của action, khác với Node chạy test ở dòng trên. |
| npm | Ghi phiên bản thực tế ở lượt đầu; các lượt tiếp theo phải cùng phiên bản. Không suy npm của CI từ máy local. |
| Dependency | `npm ci` theo cùng lockfile; workflow đặt `npm_config_build_from_source=true` khi cài. Giữ cấu hình cache hiện có; không thay đổi chiến lược cache giữa đợt. |
| Test | Một tiến trình Jest, `--runInBand`, một test thí nghiệm; timeout test 10 giây, timeout job 10 phút theo cấu hình hiện có. |
| Chế độ | `FLAKE_LATENCY_MODE=sampled`; không trộn fast/slow cố định vào mẫu chính. |

Trước đợt đo:

1. Đảm bảo workflow có thể dispatch trên repo, tài khoản có quyền chạy và tải artefact; ref được chọn chứa đầy đủ harness và test E-01. Giữ default branch là `main`; chỉ tích hợp file workflow vào `main`, phần thí nghiệm tiếp tục trên branch riêng. Với giao diện GitHub, workflow cần hiện diện trên default branch để có nút **Run workflow**; xem [GitHub Docs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow). Kiểm tra default branch thực tế trước đợt đo.
2. Chọn ref thực tế chứa phiên bản đo; hiện công việc nằm trên `test/issue-5-flaky-experiment`. Nếu quy trình đưa workflow vào repo tạo SHA mới, chốt SHA mới trước lượt đầu, không dùng SHA cũ để ghi thay.
3. Ghi mã đợt, phiên bản protocol, SHA, ref, người thực hiện, thời điểm UTC, môi trường dự kiến và danh sách lượt 01–10. Xác minh lệnh/report bằng kiểm tra cấu hình; nếu cần chạy thử thì ghi riêng là rehearsal trước đợt đo.
4. Chuẩn bị nơi lưu `docs/evidence/E-03/<batch-id>/` và bảng dữ liệu ở mục 6. Thư mục sẽ được tạo khi làm E-03; tài liệu này không chứa kết quả giả hoặc hàng run điền sẵn.

Các image GitHub-hosted có thể được cập nhật. Nếu image version hoặc Node/npm khác giữa đợt, giữ bản ghi và dừng đợt để thống nhất lại môi trường; không trộn dữ liệu khác điều kiện mà coi là cùng mẫu.

## 4. Cách thực hiện một đợt

### 4.1. Mở workflow và chạy thử một lượt trước đợt chính thức

1. Đăng nhập GitHub bằng tài khoản có quyền write vào repo, mở [trang Actions của EShop](https://github.com/SUT-group10/eshop-sut-group10/actions).
2. Ở thanh bên trái, tìm **Flaky experiment (manual only)**. Nếu chỉ thấy **Backend CI**, dừng tại đây: chọn branch trong tab Code không làm workflow mới xuất hiện trong Actions. Cần đưa riêng file `.github/workflows/flaky-experiment.yml` vào default branch `main` qua PR/review. Có thể dùng PR nhỏ chỉ đăng ký workflow, không cần đợi hoàn thành toàn bộ Issue #5. Đây là bước chuẩn bị; việc merge cần được nhóm cho phép riêng.
3. Khi workflow đã xuất hiện, bấm **Flaky experiment (manual only)** → **Run workflow** ở phía trên danh sách run. Nếu đã thấy workflow nhưng không có nút, kiểm tra file trên default branch có `workflow_dispatch` và tài khoản có quyền write; không chuyển sang chạy Backend CI thay thế.
4. Trong **Use workflow from / Branch**, chọn `test/issue-5-flaky-experiment` hoặc ref đo đã chốt, rồi bấm nút **Run workflow** để xác nhận. File hiện không yêu cầu nhập mode: job tự dùng `sampled`. Không chọn `main` khi branch đó chỉ có workflow mà chưa có harness/test thí nghiệm.
5. Chờ run mới xuất hiện, mở run đó → job **cart-timing**. Mở bước **Record source and runtime**, đối chiếu SHA và xem Node/npm. Mở **Set up job** để lấy runner image/version.
6. Mở bước **Run one sampled attempt (failure is an experimental result)**. Tìm `E-01 observation` để xem `selectedCase`, `delayMs`, thời điểm đọc và giỏ; tìm `E-01 add completed` để xem thời điểm thêm hoàn tất và HTTP status. Đọc PASS/FAIL của Jest riêng, phân loại theo mục 5.
7. Quay về trang tổng quan của chính run đó, kéo xuống **Artifacts**, tải `flaky-<run_id>-<run_attempt>`. Giải nén và tìm `console.log`, `results.json`; không chỉ lưu ảnh dấu xanh/đỏ. Trong job, dùng menu tải log (**Download log archive**) để giữ cả log setup/runtime; tên/vị trí menu có thể thay đổi theo giao diện GitHub.
8. Lưu URL của run từ thanh địa chỉ, thời gian và nguồn metadata theo mục 6. Thử ghi một bản ghi rehearsal để kiểm tra có lấy được đủ dữ liệu. Nếu thiếu log/report hoặc test không khởi chạy, xử lý trước đợt chính thức.
9. Ghi rõ lượt này là **rehearsal**, không tính vào 10 lượt E-03. Chạy thử đạt khi đúng test/mode/SHA, log/report tải và đối chiếu được; test có thể PASS hoặc TIMING_FAIL. Không dùng màu job làm tiêu chí duy nhất.

Đăng ký workflow trên default branch `main` và chọn branch thực thi là hai thao tác khác nhau. Các bước giao diện và quyền truy cập dựa trên [GitHub Docs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Rehearsal ngày 21/10/2026: [run 39615233808](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39615233808), branch `test/issue-5-flaky-experiment`, SHA `068d38559704f1262101266589c0d1f29eee1193`. Ba action `@v6` chạy được, log không còn cảnh báo Node.js 20; `sampled` chọn fast 60 ms, test pass một lần và artefact `flaky-39615233808-1` có đủ `console.log`/`results.json`. Lượt này chỉ kiểm tra cách chạy và thu file, không tính vào đợt 10 lượt E-03.

[PR #16](https://github.com/SUT-group10/eshop-sut-group10/pull/16) đã tích hợp riêng phần nâng ba action vào `main`. Giữ `main` làm default branch; khi dispatch vẫn chọn branch thí nghiệm chứa đầy đủ harness/test.

### 4.2. Thu 10 lượt chính thức sau khi chốt điều kiện

1. Trên GitHub, mở Actions → **Flaky experiment (manual only)** → **Run workflow**, chọn ref đã chốt. Một dispatch mới là một lượt; số thứ tự 01–10 theo thứ tự dispatch.
2. Chờ run kết thúc, lưu URL, metadata, toàn bộ job log và artefact của lượt đó trước khi dispatch lượt tiếp theo. Không chạy song song trong đợt, không tạo thêm tải có chủ ý.
3. Xác minh mode/SHA/môi trường, phân loại kết quả theo mục 5 và ghi dữ liệu theo mục 6, kể cả khi run đỏ. Workflow giữ exit code thật qua `pipefail`, upload report/log kể cả assertion fail; không dùng `continue-on-error` để đổi kết luận.
4. Lặp đến hết 10 lượt đã định. Không bù case, không chọn riêng lượt đẹp, không chạy tiếp chỉ vì chưa có đủ 5 pass/5 fail.

Lệnh test workflow chạy từ `backend` là `npm run test:flaky -- --json --outputFile=test-results/flaky/results.json`, với biến mode đặt ở bước chạy. Mỗi artefact chứa `console.log` và `results.json`; log đầy đủ trên Actions còn cung cấp môi trường và lỗi setup/upload.

**Retry history:** retry trong Jest bằng 0; không dùng **Re-run jobs** hoặc **Re-run all jobs** trong mẫu chính. Mỗi run phải có `run_attempt=1`. Dispatch mới là một mẫu mới, không phải retry của lượt trước. Nếu bấm rerun nhầm, giữ run ID/attempt/log và quan hệ với lượt gốc trong phần phát sinh; không thay thế kết quả gốc hoặc tính thêm một mẫu chính.

## 5. Phân loại và điều kiện thành công/thất bại

Kết luận của GitHub job và kết luận của test được ghi riêng. Job đỏ vì cài dependency hoặc upload artefact không đồng nghĩa test gặp timing flake.

| Nhãn phân loại | Điều kiện |
| --- | --- |
| `PASS` | Jest báo đúng test thí nghiệm pass; report không có test khác/lỗi khác. Log thể hiện GET 200, đúng sản phẩm số lượng 1 và thao tác thêm cuối cùng trả 200. |
| `TIMING_FAIL` | Jest fail ở assertion độ dài giỏ (expected 1, actual 0); GET 200 và giỏ rỗng, thao tác thêm cuối cùng trả 200, không có lỗi setup/cleanup/HTTP khác. Đối chiếu hai dòng log cho thấy đọc giỏ hoàn tất trước khi request thêm được gửi (`readCompletedMs < addSentMs`). |
| `OTHER_TEST_FAIL` | Test chạy nhưng lỗi khác, hoặc log không đủ xác nhận timing. Nếu khoảng đọc/thêm chồng lấn hoặc case fast fail, giữ timing thật để điều tra; không suy nguyên nhân từ `selectedCase` hay exit 1. |
| `INFRA_OR_INCOMPLETE` | Cài dependency/setup lỗi, job bị hủy/timeout, thiếu report/log, upload thất bại làm thiếu bằng chứng, sai SHA/mode/môi trường hoặc không chạy đúng test. Ghi thêm kết quả Jest nếu vẫn có. |

Đọc `E-01 observation` và `E-01 add completed` cùng nhau; ở case slow, thông tin thêm hoàn tất có thể xuất hiện sau assertion đọc. Thời gian timing tính từ lúc A/B bắt đầu; duration test/Jest và duration job là các số đo khác nhau.

**Một đợt thu dữ liệu đạt:** có đủ 10 run mới, cùng điều kiện, đầy đủ nguồn và retry history; cả 10 phân loại được là `PASS` hoặc `TIMING_FAIL`. Có ít nhất một kết quả mỗi loại thì đợt này cung cấp bằng chứng biến thiên kết quả của test dưới điều kiện đã định.

Nếu đủ 10 lượt hợp lệ nhưng tất cả cùng pass hoặc cùng fail, vẫn báo đủ dữ liệu và tỷ lệ thực tế; kết luận là đợt này **chưa quan sát được cả hai kết quả**. Không đổi mã, chọn lại mẫu hay kéo dài đợt sau khi biết kết quả.

Nếu có `OTHER_TEST_FAIL` hoặc `INFRA_OR_INCOMPLETE`, lưu cả lượt đó và dừng trước dispatch tiếp theo để điều tra. Đợt chưa đạt điều kiện đủ 10 lượt hợp lệ. Chỉ bắt đầu đợt mới sau khi ghi cách xử lý và chốt điều kiện trước; không xóa đợt cũ, không thay một lượt lỗi bằng lượt khác rồi trình bày như 10 lượt liên tục. Các đợt bổ sung báo riêng, không giấu kết quả trước.

## 6. Dữ liệu phải thu ở E-03

Giữ một bảng tổng hợp của đợt và file gốc theo từng run; đường dẫn phải phân biệt được run ID/attempt, không ghi đè artefact lượt trước.

| Nhóm trường | Nội dung cần lưu / nguồn |
| --- | --- |
| Định danh | `batch_id`, protocol version/revision, số thứ tự; GitHub `run_id`, `run_number`, `run_attempt`, run URL, ref, `head_sha`, SHA ghi trong runtime. |
| Thời gian | UTC tạo/bắt đầu/kết thúc, duration job (tính từ started/completed của job); duration test và thời điểm Jest từ JSON, ghi đơn vị rõ ràng. |
| Môi trường | OS/runner image version từ Set up job, Node/npm từ bước runtime; lockfile và workflow được truy vết qua SHA. Ghi cache hit/miss từ setup-node nếu log có. |
| Kết quả | Job/step conclusion; pass/fail và tên test/assertion từ Jest; exit code của lệnh test; nhãn phân loại ở mục 5 và lý do. Không lấy exit của bước upload thay cho exit test. |
| Timing | `mode`, `selectedCase`, `delayMs`, `readWaitMs`, `addSentMs`, `addCompletedMs`, `readSentMs`, `readCompletedMs`, HTTP status của GET/POST và giỏ quan sát từ hai dòng log. |
| Nguồn | Toàn bộ job log, `console.log`, `results.json`, tên/ID artefact và đường dẫn bản tải về. Tải trong thời hạn lưu artefact 14 ngày của workflow; giữ SHA256 các file gốc trong bảng hoặc file hash của đợt. |
| Retry / bất thường | Retry trong test = 0, lịch sử rerun nếu có, run gốc liên quan, lỗi setup/upload, dữ kiện thiếu và lý do dừng đợt. Thiếu dữ liệu ghi rõ, không điền 0 giả. |

Workflow hiện không tạo bảng metadata tự động. Khi làm E-03, lấy metadata run/job từ Actions hoặc GitHub API và đối chiếu với raw log; đó là một phần thao tác thu dữ liệu, không suy các giá trị từ ảnh chụp PASS/FAIL.

Sau đợt đo, thống kê tổng số dispatch, số từng nhãn, số fast/slow và bảng chéo case × pass/fail. Với đợt đủ 10 kết quả hợp lệ, tỷ lệ fail là số `TIMING_FAIL` / 10. Không tính lượt chẩn đoán, rehearsal hoặc rerun vào mẫu; nếu đợt dừng sớm thì báo số lượt đã chạy, không trình bày tỷ lệ đó như một mẫu đủ 10 lượt.

## 7. Giữ dữ liệu phù hợp cho phân tích người–AI

Raw log lưu nguyên bản ở nơi được phép. Trước khi chia sẻ, loại token/secrets và thông tin cá nhân; người và AI dùng cùng bản đã xử lý, cùng retry history và thông tin môi trường. Lưu quy tắc xử lý để truy lại bản gốc.

Nguyên nhân trong mục 2, README E-01, source code, tên test và các trường delay/timing có thể tiết lộ thiết kế. Người tổ chức giữ đáp án riêng; không phát nguyên protocol này như gói triage mù. Khi chuẩn bị input, xác định trước ngữ cảnh nào được cung cấp cho cả hai bên và kiểm tra các dấu hiệu lộ đáp án. Nếu thay tên/ẩn trường, làm cùng cách ở hai bản và giữ ánh xạ riêng; không sửa thông báo lỗi để làm sai ý nghĩa.

Người phân tích thủ công phải ghi nhận phân tích trước khi xem output AI. Người hoặc phiên AI đã đọc thiết kế/đáp án không được gọi là phân tích mù độc lập; phiên đang thiết kế thí nghiệm này đã biết nguyên nhân. Phần tổ chức triage và chuẩn hóa input thuộc các task tương ứng, không thực hiện thay trong E-02.

## 8. Tiêu chí hoàn thành E-02

Protocol phải xác định được: đối tượng và cách chốt SHA; môi trường và điều kiện dispatch; số lượt/mode/lệnh; retry và tính độc lập; tiêu chí phân loại; dữ liệu/nguồn cần lưu; điều kiện dừng, thay đổi và báo kết quả. Một người khác có thể làm theo để thu cùng cấu trúc dữ liệu mà không tự đặt lại các quy tắc này.

Task nhóm đã nêu đúng đầu ra, nhưng chưa chỉ định các chi tiết vận hành trên. Protocol này bổ sung chúng để thực hiện được E-03. Khả năng dispatch workflow và môi trường thực tế là các điều kiện kiểm tra trước đợt đo, không phải kết quả được giả định từ việc có file YAML. Việc thu đủ 10 run và phân tích thực tế là đầu ra của các task sau.
