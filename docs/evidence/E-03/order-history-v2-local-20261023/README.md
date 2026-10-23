# Order history v2 — Kiểm chứng local ngày 23/10/2026

Đây là kiểm chứng implementation của [protocol v2.0](../../../experiments/order-history-protocol.md), chưa phải run mới trên GitHub Actions hoặc một lượt phân tích người–AI độc lập. Không thay thế dữ liệu E-03/E-04/E-08 cũ. Thời điểm trong log gốc dùng UTC; ngày local ở đây theo UTC+7.

**Trạng thái v2:** trang này giữ bằng chứng local của đợt triển khai. Đã có [batch timed trên CI riêng](../order-history-v2-ci-39860438568/README.md), [đối chiếu người–AI](../../E-08/order-history-v2-39860438568/AI_vs_Human_Triage.md) và [kết luận E-10](../../E-10/order-history-v2-39860438568/README.md). [Kiểm chứng `awaited` trên CI](../../E-09/order-history-v2-ci-39911447981/README.md) đạt 10/10 PASS, retry=0; xem [checklist](../../../tasks/checklist.md). Phân tích và thời lượng Vượng/Sol của cart tiếp tục thuộc v1.

## Thiết kế đã chạy

Test gửi POST đặt hàng qua HTTP gateway kiểm thử rồi đọc lịch sử đơn hàng thật. Gateway chỉ làm thay đổi thời gian request POST tới app; không giả response hoặc kết quả assertion. Bản `timed` dùng khoảng chờ cố định, bản `awaited` chờ POST thành công. Mọi attempt có app/SQLite mới; lần đọc `confirmation` sau POST không thay snapshot đầu được kiểm tra.

Ba batch sampled dùng cùng seed `7353499394879107841`, cùng lịch độ trễ dự kiến cho từng vị trí attempt và cùng source fingerprint. Seed được chọn ngẫu nhiên trước khi chạy; không đổi seed theo kết quả. Mỗi batch chốt 10 run và không lấy thêm mẫu bù. Các chẩn đoán độ trễ cố định là batch riêng.

## Kết quả thực tế

| Batch | Run | Retry tối đa | Pass/fail lần đầu | Phục hồi sau retry | Fail cuối | Tổng attempt | Exit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [timed-no-retry](timed-no-retry.collector.log) | 10 | 0 | 7 pass / 3 fail | 0 | 3 | 10 | 1 |
| [timed-retry2](timed-retry2.collector.log) | 10 | 2 | 7 pass / 3 fail | 2 | 1 | 14 | 1 |
| [awaited-no-retry](awaited-no-retry.collector.log) | 10 | 0 | 10 pass / 0 fail | 0 | 0 | 10 | 0 |
| [control-low: 20 ms](control-low.collector.log) | 1 | 2 | 1 pass / 0 fail | 0 | 0 | 1 | 0 |
| [control-high: 300 ms](control-high.collector.log) | 1 | 2 | 0 pass / 1 fail | 0 | 1 | 3 | 1 |
| [awaited-high: 300 ms](awaited-high.collector.log) | 1 | 0 | 1 pass / 0 fail | 0 | 0 | 1 | 0 |

Có **33 tiến trình Jest, 39 attempt** trong sáu batch này; không cộng run của suite chính vào mẫu. Batch retry=2 có 5 attempt fail: run-02 fail rồi pass; run-03 fail cả ba attempt; run-04 fail rồi pass. Bảy run còn lại pass ngay. Jest dừng sau pass và không vượt ba attempt.

Các batch đều hoàn tất, collector không ghi evidence error. Mười run bản sửa và ca latency cao đều không dùng retry; từng run có đúng một attempt và POST được nhận response trước khi gửi GET history. Đây là bằng chứng trong điều kiện đã chạy, không phải bảo đảm mọi môi trường đều không còn lỗi.

## Ví dụ đọc trace

Trong `timed-retry2`, run-02:

| Mốc phía client, ms từ gốc của run | Attempt 1 | Attempt 2 |
| --- | --- | --- |
| Gửi POST | 162.917 | 379.636 |
| Gửi GET history | 297.424 | 512.601 |
| Nhận GET history | 304.965 | 521.067 |
| Nhận POST | 331.686 | 518.587 |
| Số đơn ở snapshot history | 0 | 1 |
| Số đơn ở confirmation sau POST | 1 | 1 |

Attempt 1 có snapshot rỗng dù lần đọc sau POST xác nhận đơn đã tồn tại. Attempt 2 pass, nhưng GET cũng được gửi trước lúc client nhận response POST. Cần dùng thêm server events và response snapshot; không đồng nhất thời điểm client nhận POST với thời điểm dữ liệu bắt đầu nhìn thấy ở server. Các mốc không được đặt lại về 0 giữa retry và không phải duration toàn job.

Nguồn: `raw/run-02/events.jsonl`, `attempts.jsonl` và native `jest.json` bên trong [archive batch retry](timed-retry2.organizer-evidence.zip). Bản public giữ nguyên events, có thêm console đánh số dòng để trích dẫn.

## Bằng chứng và gói bàn giao

- [verification.json](verification.json): kế hoạch, kết quả sáu batch, runtime, source state, kiểm tra database và các phép kiểm tra phụ.
- [analysis-input.zip](analysis-input.zip): gói của **10 run timed-retry2**, sẵn để đưa cùng dữ liệu cho người và AI. Không cần chuẩn hóa thủ công.
- [timed-no-retry.organizer-evidence.zip](timed-no-retry.organizer-evidence.zip), [timed-retry2.organizer-evidence.zip](timed-retry2.organizer-evidence.zip), [awaited-no-retry.organizer-evidence.zip](awaited-no-retry.organizer-evidence.zip): nguồn đầy đủ từng batch.
- [control-low.organizer-evidence.zip](control-low.organizer-evidence.zip), [control-high.organizer-evidence.zip](control-high.organizer-evidence.zip), [awaited-high.organizer-evidence.zip](awaited-high.organizer-evidence.zip): chẩn đoán riêng.
- [normal-suite.results.json](normal-suite.results.json), [console suite chính](normal-suite.console.log): kiểm tra discovery và regression của suite mặc định.

Archive organizer chứa native Jest JSON/console, original event/attempt/control ledger, manifest, implementation snapshot và gói participant của chính batch đó. Không gửi organizer archive hoặc README có lời giải này cho người phân tích trước khi họ lưu kết quả. Hai file log/JSON cùng biểu diễn một attempt, không phải hai lần chạy.

## Kiểm tra phụ và phạm vi

- 7/7 kiểm tra contract collector pass: phát hiện mất retry, mất HTTP event, retry sau pass, ngừng trước hết budget, sửa snapshot/verdict và rò rỉ vào ZIP; xác nhận event trong ZIP bằng bytes của event gốc.
- Lint pass, build kiểm tra cú pháp 18 file pass; Python syntax và cấu trúc YAML workflow hợp lệ khi kiểm tra local.
- Cả 12 ZIP của sáu batch kiểm tra CRC thành công. Public packet không chứa raw/source/controls và event bytes khớp nguồn.
- Suite chính vẫn có **39 test: 29 pass, 10 fail nghiệp vụ đã biết**, không chọn experiment. Danh sách failure khớp baseline, không handle mở khi dùng `--detectOpenHandles`.
- Database gốc không đổi. Ca sửa latency cao cũng được chạy với `--detectOpenHandles`; Jest không ghi handle mở.
- Môi trường: Windows, Node v24.14.0, Jest 30.5.2, Python 3.13.12. Implementation được chạy từ working tree trên base `115df94`; source fingerprint và snapshot trong từng archive giữ phần thí nghiệm chưa commit. Không gán dữ liệu này cho một SHA sạch hoặc runner Ubuntu.

Workflow chạy cùng bộ điều phối và xuất hai artifact riêng. [Batch CI trên revision 52e4006](../order-history-v2-ci-39860438568/README.md) được lưu riêng, không thay số liệu local ở trang này. Phân tích Vượng/Sol cart chỉ áp dụng bộ cũ; nhận định và thời gian của họ không được gán cho ZIP local hoặc CI v2.

## Cập nhật đóng gói sau đợt đo

Các batch chạy sau xuất `analysis-input-<batch-id>.zip` và `organizer-evidence-<batch-id>.zip`, với batch ID gồm timestamp UTC và mã ngẫu nhiên. ZIP public có `packet_id` trong history; tên không chứa variant hoặc đáp án. Những archive ở trang này giữ tên/nội dung của đợt đo ban đầu; source snapshot và fingerprint của chúng cũng thuộc thời điểm đó.

Thay đổi đặt tên được kiểm tra riêng: 8/8 contract test pass; hai batch chẩn đoán có cùng tên thư mục cuối `ci` vẫn xuất tên ZIP khác nhau, đọc được đầy đủ và giữ nguyên event bytes. Chạy lại vào thư mục đã tồn tại bị từ chối với exit 2, các ZIP cũ không đổi. Hai lượt này không được cộng vào mẫu sampled ở bảng trên; chi tiết nằm trong `packaging_update` của verification.json.
