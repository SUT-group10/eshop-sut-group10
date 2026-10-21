# NHẬT KÝ TRÒ CHUYỆN VỚI AI (AI CHAT LOG) - TUẦN 5

- **Môn học:** Kiểm thử phần mềm (Software Testing)
- **Tuần báo cáo:** Tuần 5 (Week 5)
- **Sinh viên:** Trần Quốc Vỹ
- **MSSV:** 23120410
- **Công cụ:** ChatGPT / Codex
- **Thời gian:** 19–21/10/2026.
- **Model:** Chưa xác định từ thông tin phiên.
- **Phạm vi:** Triển khai và kiểm chứng E-01; xây dựng protocol và rehearsal E-02.
- **Khai báo và Human Oversight:** [AI_Usage_Declaration.md](AI_Usage_Declaration.md).

Các prompt và trích đoạn phản hồi dưới đây được chọn từ session thực tế, không phải export toàn bộ session. Đoạn nguyên văn giữ cách diễn đạt gốc; phần tổng hợp được ghi riêng. Thao tác viết code, sửa file và chạy kiểm chứng do AI thực hiện được phân biệt với việc đọc, đặt câu hỏi và yêu cầu chỉnh sửa.

## Phiên chat 1: Tạo, kiểm chứng và chỉnh hướng dẫn chạy E-01

- **Thời gian:** 19/10/2026.
- **Phạm vi:** Làm rõ yêu cầu và định nghĩa, chọn luồng test, kiểm tra cơ chế timing, tạo test, kiểm chứng và ghi lại các yêu cầu bỏ/sửa.

<a id="e01-scope"></a>

### 1. Làm rõ yêu cầu E-01 và trạng thái repo

#### Prompt (Sinh viên, trích đoạn nguyên văn):

````text
đọc task E-01 và kiểm tra trạng thái repo liên quan. Giải thích cho tôi mục tiêu, đầu vào, đầu ra, dependency và tiêu chí hoàn thành. Phân biệt yêu cầu của đề với checklist nhóm.
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**E-01 chưa có bằng chứng hoàn thành trong repo đã kiểm tra.** Task này tạo một flaky test do timing/sleep có nguyên nhân đã biết, làm đầu vào cho thí nghiệm và phân tích người–AI phía sau. Chưa cần hoàn tất toàn bộ chuỗi E-02–E-10 để hoàn thành riêng E-01.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Đây là trạng thái lúc khảo sát, trước khi tạo test. Đầu vào, dependency và điều kiện nghiệm thu được đối chiếu giữa đề chính thức, checklist nhóm và repo thực tế.

<a id="e01-wording"></a>

### 2. Làm rõ “do timing/sleep”

#### Prompt (Sinh viên, trích đoạn nguyên văn):

````text
do hay đo thế
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Là **“do”**, nghĩa là **“gây ra bởi”**, không phải “đo”.
````

<a id="e01-definition"></a>

### 3. Định nghĩa flaky test

#### Prompt (Sinh viên, trích đoạn nguyên văn):

````text
2. flaky test là cái gì? định nghĩa
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Flaky test** là test có thể **lúc pass, lúc fail qua các lần chạy mà không có thay đổi liên quan trong mã nguồn hay đầu vào kiểm thử**. Kết quả phụ thuộc vào yếu tố chưa được kiểm soát, như thời gian xử lý, thứ tự chạy, mạng hoặc dữ liệu dùng chung.
````

<a id="e01-scenario"></a>

### 4. Chọn luồng thêm sản phẩm rồi đọc giỏ

#### Prompt (Sinh viên, nguyên văn):

````text
hãy gợi ý phần nào nên dùng để làm flaky test
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Tôi đề xuất **luồng “thêm một sản phẩm vào giỏ → đọc lại giỏ hàng”**, dựa trên test [`A-CART-02`](/D:/Workspace/SoftwareTesting/eshop-sut-group10/backend/tests/api/cart-orders.test.js:28).
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Luồng này ngắn, có baseline pass và dùng lại fixture cô lập. Các luồng đang có lỗi nghiệp vụ như thêm trùng sản phẩm, coupon hoặc xóa giỏ sau checkout dễ làm lẫn lỗi SUT với flake thí nghiệm.

<a id="e01-ordering"></a>

### 5. Làm rõ thứ tự của A và B

#### Prompt (Sinh viên, nguyên văn):

````text
sleep ở đây là sleep tiến trình của việc thêm sản phẩm hã? cho tiến trình sleep trong 60ms, và cho tiến trình sleep trong 160ms? sau đó mới tới tiến trình B là đọc kết quả thêm sp đúng không
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Gần đúng. Điểm quan trọng là **B không chờ A hoàn tất**; B chỉ chờ cố định 100 ms rồi đọc giỏ.
````

<a id="e01-fixed-sleep"></a>

### 6. Kiểm tra sleep cố định có đủ để gọi là flaky không

#### Prompt (Sinh viên, nguyên văn):

````text
việc sleep tiến trình A trong 1 thời gian cố định, vẫn thỏa đây là flaky test đúng không? vì đây là test nên mình sẽ có quyền sleep giả định như thế
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Vì vậy, **sleep cố định vẫn có thể là một phần của flaky test**, nếu sự biến thiên khi chạy khiến kết quả thay đổi. Nhưng không được mặc định rằng nó sẽ flaky trước khi kiểm chứng.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Phân biệt việc chủ động tạo một khoảng chờ với bằng chứng test có lúc pass, lúc fail. Chỉ có lệnh sleep chưa đủ để kết luận đã tạo được flake.

<a id="e01-runtime"></a>

### 7. Tính thêm thời gian xử lý sau sleep

#### Prompt (Sinh viên, nguyên văn):

````text
đúng rồi, khi sleep 60ms, cho tiến trình A chạy, nhưng vì vấn đề mạng hay gì đó mà nó chạy hơn 40ms, thì cũng có khả năng fail
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Riêng harness hiện tại dùng Supertest với app trong cùng tiến trình, nên không có mạng Internet bên ngoài. Độ trễ có thể đến từ lập lịch, tải máy hoặc phần mô phỏng của thí nghiệm. **Khả năng fail là hợp lý, nhưng phải chạy thực tế mới biết thiết kế có tạo được cả pass lẫn fail hay không.**
````

<a id="e01-test-type"></a>

### 8. Phân biệt loại test với tính flaky

#### Prompt (Sinh viên, nguyên văn):

````text
flaky test tạo bằng gì? nó cũng là unit test hã, hay nó mang tên là flaky test luôn? cũng viết bằng js đúng không
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Đúng, trong repo này mình viết bằng JavaScript và chạy bằng Jest**, giống các test hiện có.

“Flaky” mô tả **tính không ổn định của test**, còn unit/API/smoke mô tả **phạm vi kiểm thử**.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Phương án được chọn là API test bằng JavaScript, chạy bằng Jest và gọi API qua Supertest. Flaky là đặc tính timing được chủ động đưa vào test.

<a id="e01-create"></a>

### 9. Yêu cầu tạo test và tự kiểm chứng

#### Prompt (Sinh viên, nguyên văn):

````text
à oke, vậy hãy tạo giúp tôi flaky test, tự kiểm thử kết quả, và hướng dẫn tôi cách chạy để kiểm tra
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Test giữ A chờ 60 ms, thêm độ trễ mô phỏng 0/160 ms trước khi gửi request thêm sản phẩm. B chờ 100 ms rồi đọc giỏ. API và assertion đều chạy thật.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Đây là thiết kế ban đầu, sau đó được yêu cầu đơn giản hóa. Không dùng đoạn này để mô tả phiên bản cuối.

<a id="e01-sampled"></a>

### 10. Làm rõ ý nghĩa của sampled và tỷ lệ pass/fail

#### Prompt (Sinh viên, nguyên văn):

````text
sampled là điều kiện gì? bạn chạy 10 lượt là chạy sampled à, sao không phải là 5 pass 5 fail
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Xác suất 50% mỗi lượt không có nghĩa mười lượt bắt buộc chia đúng 5–5.** Giống tung đồng xu mười lần: có thể ra 4–6, 7–3 hoặc tỷ lệ khác. Mỗi lượt chọn độc lập, không bù kết quả cho những lượt trước.
````

<a id="e01-controlled-cases"></a>

### 11. So sánh 5 fast/5 slow với 10 lượt sampled

#### Prompt (Sinh viên, nguyên văn):

````text
ý tôi là sao mình không chạy 5 lượt slow 5 lượt fast để chứng minh fast và slow hoạt động đúng? hay bản chất flaky test là sẽ chạy ngẫu nhiên, thế thì sao biết nó đang ở case nào và test có thật sự đúng không. ý nghĩ của chạy 10 lần sampled là gì
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Ý của bạn đúng: chạy 5 lượt `fast` và 5 lượt `slow` là cách tốt để kiểm chứng thiết kế.** Nó trả lời câu hỏi khác với 10 lượt `sampled`.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Chạy từng chế độ cố định giúp kiểm tra điều kiện nhanh/chậm có hoạt động như dự kiến. Chạy sampled giúp quan sát cùng một cách chạy với độ trễ được lấy mẫu mỗi lượt. Random chỉ là cách mô phỏng được chọn, không phải điều kiện bắt buộc của flaky test. Thực tế đã chạy một lượt fast, một lượt slow riêng và 10 lượt sampled; không ghi thành đã chạy 5 lượt cho mỗi chế độ.

<a id="e01-acceptance"></a>

### 12. Kiểm tra điều kiện nghiệm thu E-01

#### Prompt (Sinh viên, nguyên văn):

````text
vậy nghiệm thu được e01 chưa?
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Phần kỹ thuật local đã đạt; chưa đủ để tick E-01 hoàn tất theo checklist nhóm.**
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Phân biệt phần triển khai và kiểm chứng local với đầu ra commit/PR/review của nhóm. Tại thời điểm ghi báo cáo, các thay đổi E-01 vẫn chưa commit và chưa có run CI.

<a id="e01-scope-reject"></a>

### 13. Yêu cầu bỏ nội dung sang task sau

#### Prompt (Sinh viên, trích đoạn nguyên văn):

````text
2. sao lại nhắc tới E09 trong khi ta vẫn ở E01? có thật sự đang là báo cáo cho việc làm task ở E01 không? thường thì người ta đọc task đến đâu làm đến đó chứ nhỉ
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Tuy nhiên, **chi tiết này không cần thiết trong hướng dẫn E-01 hiện tại** và khiến tài liệu giống đang triển khai cả chuỗi task.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Phần nói trước về sửa flake ở E-09 được yêu cầu bỏ khỏi hướng dẫn. Hướng dẫn được thu gọn về tạo test, nguyên nhân đã biết, cách chạy, cô lập thí nghiệm và bằng chứng kiểm chứng E-01.

<a id="e01-simplify"></a>

### 14. Yêu cầu đơn giản hóa timing và thu gọn phạm vi hướng dẫn

#### Prompt (Sinh viên, nguyên văn):

````text
vậy sửa cả 2 đi, mục 1 đừng phức tạp hóa lên, chỉ 60 hoặc 160
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Đã chạy lại 10 lượt sampled: **4 lượt fast pass, 6 lượt slow fail**. Lint/build và kiểm tra isolation đều đạt; database gốc không đổi.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

“Cả 2” nói đến việc đổi A sang chờ trực tiếp 60 hoặc 160 ms và bỏ phần nhắc các task sau khỏi hướng dẫn E-01.

Thiết kế 60 ms cộng thêm 0/160 ms bị yêu cầu bỏ vì làm cách giải thích phức tạp hơn cần thiết. AI sửa thành một lần chờ 60 hoặc 160 ms cho A, giữ B chờ 100 ms, rồi chạy lại kiểm chứng. Kết quả trong log hiện tại thuộc phiên bản đã sửa.

<a id="e01-observation"></a>

### 15. Đọc case fast/slow trong log sampled

#### Prompt (Sinh viên, nguyên văn):

````text
khi chạy sampled, nhìn đâu để biết nó là slow hay fast
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**`selectedCase`** cho biết case đã chọn; **`PASS`/`FAIL` của Jest** cho biết kết quả thực tế. Hai thông tin này cần đọc riêng, không suy case chỉ từ kết quả pass/fail.
````

<a id="e01-remove-old-evidence"></a>

## Phiên chat 2: Chốt protocol và kiểm chứng cách chạy E-02

- **Thời gian:** 19–21/10/2026.
- **Phạm vi:** Từ mốc bắt đầu E-02 đã xác nhận đến lúc đánh dấu hoàn thành checklist; làm rõ yêu cầu, viết protocol, rehearsal trên GitHub, nâng action và chốt cách tích hợp workflow.

<a id="e02-boundary"></a>

### 1. Xác nhận mốc bắt đầu E-02

#### Prompt (Sinh viên, nguyên văn):

````text
oke, bắt đầu start E02 từ đây (chưa làm gì, đặc cột mốc để sau này chatlog và ai usage declaration
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Đã đánh dấu **bắt đầu E-02 từ tin nhắn này**. Khi chuẩn bị chatlog và AI Usage Declaration, sẽ dùng đây làm mốc tách phần E-02 khỏi E-01. Chưa thực hiện E-02.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Phần E-02 bắt đầu từ mốc này. Các trao đổi về hoàn thiện báo cáo, chia commit và lập branch trước mốc vẫn thuộc E-01.

<a id="e02-scope"></a>

### 2. Đọc yêu cầu và phân biệt đề với checklist nhóm

#### Prompt (Sinh viên, trích đoạn nguyên văn):

````text
đọc task E-02. Giải thích cho tôi mục tiêu, đầu vào, đầu ra, dependency và tiêu chí hoàn thành. Phân biệt yêu cầu của đề với checklist nhóm.
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**E-02 là chốt kế hoạch thí nghiệm trước khi thu dữ liệu chính thức.** “Protocol” ở đây là bản quy định cách chạy, cách đánh giá và thông tin phải lưu để các lượt đo nhất quán.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Đề T07 yêu cầu tạo sleep-based flake, quan sát qua 10 lượt và so sánh người với AI. E-02 là cách nhóm tách việc định nghĩa protocol trước; các chi tiết như số dispatch, retry và tiêu chí phân loại cần chốt thành quy tắc thực hiện.

<a id="e02-implement"></a>

### 3. Yêu cầu triển khai protocol và kiểm tra điểm thiếu

#### Prompt (Sinh viên, nguyên văn):

````text
hãy implement e02 theo plan ở trên của bạn, bám theo task của nhóm và đề thực tế từ T07 (nếu task chưa đủ thì nói với tôi là thiếu ở điểm nào)
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Checklist nhóm còn thiếu chi tiết vận hành**, gồm retry, cách phân loại lỗi, dữ liệu cụ thể và điều kiện dừng. Protocol đã bổ sung và ghi rõ đây là quyết định triển khai.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

AI tạo docs/experiments/flaky-test-protocol.md và thêm link trong hướng dẫn E-01. Protocol quy định 10 lượt sampled độc lập, giữ cùng phiên bản và môi trường, không retry, phân loại lỗi, dữ liệu cần lưu và điều kiện dừng. AI kiểm tra link, cấu hình Jest, test discovery và sự khớp với workflow; các bước này là kiểm tra cấu hình, không phải một lượt job CI.

<a id="e02-purpose"></a>

### 4. Phản hồi tài liệu dài và làm rõ cách nghiệm thu

#### Prompt (Sinh viên, nguyên văn):

````text
file dài quá, tôi cần làm gì để hiểu được đã hoàn thiện e02? mục đích của e02 là gì
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Mục đích E-02 là thống nhất cách làm thí nghiệm trước khi chạy**, để không thấy kết quả rồi mới đổi cách đo.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Yêu cầu giải thích cách biết task đã hoàn thành, thay vì chỉ nhận một tài liệu dài. AI giải thích lại qua các câu hỏi: chạy gì, chạy thế nào, đọc kết quả ra sao, lưu gì và có được đổi giữa chừng không. Lượt này làm rõ nội dung; không ghi thành đã thu gọn toàn bộ file.

<a id="e02-rehearsal"></a>

### 5. Chất vấn việc chỉ có tài liệu và bổ sung rehearsal

#### Prompt (Sinh viên, nguyên văn):

````text
vậy e02 chỉ có protocal, tôi không thể chạy job hay lệnh để chứng minh protocal đúng à? protocal có step by step nhưng work trên github job
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Có, hoàn toàn có thể chạy thử trên GitHub để kiểm chứng protocol có làm theo được hay không.** Phần giải thích trước đã thiếu bước này.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Yêu cầu kiểm chứng protocol bằng thao tác thật trên GitHub. Từ đó tách rehearsal kiểm tra cách chạy/thu file khỏi 10 lượt chính thức E-03. Đây là bước kiểm chứng thực hành bổ sung, không gọi là yêu cầu nguyên văn riêng của checklist E-02.

<a id="e02-steps"></a>

### 6. Yêu cầu hướng dẫn mở workflow từng bước

#### Prompt (Sinh viên, nguyên văn):

````text
cách để mở workflow ? hướng dẫn tôi? protocol có hướng dẫn step by step chưa
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Hiện đang vướng ở bước 2:** GitHub chỉ hiển thị `Backend CI`. Workflow thí nghiệm cần hiện diện trên default branch `main` để chạy thủ công theo [quy định GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

AI bổ sung mục 4.1: mở Actions, chọn workflow/ref, chạy rehearsal, đọc job và tải console.log/results.json. Hướng dẫn ban đầu giả định workflow đã xuất hiện; kiểm tra repo cho thấy cần đăng ký YAML trên default branch trước.

<a id="e02-missing-workflow"></a>

### 7. Đối chiếu hướng dẫn với ảnh giao diện thực tế

#### Prompt (Sinh viên, nguyên văn):

````text
đâu
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Trong ảnh **chưa có workflow thí nghiệm** — thanh bên trái chỉ có `Backend CI`. Hướng dẫn trước đã đưa bước chọn workflow khi nó chưa xuất hiện nên chưa làm theo được.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Ảnh được gửi cùng prompt cho thấy chỉ có Backend CI. AI xác nhận trở ngại nằm ở workflow chưa được đăng ký, giải thích New workflow là tạo mới, không phải nút chạy test.

<a id="e02-register-pr"></a>

### 8. Yêu cầu thực hiện PR đăng ký workflow theo convention

#### Prompt (Sinh viên, nguyên văn):

````text
bạn thực hiện giúp tôi được chứ? chuẩn convetion
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Đã tạo [PR #13](https://github.com/SUT-group10/eshop-sut-group10/pull/13) vào `main`, đúng convention:
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

AI tạo branch ci/issue-5-register-flaky-workflow từ main, commit ci(E-02): register manual flaky workflow on main và PR chỉ có một file YAML. Dùng Refs #5 để liên kết phần việc mà không đóng toàn bộ issue. PR sau đó được merge; không gán thao tác merge PR #13 cho AI vì AI chỉ tạo PR trong lượt này.

<a id="e02-default-branch"></a>

### 9. Làm rõ default branch với base PR và branch thực thi

#### Prompt (Sinh viên, nguyên văn):

````text
ý là, chuyển defult branch về develop là run được đúng không
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Đúng**, nếu đổi default branch thành `develop` **và file `flaky-experiment.yml` đã có trên `develop`**, thì có thể mở workflow và bấm **Run workflow**.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Các lượt hỏi trước đó phân biệt đổi base PR sang develop với đổi default branch của repo. Chỉ đổi base PR không tự làm workflow xuất hiện; sau khi đăng ký, vẫn có thể chọn branch thí nghiệm để thực thi.

<a id="e02-wrong-ref"></a>

### 10. Kiểm tra lượt chạy thử và phát hiện chọn nhầm branch

#### Prompt (Sinh viên, nguyên văn):

````text
tôi đã chạy thử, chúng ta đang làm tới bước nào của task nào vậy
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Ảnh cho thấy đã dispatch được workflow, nhưng **đang chọn branch `ci/issue-5-register-flaky-workflow`, SHA `20525b8`**. Branch này chỉ thêm YAML từ `main`, chưa chứa harness/test E-01 nên chưa phù hợp để chạy thí nghiệm.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Có thao tác chạy thử và gửi ảnh để hỏi trạng thái. AI chỉ ra ref chưa có dependency và hướng dẫn chọn test/issue-5-flaky-experiment. Không suy kết luận lỗi cuối cùng chỉ từ dấu đỏ/Queued trong ảnh.

<a id="e02-user-run"></a>

### 11. Gửi artefact của lượt chạy đúng và hỏi cảnh báo Node 20

#### Prompt (Sinh viên, trích đoạn nguyên văn):

````text
đã success, nhưng có warning: Node.js 20 is deprecated.
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Đã kiểm tra: **lượt rehearsal chạy đúng và có artefact hợp lệ**.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Prompt được trích từ phần thông báo thành công/cảnh báo; hai file console.log và results.json được gửi kèm để kiểm tra. Run 39612964275 trên branch thí nghiệm, SHA bb96998, chọn fast 60 ms và pass; JSON ghi một test, một lần thực thi, không retry. Đây là lần chạy do sinh viên thao tác trên GitHub, AI đọc artefact và metadata. AI phân biệt cảnh báo runtime action @v4 với Node 24.14.0 dùng chạy test.

<a id="e02-node24-next"></a>

### 12. Xác nhận việc nâng action trước đợt đo

#### Prompt (Sinh viên, nguyên văn):

````text
là sao? bước tiếp theo là gì, là nâng action lên để thành node 24 để không có cảnh báo à
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**Đúng. Bước tiếp theo nên là nâng các action sang phiên bản hỗ trợ Node 24 để hết cảnh báo.** Node chạy test EShop vốn đã là `24.14.0`; cần cập nhật các dòng `uses: actions/...@v4`.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Chốt thứ tự nâng action, chạy lại một rehearsal rồi mới cố định điều kiện đo. Kết quả rehearsal cũ vẫn hợp lệ cho phiên bản cũ, không biến thành dữ liệu của workflow đã nâng.

<a id="e02-upgrade"></a>

### 13. Yêu cầu nâng action và thử hướng tích hợp develop

#### Prompt (Sinh viên, nguyên văn):

````text
oke, implement, và chắc là sau sẽ đổi sang merge vào develop, vì merge main thì rất phiền. đổi branch default về develop
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Lượt rehearsal với ba action `@v6` đã thành công: case fast pass, artefact tải được và log không còn cảnh báo Node.js 20.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Đây là trích đoạn cập nhật tiến độ của AI trong cùng lượt. AI nâng checkout, setup-node và upload-artifact lên @v6; test, timing và Node 24.14.0 giữ nguyên. AI dispatch run 39615233808 trên SHA 068d385, tải và đối chiếu artefact, job log cùng check annotations; không có cảnh báo Node 20. AI cũng tạo PR #14 vào develop. Tài khoản chỉ có quyền push, không có admin nên default branch thực tế vẫn là main.

<a id="e02-keep-main"></a>

### 14. Đổi quyết định: giữ main và chỉ merge file YAML

#### Prompt (Sinh viên, nguyên văn):

````text
à, cứ tiếp tục ở main, cứ merge vào main file yml, chả sao hết. tôi đổi ý rồi
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Đã merge PR #16 vào `main`: chỉ đổi ba dòng phiên bản action. Default branch vẫn là `main`, và PR #14 vào `develop` đã được đóng. Sẽ chốt lại hướng dẫn trong protocol cho khớp với cấu hình này.
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Đây là trích đoạn cập nhật tiến độ của AI sau khi nhận câu trả lời đổi quyết định. AI tạo branch sạch từ main và PR #16, kiểm tra diff một file với ba dòng nâng phiên bản rồi merge theo yêu cầu. PR #14 được đóng; protocol sửa lại về main. Không ghi thành đã chuyển default branch sang develop rồi chuyển ngược lại, vì thao tác đổi default chưa xảy ra.

<a id="e02-next-task"></a>

### 15. Phân biệt kết thúc rehearsal với bắt đầu E-03

#### Prompt (Sinh viên, nguyên văn):

````text
tiếp đến là gì? sau khi đã rehersal xong?
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
Sau rehearsal, **chốt E-02 rồi chuyển sang E-03**:
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

AI giải thích cần duyệt protocol, chốt SHA rồi dispatch 10 lượt mới để thu dữ liệu. Các rehearsal được giữ riêng, không tính vào mẫu chính và không ép tỷ lệ 5–5.

<a id="e02-acceptance"></a>

### 16. Xác nhận hoàn thành và đánh dấu checklist

#### Prompt (Sinh viên, trích đoạn nguyên văn):

````text
xong chưa? xong rồi đánh x vô giúp tôi, để đến E03, checkout ra từ nhánh E... theo những gì đã làm ấy
````

#### Phản hồi từ AI (Assistant, trích đoạn nguyên văn):

````text
**E-01 và E-02 đã đạt các tiêu chí được trích.**
````

#### Ghi chú tổng hợp (không phải trích nguyên văn):

Prompt được trích từ yêu cầu đối chiếu hai dòng checklist và đánh dấu hoàn thành. AI kiểm tra protocol, run rehearsal và PR workflow, tick riêng E-01/E-02 trong docs/tasks/checklist.md rồi commit/push b9b0a25. Tiếp tục dùng branch chung test/issue-5-flaky-experiment theo cách tổ chức đã chốt; phần này không ghi thành đã thực hiện đợt 10 lượt E-03.

### Sản phẩm và minh chứng E-02

- [Protocol thí nghiệm](../../../experiments/flaky-test-protocol.md).
- [Workflow](../../../../.github/workflows/flaky-experiment.yml).
- [Rehearsal do sinh viên chạy](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39612964275).
- [Rehearsal sau nâng action do AI chạy](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39615233808).
- [PR #13 đăng ký workflow](https://github.com/SUT-group10/eshop-sut-group10/pull/13); [PR #16 nâng action trên main](https://github.com/SUT-group10/eshop-sut-group10/pull/16).
