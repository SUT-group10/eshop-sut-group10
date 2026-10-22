# Nguồn và phạm vi điều chỉnh

Bản điều chỉnh phục vụ phân tích log tĩnh, không phải bản sao đầy đủ của bộ superpowers. Ngày đối chiếu: 22/10/2026.

- Repo nguồn: https://github.com/obra/superpowers
- Commit đã đối chiếu: `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`.
- File chính: ['systematic-debugging/SKILL.md'](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/systematic-debugging/SKILL.md).
- Giấy phép: MIT, Copyright (c) 2025 Jesse Vincent. Giữ thông báo ở LICENSE.txt.

## Các file trong thư mục gốc

| File | Vai trò và quyết định |
| --- | --- |
| SKILL.md | Giữ phương pháp đọc lỗi, đối chiếu trường hợp hoạt động/lỗi, lập giả thuyết và xác minh; viết lại cho dữ liệu tĩnh |
| root-cause-tracing.md | Tham khảo nguyên tắc truy ngược; chỉ áp dụng cho chuỗi sự kiện/stacktrace đã cung cấp, không truy cập code hoặc chèn log |
| condition-based-waiting.md | Hướng sửa một nhóm lỗi cụ thể; không nạp vào skill để tránh định hướng sẵn loại nguyên nhân |
| condition-based-waiting-example.ts | Code sửa/đồng bộ, không cần cho triage chỉ đọc log |
| defense-in-depth.md | Thay đổi validation trong code, ngoài phạm vi |
| find-polluter.sh | Chạy test để tìm tác nhân gây nhiễm trạng thái, ngoài phạm vi; không mang sang hoặc thực thi |
| CREATION-LOG.md | Nhật ký xây skill gốc, không phải đầu vào phân tích |
| test-academic.md | Kịch bản đánh giá hành vi skill gốc, không phải log CI cần phân tích |
| test-pressure-1.md / test-pressure-2.md / test-pressure-3.md | Kịch bản đánh giá dưới áp lực, không cần cho bản điều chỉnh |

## Giữ, bỏ và thêm

**Giữ:** evidence-first investigation, so sánh trường hợp thành công/thất bại, truy ngược trong phạm vi bằng chứng, giả thuyết có thể kiểm chứng và thử từng yếu tố.

**Bỏ:** yêu cầu tái hiện trực tiếp, kiểm tra Git/source, instrument, viết regression test, thực thi bản sửa; bỏ dependency vào các skill khác và các quy tắc khẳng định nguyên nhân/kiến trúc quá mức chỉ từ số lần thử.

**Thêm theo nhu cầu nhóm:** chỉ đọc dữ liệu được giao; không đếm lặp report; dẫn chứng theo run/file/dòng hoặc JSON path; tối đa ba giả thuyết; đúng ba next-checks; giới hạn độ chắc chắn; tách setup/test failure và quan sát/giả thuyết; không mặc định lỗi là flaky hoặc timing.

Đây là systematic debugging được điều chỉnh với ràng buộc bằng chứng và cấu trúc đầu ra. Không gọi là Few-Shot hoặc Chain-of-Thought chỉ vì quy trình có nhiều bước. Chưa có thử nghiệm so sánh hiệu quả; kiểm tra cấu trúc không chứng minh chất lượng chẩn đoán.

## Sử dụng độc lập

Trong môi trường hỗ trợ skills, gọi `ci-log-triage` cùng gói dữ liệu được phép đọc. Với chat chỉ nhận văn bản, cung cấp nội dung SKILL.md làm hướng dẫn cùng bộ dữ liệu; đây là dùng hướng dẫn từ skill, không mặc nhiên là đã cài hoặc chạy tích hợp skill.

Chỉ cấp SKILL.md (và LICENSE nếu phân phối), cùng dữ liệu chuẩn hóa. SOURCES.md là hồ sơ phương pháp của người tổ chức, không cần đưa cho bên phân tích khi giới hạn chỉ đọc gói dữ liệu. Không chuyển cả lịch sử chat đã biết đáp án sang ngữ cảnh đánh giá. Bản skill không tự tạo chat hoặc gửi dữ liệu.
