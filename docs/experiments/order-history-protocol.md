# E-01–E-03, E-05, E-09 — Protocol thí nghiệm order history v2.0

Tài liệu dành cho người tổ chức, có mô tả nguyên nhân. Không đưa tài liệu này hoặc organizer evidence cho người/AI trước khi họ hoàn thiện phân tích. Dữ liệu E-03 và kết quả E-04/E-08 trước đây vẫn giữ nguyên phạm vi; thí nghiệm này tạo bộ dữ liệu mới.

**Trạng thái hiện tại:** v2 là bản chạy hiện hành; đã có [kiểm chứng local](../evidence/E-03/order-history-v2-local-20261023/README.md), [batch CI timed 10 run/retry=2](../evidence/E-03/order-history-v2-ci-39860438568/README.md), [đối chiếu người–AI](../evidence/E-08/order-history-v2-39860438568/AI_vs_Human_Triage.md) và [kết luận E-10](../evidence/E-10/order-history-v2-39860438568/README.md). [Kiểm chứng `awaited` trên CI](../evidence/E-09/order-history-v2-ci-39911447981/README.md) đạt 10/10 PASS không retry. Protocol cart v1 và các thời lượng phân tích cũ không được dùng thay cho kết quả v2.

## 1. Mục tiêu và căn cứ

Đề T07 yêu cầu chủ động tạo sleep-based flake, quan sát 10 lượt, phân tích log và retry history, rồi so sánh người với AI. Thiết kế này kiểm tra một lỗi đồng bộ trong test bằng luồng đặt hàng thật, đồng thời quan sát sự khác biệt giữa kết quả lần đầu và verdict cuối sau retry.

Đây là flaky test được chủ động tạo cho seminar; không phải bằng chứng EShop tự có lỗi mạng hoặc xử lý đặt hàng không ổn định. Không mở rộng thành kiểm thử đầy đủ FR-08: các lỗi nghiệp vụ checkout đã biết vẫn thuộc bộ test chính.

## 2. Cơ chế và oracle

- Mỗi attempt tạo app EShop thật và SQLite `:memory:` mới, đăng nhập fixture, thêm một sản phẩm vào giỏ và xác nhận chưa có đơn hàng.
- Supertest gửi `POST /api/checkout` ngay, qua một Express gateway chỉ dùng trong thí nghiệm. Gateway ghi nhận request đã đến rồi chờ một độ trễ trước khi chuyển cho ứng dụng thật. Chỉ POST chịu độ trễ; GET chạy bình thường. Response, thao tác ghi SQLite và các assertion không được mock.
- Độ trễ sampled là số nguyên trong **20–220 ms**. Mỗi batch chọn seed ngẫu nhiên và lưu riêng cho người tổ chức; mỗi run có ba vị trí độ trễ dự kiến, tương ứng tối đa ba attempt. Không chọn seed theo kết quả hoặc ép tỷ lệ pass/fail. Những vị trí không được thực thi không được tính là attempt.
- Bản `timed` chỉ đợi **120 ms** sau khi gửi POST rồi đọc `GET /api/orders/my-orders`. Khoảng chờ này không phải SLA nghiệp vụ. Test dùng thời gian thay cho điều kiện hoàn tất nên có thể nhận snapshot chưa có đơn hàng.
- Sau lần đọc được đánh giá, test chờ POST kết thúc và thực hiện một GET `confirmation`. Lần đọc này xác minh đơn hàng có thể đọc được sau POST; không thay thế snapshot đầu để làm assertion pass.
- Oracle: POST/GET trả 200; lần đọc xác minh có đúng một đơn với ID vừa tạo; snapshot lịch sử đầu phải có đúng một đơn với ID, owner, tổng tiền và trạng thái đúng. Fail mục tiêu là `HISTORY_ORDER_COUNT`, expected 1, actual 0. Setup, HTTP, transport, identity, cleanup hoặc lỗi khác là sự cố cần điều tra riêng.
- Bản `awaited` thay đúng quan hệ chờ: POST hoàn tất và đạt HTTP 200 mới gửi GET. Giữ API, fixture, latency và oracle. Không tăng sleep, retry thêm hoặc đổi expected để sửa lỗi.

Mỗi batch chỉ chọn **một** variant. Retry chạy lại cùng variant; không tự chuyển từ `timed` sang `awaited` khi fail. Gói phân tích chính lấy từ `timed`; `awaited` dùng xác nhận bản sửa.

Đây là sự biến thiên kết quả do thứ tự thực thi bất đồng bộ, với độ trễ có kiểm soát. Không có câu lệnh ngẫu nhiên chọn PASS/FAIL. Hiệu năng máy và event loop vẫn ảnh hưởng thời điểm thực tế; log thực tế quyết định kết luận, không phải con số độ trễ dự kiến.

## 3. Đơn vị đo và retry

**Một run** là một tiến trình Jest mới. **Một attempt** là một lần Jest thực thi toàn bộ test body, gồm setup, API, assertion và cleanup. Jest tự retry khi test fail, qua `jest.retryTimes(2, {logErrorsBeforeRetry: true, retryImmediately: true})`: tối đa **1 lần đầu + 2 retry = 3 attempt**. Pass thì dừng ngay. Mỗi attempt có fixture mới; không tiếp tục dùng trạng thái của attempt trước.

Một workflow GitHub Actions mặc định điều phối 10 tiến trình Jest tuần tự trên cùng runner/revision; không phải 10 dispatch. `GITHUB_RUN_ATTEMPT` là số rerun của workflow, không phải số retry của test. Hai loại được lưu riêng. Mười run cùng mỗi attempt có nhiều file biểu diễn; không cộng số file thành số quan sát mới.

Nguồn API retry: [Jest retryTimes](https://jestjs.io/docs/jest-object#jestretrytimesnumretries-options).

## 4. Kế hoạch chạy chốt trước khi thu mẫu

Giữ test, SUT, fixture, dependency, runtime, gateway, retry policy và bộ thu log không đổi trong từng batch. Bộ chạy lưu SHA, tình trạng source, hash các file đầu vào và snapshot implementation thí nghiệm; phát hiện source đổi giữa batch thì dừng với lỗi evidence. Không gán chạy local chưa commit cho một SHA sạch.

| Batch | Variant | Run | Retry tối đa | Mục tiêu |
| --- | --- | --- | --- | --- |
| Chính | timed, sampled | 10 | 2 | Quan sát attempt ban đầu, chuỗi retry và verdict cuối |
| Đối chứng retry | timed, sampled | 10 | 0 | So với policy retry, dùng cùng seed và môi trường nếu cần đo ảnh hưởng |
| Sau sửa | awaited, sampled | 10 | 0 | Xác nhận không dựa vào retry để xanh |
| Chẩn đoán riêng | timed, latency cố định thấp/cao | 1 mỗi trường hợp | 2 | Kiểm tra oracle và giới hạn ba attempt; không trộn vào mẫu sampled |
| Chẩn đoán sửa | awaited, latency cố định cao | 1 | 0 | Kiểm tra chờ hoàn tất thay vì hết thời gian |

Hai batch dùng cùng seed sẽ có cùng độ trễ dự kiến ở attempt đầu từng run, kể cả khi retry policy khác. Không bảo đảm duration hoặc verdict giống tuyệt đối do lịch thực thi thật. Nếu không làm batch đối chứng retry thì không đưa kết luận định lượng về chi phí/lợi ích retry.

Không sửa test giữa các run, xóa run bất lợi hoặc chạy tiếp đến khi có tỷ lệ đẹp. Nếu 10 run chưa có cả pass/fail ở attempt đầu, báo giới hạn đó; đợt bổ sung phải có mã batch và kế hoạch riêng. Chuỗi fail → pass là kết quả có thể quan sát, không phải điều kiện được ép. Luôn lưu cả chuỗi fail → fail → fail nếu có.

## 5. Cách chạy local — PowerShell

Từ repo root; cần Node theo workflow, Python 3 và dependency đã cài:

```powershell
cd backend
npm ci
npm run experiment:orders -- --runs 10 --retries 2
$LASTEXITCODE
```

Bộ chạy in đường dẫn batch mới dưới `backend/test-results/order-history/`. Mặc định dùng sampled và retry=2. Mỗi batch có ID gồm timestamp UTC và mã ngẫu nhiên, ví dụ `20261023T031500Z-7f91a2c4`, kể cả khi dùng `--output` riêng. ZIP cũng mang ID này; không ghi đè thư mục hoặc archive đã tồn tại. `history.json` public có `packet_id` để ghép đúng kết quả phân tích với gói dữ liệu. Đọc `seed` trong organizer.json để dùng cùng lịch độ trễ cho đợt đối chứng:

```powershell
npm run experiment:orders -- --runs 10 --variant timed --retries 0 --seed 20261023
npm run experiment:orders -- --runs 10 --variant timed --retries 2 --seed 20261023
npm run experiment:orders -- --runs 10 --variant awaited --retries 0 --seed 20261023
```

Seed trên là ví dụ cách nhập, không phải seed được chọn để bảo đảm kết quả. Chẩn đoán riêng:

```powershell
npm run experiment:orders -- --runs 1 --retries 2 --latency-ms 20
npm run experiment:orders -- --runs 1 --retries 2 --latency-ms 300
npm run experiment:orders -- --runs 1 --variant awaited --retries 0 --latency-ms 300 --detect-open-handles
```

`npm run test:flaky` chạy trực tiếp một Jest process với retry mặc định 2 và xuất JSONL vào thư mục `direct-*`; dùng bộ điều phối ở trên khi cần ZIP và đối chiếu evidence đầy đủ. Test cart E-09 cũ vẫn được giữ để đối chiếu lịch sử, không nằm trong discovery của thí nghiệm mới hoặc suite chính.

## 6. Cách chạy GitHub Actions

Workflow hiện có: **Flaky experiment (manual only)**, job mới `order-history`; chỉ dispatch thủ công, tách khỏi required checks. Workflow dùng Ubuntu 22.04, Node 24.14.0, `npm ci` và cùng lệnh Python/Jest như local. Không sửa pipeline CI chính hoặc Jenkins.

1. Đưa phiên bản implementation lên branch thực sự muốn đo. Workflow đã đăng ký trên default branch; cập nhật file ở default branch khi cần hiển thị các input mới trên giao diện.
2. Actions → Flaky experiment → Run workflow → chọn branch. Nhập `variant=timed`, `runs=10`, `retries=2` cho batch chính.
3. Kiểm tra SHA thực thi, runtime và thông tin batch. Mỗi dispatch là một batch riêng. Không bấm Re-run run cũ để kiểm chứng code mới: rerun dùng SHA cũ.
4. Đọc bảng trong job summary: first_attempt_pass, recovered_after_retry, final_fail, total_attempts và evidence_errors. Job xanh vẫn có thể đã có attempt fail rồi retry pass.
5. Tải artifact **api-analysis-input-…** để đưa cùng một ZIP cho người/AI. Artifact này chỉ gồm dữ liệu participant. **organizer-evidence-…** chứa dữ liệu gốc và đáp án thiết kế, dành cho người tổ chức.

Nguồn: [manual dispatch](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow), [rerun dùng lại SHA/ref](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs).

## 7. Log, đóng gói và ranh giới dữ liệu

Mỗi event có schema version, run ID, sequence, attempt, UTC và thời gian đơn điệu từ cùng gốc trong tiến trình Jest. Request ID nối client sent → server received → server completed → client received. Lưu status HTTP, response order fields an toàn, expected/actual từng assertion, fixture lifecycle và failure category. Thời gian toàn process, duration test, timestamp Jest và UTC của bộ điều phối được đặt tên riêng.

| Thành phần | Nội dung | Gửi người phân tích? |
| --- | --- | --- |
| `raw/run-NN/` | Native Jest JSON, console gốc, events, attempts, controls | Không gửi cả thư mục |
| `organizer.json`, `source/` | SHA/source state, môi trường, seed, mapping, latency, variant, implementation snapshot | Không |
| `participant/run-NN/` | Events JSONL, bản console đánh số dòng, attempts và kết quả đã đối chiếu Jest | Có |
| `analysis-input-<batch-id>.zip` | Chỉ participant data, README định nghĩa dữ liệu và prompt chung | Có, gửi cùng gói cho cả hai bên |
| `organizer-evidence-<batch-id>.zip` | Raw, source, organizer.json và ZIP participant | Chỉ người tổ chức |

Không cần sửa/chuẩn hóa log thủ công. Public event được ghi ngay theo schema an toàn; bộ đóng gói giữ nguyên giá trị và chỉ tạo các biểu diễn dễ đọc. Tham số thiết kế, source/code frame, tên có đáp án, ID/link có thể lần về source nằm ngoài gói participant. Tokens, credentials, header Authorization và địa chỉ giao hàng không được ghi vào public events. Bộ đóng gói kiểm tra rò rỉ và từ chối xuất ZIP nếu thấy mẫu cấm.

Tên ZIP public không chứa `timed`, `awaited` hoặc nhãn nguyên nhân. Artifact trên GitHub cũng có run ID và workflow attempt riêng, nên tải các đợt khác nhau có tên phân biệt. Các archive kiểm chứng đã lưu trước thay đổi đặt tên vẫn giữ nội dung và tên lịch sử của chúng.

Public packet vẫn giữ mọi dấu hiệu chẩn đoán thực tế như thứ tự, duration HTTP và snapshot trả về. Che đáp án không có nghĩa xóa bằng chứng. Không gọi một packet đã cung cấp cho chat biết trước nguyên nhân là thử nghiệm phân tích mù.

## 8. Tiêu chí nghiệm thu và exit code

- Collector đối chiếu native Jest `invocations`, `retryReasons`, verdict, exit code với ledger; kiểm tra thứ tự event, lifecycle request/fixture và retry dừng khi pass. Không tự tính lại verdict để đổi đỏ thành xanh.
- Exit **0**: mọi run hợp lệ có verdict cuối pass; vẫn cần xem initial failures/recoveries. Exit **1**: dữ liệu hợp lệ nhưng có run fail sau hết retry. Exit **2**: có sự cố evidence/setup/transport/HTTP/cleanup hoặc batch chưa hoàn tất. Raw của run lỗi được giữ, batch ghi incomplete và không âm thầm lấy run khác bù.
- Chứng minh flakiness bằng cả pass và fail của attempt trên cùng implementation/điều kiện; báo riêng first-attempt result và final result. Không coi mọi lỗi hạ tầng là flake mục tiêu.
- Chứng minh bản sửa bằng sampled và độ trễ cao, **retry=0**; timing phải cho thấy POST hoàn tất trước khi GET history được gửi. Suite chính vẫn loại experiment; database gốc không đổi và không có handle mở khi kiểm tra tương ứng.
- Manual/AI triage là bước sau: hai bên nhận cùng analysis ZIP, lưu phân tích, thời lượng và review thật. Chưa có phân tích mới thì không gán kết quả Vượng/Sol cũ cho bộ dữ liệu mới.

Protocol v2.0 là thiết kế/kế hoạch. Kết quả local hoặc CI chỉ được bổ sung khi có log thực thi tương ứng.
