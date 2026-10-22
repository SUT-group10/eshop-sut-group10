# Phân tích ORDER-HISTORY-01 (10 run, revision-01)
## 1. Kết quả

| | Số lượng |
|---|---|
| Run | 10, gồm 19 attempt |
| Attempt đầu | 5 pass (run-01, 06, 07, 09, 10), 5 fail (run-02, 03, 04, 05, 08) |
| Retry | 9 lần. Run-02 pass ở retry 1. Run-03 và 08 pass ở retry 2. Run-04 và 05 fail cả 3 attempt |
| Kết quả cuối | 8 pass, 2 fail (`history.json → runs[].status`, khớp với `result.json` của từng run) |

Mọi attempt fail đều hỏng ở cùng một assertion: `HISTORY_ORDER_COUNT expected 1, actual 0`, ví dụ run-02 L0024 và run-04 L0024/L0050/L0076. Không có lỗi HTTP: submit luôn trả 200 kèm `order_id: 1`. Request `confirmation` luôn thấy 1 đơn (`attempts.json → confirmation_order_count = 1` ở cả 19 attempt).

> Suy luận: đơn hàng luôn được tạo thành công. Thứ thiếu chỉ là kết quả của **riêng request `history`**. Vì vậy câu hỏi đúng không phải "vì sao đặt hàng lỗi" mà là "vì sao `history` đọc ra 0 trong khi `confirmation` ngay sau đó đọc ra 1".

## 2. Quan sát thời gian

| | Pass (8 attempt) | Fail (11 attempt) |
|---|---|---|
| history gửi sau submit gửi | 120.0–121.2 ms | 119.6–121.4 ms |
| Server xử lý submit | 22.9–116.3 ms | 124.6–211.0 ms |
| history vào server so với submit hoàn tất | sau 3.8–97.7 ms | **trước** 4.4–91.5 ms |
| confirmation gửi sau khi nhận response submit | 5–99 ms (sau history) | 0.2–0.3 ms |

Ví dụ run-02 attempt 1:
- L0005: gửi submit lúc 172.6 ms.
- L0007: gửi history lúc 292.9 ms.
- L0008–L0009: server nhận history và trả về 0 đơn.
- L0011: server mới hoàn tất submit, lúc 329.1 ms (xử lý 154.7 ms).
- L0014: confirmation được gửi ngay sau response submit, lúc 330.1 ms, và thấy 1 đơn.

Đối chiếu với run-01 attempt 1: submit hoàn tất ở L0007 (250.6 ms) rồi history mới vào server ở L0010 (295.0 ms), nên pass.

> Suy luận:
> - **Khoảng cách gửi history gần như là hằng số (~120 ms ± 1 ms)**, dù submit nhanh (23 ms) hay chậm (211 ms). Nếu history được gửi sau khi submit trả về, khoảng này phải co giãn theo thời gian submit. Việc nó không đổi cho thấy history được bắn theo mốc thời gian, không theo sự kiện submit xong.
> - **Confirmation thì ngược lại**: ở attempt fail nó đi ngay sau response submit (0.2–0.3 ms), đúng hành vi của một request có `await`. Ở attempt pass nó đến sau history, tức nó chờ cả history. Như vậy trong cùng một test có hai cách gửi khác nhau, và chỉ request không chờ submit là request hỏng.
> - Pass hay fail tách sạch ở ngưỡng ~120 ms, không có ngoại lệ. Run-07 pass sát nhất: submit 116.3 ms, history vào server chỉ 3.8 ms sau khi submit xong.

## 3. Giả thuyết (xếp theo mức bằng chứng)

**H1 (mạnh nhất): test gửi `history` theo mốc thời gian cố định (~120 ms sau submit) chứ không chờ submit hoàn tất.**
- Bằng chứng: 19/19 attempt khớp quy tắc "history đến server trước khi submit xong thì fail". Khoảng gửi cố định ~120 ms. Cách gửi history khác hẳn confirmation (mục 2).
- Chưa đủ: gói không có source test, nên chưa biết đó là `setTimeout`, `Promise.all` có delay, hay thiếu `await`. "Mốc cố định" vẫn là suy ra từ số đo.

**H2: `/api/checkout` có thời gian xử lý dao động mạnh (22.9–211.0 ms) và đó là biến quyết định race thắng hay thua.**
- Bằng chứng: 11/19 attempt có submit vượt 120 ms và đúng 11 attempt đó fail. Response history và confirmation chỉ mất 1–2 ms, nên phần chậm nằm riêng ở checkout.
- Run-04 và 05 chậm cả 3 attempt dù mỗi attempt dùng instance và fixture mới. Có thể có yếu tố theo process, nhưng chưa đủ để khẳng định. Với tỉ lệ chậm ~58% (11/19), xác suất 3 attempt liên tiếp đều chậm khoảng 0.19, nên 2/5 run fail ban đầu bị như vậy vẫn có thể do ngẫu nhiên.
- Chưa đủ: không có log bên trong checkout. README nói "experiment controls" do bên tổ chức giữ, nên độ trễ có thể được đưa vào có chủ đích.

**H3 (yếu): backend chưa cho đọc thấy đơn ngay sau khi ghi (read-after-write).**
- Bác: mọi request đọc đến server sau khi submit hoàn tất đều thấy 1 đơn, gồm toàn bộ confirmation và history ở attempt pass. Ở attempt fail, history vào server khi submit còn đang xử lý, nên trả 0 là đúng với trạng thái lúc đó.
- Chưa loại hẳn: log chỉ có `http.server.completed`, không có mốc commit DB. Vì vậy chưa chứng minh được commit xảy ra trước hay sau khi gửi response.

## 4. Lưu ý thêm từ dữ liệu

- **Retry đang che flaky:** 3/8 run pass cuối cùng (02, 03, 08) chỉ pass nhờ retry. Nếu chỉ nhìn `status` cuối thì tỉ lệ lỗi là 2/10, nhưng ở attempt đầu là 5/10, và tính trên mọi attempt là 11/19.
- **`jest_test_duration_ms` chỉ phản ánh attempt cuối.** Ví dụ run-03 = 155 ms, khớp attempt 3 (154.9 ms), trong khi 3 attempt cộng lại khoảng 660 ms. Nhìn trường này thì các run có retry lại trông như *nhanh hơn*. Muốn thấy chi phí retry thì dùng `process_duration_ms`: run có retry mất 1322–1671 ms, run không retry mất 1118–1171 ms.

## 5. Ba bước kiểm tra tiếp theo

1. **Đọc source test ở đoạn gửi `history`.**
   - Nếu history được gửi bằng timer hoặc không `await` submit thì xác nhận H1.
   - Nếu có `await submit` trước history thì H1 sai: lúc đó khoảng 120 ms cố định phải đến từ chỗ khác (lớp client/Supertest), và cần xem lại H3.
2. **Thêm mốc thời gian bên trong checkout** (validate, ghi DB, commit, gửi response), cùng mốc commit DB.
   - Nếu phần vượt 120 ms rơi vào một bước cụ thể thì H2 được giải thích.
   - Nếu commit xảy ra *trước* khi history vào server mà history vẫn trả 0 thì H3 được ủng hộ, H1 yếu đi.
3. **Chạy lại có kiểm soát, mỗi biến thể ≥20 lần:** (a) chỉ gửi history sau khi nhận response submit; (b) giữ nguyên test và ghi lại thời gian xử lý submit.
   - Nếu (a) pass 100% và (b) fail đúng khi submit vượt ~120 ms thì H1 và H2 được củng cố.
   - Nếu (a) vẫn fail thì phải xem lại H3.

## 6. Mức chắc chắn và thông tin còn thiếu

- **Cao (quan sát trực tiếp):** fail khi và chỉ khi history đến server trước lúc submit hoàn tất (19/19). Khoảng gửi history cố định ~120 ms.
- **Trung bình–cao (suy luận, chưa kiểm chứng):** nguyên nhân gốc là cách test gửi history (H1).
- **Thấp / chưa đủ dữ liệu:** vì sao checkout lúc nhanh lúc chậm (H2), và khả năng có vấn đề commit phía backend (H3).
- Chưa có nguyên nhân nào được xác nhận. Không có bước kiểm tra nào ở trên đã được chạy.
- Còn thiếu: source test, log bên trong checkout và mốc commit, các experiment controls. Gói không kèm checksum nên không kiểm tra được toàn vẹn. Mình chỉ xác nhận được số dòng `console.log` bằng số event trong `events.jsonl` ở mọi run.

