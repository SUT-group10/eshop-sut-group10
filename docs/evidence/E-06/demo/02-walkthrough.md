# 02 — Walkthrough: dấu vết nào dẫn tới kết luận nào?

[Trở về mục lục](README.md) · [Output Sol gốc](../../E-08/ai-sol/response.md)

Đây là ánh xạ giữa quy trình skill và nội dung quan sát được trong output. Không phải tool trace hay bản tái dựng suy nghĩ nội bộ. Các dẫn chứng dưới đây dùng số L theo từng run trong input.md; L016 của run-01 khác L016 của run-02.

## Bước 1 — Kiểm kê và đọc lỗi

**Đầu vào:** README, history, console và Jest JSON trong [gói E-05](../../E-05/participant-input.zip).

**Skill yêu cầu:** nhận diện số lượt thật, test identifier, loại lỗi và những file đang biểu diễn cùng một lượt.

**Output Sol thể hiện:** đã đọc dữ liệu của 10 lượt, không cộng số lượt vì có nhiều file; nhận diện test `Cart contains the added product`, 5 pass/5 fail, invocation 1 và retry 0.

Điểm lỗi được dẫn tại run-01/03/05/07/10: expected length 1, actual 0, frame cart.test.js:53:23. GET/POST đều 200. Từ đó có thể nói test fail ở assertion về giỏ; không gán thành lỗi cài dependency hoặc HTTP thất bại. Assertion quantity nằm sau assertion fail, nên chưa được kiểm tra ở các lượt đó.

**Sản phẩm của bước:** tóm tắt dữ liệu và triệu chứng, chưa phải nguyên nhân.

## Bước 2 — Đối chiếu lượt thành công và thất bại

**Skill yêu cầu:** tìm khác biệt liên quan trong dữ liệu, phân biệt timestamp tuyệt đối, duration và thời gian tương đối.

**Ví dụ kiểm tra trực tiếp:**

| Dấu vết | Run-01 FAIL | Run-02 PASS |
| --- | --- | --- |
| Thêm được gửi | 161.179 ms | 60.359 ms |
| Thêm hoàn tất | 164.156 ms | 64.486 ms |
| Đọc được gửi | 100.610 ms | 100.395 ms |
| Đọc hoàn tất | 105.484 ms | 102.889 ms |
| So thứ tự | Đọc xong trước khi thêm được gửi | Thêm xong trước khi đọc được gửi |
| Giỏ | Rỗng | Một sản phẩm quantity 1 |

Nguồn: run-01 L016/L021 và run-02 L016/L021 trong [input.md](../../E-05/participant-input/input.md). Mốc *Ms có cùng gốc theo bối cảnh của gói.

Phép đối chiếu cụ thể:

```text
Run-01: readCompletedMs 105.484 < addSentMs 161.179
Run-02: addCompletedMs 64.486 < readSentMs 100.395
```

Bảng 10 lượt trong output cho thấy bốn lượt fail khác giống quan hệ run-01; bốn lượt pass khác giống quan hệ run-02. Cùng revision có hai kết quả là quan sát về sự biến thiên; quan hệ thời gian cung cấp dấu vết để giải thích sự biến thiên đó.

Sol còn nêu history started_at và Jest startTime khác nhau và không dùng chúng để suy thứ tự GET/POST. Theo đối chiếu nguồn ở E-08, đây là thời điểm bắt đầu workflow run và Jest; output chỉ phỏng đoán có thể là job/Jest. Khi trình bày cần giữ khác biệt này, không chép phỏng đoán thành định nghĩa trường.

**Sản phẩm của bước:** mẫu quan sát “đọc trước thêm gắn với FAIL; thêm xong trước đọc gắn với PASS”.

## Bước 3 — Từ quan sát tới giả thuyết

| Mức phát biểu | Phát biểu phù hợp | Tại sao? |
| --- | --- | --- |
| Quan sát | Run-01 đọc xong trước khi thêm được gửi | Có số liệu và bất đẳng thức trực tiếp |
| Giả thuyết cơ chế | Luồng điều phối chưa bảo đảm thêm hoàn tất trước đọc | Giải thích được mẫu của 10 lượt |
| Điều chưa biết | Đoạn mã thiếu await, dùng timer hay cấu trúc khác? | Không có implementation đầy đủ trong gói |
| Xác nhận nguyên nhân | Phải kiểm tra điều phối và thực nghiệm có kiểm soát | Log hiện tại chưa phải kết quả thực hiện các bước này |

Output Sol đưa **một** giả thuyết chính, không tạo thêm cache/database chỉ để đủ ba. Nó nêu mức chắc chắn cao về quan hệ thứ tự trong mẫu, trung bình về trách nhiệm test/harness. Hai mức này nói về hai phát biểu khác nhau, không mâu thuẫn.

Skill không có quy tắc cứng “thấy HTTP 200 thì backend đúng” hoặc “có 5 fail thì lỗi timing”. Model phải giải thích mối nối từ dấu vết tới giả thuyết và nêu phần chưa biết. HTTP 200 không tự bảo đảm dữ liệu được ghi đúng; các lượt fail chưa có GET sau khi thêm hoàn tất.

**Sản phẩm của bước:** giả thuyết có cơ sở và giới hạn, chưa phải bản sửa.

## Bước 4 — Tạo ba next-checks để giải quyết phần chưa biết

Không phải ba lời khuyên chung chung. Mỗi bước phải trả lời một câu hỏi còn thiếu của giả thuyết.

| Thông tin chưa biết | Bước Sol đề xuất | Quan sát phân biệt |
| --- | --- | --- |
| Điều gì cho phép bắt đầu đọc? | Rà quan hệ chờ trong điều phối | Đọc không phụ thuộc thêm hoàn tất hỗ trợ giả thuyết; chuỗi chờ thật thì phải xem lại log/cách đo |
| Thứ tự có thực sự quyết định kết quả? | Thử có kiểm soát đọc sau xác nhận thêm so với đọc trước thêm | Kết quả đổi theo thứ tự củng cố giả thuyết; đọc sau vẫn rỗng cho thấy giả thuyết chưa đủ |
| Thêm hàng cuối cùng có tạo đúng trạng thái không? | Đọc lại sau khi thêm hoàn tất ở kịch bản từng fail | Đọc sau có item hỗ trợ nhận định snapshot quá sớm; vẫn rỗng cần điều tra ghi/định danh giỏ |

Sol chỉ **đề xuất**, không tự nhận đã mở source/chạy lại. Việc gợi ý đọc source cho bước xác minh sau không vi phạm giới hạn “không mở source trong lượt triage”.

Một điểm cần sửa cách diễn đạt khi thực hiện: output nói giữ revision khi đổi thứ tự. Nếu đổi thứ tự bằng sửa code thì phải lưu patch/revision mới; nếu dùng điều khiển sẵn có thì ghi điều kiện thay đổi. Không che thay đổi phiên bản để tạo cảm giác cùng mã.

**Sản phẩm của bước:** kế hoạch có kết quả hỗ trợ/bác bỏ, rồi dừng.

## Kết luận đầu ra hình thành thế nào?

```text
Assertion fail + timing của các lượt
    → xác định triệu chứng và mẫu khác biệt
    → đề xuất cơ chế giải thích mẫu đó
    → nêu dữ liệu còn thiếu để phân biệt các khả năng
    → đề xuất kiểm tra để thu dữ liệu còn thiếu
    → kết luận tạm thời, không tự gọi là đã xác nhận
```

Đây là cách kiểm tra lập luận công khai trong câu trả lời, không mô tả chính xác cơ chế tính toán hoặc suy nghĩ bên trong model.

## Đối chiếu sau demo: điều gì đã được xác minh ở E-09?

Sau lượt triage, nhóm đã tái hiện slow fail trên bản cũ, sửa để chờ thêm hoàn tất và chạy 12 lượt mới gồm fast/slow/sampled: 12 PASS. [Bằng chứng E-09](../../E-09/README.md) hỗ trợ giả thuyết chính về đồng bộ. Hoạt động đó do phiên triển khai sau thực hiện, không phải skill đã tự chạy trong lượt Sol.

Không ghi thành cả ba next-checks của Sol đều đã được thực hiện nguyên vẹn. Chưa có ở đây bộ log server/request id, và lượt kiểm chứng E-09 không phải thí nghiệm 20 lần cho từng biến thể. Kết quả một ca cũng chưa chứng minh hiệu quả chung hoặc mức cải thiện do skill so với không dùng skill.
