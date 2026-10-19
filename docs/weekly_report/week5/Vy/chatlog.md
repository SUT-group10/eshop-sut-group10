# NHẬT KÝ TRÒ CHUYỆN VỚI AI (AI CHAT LOG) - TUẦN 5

- **Môn học:** Kiểm thử phần mềm (Software Testing)
- **Tuần báo cáo:** Tuần 5 (Week 5)
- **Sinh viên:** Trần Quốc Vỹ
- **MSSV:** 23120410
- **Công cụ:** ChatGPT / Codex
- **Thời gian:** 19/10/2026.
- **Model:** Chưa xác định từ thông tin phiên.
- **Phạm vi:** Triển khai và kiểm chứng local E-01.
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