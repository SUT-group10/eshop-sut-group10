# Đặc tả Yêu cầu Hệ thống (System Requirements Specification)

# EShop — Phiên bản dành cho Kiểm thử Phần mềm

> **Phạm vi tài liệu**: Mô tả **yêu cầu nghiệp vụ đúng** của hệ thống EShop.
> Sinh viên sử dụng tài liệu này làm cơ sở thiết kế test case, sau đó kiểm thử hệ thống thực để tìm ra các điểm triển khai không tuân thủ đặc tả.

**Seminar T07:** xem [hướng dẫn bộ test](backend/tests/README.md) và [checklist](docs/tasks/checklist.md). Thí nghiệm flaky hiện hành là **v2 — order history**, có [protocol và lệnh chạy](docs/experiments/order-history-protocol.md), [bằng chứng local](docs/evidence/E-03/order-history-v2-local-20261023/README.md), [batch CI](docs/evidence/E-03/order-history-v2-ci-39860438568/README.md), [đối chiếu người–AI](docs/evidence/E-08/order-history-v2-39860438568/AI_vs_Human_Triage.md) và [kết luận E-10 với ba failure modes](docs/evidence/E-10/order-history-v2-39860438568/README.md). [Bản sửa awaited đã xác nhận trên CI](docs/evidence/E-09/order-history-v2-ci-39911447981/README.md): 10/10 PASS, retry=0. Thí nghiệm cart **v1** và kết quả của đợt cũ được giữ làm lịch sử.

---

## 1. Tổng quan Hệ thống

Hệ thống EShop là nền tảng thương mại điện tử bao gồm 4 thành phần:

| Thành phần   | Công nghệ                   | URL mặc định            |
| ------------ | --------------------------- | ----------------------- |
| Backend API  | Node.js + Express + SQLite  | `http://localhost:3000` |
| Frontend Web | React + Vite + Tailwind CSS | `http://localhost:5173` |
| Web Admin    | React + Vite + Tailwind CSS | `http://localhost:5174` |
| Mobile App   | React Native + Expo         | IP LAN của máy chủ      |

**Tài khoản mặc định:**

- Admin: `admin@eshop.com` / `Admin123!`
- User test: `test@eshop.com` / `Test1234!`

---

## 2. Quản lý Tài khoản (Authentication & Authorization)

### FR-01: Đăng ký tài khoản

- Người dùng phải cung cấp: **Họ Tên**, **Email**, **Mật khẩu**.
- Email phải có định dạng hợp lệ (`user@domain.com`) và là duy nhất trong hệ thống.
- **Yêu cầu mật khẩu mạnh**: Tối thiểu 8 ký tự, có ít nhất 1 chữ hoa, 1 chữ thường, 1 chữ số và 1 ký tự đặc biệt (`@`, `$`, `!`, `%`, `*`, `?`, `&`).
- Phải có trường **Xác nhận mật khẩu** — hệ thống từ chối nếu hai trường không khớp.
- Sau khi đăng ký thành công, người dùng được chuyển tới trang Đăng nhập.

### FR-02: Đăng nhập & Khóa tài khoản

- Người dùng nhập Email và Mật khẩu.
- Sau mỗi lần đăng nhập sai, hệ thống tăng bộ đếm lên **đúng 1 đơn vị**.
- Nếu đăng nhập sai từ **3 lần trở lên** liên tiếp, tài khoản bị tạm khóa **30 giây** (môi trường demo). Hệ thống trả về thông báo lỗi phù hợp; không để lộ chi tiết nguyên nhân.
- Đăng nhập thành công trả về JWT Token. Token được lưu phía client và gửi kèm tất cả các yêu cầu có xác thực qua header `Authorization: Bearer <token>`.
- Trường email phải dùng `type="email"` (có validate HTML5 format).

### FR-03: Quên mật khẩu & Đặt lại mật khẩu (2 bước)

**Bước 1 — Lấy mã OTP:**

- Người dùng nhập địa chỉ Email đã đăng ký.
- Hệ thống sinh mã OTP **6 chữ số ngẫu nhiên** và gửi qua Email (trong môi trường demo: hiển thị trực tiếp trên màn hình).
- Giao diện phải hiển thị **chỉ báo bước (Step Indicator)** — ví dụ: "Bước 1 / 2".
- Có nút **Quay lại đăng nhập**.

**Bước 2 — Đặt lại mật khẩu:**

- Người dùng nhập OTP, Mật khẩu mới, và **Xác nhận mật khẩu mới**.
- Mật khẩu mới phải tuân thủ điều kiện như FR-01.
- Hai trường mật khẩu phải khớp nhau.
- OTP chỉ hợp lệ cho email đã yêu cầu, không thể dùng cho email khác.

### FR-04: Quản lý hồ sơ cá nhân

- Người dùng đã đăng nhập có thể cập nhật: **Họ Tên**, **Số điện thoại**, **Địa chỉ giao hàng mặc định**.
- **Số điện thoại hợp lệ**: bắt đầu bằng số `0`, từ 10–11 chữ số.
- Email không được phép thay đổi qua giao diện.
- Người dùng chỉ có thể cập nhật hồ sơ của chính mình; không thể tự thay đổi thuộc tính `role`.

---

## 3. Danh mục & Sản phẩm

### FR-05: Xem danh sách & Tìm kiếm sản phẩm

- Trang chủ hiển thị danh sách tất cả sản phẩm dạng lưới (grid).
- Mỗi sản phẩm hiển thị: **Ảnh** (tỷ lệ chuẩn, có alt text mô tả), **Tên sản phẩm**, **Giá** (đơn vị: ₫, định dạng phân cách hàng nghìn).
- Thanh tìm kiếm tìm theo tên sản phẩm. Từ khóa tìm kiếm phải được **hiển thị an toàn** (không render HTML).
- Khi đang tải dữ liệu phải hiển thị trạng thái **loading**.
- Khi không có kết quả tìm kiếm phải hiển thị thông báo **empty state** phù hợp.
- Trang chủ chỉ có **đúng một thẻ `<h1>`**.
- Mỗi trang chỉ có 1 `<h1>` duy nhất.

### FR-06: Xem chi tiết sản phẩm

- Hiển thị đầy đủ: Ảnh lớn, Tên, Giá, Mô tả, Danh mục.
- Có ô nhập **Số lượng** (chỉ nhận số nguyên dương, tối thiểu là 1).
- Nút **Thêm vào giỏ hàng** — sau khi bấm hiển thị phản hồi trực quan (toast notification hoặc badge cập nhật).

---

## 4. Giỏ hàng & Thanh toán

### FR-07: Giỏ hàng (Shopping Cart)

- Hiển thị danh sách sản phẩm với các cột: **Sản phẩm**, **Đơn giá**, **Số lượng** (có nút +/- để chỉnh), **Thành tiền**, **Thao tác**.
- Thêm cùng một sản phẩm vào giỏ sẽ tăng số lượng, không tạo dòng mới.
- Nút **Xóa sản phẩm** phải có dialog xác nhận trước khi thực hiện.
- Có nút **Tiếp tục mua sắm** để quay về trang chủ.
- Tổng tiền hiển thị nhãn chính xác: **"Tổng cộng"** (không phải "Tổng tạm tính").
- Giỏ hàng trống phải có hình minh họa và thông báo rõ ràng.

### FR-08: Thanh toán (Checkout)

- Chỉ người dùng **đã đăng nhập** mới tiến hành thanh toán được.
- **Tổng tiền thanh toán** được tính tự động từ giỏ hàng và không cho phép người dùng chỉnh sửa trực tiếp.
- Giao diện hiển thị đầy đủ danh sách sản phẩm đặt mua.
- Backend phải tự tính lại tổng tiền; không chấp nhận giá trị `total_amount` do client gửi lên.
- Sau thanh toán thành công, giỏ hàng được xóa.

### FR-09: Mã Giảm Giá (Coupon)

Tại bước Checkout, người dùng có thể nhập mã giảm giá. Hệ thống áp dụng giảm giá dựa trên **5 điều kiện** sau, tất cả phải thỏa mãn:

| #   | Điều kiện              | Mô tả                                                       |
| --- | ---------------------- | ----------------------------------------------------------- |
| C1  | **Mã tồn tại**         | Mã phải có trong CSDL và đang hoạt động (`is_active = 1`)   |
| C2  | **Còn hạn sử dụng**    | Ngày hiện tại phải trước `expired_at`                       |
| C3  | **Đủ ngưỡng đơn hàng** | Tổng đơn hàng **>= (lớn hơn hoặc bằng)** `min_order_amount` |
| C4  | **Đã đăng nhập**       | Người dùng phải có JWT Token hợp lệ                         |
| C5  | **Chưa dùng hết lượt** | Số lần đã dùng mã này của user < `max_uses_per_user`        |

**Công thức tính giảm giá:**

- Loại `percent`: `discount_amount = total × discount_value / 100`
- Loại `fixed`: `discount_amount = discount_value`
- `final_amount = total - discount_amount`

**Mã giảm giá mẫu trong hệ thống:**

| Mã        | Loại    | Giá trị   | Ngưỡng tối thiểu | Hạn dùng   | Số lần/người |
| --------- | ------- | --------- | ---------------- | ---------- | ------------ |
| `SAVE10`  | percent | 10%       | 300,000 ₫        | 2099-12-31 | 1            |
| `BIGBUY`  | fixed   | 50,000 ₫  | 500,000 ₫        | 2099-12-31 | 1            |
| `VIP100`  | fixed   | 100,000 ₫ | 300,000 ₫        | 2099-12-31 | 2            |
| `EXPIRED` | percent | 20%       | 100,000 ₫        | 2020-01-01 | 1            |

---

## 5. Quản lý Đơn hàng

### FR-10: Trạng thái Đơn hàng (Order State Machine)

Đơn hàng có **5 trạng thái** và phải tuân theo sơ đồ chuyển đổi sau:

```
                 [Admin xác nhận]          [Admin giao hàng]      [Admin hoàn tất]
  ┌──────────┐ ─────────────────► ┌───────────┐ ──────────────► ┌──────────┐ ──────────► ┌───────────┐
  │ pending  │                    │ confirmed │                  │ shipping │             │ delivered │
  └──────────┘                    └───────────┘                  └──────────┘             └───────────┘
       │                               │
       │ [User/Admin hủy]              │ [User/Admin hủy]
       ▼                               ▼
  ┌──────────┐                    ┌──────────┐
  │ canceled │                    │ canceled │
  └──────────┘                    └──────────┘
```

**Ràng buộc trạng thái kết thúc (Final States):**

- Trạng thái `delivered` và `canceled` là **trạng thái kết thúc** — không được phép chuyển sang bất kỳ trạng thái nào khác.
- Khi đơn hàng đã ở trạng thái `shipping`, **User không được phép tự hủy** — chỉ Admin mới có thể thao tác.
- Mọi chuyển đổi không hợp lệ phải trả về lỗi với thông báo phù hợp.

### FR-11: Xem lịch sử đơn hàng (User)

- Người dùng chỉ xem được đơn hàng của chính mình.
- Hiển thị: Mã đơn, Ngày đặt, Tổng tiền, Trạng thái hiện tại.
- Trạng thái phải được dịch sang tiếng Việt rõ ràng và phân biệt màu sắc.

---

## 6. Phân hệ Web Admin

### FR-12: Kiểm soát truy cập (Access Control)

- Phân hệ Admin chỉ dành cho tài khoản có `role = 'admin'`.
- **Tất cả** các API Admin (`/api/admin/*`) và các API có tính ảnh hưởng dữ liệu (`POST/PUT/DELETE /api/products`, `/api/categories`, `/api/coupons`) đều phải yêu cầu:
  1. Token JWT hợp lệ.
  2. `role = 'admin'` trong Token.

### FR-13: Dashboard

- Hiển thị tổng doanh thu: Chỉ tính tổng `total_amount` của các đơn có `status = 'delivered'`.
- Hiển thị tổng số đơn hàng.

### FR-14: Quản lý Danh mục (Category CRUD)

- Admin có thể Thêm / Xem / Xóa danh mục.
- Tên danh mục là bắt buộc, không được để trống.

### FR-15: Quản lý Sản phẩm (Product CRUD)

- Admin có thể Thêm / Xem / Sửa / Xóa sản phẩm.
- **Ràng buộc đầu vào:**
  - Tên sản phẩm: bắt buộc, tối đa 255 ký tự.
  - Giá: bắt buộc, phải là số **dương** (> 0).
  - Danh mục: bắt buộc, phải chọn từ danh sách có sẵn.
- Khi Sửa một sản phẩm, chỉ sản phẩm đó bị thay đổi — các sản phẩm khác giữ nguyên.

### FR-16: Import Sản phẩm từ CSV

- Admin có thể tải lên file CSV để import nhiều sản phẩm cùng lúc.
- **Yêu cầu file CSV:**
  - Đuôi file phải là `.csv`.
  - Dòng đầu tiên là header: `name,price,description,imageUrl,category_id`.
  - Hỗ trợ các trường có chứa dấu phẩy nếu được bọc trong dấu nháy kép (RFC 4180).
- **Validation trước khi import:**
  - `name` không được rỗng.
  - `price` phải là số dương.
- Nếu có lỗi ở bất kỳ dòng nào, toàn bộ import phải được **rollback** (giao dịch nguyên tử — all-or-nothing).
- Hệ thống hiển thị báo cáo rõ ràng: bao nhiêu dòng thành công, bao nhiêu dòng lỗi và lý do.

### FR-17: Quản lý Mã Giảm Giá (Coupon CRUD)

- Admin có thể Thêm / Xem / Xóa mã giảm giá.
- Các trường bắt buộc: `code` (duy nhất), `type` (percent/fixed), `discount_value` (dương), `expired_at`, `min_order_amount` (>= 0), `max_uses_per_user` (>= 1).

### FR-18: Quản lý Đơn hàng (Admin)

- Admin xem toàn bộ đơn hàng của tất cả người dùng.
- Admin có thể chuyển đổi trạng thái đơn hàng theo đúng State Machine đã định nghĩa ở FR-10.
- Địa chỉ giao hàng phải được hiển thị **an toàn** (không render HTML).

### FR-19: Quản lý Người dùng (Admin)

- Admin xem danh sách tất cả người dùng (không lộ mật khẩu).
- Admin có thể xóa người dùng, **ngoại trừ không được xóa chính tài khoản đang đăng nhập**.

---

## 7. Phân hệ Mobile (React Native)

### FR-20: Tính năng Mobile

- Đầy đủ các chức năng: Xem sản phẩm, Đăng nhập, Đăng xuất, Đăng ký, Giỏ hàng, Thanh toán, Hồ sơ, Lịch sử đơn hàng.
- Chức năng Hủy đơn hàng tuân theo đúng State Machine ở FR-10 (chỉ được hủy khi `pending` hoặc `confirmed`).

---

## 8. Yêu cầu Giao diện (GUI Requirements)

### FR-21: Tiêu chuẩn Giao diện Chung

- **Nhất quán ngôn ngữ**: Toàn bộ giao diện dùng tiếng Việt (trừ thuật ngữ kỹ thuật chuẩn).
- **Nhất quán màu sắc**: Các nút hành động tích cực (Submit, Mua hàng) dùng màu xanh dương. Các nút nguy hiểm/hủy bỏ dùng màu đỏ.
- **Nhất quán đơn vị tiền**: Luôn dùng ký hiệu `₫` với định dạng phân cách hàng nghìn.
- **Tiêu đề trang**: Mỗi trang có đúng 1 thẻ `<h1>` mô tả nội dung trang.
- **Tab Order**: Thứ tự focus theo Tab phải đi từ trên xuống dưới, trái sang phải.

### FR-22: Form Requirements

- Tất cả trường bắt buộc phải có ký hiệu `*` bên cạnh nhãn.
- Trường Email phải dùng `type="email"`.
- Trường Mật khẩu phải dùng `type="password"` (không hiển thị rõ).
- Thông báo lỗi phải xuất hiện **trên** nút submit, không phải bên dưới.
- Các form có từ 2 bước trở lên phải có **Step Indicator** rõ ràng.

### FR-23: Navigation Requirements

- Thanh điều hướng (Navbar) phải **highlight** trang đang được chọn.
- Link "Giỏ hàng" phải hiển thị **badge số lượng** sản phẩm trong giỏ.
- Nút Đăng xuất phải nhãn là "Đăng xuất" (không phải "Thoát").
- Breadcrumb bắt buộc có ở các trang con (Giỏ hàng, Thanh toán, Chi tiết sản phẩm).

### FR-24: Feedback & State Requirements

- Sau khi bấm "Thêm vào giỏ", phải có phản hồi trực quan (toast/badge).
- Khi xóa item khỏi giỏ phải có dialog xác nhận.
- Trang trống (Empty State) phải có icon/hình minh họa và message thân thiện.
- Tất cả ảnh sản phẩm phải có thuộc tính `alt` mô tả nội dung ảnh (không để rỗng).

---

## 9. Yêu cầu Bảo mật (Security Requirements — Tham khảo)

| ID     | Yêu cầu                                                                                                         |
| ------ | --------------------------------------------------------------------------------------------------------------- |
| SEC-01 | Mật khẩu **không** được lưu dưới dạng plaintext.                                                                |
| SEC-02 | Các API có tính bảo mật phải yêu cầu JWT Token hợp lệ.                                                          |
| SEC-03 | API Admin phải kiểm tra `role = 'admin'` trong Token, không chỉ kiểm tra sự tồn tại của Token.                  |
| SEC-04 | Mọi dữ liệu từ user nhập vào khi hiển thị trên UI phải được escape đúng cách, không dùng `innerHTML` trực tiếp. |
| SEC-05 | Truy vấn CSDL phải dùng Parameterized Query, không nối chuỗi trực tiếp.                                         |
| SEC-06 | API cập nhật hồ sơ không được cho phép thay đổi trường `role` từ client.                                        |
| SEC-07 | OTP đặt lại mật khẩu phải đủ entropy (tối thiểu 6 chữ số), có thời hạn và vô hiệu hóa sau khi dùng.             |

---

_Tài liệu này phục vụ cho mục đích học tập và thực hành Kiểm thử Phần mềm. Phiên bản: 2.0 — Cập nhật: 2026-05-14._
