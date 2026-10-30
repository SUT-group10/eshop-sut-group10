Dưới đây là bản trích xuất 10 lỗi API từ log kiểm thử của bạn. Nội dung đã được lọc bỏ toàn bộ nhiễu (như `console.log` khởi tạo DB) và cấu trúc lại ngắn gọn, chỉ định rõ Endpoint, Kỳ vọng (Expected) vs. Thực tế (Received) và Hướng sửa trong `backend/server.js` để bạn có thể copy-paste trực tiếp làm prompt cho LLM:

---

### Nhóm 1: Giỏ hàng, Thanh toán & Đơn hàng (`tests/api/cart-orders.test.js`)

1. **`A-CART-03` — Thêm trùng sản phẩm vào giỏ không được gộp dòng (FR-07)**

* **Endpoint:** `POST /api/cart` và `GET /api/cart`

* **Expected vs. Received:** Kỳ vọng mảng giỏ hàng có độ dài `1` với `quantity: 3` (khi thêm cùng `product_id: 1` hai lần: 1 + 2). Thực tế nhận mảng độ dài `2` (tạo 2 dòng riêng biệt).
* **Hướng sửa cho LLM:** Khi thêm sản phẩm vào giỏ, kiểm tra nếu sản phẩm (`id` / `product_id`) đã tồn tại trong giỏ của user thì thực hiện cộng dồn `quantity` (`UPDATE`), không `INSERT` dòng mới.




2. **`A-CHECKOUT-02` — Tin tưởng `total_amount` do client gửi lên thay vì tự tính (FR-08)**

* **Endpoint:** `POST /api/checkout`

* **Expected vs. Received:** Giỏ hàng có 2 sản phẩm giá `30,000,000` nhưng client cố tình gửi `total_amount: 1`. Kỳ vọng `order.total_amount` lưu trong DB là `60000000`, nhưng thực tế lưu `1`.


* **Hướng sửa cho LLM:** Không lấy `req.body.total_amount` ghi vào bảng `orders`. Backend phải truy vấn các item hiện có trong giỏ hàng của user và tự tính tổng `SUM(price * quantity)`.




3. **`A-CHECKOUT-03` — Không xóa giỏ hàng sau khi thanh toán thành công (FR-08)**

* **Endpoint:** `POST /api/checkout`

* **Expected vs. Received:** Sau khi checkout thành công (`200`), gọi `GET /api/cart` kỳ vọng trả về mảng rỗng `[]`, nhưng thực tế vẫn còn nguyên sản phẩm trong giỏ.


* **Hướng sửa cho LLM:** Sau khi tạo đơn hàng thành công trong `POST /api/checkout`, thực thi lệnh xóa toàn bộ giỏ hàng của user hiện tại.




4. **`A-ORDER-03` — Cho phép User tự hủy đơn hàng đang ở trạng thái `shipping` (FR-10)**

* **Endpoint:** `PUT /api/orders/:id/cancel`

* **Expected vs. Received:** Khi đơn hàng có `status = 'shipping'`, user gọi API hủy kỳ vọng trả về mã lỗi `4xx` (`>= 400`, `< 500`) và giữ nguyên trạng thái `shipping`. Thực tế trả về `200`.
* **Hướng sửa cho LLM:** Kiểm tra trạng thái hiện tại của đơn hàng trước khi hủy; user chỉ được phép hủy khi trạng thái là `pending` hoặc `confirmed` (nếu là `shipping`, `delivered`, `canceled` thì trả về `400 Bad Request`).




5. **`A-ORDER-04` — Cho phép Admin chuyển trạng thái của đơn hàng đã bị hủy `canceled` (FR-10)**

* **Endpoint:** `PUT /api/admin/orders/:id/status`

* **Expected vs. Received:** Đơn hàng đang ở trạng thái kết thúc `canceled`, Admin gọi API đổi sang `delivered` kỳ vọng bị chặn với mã lỗi `4xx` (`>= 400`, `< 500`). Thực tế trả về `200`.
* **Hướng sửa cho LLM:** Tuân thủ State Machine (FR-10): `delivered` và `canceled` là trạng thái kết thúc (final states), chặn mọi cập nhật trạng thái tiếp theo và trả về `400 Bad Request`.





---

### Nhóm 2: Xác thực & Phân quyền (`tests/api/catalog-auth.test.js`)

6. **`A-AUTH-03` — Đăng nhập sai 1 lần nhưng bộ đếm `login_attempts` tăng lên 2 (FR-02)**

* **Endpoint:** `POST /api/login`

* **Expected vs. Received:** Gửi sai mật khẩu 1 lần cho `test@eshop.com`, kỳ vọng `login_attempts` trong bảng `users` là `1`, nhưng thực tế nhận `2`.
* **Hướng sửa cho LLM:** Kiểm tra câu lệnh `UPDATE users SET login_attempts = ...` khi đăng nhập thất bại, sửa lại chỉ cộng thêm đúng `1` đơn vị (`login_attempts + 1`) cho mỗi lần sai.




7. **`A-ACCESS-02` — Tài khoản User thường truy cập được API danh sách người dùng của Admin (FR-12, SEC-03)**

* **Endpoint:** `GET /api/admin/users`

* **Expected vs. Received:** Gửi request với JWT token của user thường (`role = 'user'`), kỳ vọng trả về lỗi phân quyền `403 Forbidden` (nằm trong khoảng `400–499`). Thực tế trả về `200 OK`.
* **Hướng sửa cho LLM:** Bổ sung kiểm tra `req.user.role === 'admin'` (middleware phân quyền Admin) cho endpoint `GET /api/admin/users` và các route `/api/admin/*`; trả về `403` nếu không phải admin.





---

### Nhóm 3: Mã giảm giá (`tests/api/coupons.test.js`)

8. **`A-COUPON-05` — Sai điều kiện biên đối với giá trị đơn hàng tối thiểu `min_order_amount` (FR-09 - C3)**

* **Endpoint:** `POST /api/apply-coupon`

* **Expected vs. Received:** Áp mã `BIGBUY` (`min_order_amount = 500000`, giảm cố định `50000`) cho đơn hàng có `total_amount = 500000` (bằng đúng ngưỡng tối thiểu). Kỳ vọng `200 OK` (`discount_amount: 50000`, `final_amount: 450000`), nhưng thực tế trả về `400`.


* **Hướng sửa cho LLM:** Sửa toán tử kiểm tra điều kiện ngưỡng đơn hàng tối thiểu từ `<` / `<=` sai lệch sang cho phép `total_amount >= coupon.min_order_amount` (chỉ báo lỗi `400` khi `total_amount < coupon.min_order_amount`).




9. **`A-COUPON-07` — Cho phép áp dụng mã giảm giá mà không cần JWT Token xác thực (FR-09 - C4)**

* **Endpoint:** `POST /api/apply-coupon`

* **Expected vs. Received:** Gửi request không có header `Authorization: Bearer <token>` (dù trong body có truyền `user_id`), kỳ vọng bị từ chối với mã `401`/`403` (`400–499` kèm `body.error`). Thực tế trả về `200`.
* **Hướng sửa cho LLM:** Gắn middleware `authenticateToken` (kiểm tra JWT hợp lệ) vào route `POST /api/apply-coupon` và lấy `user_id` từ token đã xác thực.




10. **`A-COUPON-09` — Sai công thức tính giảm giá theo phần trăm `percent` (FR-09)**

* **Endpoint:** `POST /api/apply-coupon`

* **Expected vs. Received:** Áp mã `SAVE10` (loại `percent`, `discount_value = 10`) cho `total_amount = 500000`. Kỳ vọng `{ discount_amount: 50000, final_amount: 450000 }`, nhưng thực tế nhận `{ discount_amount: -4500000, final_amount: 5000000 }` (đang nhân trực tiếp với 10 thay vì chia 100).


* **Hướng sửa cho LLM:** Sửa công thức tính giảm giá cho loại `percent` thành: `discount_amount = (total_amount * coupon.discount_value) / 100` và `final_amount = total_amount - discount_amount`.