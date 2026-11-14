# Phân tích test giỏ hàng (10 lượt, revision-01)

## 1. Kết quả

5 pass (run-02, 04, 06, 08, 09), 5 fail (run-01, 03, 05, 07, 10). Không có retry (`history.json[*].test_retry_count = 0`).

Các lượt fail đều hỏng cùng một chỗ: `expect(cart.body).toHaveLength(1)` nhận `[]` (L030–L034, `cart.test.js:53:23` ở L044). Mọi request đều trả 200.

Điểm khác nhau giữa hai nhóm nằm ở thứ tự thêm hàng và đọc giỏ:

| | add gửi lúc | read gửi lúc | cart |
|---|---|---|---|
| Pass | ~60 ms | ~100 ms | 1 item |
| Fail | ~160 ms | ~100 ms | `[]` |

Ở lượt fail, giỏ đã được đọc xong trước khi request thêm hàng được gửi đi. Ví dụ run-01 L021: `readCompletedMs 105.484`, `addSentMs 161.179`. Thứ tự log cũng đảo: lượt fail in "Cart observation" ở L016 trước "Add completed" ở L021, lượt pass thì ngược lại.

## 2. Giả thuyết

**H1: test bị race, đọc giỏ không chờ thêm hàng xong.** Mạnh nhất.
- Ủng hộ: đúng ở cả 10/10 lượt (L016/L021). Comment ở L042, *"Even a failed assertion must drain A before closing its isolated fixture"*, cho thấy thao tác A còn chạy sau assertion, tức không được await trước khi đọc.
- Chưa đủ: chưa có source test, chỉ thấy dòng 51–56. "A" là thao tác thêm hàng mới chỉ là suy đoán.

**H2: đường thêm hàng có độ trễ ~100 ms, khi có khi không.**
- Ủng hộ: `addSentMs` chỉ rơi vào hai cụm rất sát, 60.3–60.6 và 159.5–161.2, giống một delay cố định hơn là nhiễu. README cũng nói đã bỏ "tham số điều khiển mô phỏng".
- Chưa đủ: log không có mốc nào trước addSent, nên không biết 100 ms nằm ở bước nào. H2 chỉ giải thích vì sao race lúc thắng lúc thua, không thay thế H1.

**H3: lỗi phía backend hoặc môi trường.** Yếu.
- Phản bác: ở lượt fail, read xong trước khi add được gửi, nên backend chạy đúng vẫn phải trả `[]`. Seed và kết nối giống hệt nhau ở mọi lượt (L006, L011). Pass/fail xen kẽ, không theo thời gian (`started_at_utc`).
- Chưa loại hẳn: mốc thời gian đều đo ở client, không có log server.

## 3. Bước kiểm tra tiếp theo

1. **Đọc `cart.test.js` dòng 30–56** để xem add và read được gọi thế nào. Nếu read không chờ add thì xác nhận H1. Nếu có `await add` trước read thì H1 sai, chuyển sang xem H3.
2. **Thêm timestamp** ở client (trong đường add, trước khi gửi) và ở server (nhận/commit, kèm request id). Nếu thấy 100 ms nằm ở một bước cụ thể phía client thì xác nhận H2. Nếu server đã commit add trước read mà read vẫn rỗng thì nghiêng về H3.
3. **Chạy lại khoảng 20 lần mỗi kiểu**: (a) ép add xong rồi mới đọc, (b) ép đọc trước. Nếu (a) pass hết và (b) fail hết thì H1 gần như chắc chắn. Nếu (a) vẫn fail thì phải xem lại H3.

## 4. Mức chắc chắn

- Lượt fail đọc giỏ trước khi thêm hàng: chắc chắn, thấy trực tiếp trong log.
- Nguyên nhân là test thiếu await (H1): khá chắc nhưng chưa kiểm chứng.
- H2, H3: chưa đủ dữ liệu.

Còn thiếu: source test, log server, tham số mô phỏng đã bị bỏ. Ngoài ra mẫu chỉ có 10 lượt.

## 5. Thời lượng và trình tự thực hiện

- **Người phân tích:** Nguyễn Khắc Vượng.
- **Thời lượng hoàn thiện:** 20 phút.
- **Trình tự:** hoàn thiện bản phân tích trước khi xem output Codex GPT-6.1 Sol.
