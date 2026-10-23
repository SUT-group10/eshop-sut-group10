# E-03 — Đợt đo 20261021-b252db4-01

> Đây là **evidence v1 — cart**: 10 dispatch trên revision đã chốt, không retry test. Log, ZIP và metadata bên dưới giữ nguyên phạm vi v1. [Protocol v2 hiện hành](../../../experiments/order-history-protocol.md).

- **Protocol:** [E-02 v1.1](../../../experiments/flaky-test-protocol.md), revision `b252db4aa9e236b78879dfbbf7b882cdadb8580c`.
- **Phiên bản đo:** `b252db4aa9e236b78879dfbbf7b882cdadb8580c`; branch `test/issue-5-flaky-experiment`; workflow `flaky-experiment.yml`.
- **Kế hoạch chốt trước lượt đầu:** 10 dispatch mới, tuần tự, `sampled`, không retry test, không dùng rerun/rehearsal làm mẫu.
- **Người thực hiện thu dữ liệu:** AI qua GitHub API theo yêu cầu; đây không phải manual triage của E-04.
- **Bắt đầu UTC:** 2026-10-21T15:10:54.836021Z; **kết thúc UTC:** 2026-10-21T15:53:36.211516Z.
- **Trạng thái:** completed.

## Bảng run

Mỗi run dùng SHA đầy đủ ở trên; SHA từng run, SHA ghi trong runtime và toàn bộ thời gian UTC được lưu trong [batch.json](batch.json). Duration job và duration test là hai số đo riêng.

| Lượt | Run URL | Case | Jest | Phân loại | Job (s) | Test (ms) | File gốc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 | [39623369899](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39623369899) | slow | failed | TIMING_FAIL | 74.0* | 339 | [console](01-39623369899/console.log), [JSON](01-39623369899/results.json), [job logs](01-39623369899/job-logs.zip) |
| 02 | [39624265758](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39624265758) | fast | passed | PASS | 64.0 | 214 | [console](02-39624265758/console.log), [JSON](02-39624265758/results.json), [job logs](02-39624265758/job-logs.zip) |
| 03 | [39624665367](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39624665367) | slow | failed | TIMING_FAIL | 90.0 | 353 | [console](03-39624665367/console.log), [JSON](03-39624665367/results.json), [job logs](03-39624665367/job-logs.zip) |
| 04 | [39624963584](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39624963584) | fast | passed | PASS | 113.0 | 319 | [console](04-39624963584/console.log), [JSON](04-39624963584/results.json), [job logs](04-39624963584/job-logs.zip) |
| 05 | [39625334520](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39625334520) | slow | failed | TIMING_FAIL | 61.0 | 298 | [console](05-39625334520/console.log), [JSON](05-39625334520/results.json), [job logs](05-39625334520/job-logs.zip) |
| 06 | [39625583748](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39625583748) | fast | passed | PASS | 90.0 | 298 | [console](06-39625583748/console.log), [JSON](06-39625583748/results.json), [job logs](06-39625583748/job-logs.zip) |
| 07 | [39625896690](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39625896690) | slow | failed | TIMING_FAIL | 84.0 | 362 | [console](07-39625896690/console.log), [JSON](07-39625896690/results.json), [job logs](07-39625896690/job-logs.zip) |
| 08 | [39626153807](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39626153807) | fast | passed | PASS | 85.0 | 312 | [console](08-39626153807/console.log), [JSON](08-39626153807/results.json), [job logs](08-39626153807/job-logs.zip) |
| 09 | [39629190485](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39629190485) | fast | passed | PASS | 97.0* | 311 | [console](09-39629190485/console.log), [JSON](09-39629190485/results.json), [job logs](09-39629190485/job-logs.zip) |
| 10 | [39629561358](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39629561358) | slow | failed | TIMING_FAIL | 73.0 | 302 | [console](10-39629561358/console.log), [JSON](10-39629561358/results.json), [job logs](10-39629561358/job-logs.zip) |

## Môi trường

Node `v24.14.0`, npm `11.9.0`, image `ubuntu-22.04` version `20261018.327.1`, runner `2.338.0`. Các lượt phải khớp baseline này; action SHA được lưu trong metadata.

## Kết quả

Đã ghi 10/10 lượt. Kết quả Jest: **5 PASS, 5 FAIL do timing**; không có lỗi test khác.

Đủ 10 lượt có kết quả test theo protocol đã chốt. Tỷ lệ test fail quan sát: 5/10 = 50%. Đã quan sát cả pass và fail trong đợt này.

| Case | PASS | TIMING_FAIL |
| --- | --- | --- |
| fast | 5 | 0 |
| slow | 0 | 5 |

Dấu `*` ở thời gian job là khoảng quan sát từ `started_at` của job đến `completed_at` của bước Complete job, khi metadata cấp job chưa được GitHub hoàn tất. Đây không phải giá trị `job_duration_seconds`; trường đó giữ null trong batch.json, kèm nguồn và ghi chú. Metadata gốc không bị sửa.

## Nguồn và retry history

- `run.json`, `jobs.json`, `artifacts.json` ở từng thư mục run là metadata từ GitHub API; `run.json` lưu các trường được chọn, không chứa credential hoặc email tác giả commit.
- `job-logs.zip` là log job gốc; `artifact.zip` là artefact gốc; `console.log` và `results.json` lấy nguyên byte từ artefact, không sửa output.
- `run_attempt`, số lần thực thi Jest, retry messages/reasons và exit code cùng nguồn xác định được lưu cho từng lượt trong `batch.json`. Retry HTTP khi tải metadata/file, nếu có, ghi riêng; không phải retry test.
- [SHA256SUMS](SHA256SUMS) kiểm tra tính toàn vẹn các file đã lưu, gồm cả archives và metadata. Không tính chính file checksum vào danh sách hash.
- Phân loại theo protocol để thu dữ liệu; các file này không phải kết quả manual triage hay AI triage mù. Các lượt rehearsal được loại khỏi đợt đo này.
