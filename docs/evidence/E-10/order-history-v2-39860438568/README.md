# E-10 — Giá trị, nhiễu và ba failure modes của AI, v2

Ngày chốt: 23/10/2026. Phạm vi: GPT-6.1 Sol dùng `ci-log-triage`, phân tích batch order history [CI 39860438568](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39860438568). Nguồn gồm [output AI nguyên bản](../../E-08/order-history-v2-39860438568/ai-skill/response.md), [phân tích Vượng](../../E-04/order-history-v2-39860438568/README.md), [đối chiếu E-08](../../E-08/order-history-v2-39860438568/AI_vs_Human_Triage.md), [packet đầu vào](../../E-08/order-history-v2-39860438568/ai-skill/api-analysis-input-39860438568-1.zip) và [metadata CI](../../E-03/order-history-v2-ci-39860438568/batch.json).

## 1. Mục tiêu và cách hiểu failure mode

Đề T07 yêu cầu đánh giá AI mang lại giá trị hay tạo nhiễu trong CI, đồng thời User Guide phải nêu ba cách công cụ có thể gây hiểu nhầm. Xem [brief, mục 2 và 9](../../../requirements/T07_CI-CD_and_Test-Harness_Engineering.docx.md). Failure mode ở đây là **cơ chế khiến việc đọc hoặc sử dụng kết quả AI dẫn tới kết luận sai**, có dữ liệu thực tế minh họa và cách phát hiện/phòng tránh.

Ba mục dưới phân biệt rõ trạng thái: **FM-01 có cách đặt nhãn dễ gây hiểu nhầm trong output Sol; FM-02 và FM-03 là rủi ro được dữ liệu cho thấy, nhưng Sol đã xử lý đúng trong lượt này**. Đây không phải hồ sơ ba lần Sol chẩn đoán sai. Checklist nhóm về failure modes không được diễn giải thành yêu cầu phải tạo đủ ba lỗi AI; kết quả đúng vẫn được giữ nguyên.

## 2. AI thực sự mang lại giá trị ở đâu?

Sol tổng hợp đúng **10 run, 19 attempt, 9 retry**; tách **5 pass/5 fail lần đầu**, **3 run phục hồi** và **8 pass/2 fail cuối**. AI nối request ID, phân biệt snapshot history với confirmation và chỉ ra thứ tự đọc trước khi submit hoàn tất ở cả 11 attempt fail. Kết luận chính đồng thuận với Vượng và phù hợp thiết kế được kiểm tra sau triage.

Output đưa một giả thuyết có dẫn chứng và đúng ba bước xác minh, giữ giới hạn thiếu source/commit DB. Giá trị quan sát được là tổ chức và đối chiếu dữ liệu, lập hướng điều tra có thể kiểm chứng. Vượng cũng tìm đúng vấn đề, nên chưa có bằng chứng AI phát hiện điều con người bỏ sót hoặc chính xác hơn người.

Vượng tự phân tích **20 phút**, trước khi xem output AI. Sol ghi **39 giây đến mốc chốt bằng chứng**, loại thời gian soạn trả lời; chưa có tổng thời lượng tương đương để tính mức tiết kiệm thời gian. Chưa có lượt đối chứng không dùng skill để tách riêng hiệu quả của skill khỏi năng lực model.

## 3. FM-01 — Gán sai phạm vi cho số đo thời gian

**Cơ chế:** AI trích đúng con số nhưng đặt tên quá rộng, khiến người đọc dùng thời gian một phần làm duration toàn CI hoặc so hai số khác phạm vi.

- **Dữ kiện:** phần Thời gian của output gọi khoảng **13.418 giây** là “cửa sổ CI”. Theo `history.json`, đó là từ bắt đầu process Jest đầu đến kết thúc process cuối. Metadata GitHub ghi **job 104 giây**; collector là **13.441 giây**. Các con số đo những phạm vi khác nhau.
- **Hậu quả nếu tin nhãn:** báo cáo sai tốc độ toàn pipeline, bỏ thời gian cài đặt và upload. Tương tự, lấy 39 giây chốt bằng chứng so trực tiếp với 20 phút hoàn thiện sẽ làm sai phép so người–AI; Sol đã nêu đúng giới hạn của 39 giây.
- **Kiểm chứng:** mở `batch.json → timing`, `github_job.started_at/completed_at` và `history.json → runs[]`; ghi tên đại lượng, đơn vị, hai đầu mốc và phạm vi. Run-03 còn có native Jest duration **155 ms**, tổng ba attempt **660.670 ms**, toàn process **1519.160 ms**: không dùng thay cho nhau.
- **Biện pháp:** khi AI báo duration, yêu cầu kèm trường nguồn và định nghĩa khoảng đo. Dùng nhãn “cửa sổ các process Jest” cho 13.418 giây.

**Đánh giá lượt Sol:** có nhãn cần làm rõ; các giá trị được trích đúng. Chưa có lỗi kết luận root cause từ điểm này.

## 4. FM-02 — Tóm tắt verdict cuối làm mất failure trước retry

**Cơ chế:** AI chỉ đọc `status` cuối hoặc rút gọn bảng thành “8/10 pass”, rồi kết luận test ổn định hoặc retry đã sửa lỗi. Nhiều bản log/JSON biểu diễn cùng dữ liệu còn có thể khiến AI đếm trùng run.

- **Dữ kiện:** run-02 là **F → P**, run-03/08 là **F → F → P**; run-04/05 là **F → F → F**. Chỉ đọc kết quả cuối thấy 2/10 fail, trong khi lần đầu là 5/10; tổng cộng có 11 attempt fail. Mỗi attempt dùng fixture mới, nên lần retry pass không chứng minh đơn của attempt trước vừa xuất hiện.
- **Hậu quả:** đánh giá thấp flakiness, coi retry là cách sửa đồng bộ hoặc báo sai tỷ lệ fail khi dùng 19 attempt như 19 run độc lập.
- **Kiểm chứng:** đối chiếu `history.json → initial_status/status/invocations/test_retries_used`, `run-NN/attempts.json` và fixture ID. Người tổ chức kiểm tra thêm native Jest `invocations/retryReasons` trong organizer. Báo ba mẫu số riêng: run lần đầu, run cuối và toàn bộ attempt.
- **Biện pháp:** yêu cầu AI luôn xuất retry chain và kết quả đầu/cuối; giữ các attempt fail trong dữ liệu bàn giao, kể cả run cuối pass. Không tính console, JSONL và JSON report thành các run mới.

**Đánh giá lượt Sol:** tránh được failure mode này. Output giữ đủ chuỗi retry, mẫu số và lưu ý fixture mới; bằng chứng batch minh họa rõ hậu quả nếu bỏ bước đó.

## 5. FM-03 — Biến quan hệ timing thành nguyên nhân mã đã xác nhận

**Cơ chế:** từ mẫu “đọc sớm thì fail” hoặc HTTP 200, AI khẳng định chính xác thiếu `await`, lỗi backend/DB hay timer cụ thể, rồi đề nghị sửa mà chưa kiểm tra source và hợp đồng API. Đồng thuận giữa người và AI dễ làm giả thuyết có vẻ đã được xác minh.

- **Dữ kiện:** ở run-02/attempt 1, history nhận 0 đơn tại **297.566 ms**, trước khi client nhận submit tại **329.849 ms**; confirmation sau đó thấy 1 đơn. Cả 57 response trong batch đều HTTP 200. Packet không có source hay mốc commit DB; các dấu vết này hỗ trợ vấn đề thứ tự nhưng chưa xác định chính xác mã hoặc thời điểm dữ liệu được commit.
- **Hậu quả:** sửa nhầm nghiệp vụ, tăng sleep hoặc retry để che lỗi, hoặc coi việc hai bên cùng kết luận là bằng chứng bản sửa đã chạy thành công. HTTP 200 của một request không xác nhận mọi assertion nghiệp vụ hay quan hệ chờ giữa các request.
- **Kiểm chứng:** giữ giả thuyết gắn với các mốc cùng request ID/fixture, rồi kiểm tra quan hệ chờ trong source; nếu cần, thêm mốc commit/query. Sau đó đổi riêng điều kiện gửi history từ chờ thời gian sang chờ submit hoàn tất và chạy xác nhận không dùng retry.
- **Biện pháp:** tách ba trạng thái trong output: quan sát, giả thuyết và kết quả xác minh. Yêu cầu mỗi next-check nêu kết quả nào hỗ trợ/bác bỏ giả thuyết. Người tổ chức mới mở source/controls sau khi lưu các phân tích.

**Đánh giá lượt Sol:** tránh được failure mode này. Output không xác nhận thiếu `await` hoặc một lỗi sản phẩm cụ thể; ba next-checks là đề xuất, không được tự nhận là đã chạy.

## 6. Kết luận và nghiệm thu E-10

**Chốt E-10 v2:** đã đánh giá giá trị/nhiễu của lượt Sol, nêu ba failure modes có dữ liệu minh họa, phân loại điểm thực sự xuất hiện và rủi ro đã tránh, kèm cách kiểm chứng/phòng tránh. Nội dung có thể dùng cho báo cáo, User Guide và demo; khi chuyển sang sản phẩm khác phải giữ nhãn trạng thái của từng mode.

AI có ích khi giảm công đọc và tổ chức log, giữ retry history và đưa kế hoạch xác minh. AI tạo nhiễu khi nhãn số liệu không rõ hoặc khi người dùng bỏ kiểm chứng và nâng lời giải thích thành kết luận chắc chắn. Kết quả của một ca chưa cho phép khái quát tỷ lệ lỗi hoặc năng suất AI trên mọi CI log.

[Source và kiểm chứng local v2](../../E-03/order-history-v2-local-20261023/README.md) hỗ trợ cơ chế: batch `timed` không retry có 7 pass/3 fail, batch `awaited` không retry có 10/10 pass; ca `awaited` latency cao cũng pass. Hai batch sampled dùng cùng seed/lịch latency và source fingerprint của đợt local. Chúng không được gộp thành kết quả của revision CI. [E-09 trên CI](../../E-09/order-history-v2-ci-39911447981/README.md) đã xác nhận `awaited`: 10/10 PASS ngay lần đầu, retry=0, mọi POST hoàn tất trước khi gửi GET. Hai batch CI giữ revision/seed riêng; không dùng để suy riêng hiệu quả retry hoặc tốc độ. Xem [checklist](../../../tasks/checklist.md).

Đối chiếu E-08 và kết luận này được review qua [PR #21](https://github.com/SUT-group10/eshop-sut-group10/pull/21). Các phân tích gốc, thời lượng và dữ liệu v1/v2 được giữ theo từng đợt.
