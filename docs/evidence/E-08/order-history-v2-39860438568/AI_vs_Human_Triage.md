# E-08 — So sánh người và AI, order history v2

Ngày đối chiếu: 23/10/2026. Batch `20261022T215153Z-1abf079b`, CI [39860438568](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39860438568), revision `52e400689109b5423ad04eb2bef41280a0f149ff`.

## 1. Kết quả chính

**Vượng và AI cùng nhận diện vấn đề thứ tự: history được gửi khoảng 120 ms sau submit, có thể đọc khi thao tác đặt hàng chưa hoàn tất.** Cả hai đọc đúng retry history: 5 run fail lần đầu, 3 phục hồi sau retry và 2 vẫn fail cuối cùng. Confirmation của cả 19 attempt đều thấy một đơn; kết quả đó không thay thế snapshot history bị assertion kiểm tra.

Vượng tự thực hiện trong **20 phút**, hoàn thiện **trước khi xem output AI**; lượt AI v2 do **GPT-6.1 Sol** thực hiện, theo xác nhận của người dùng. AI ghi **39 giây đến mốc chốt bằng chứng**, chưa gồm thời gian soạn trả lời. Hai khoảng đo khác phạm vi, nên không tính hệ số nhanh hơn hoặc kết luận AI tiết kiệm bao nhiêu phút.

## 2. Nguồn và điều kiện so sánh

| Thành phần | Hồ sơ |
| --- | --- |
| Dữ liệu đối chiếu chung | [ZIP participant](ai-skill/api-analysis-input-39860438568-1.zip): 43 file, 10 tiến trình Jest, 19 attempt; console và JSONL biểu diễn cùng sự kiện |
| Phân tích thủ công | [Bản của Vượng](../../E-04/order-history-v2-39860438568/phan-tich-order-history.md), giữ nguyên file bàn giao; thời lượng 20 phút do người dùng xác nhận |
| Phân tích AI | **GPT-6.1 Sol**, dùng skill `ci-log-triage`; [output nguyên bản](ai-skill/response.md), [prompt](ai-skill/prompt.md), [metadata](ai-skill/metadata.json). Model v2 do người dùng xác nhận |
| Phạm vi đầu vào | Packet có HTTP trace, assertion, fixture và retry; không có source, latency controls hoặc đáp án thiết kế. README cho biết đây là dữ liệu thí nghiệm, nên không mô tả là log sản xuất hoặc hoàn toàn không có gợi ý về bối cảnh |
| Đối chứng của người đánh giá | [CI và organizer evidence E-03](../../E-03/order-history-v2-ci-39860438568/README.md), chỉ dùng sau khi nhận các bản phân tích; không coi phần này là dữ liệu người/AI đã được đọc lúc triage |

Tài liệu Vượng khớp dữ kiện của packet trên. Người dùng xác nhận riêng cho v2 rằng Vượng tự phân tích trong 20 phút, trước khi xem output AI. Hồ sơ AI gồm output bàn giao và model được xác nhận; chưa có đầy đủ phiên AI gốc để kiểm toán bối cảnh của lượt chạy. Thời lượng 90 giây và review của v1 tiếp tục thuộc đợt cũ. Bản so sánh v2 được review qua [PR #21](https://github.com/SUT-group10/eshop-sut-group10/pull/21).

## 3. Kiểm tra kết quả và retry

| Run | Chuỗi attempt | Retry đã dùng | Kết quả cuối |
| --- | --- | ---: | --- |
| 01 | P | 0 | PASS |
| 02 | F → P | 1 | PASS |
| 03 | F → F → P | 2 | PASS |
| 04 | F → F → F | 2 | FAIL |
| 05 | F → F → F | 2 | FAIL |
| 06 | P | 0 | PASS |
| 07 | P | 0 | PASS |
| 08 | F → F → P | 2 | PASS |
| 09 | P | 0 | PASS |
| 10 | P | 0 | PASS |

Đối chiếu `history.json`, từng `result.json`, `attempts.json` và trace: **10 run, 19 attempt, 9 retry; 8 attempt pass, 11 attempt fail; verdict cuối 8 run pass/2 fail**. Cả 11 failure là `HISTORY_ORDER_COUNT`, expected 1/actual 0, không có additional failure. Cả 57 response của ba thao tác submit/history/confirmation trả HTTP 200. Native Jest trong organizer khớp invocation, retry reasons và verdict; không có retry sau pass hoặc quá ba attempt.

Hai bên tổng hợp đúng các số liệu này. Tỷ lệ fail lần đầu **5/10**, tỷ lệ fail cuối **2/10** và tỷ lệ fail trên toàn bộ attempt **11/19** có mẫu số khác nhau. Attempt bổ sung chỉ xuất hiện sau fail; không coi 19 attempt là 19 mẫu độc lập được chọn sẵn.

## 4. Đối chiếu theo rubric E-08

| Tiêu chí | Vượng | AI dùng skill | Đánh giá |
| --- | --- | --- | --- |
| Root cause | H1: history theo mốc gần cố định, không chờ submit; H2 phân tích biến thiên submit; H3 read-after-write yếu | Một H1 về điều phối và thời điểm đọc; chưa quy trách nhiệm cho test hoặc sản phẩm | Đồng thuận về cơ chế nghi ngờ. H2 là yếu tố làm race biến thiên; H3 chưa được dữ liệu ủng hộ như nguyên nhân chính |
| Bằng chứng | So sánh server received/completed, khoảng thời gian hai nhóm, confirmation và duration attempt cuối | Nối client sent/received, request ID, toàn bộ attempt, retry/fixture mới | Cả hai có dẫn chứng đúng. Server completion và client receive là hai mốc khác nhau; chênh lệch số không phải mâu thuẫn |
| Next-checks | Rà điều phối; thêm mốc DB; chạy hai biến thể có kiểm soát, đề nghị ≥20 lần mỗi biến thể | Rà đúng promise được chờ; điều khiển latency; nối commit/query bằng request ID | Đều có đúng ba hướng khả thi. Số lần Vượng đề xuất là kế hoạch xác minh, không phải số lần đã chạy hoặc yêu cầu của đề |
| Thời gian | 20 phút hoàn thiện | 39 giây đến chốt bằng chứng, loại thời gian soạn output | Chưa so sánh tốc độ hoàn thiện trên cùng phạm vi đo |
| Suy diễn/hallucination | Giữ giới hạn thiếu source/commit, nhưng nhận xét GET và phép tính xác suất cần thu hẹp | Không khẳng định timer/thiếu await cụ thể; nhãn “cửa sổ CI” quá rộng | Không có chẩn đoán bịa được xác nhận. Có các điểm diễn đạt hoặc suy luận cần review ở mục 5 |

## 5. Dẫn chứng cụ thể và điểm cần làm rõ

**Quan hệ thời gian chính được kiểm chứng.** Ở run-02/attempt 1, console L0005 ghi gửi submit tại 172.552 ms; L0007 gửi history tại 292.894 ms; L0008 history đến server tại 294.763 ms và L0010 client nhận 0 đơn tại 297.566 ms. L0011 submit hoàn tất phía server tại 329.099 ms; L0012 client nhận submit tại 329.849 ms. Confirmation sau đó thấy 1 đơn, còn L0024 vẫn fail trên snapshot history. Vượng dùng mốc server, AI dùng mốc client, đều đúng ở ví dụ này.

Trong cả 19 attempt, 11 failure có history đến server trước submit server completion; 8 pass có thứ tự ngược lại. Khoảng từ client gửi submit đến gửi history là **119.636–121.437 ms**. Đây là quan hệ quan sát trong mẫu, không phải chứng minh rằng mọi request vượt đúng 120 ms sẽ fail ở mọi môi trường. Mốc response cũng không tự là mốc commit DB.

**Nhận xét GET “chỉ mất 1–2 ms” của Vượng không đúng cho toàn bộ mẫu.** Ở run-10/attempt 1, `console.log` L0011 ghi history server duration **8.780 ms**, L0016 ghi confirmation **11.585 ms**. Các GET vẫn nhanh hơn submit ở ca này; hai ngoại lệ không bác bỏ H1. Cần đọc nhận xét đó như xu hướng, không dùng nó để loại tuyệt đối mọi biến thiên phía đọc. “Server xử lý submit” trong log đo từ gateway nhận request đến response hoàn tất; khi đối chiếu implementation, khoảng này bao gồm độ trễ gateway, không chỉ thời gian handler nghiệp vụ hoặc DB.

**Nhận xét duration của Vượng đúng ở bộ dữ liệu này.** Run-03 có native Jest `duration = 155 ms`; ledger ghi attempt cuối **154.867 ms**, còn tổng ba attempt **660.670 ms**; toàn process **1519.160 ms**. Không dùng duration attempt cuối làm tổng chi phí retry. Các process có retry trong mẫu dài hơn nhóm không retry, nhưng để ước lượng riêng tác động của policy cần đối chứng cùng seed/điều kiện; so hai nhóm quan sát không tự là phép đo nhân quả.

**Phép tính xác suất trong H2 của Vượng chỉ có ý nghĩa minh họa.** `(11/19)^3 ≈ 0.19` cần giả định các attempt độc lập và cùng xác suất chậm; packet chưa chứng minh giả định đó. Sau khi đã điều kiện hóa run fail ở attempt đầu, còn hai attempt cần xét, không phải ba. Thêm nữa, 11/19 là tỷ lệ trên mẫu có dừng sau pass. Không dùng phép tính này để ước lượng xác suất lỗi thật hoặc xác nhận/bác bỏ ảnh hưởng theo process. Bản gốc cũng ghi chưa đủ để khẳng định yếu tố process.

**“Cửa sổ CI” 13.418 giây trong output AI cần đặt đúng tên.** Đây là khoảng từ bắt đầu process Jest đầu đến kết thúc process cuối theo history, không phải duration toàn job. Metadata [E-03](../../E-03/order-history-v2-ci-39860438568/batch.json) ghi job 104 giây; khoảng `run_started_at → updated_at` của workflow là 109 giây. Output không bịa mốc, nhưng nhãn có thể gây so sánh hiệu năng sai nếu chép thẳng vào report.

**Retry không đợi đơn cũ xuất hiện.** Mỗi attempt có fixture/database mới; AI nêu rõ điều này. Vượng cũng ghi fixture mới. Run-02 phục hồi ở retry nghĩa là lần thực thi mới pass; confirmation trong cùng attempt mới là quan sát đơn đã đọc được sau submit. Không có bằng chứng hai bên nhầm trạng thái từ attempt trước.

## 6. Đối chiếu với thiết kế đã biết

Phần này thuộc đánh giá của người tổ chức. Source snapshot của revision đo trong organizer cho thấy bản `timed` khởi phát POST, đợi cố định 120 ms rồi gửi GET history; chỉ chờ POST sau khi đã giữ snapshot history. Gateway làm biến thiên thời gian chuyển POST tới app thật. Lần đọc confirmation và fixture reset được giữ riêng. **H1 của cả hai phù hợp thiết kế đã biết; H2 mô tả đúng yếu tố biến thiên nhưng log participant không cho phép xác định độ trễ nằm ở gateway.** H3 chưa có bằng chứng read-after-write sau response bị lỗi trong batch này.

Bản `awaited` đổi điều kiện gửi history thành POST hoàn tất và trả HTTP 200. [Kiểm chứng local v2](../../E-03/order-history-v2-local-20261023/README.md) đã có đối chứng trước/sau và latency cao, thuộc đợt/revision làm việc riêng. Đối chiếu source và kết quả local hỗ trợ cơ chế. Sau khi lưu hai bản phân tích, [batch CI awaited 39911447981](../../E-09/order-history-v2-ci-39911447981/README.md) xác nhận 10/10 PASS không retry và POST hoàn tất trước GET. Đây là bước kiểm chứng của người tổ chức, không ghi thành các next-checks do hai bên đã thực hiện lúc triage.

## 7. Giá trị của AI và trạng thái

AI có giá trị ở việc tổng hợp đủ retry chain, tách verdict lần đầu/cuối, nối request ID và giữ giới hạn suy luận từ log. Vượng đạt cùng chẩn đoán chính, đồng thời chỉ ra rõ duration attempt cuối có thể làm run retry trông nhanh hơn. Kết quả đồng thuận là hợp lệ; không cần tạo khác biệt hoặc ép đủ ba lỗi AI để đánh giá.

Nhiễu thực tế cần kiểm soát là nhãn duration “CI” quá rộng. Việc biến 39 giây thành thời gian hoàn thiện toàn bộ sẽ là lỗi của phép so sánh, không phải điều output AI đã khẳng định. Bản thủ công cũng cần review các khái quát về GET và xác suất. Bộ dữ liệu có chủ đích, trace tương đối đầy đủ và một output AI được bàn giao; chưa đủ để kết luận chất lượng trên mọi CI log hoặc hiệu quả riêng của skill so với không dùng skill.

**Đã hoàn thiện E-08 v2:** lưu hai bản gốc và đối chiếu theo năm tiêu chí; xác nhận Vượng tự phân tích 20 phút trước khi xem output AI và model AI v2 là GPT-6.1 Sol. Review thực hiện qua PR. Tổng thời gian hoàn thiện output AI giữ chưa xác định; 39 giây chỉ đến mốc chốt bằng chứng. [E-10 v2](../../E-10/order-history-v2-39860438568/README.md) chốt giá trị/nhiễu và ba failure modes; [E-09](../../E-09/order-history-v2-ci-39911447981/README.md) đã xác nhận `awaited` trên CI, 10/10 PASS không retry.
