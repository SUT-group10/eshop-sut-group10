# E-09 — Xác nhận bản sửa order history v2 trên CI

**Đã xác nhận 10/10 run PASS ngay lần đầu, retry=0.** Cả 10 run đều nhận POST thành công trước khi gửi GET history; snapshot history và confirmation đều có đúng một đơn. Đây là kết quả thực thi và kiểm tra trace, không chỉ dựa trên màu xanh của workflow.

## Revision và điều kiện chạy

- [GitHub run 39911447981](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39911447981), workflow `Flaky experiment (manual only)`, attempt 1; branch `test/issue-5-flaky-retry-v2`.
- Revision đo: `13e50679ef6fa9261dfe933babf62a4a5722fb86`, working tree sạch; batch `20261023T062730Z-ccd45ce7`.
- Variant **awaited**, 10 tiến trình Jest độc lập, **retry limit 0**; [protocol v2](../../../experiments/order-history-protocol.md).
- Node v24.14.0, Jest 30.5.2, Python 3.10.12, Linux; runner Ubuntu 22.04 theo workflow. Runtime, seed, thời điểm và toàn bộ run được lưu trong [batch.json](batch.json).
- Job bắt đầu 23/10/2026 **06:26:09 UTC**, kết thúc **06:27:47 UTC**; tương ứng 13:26:09–13:27:47 UTC+7.

## Kết quả và quan hệ chờ

| Metric | Count |
| --- | ---: |
| planned_runs / validated_runs | 10 / 10 |
| first_attempt_pass | 10 |
| recovered_after_retry / final_fail | 0 / 0 |
| total_attempts / failed_attempts | 10 / 0 |
| evidence_errors | 0 |

Cả 10 native Jest report có `invocations=1`, không `retryReasons`, status passed và process exit 0. Có 300 event, 30 response của submit/history/confirmation đều HTTP 200, 10 fixture đóng thành công và không assertion fail.

Ví dụ run-01: client nhận POST lúc **361.895 ms**, gửi history lúc **362.339 ms**. Run-10: nhận POST **328.837 ms**, gửi history **329.170 ms**. [batch.json → ordering_verification](batch.json) lưu hai mốc của cả 10 run; mọi run có `submit_response_ms < history_sent_ms`. Các mốc chỉ so trong cùng run, không phải duration toàn job.

## File gốc và kiểm tra

- [organizer-evidence-39911447981-1.zip](organizer-evidence-39911447981-1.zip): artifact gốc chứa ZIP organizer, raw/native Jest, events, attempts, controls, source snapshot và packet participant.
- [api-analysis-input-39911447981-1.zip](api-analysis-input-39911447981-1.zip): artifact participant của batch sau sửa, giữ riêng với đầu vào triage `timed`.
- [job-logs.zip](job-logs.zip): log CI gốc.
- [batch.json](batch.json): metadata GitHub, kế hoạch thực thi, runtime, source fingerprint, kết quả từng run, kiểm tra thứ tự và checksum.

Cả hai artifact khớp digest GitHub API; các archive qua kiểm tra CRC. Toàn bộ 43 file participant khớp packet nằm trong organizer; events và attempts khớp raw; native Jest khớp verdict và invocation. Cả 13 source fingerprint khớp revision đã chạy. Việc thu hồ sơ chỉ tải run người dùng đã thực hiện, không tạo run mới.

## Kết luận

[Batch timed trước sửa](../../E-03/order-history-v2-ci-39860438568/README.md) có 5/10 run fail lần đầu và 2 fail cuối sau retry. Batch `awaited` này có 10/10 pass không retry, cùng quan hệ POST hoàn tất trước GET trong cả 10 trace. Kết quả hỗ trợ nguyên nhân đồng bộ mà [Vượng và Sol nhận diện ở E-08](../../E-08/order-history-v2-39860438568/AI_vs_Human_Triage.md), cùng [đối chứng local](../../E-03/order-history-v2-local-20261023/README.md).

Hai batch CI có revision, seed và thời điểm riêng; không dùng chúng để tính riêng tác động của retry hoặc so tốc độ. Source fingerprint của các file thực thi được đối chiếu trong metadata; revision sau cập nhật hồ sơ không thay revision đo. E-09 v2 hoàn thành trên các điều kiện đã chạy; số mẫu hữu hạn không bảo đảm mọi lỗi đều đã bị loại bỏ.
