# Bộ dữ liệu phân tích test giỏ hàng

Có 10 lượt chạy độc lập của cùng một API test trên cùng revision-01. Mỗi lượt dùng fixture/database riêng. Test kiểm tra giỏ hàng chứa sản phẩm vừa thêm, quantity bằng 1. Log chứa quan sát thao tác thêm và đọc giỏ; các mốc *Ms là mili giây tương đối từ lúc hai thao tác bắt đầu, không phải thời gian toàn job.

Môi trường chung: Node v24.14.0, npm 11.9.0, Ubuntu 22.04 image 20261018.327.1, runner 2.338.0. Không sửa mã giữa các lượt. Lịch sử thực thi và retry nằm trong history.json.

Đây là bản dữ liệu đã chuẩn hóa: tên test, đường dẫn, lệnh và mã định danh được thay bằng bí danh; bỏ nhãn thiết kế và tham số điều khiển mô phỏng. Giữ thời gian quan sát, thứ tự log, HTTP status, dữ liệu giỏ hàng, assertion, stack frame với số dòng, kết quả và retry. Tên/lệnh trong bản này chỉ là bí danh, không phải hướng dẫn chạy.

Đọc input.md (console có số dòng), history.json và results.json của cả 10 lượt. Không cần mở repo hoặc tra cứu nguồn bên ngoài gói dữ liệu này. Phân biệt bằng chứng trong log với suy đoán; có thể kết luận chưa đủ dữ liệu.
