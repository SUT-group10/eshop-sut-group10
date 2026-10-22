# E-08 — So sánh phân tích thủ công và Codex dùng skill

Ngày đánh giá: 22/10/2026. Đối tượng: 10 lượt API test giỏ hàng của bộ E-05, cùng bí danh revision-01.

## 1. Kết quả chính

**Vượng và Codex GPT-6.1 Sol cùng nhận diện vấn đề thứ tự: ở 5 lượt FAIL, giỏ đã được đọc xong trước khi thao tác thêm được gửi; ở 5 lượt PASS, thêm hoàn tất trước khi đọc.** Cả hai đề xuất kiểm tra cách điều phối thêm/đọc và chưa coi nguyên nhân mã cụ thể là đã được xác nhận bằng thực nghiệm sửa lỗi.

Sự đồng thuận là kết quả hợp lệ. Lượt AI này bổ sung bảng timing đầy đủ và lưu ý về ý nghĩa timestamp, chưa chứng minh AI tốt hơn người về tốc độ hoặc độ chính xác. Không ép tìm lỗi AI để tạo khác biệt.

## 2. Dữ liệu, công cụ và cách đánh giá

| Thành phần | Nguồn |
| --- | --- |
| Đầu vào chung tham chiếu | [participant-input.zip](../E-05/participant-input.zip), đủ 10 lượt và lịch sử retry |
| Phương pháp AI | [ci-log-triage đã chốt tại E-06](../E-06/ci-log-triage/SKILL.md), điều chỉnh từ systematic-debugging |
| Bản phân tích thủ công | [phan-tich-vuong.md](../E-04/phan-tich-vuong.md), tác giả Vượng theo xác nhận của người dùng |
| Output AI | [response.md](ai-sol/response.md), Codex GPT-6.1 Sol theo xác nhận của người dùng |
| Prompt và thông tin phiên được cung cấp | [prompt.md](ai-sol/prompt.md), [metadata.json](ai-sol/metadata.json) |
| Kiểm tra số liệu phục vụ so sánh | [evidence-check.json](evidence-check.json) |

Báo cáo do AI hỗ trợ tổng hợp và đối chiếu hai bản đã được cung cấp; không tạo lại câu trả lời của người hoặc chạy lại AI triage. Giữ nguyên các bản gốc, kể cả phát biểu cần làm rõ. Chỉ đánh giá một output AI đã nhận, không tự suy ra tổng số lần thử hay việc đây là lần thử đầu tiên.

Đánh giá định tính theo cùng năm tiêu chí của E-08: nguyên nhân, bằng chứng, bước kiểm tra, thời gian và suy diễn. Không tự chấm điểm số khi nhóm chưa có thang điểm định lượng. Vượng đã review báo cáo theo xác nhận của người dùng. Hồ sơ chưa có thời gian phân tích và xác nhận thứ tự hoàn thành E-04 trước khi xem AI; không tự bổ sung hai dữ kiện này.

Đã đối chiếu 40 giá trị timing và kết quả 10 lượt trong dữ liệu chuẩn hóa với metadata E-03: khớp. Việc đối chiếu bản đã lưu không thay cho export phiên gốc hoặc chứng minh toàn bộ tài nguyên AI đã truy cập.

## 3. Đối chiếu theo cùng tiêu chí

| Tiêu chí | Vượng — E-04 | Codex GPT-6.1 Sol | Đánh giá |
| --- | --- | --- | --- |
| Nguyên nhân chính | H1: test đọc giỏ không đợi thêm hoàn tất | Test/harness chưa bảo đảm thêm hoàn tất trước đọc | Đồng thuận ở mức cơ chế. Khớp dấu vết của cả 10 lượt |
| Phạm vi giả thuyết | H1 thứ tự, H2 hai cụm độ trễ, H3 backend/môi trường yếu | Một giả thuyết chính; không thêm cache/database khi chưa có bằng chứng | Vượng tách rõ yếu tố gây biến thiên; AI tập trung hơn. Số giả thuyết nhiều hơn không tự tốt hơn |
| Bằng chứng | Khoảng timing hai nhóm, L016/L021, assertion, comment cleanup và metadata | Timing từng run, L016/L021, assertion, HTTP status, invocation/retry, timestamp history/Jest | Cả hai dẫn được dấu vết chính; AI trình bày chi tiết hơn ở bảng từng run |
| Bước kiểm tra | Rà điều phối; bổ sung log client/server; thử hai thứ tự khoảng 20 lần mỗi kiểu | Rà điều phối; thử thay đổi thứ tự; đọc lại sau khi thêm xong | Cùng có ba bước khả thi để đề xuất. Chưa bên nào thực hiện chúng trong hồ sơ này |
| Thời gian | File bàn giao không có thời gian bắt đầu/kết thúc hoặc tổng thời lượng | Metadata không có thời gian bắt đầu/kết thúc hoặc thời lượng | Không đo được chênh lệch, không kết luận bên nào nhanh hơn |
| Suy diễn và mức chắc chắn | Có phân hạng H1–H3, nhưng dùng comment để suy ra thiếu await hơi mạnh | Không khẳng định thiếu await/timer cụ thể; lưu ý dữ liệu thiếu | AI giữ giới hạn tốt hơn ở chi tiết implementation; cả hai vẫn cần kiểm chứng |

## 4. Kiểm tra dẫn chứng và những điểm cần làm rõ

### 4.1. Dấu vết chính: đúng và đủ để đặt giả thuyết

Ở run-01, L016 ghi readCompletedMs = 105.484; L021 ghi addSentMs = 161.179. Bốn lượt fail còn lại có cùng quan hệ. Năm lượt pass đều có addCompletedMs < readSentMs. Các giá trị trong bảng Sol và các khoảng timing trong bản Vượng khớp bộ dữ liệu.

Assertion độ dài giỏ có expected 1, actual 0 tại L032–L034; frame ở L044 là cart.test.js:53:23. Assertion status ở dòng mã 52 đứng trước assertion fail; quantity ở dòng 54 chưa được thực hiện trong các lượt đó. Đây là dấu vết test fail, không phải lỗi setup hoặc HTTP thất bại. Nguồn: [console run-01](../E-05/participant-input/run-01/console.log), [report run-01](../E-05/participant-input/run-01/results.json).

### 4.2. Bản Vượng: comment cleanup là gợi ý, không tự chứng minh thiếu await

Bản E-04 dùng comment “Even a failed assertion must drain A…” để suy ra thao tác A còn chạy sau assertion và chưa được await trước đọc. Comment mô tả ý định cleanup; tự nó chưa chứng minh đường điều phối đã thực thi như vậy trong mọi lượt. Bằng chứng timing mới trực tiếp hỗ trợ nhận định ở 5 lượt fail. Bản Vượng cũng ghi thiếu source và chưa xác nhận, nên đây là điểm cần làm chặt cách diễn đạt, không phải bịa nguồn.

H2 nhận diện hai cụm thời điểm gửi là quan sát có cơ sở. Tuy nhiên, không thể từ đó xác nhận có bước cộng thêm đúng 100 ms trong code: dữ liệu chỉ cho thấy hai cụm xấp xỉ 60/160 ms. H3 được ghi yếu và có bằng chứng ngược; không tính việc nêu khả năng chưa loại trừ là hallucination.

### 4.3. Output AI: cách diễn đạt bước xác minh cần chỉnh

Bước 2 viết “Giữ nguyên revision” trong khi đề nghị thay đổi thứ tự thao tác. Nếu thực hiện bằng sửa code test thì phải tạo và ghi revision/patch mới; không gọi đó là chạy nguyên SHA cũ. Nếu điều khiển được bằng cấu hình sẵn có thì có thể giữ code revision nhưng cần ghi cấu hình thay đổi. Hướng thử nghiệm vẫn hữu ích; phần ghi nhận phiên bản cần chính xác.

Output ghi giá trị history khác Jest là đúng. Đối chiếu nguồn cho thấy started_at_utc trong history là thời điểm bắt đầu workflow run; $.startTime là lúc Jest bắt đầu. Cụm “có thể là thời điểm bắt đầu job và Jest” chỉ là phỏng đoán có nêu giới hạn; nguồn thực tế là workflow run, không phải job. Đây cũng cho thấy bộ E-05 nên định nghĩa rõ trường thời gian ở các lần chuẩn bị dữ liệu sau; không sửa đầu vào đã dùng trong phép so sánh này.

### 4.4. Bộ dữ liệu vẫn có gợi ý về thí nghiệm

E-05 đã che tên “flaky” và kết luận nguyên nhân, nhưng README còn nói bỏ “tham số điều khiển mô phỏng”; code frame còn comment cleanup. Vượng đã dùng cả hai trong phân tích. Đây là thông tin nằm trong cùng bộ dữ liệu được cấp, không phải bằng chứng truy cập ngoài phạm vi. Tuy vậy, không nên mô tả đầu vào là đã loại sạch mọi gợi ý thiết kế. Nhận định về khả năng khái quát sang log sản xuất cần thận trọng.

## 5. Đối chiếu với cơ chế đã biết của thí nghiệm

Phần này do người đánh giá đọc sau các bản phân tích, không phải thông tin cấp bổ sung cho người/AI lúc triage. [Test E-01](../../../backend/tests/experiments/cart-timing.flaky.js) khởi chạy thao tác thêm sau độ trễ chọn 60/160 ms, trong khi thao tác đọc đợi cố định 100 ms và không đợi thêm hoàn tất. [Protocol E-02](../../experiments/flaky-test-protocol.md) mô tả thiết kế này.

H1 của hai bên phù hợp cơ chế đó. H2 của Vượng nhận ra hai cụm do điều khiển thời điểm nhưng chưa biết cách chọn; việc không suy ra chính xác mã là phù hợp với giới hạn đầu vào. Không có bằng chứng từ dữ liệu này buộc phải quy lỗi cho backend.

Đối chiếu source giúp đánh giá giả thuyết có đúng hướng, không thay cho bước sửa và chạy xác nhận E-09. Chưa thực hiện E-09 trong báo cáo này.

## 6. AI mang lại giá trị và tạo nhiễu ở đâu?

**Giá trị quan sát được:** AI tự tổng hợp đúng kết quả 10 lượt; trình bày quan hệ timing từng lượt; nối quan sát với giả thuyết và đề xuất kiểm tra có điều kiện xác nhận/bác bỏ. Output không ép đủ ba giả thuyết và không gọi nghi ngờ là đã sửa hoặc xác nhận. Trong trường hợp này, AI hữu ích như một bản phân tích thứ hai có cấu trúc, nhưng chưa chứng minh phát hiện được điều người phân tích không thấy.

**Nhiễu/rủi ro cụ thể trong output:** yêu cầu giữ revision khi thay thứ tự chưa nêu cách tổ chức thay đổi; phỏng đoán timestamp workflow là timestamp job nếu được chép lại như kết luận sẽ gây hiểu nhầm. Đây là các điểm cần review, không làm sai kết luận timing chính. Không quan sát thấy trong output này việc bịa lỗi mạng/database hay bịa số liệu. Không lấy các failure modes giả định đó làm lỗi thực tế để đủ E-10.

**Giới hạn phép so sánh:** một ca có chủ đích, đủ log timing và hai cụm độ trễ rõ ràng; một output AI đã được bàn giao; thiếu số đo thời gian và xác nhận trình tự thực hiện. Không kết luận về mọi CI log, không chứng minh skill này vượt ba ứng viên chưa thử và không khẳng định nhân quả “nhờ skill nên AI đúng” khi chưa có lượt đối chứng không dùng skill.

## 7. Kết luận và trạng thái

Đã hoàn thành bản đối chiếu nội dung theo năm tiêu chí E-08. Hai bên đồng thuận nguyên nhân chính và đều đưa được bước xác minh. AI mạnh ở trình bày bảng chi tiết và giữ giới hạn implementation; Vượng bổ sung phân tích hai cụm độ trễ và các khả năng phụ có phân hạng.

Vượng đã review theo xác nhận của người dùng. Chốt E-08 với kết quả so sánh nội dung nêu trên; thời gian ghi là không đủ dữ liệu nên không kết luận tốc độ. Thứ tự manual-before-AI chưa có xác nhận trong hồ sơ và được giữ là giới hạn phép so sánh. Không dựng lại hoặc ước lượng thời gian đã mất. Bằng chứng gốc E-04 và output ai-sol được giữ nguyên.
