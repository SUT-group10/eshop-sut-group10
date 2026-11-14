# E-03 — Batch CI order history v2, 39860438568

**Đã thu đủ 10 run, 19 attempt, retry tối đa 2; dữ liệu hợp lệ, collector không ghi evidence error.** Kết quả lần đầu 5 pass/5 fail; 3 run phục hồi sau retry; kết quả cuối 8 pass/2 fail. Workflow đỏ vì hai run vẫn fail sau retry, không phải do thất bại cài đặt hoặc upload artifact.

## Revision và môi trường

- [GitHub Actions run 39860438568](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39860438568), workflow `Flaky experiment (manual only)`, workflow attempt **1**; branch `test/issue-5-flaky-retry-v2`.
- Source revision `52e400689109b5423ad04eb2bef41280a0f149ff`, working tree sạch lúc đo. Batch `20261022T215153Z-1abf079b`, [protocol v2.0](../../../experiments/order-history-protocol.md).
- Variant `timed`, 10 tiến trình Jest mới chạy tuần tự trong **một dispatch**, retry=2; tối đa 3 attempt mỗi run. Số workflow attempt không phải số retry của test.
- Ubuntu 22.04.5, image `ubuntu-22.04` phiên bản `20261012.322.1`; Node v24.14.0, npm 11.9.0, Jest 30.5.2, Python 3.10.12.
- Seed `17264554395344709815`, sampled latency 20–220 ms, observation wait 120 ms. Đây là thông tin organizer, không nằm trong ZIP participant.

## Kết quả và thời gian

Run-01/06/07/09/10 pass ngay; run-02 **F → P**; run-03/08 **F → F → P**; run-04/05 **F → F → F**. Có 9 attempt retry thực tế. Cả 11 attempt fail ở `HISTORY_ORDER_COUNT`, expected 1/actual 0. Cả 19 confirmation thấy 1 đơn; 57 response được theo dõi đều HTTP 200. Không loại run bất lợi hoặc lấy thêm mẫu bù.

Collector chạy **22/10/2026 21:51:53.804–21:52:07.245 UTC**, tương ứng 04:51:53.804–04:52:07.245 ngày 23/10 UTC+7. Các khoảng thời gian khác nhau:

| Phạm vi | Thời lượng | Nguồn |
| --- | ---: | --- |
| Process Jest đầu bắt đầu → process cuối kết thúc | 13.418 giây | `organizer.json → runs[]` |
| Toàn collector | 13.441 giây | `organizer.json → started_at_utc/completed_at_utc` |
| Job order-history | 104 giây | GitHub job `started_at/completed_at` |
| Workflow `run_started_at → updated_at` | 109 giây | Metadata GitHub; `updated_at` không phải trường `completed_at` chuyên biệt |

`jest_test_duration_ms`, duration attempt, process duration và duration job không dùng thay cho nhau. Toàn bộ thời điểm và duration từng run được giữ trong [batch.json](batch.json) và organizer archive.

## File gốc và kiểm tra

- [organizer-evidence-39860438568-1.zip](organizer-evidence-39860438568-1.zip): artifact người dùng bàn giao, giữ nguyên byte. ZIP ngoài chứa ZIP organizer của batch, bên trong có `organizer.json`, `raw/run-NN/` (native Jest JSON/console, events, attempts, controls), source snapshot và ZIP participant.
- [ZIP participant](../../E-08/order-history-v2-39860438568/ai-skill/api-analysis-input-39860438568-1.zip): artifact analysis đã lưu cùng output AI; dùng file này để bàn giao cho người/AI. Không gửi organizer archive, trang này hoặc bản so sánh trước khi phân tích.
- [job-logs.zip](job-logs.zip): log workflow lấy từ GitHub API, giữ nguyên archive tải về.
- [batch.json](batch.json): metadata được chọn từ GitHub run/job/artifacts, runtime, plan, 10 run, checksum artifact và kết quả đối chiếu. Không lưu credential hay email commit author.

Cả hai artifact có checksum khớp digest GitHub API. Các ZIP qua kiểm tra CRC; 43 file participant khớp nội dung ZIP nằm trong organizer; event bytes và per-attempt ledger khớp bản raw. Mười native Jest report khớp invocation, retry reasons, status và duration; có 9 retry reasons, 526 event và 19 fixture đóng thành công. Cả 13 source fingerprint khớp file tại revision đo.

Việc lưu và kiểm tra hồ sơ này đọc lại batch hiện có, **không tạo dispatch hoặc run mới**. [Phân tích Vượng](../../E-04/order-history-v2-39860438568/README.md) và [đối chiếu E-08](../../E-08/order-history-v2-39860438568/AI_vs_Human_Triage.md) được lưu riêng. [Batch `awaited` trên CI](../../E-09/order-history-v2-ci-39911447981/README.md) đã đạt 10/10 PASS với retry=0; giữ riêng hai batch và các kết quả local.
