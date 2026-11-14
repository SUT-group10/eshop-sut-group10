# 03 — Kịch bản trình bày và cách dùng lại

[Trở về mục lục](README.md) · [Walkthrough có lời giải](02-walkthrough.md)

## 1. Chuẩn bị

Có hai cách demo, không trộn thành một:

- **Giải thích lượt đã có:** mở skill, dữ liệu E-05 và output Sol gốc. Có thể trình bày lại ngay, không phụ thuộc model sinh câu trả lời giống lần trước.
- **Chạy lượt mới:** cấp skill và cùng ZIP cho ngữ cảnh độc lập, lưu prompt/output/model và thời gian thực tế nếu đo được. Kết quả mới phải lưu riêng, không thay bản Sol đã có; không gọi chat đang biết đáp án là phân tích độc lập.

Với cả hai cách, người xem cần biết bên nào là dữ liệu, bên nào là hướng dẫn và bên nào là kết quả. Người làm bài độc lập chỉ nhận skill và gói dữ liệu; tài liệu demo có lời giải này chỉ mở sau khi đã lưu câu trả lời.

## 2. Trình tự demo gợi ý 5–7 phút

Thời lượng là kế hoạch trình bày, chưa phải kết quả diễn tập hoặc thời gian model phân tích.

| Chặng | Mở thành phần nào? | Thao tác/điểm cần nói |
| --- | --- | --- |
| 1. Mục tiêu | SKILL.md, mục Phạm vi dữ liệu | “Phân tích log đã cấp; không mở code hay sửa test. Đầu ra là giả thuyết và kế hoạch kiểm tra.” |
| 2. Kiểm kê | history.json, danh sách run-01…run-10 | Chỉ có 10 lượt; mỗi lượt có nhiều file. Nhìn retry_count = 0; không gọi 10 dispatch là 10 retry |
| 3. Đọc lỗi | input.md, run-01 L032–L044 | Giỏ expected 1, actual 0. Phân biệt assertion fail với HTTP/setup fail |
| 4. So pass/fail | run-01 và run-02 L016/L021 | Tính hai bất đẳng thức trên màn hình; đề nghị người xem tự chỉ ra thao tác nào đến trước |
| 5. Đặt giả thuyết | Output Sol mục 2 | Phân biệt “đọc trước thêm” là quan sát và “điều phối thiếu đồng bộ” là giả thuyết |
| 6. Next-checks | Output Sol mục 3 | Chỉ ra mỗi bước xử lý một phần chưa biết; không phải AI đã thực hiện các bước đó |
| 7. Chốt | Output mục 4, E-09 nếu đã công bố lời giải | Triage kết thúc ở kết luận tạm thời; bản sửa/kiểm chứng là hoạt động riêng. Nêu một điểm output cần review |

### Lời dẫn ngắn

“Skill không cung cấp đáp án về timing. Nó yêu cầu model kiểm kê dữ liệu, so trường hợp thành công/thất bại và dẫn chứng. Ở đây, các lượt fail đều đọc giỏ trước khi gửi thao tác thêm; các lượt pass có thứ tự ngược lại. Model dùng mẫu đó để đặt giả thuyết về điều phối, nhưng chưa biết cách viết mã cụ thể. Vì vậy nó đề nghị ba kiểm tra nhằm xác minh quan hệ chờ, tác động của thứ tự và trạng thái giỏ sau khi thêm. Những bước này là kế hoạch, chưa phải hành động đã chạy.”

## 3. Lệnh mở dữ liệu trong PowerShell

Chạy từ repo root, chỉ đọc file:

```powershell
Get-Content docs/evidence/E-06/ci-log-triage/SKILL.md
Get-Content docs/evidence/E-05/participant-input/history.json
Get-Content docs/evidence/E-05/participant-input/run-01/console.log
Get-Content docs/evidence/E-05/participant-input/run-02/console.log
Get-Content docs/evidence/E-08/ai-sol/response.md
```

Nếu cần thấy số L như output trích dẫn, mở input.md. L là số dòng cục bộ của console trong từng lượt, không phải số dòng toàn input.md hay số dòng source code.

## 4. Prompt cho một lượt mới

Trong môi trường hỗ trợ skill, chọn bản ci-log-triage đã lưu và đính kèm participant-input.zip. Nếu chỉ cung cấp nội dung hướng dẫn bằng văn bản thì ghi đúng đó là áp dụng hướng dẫn từ skill, không tự gọi là đã cài tích hợp.

```text
Áp dụng hướng dẫn ci-log-triage đã cung cấp để phân tích toàn bộ gói đính kèm.
Chỉ dùng dữ liệu trong gói. Không mở repo/source hoặc nguồn ngoài.
Trả kết quả theo cấu trúc skill, gồm dẫn chứng, mức chắc chắn và ba bước xác minh đề xuất.
Nếu không đọc được file hoặc thiếu dữ liệu, nói rõ; không tự bổ sung đáp án.
```

Đây là prompt gợi ý mới cho demo, không phải prompt gốc của phiên Sol. Prompt gốc được lưu riêng ở [E-08](../../E-08/ai-sol/prompt.md).

## 5. Kiểm tra sau khi nhận output

- Có đọc đủ dữ liệu hay công khai phần không đọc được? Có đếm lặp hoặc nhầm skip/setup thành fail không?
- Dẫn chứng có tồn tại và số liệu có khớp không? Timestamp có cùng gốc trước khi suy thứ tự không?
- Giả thuyết giải thích điều gì, còn thiếu gì? Có khẳng định implementation khi chỉ thấy log không?
- Ba next-checks có kết quả phân biệt giả thuyết không? Có tự nhận đã chạy hoặc đã sửa không?
- Có đưa số đo thời gian thật không? Không đo được thì giữ là không đo được.

Bản Sol được cung cấp không có toàn bộ tool trace; không dùng riêng lời “đã đọc” để chứng nhận mọi thao tác. Việc skill đúng cấu trúc không bảo đảm output đúng; người review vẫn phải đối chiếu bằng chứng.

## 6. Dùng cho CI log khác

Cấp log/report/history của ca mới cùng bối cảnh cần thiết, không kèm đáp án. Nếu chỉ có một lượt fail, model có thể phân tích lỗi trong lượt đó nhưng không có căn cứ để tuyên bố đã quan sát cả pass và fail. Nếu thiếu timing, không được suy ra thứ tự chỉ từ kiến thức về ca EShop. Với lỗi setup, dừng ở phân loại và bước xác minh phù hợp, không ép mọi trường hợp thành flaky test.

Bản skill không có kiến thức riêng về endpoint giỏ hàng hay hai mức delay. Khả năng dùng lại nằm ở phương pháp đọc bằng chứng, không phải thuộc kết luận của ví dụ này.
