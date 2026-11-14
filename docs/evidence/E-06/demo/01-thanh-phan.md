# 01 — Từng thành phần của ci-log-triage

[Trở về mục lục](README.md) · [Skill được lưu](../ci-log-triage/SKILL.md)

## 1. Skill, model và công cụ có vai trò khác nhau

- **Skill:** một bộ hướng dẫn bằng Markdown quy định mục tiêu, phạm vi dữ liệu, cách phân tích và cấu trúc output. Nó không tự chạy nếu không được một hệ thống/model sử dụng.
- **Model:** ở lượt đã bàn giao là Codex GPT-6.1 Sol, theo xác nhận của người dùng. Model áp dụng hướng dẫn và thông tin trong ngữ cảnh để tạo phân tích. Cùng skill không bảo đảm mọi model hoặc mọi lần chạy cho cùng câu trả lời.
- **Công cụ đọc/tính toán:** nếu môi trường hỗ trợ, model có thể đọc, giải nén và tính toán trên file đầu vào. Skill giới hạn phạm vi sử dụng; nó không phải cơ chế sandbox kỹ thuật ngăn truy cập file.
- **Người dùng:** chọn đúng bộ dữ liệu, cung cấp ngữ cảnh độc lập, kiểm tra output và thực hiện các bước xác minh về sau.

## 2. Ba file trong folder skill

| File | Chức năng | Có cần cho lượt phân tích? |
| --- | --- | --- |
| [SKILL.md](../ci-log-triage/SKILL.md) | Hướng dẫn tự chứa; điều khiển phạm vi, quy trình và output | Có |
| [SOURCES.md](../ci-log-triage/SOURCES.md) | Repo/commit nguồn, lý do giữ/bỏ/thêm từng phần khi điều chỉnh | Hồ sơ phương pháp; không cần đưa cho bên phân tích log |
| [LICENSE.txt](../ci-log-triage/LICENSE.txt) | Giấy phép và thông báo bản quyền của nguồn | Giữ khi phân phối; không phải dữ liệu chẩn đoán |

Các script chạy test và ví dụ sửa code của thư mục gốc superpowers không có trong bản điều chỉnh. Không cần cài cả bộ gốc để đọc hướng dẫn tự chứa này.

## 3. Các khối trong SKILL.md

| Khối | Chức năng cụ thể | Dấu hiệu có thể kiểm tra ở output |
| --- | --- | --- |
| YAML frontmatter: name/description | Định danh và mô tả thời điểm dùng skill | Tên ci-log-triage; không tự chứng minh chất lượng phân tích |
| Mục tiêu đầu file | Phân biệt quan sát với giả thuyết; không mặc định loại lỗi | Không kết luận trước rằng lỗi là timing, mạng hay sản phẩm |
| Phạm vi dữ liệu | Chỉ dùng file được giao; không mở source/web, không chạy test hoặc sửa mã | Output chỉ dẫn chứng trong gói; việc không truy cập ngoài cần kiểm tra thêm tool log nếu có |
| Bước 1 | Kiểm kê, nhận diện cùng lượt ở nhiều file, đọc expected/actual | Nêu 10 lượt thay vì đếm console/JSON thành 20 hay 30 lượt |
| Bước 2 | So sánh pass/fail, điều kiện, timeline, retry | Bảng các lượt, quan hệ sự kiện, trường thiếu hoặc mâu thuẫn |
| Bước 3 | Tối đa ba giả thuyết có thể bác bỏ | Mỗi giả thuyết có cơ chế, dẫn chứng, thông tin thiếu và mức chắc chắn |
| Bước 4 | Đề xuất đúng ba kiểm tra rồi dừng | Mỗi kiểm tra cho biết kết quả nào hỗ trợ/bác bỏ; không nhận là đã chạy |
| Cấu trúc câu trả lời | Bốn phần đầu ra nhất quán | Dữ liệu → giả thuyết → ba bước → kết luận hiện tại |

Tối đa ba giả thuyết không có nghĩa phải tạo đủ ba. Đúng ba next-checks là quy ước nhóm để so sánh đầu ra, không phải một thuật toán bảo đảm đúng.

## 4. Thành phần đầu vào E-05

| Thành phần | Dùng để trả lời câu hỏi nào? |
| --- | --- |
| README trong ZIP | Đang kiểm thử gì, điều kiện chung, đơn vị/gốc thời gian và giới hạn dữ liệu? |
| history.json | Có bao nhiêu lượt, cùng revision không, pass/fail ra sao, có retry không? |
| input.md | Console của từng lượt có số L để trích dẫn; không phải lịch sử thực thi thứ hai |
| run-XX/console.log | Thông báo lỗi, quan sát HTTP/giỏ, timing và stacktrace |
| run-XX/results.json | Kết quả máy đọc được: status, duration, assertion, invocation, retry |
| prompt.md | Yêu cầu phân tích chung; không chứa đáp án |

SHA256SUMS nếu có chỉ giúp kiểm tra file, không giải thích nguyên nhân. Run-01 là một lượt có nhiều dạng biểu diễn; không được coi từng file là mẫu độc lập.

## 5. Những gì skill không làm

Không đọc implementation theo đường dẫn stacktrace; không gọi API để thử; không sửa test; không tăng timeout; không tự skip/quarantine. Nó có thể đề xuất người xác minh làm việc đó sau khi lưu phân tích. Snippet mã vốn được in trong report vẫn là đầu vào được cấp, khác với mở source đầy đủ.

Trong gói hiện tại retry count bằng 0. Skill đọc và báo đúng điều đó; nó không tự tạo retry. Nhiều lượt độc lập là run history, không đổi tên thành retry history có các attempt phát sinh.
