# BÁO CÁO TUYÊN BỐ SỬ DỤNG AI (AI USAGE DECLARATION)

- **Môn học:** Kiểm thử phần mềm (Software Testing)
- **Tuần báo cáo:** Tuần 5 (Week 5)
- **Họ và tên sinh viên:** Trần Quốc Vỹ
- **MSSV:** 23120410
- **Nhóm / Đề tài:** Nhóm 10 — T07: CI/CD & Test-Harness Engineering
- **Thời gian:** 19/10/2026.
- **Phạm vi:** Triển khai và kiểm chứng local E-01.

## 1. Trạng thái sử dụng AI trong tuần

- [ ] Không sử dụng AI.
- [x] Có sử dụng AI để làm rõ yêu cầu, viết test, chạy kiểm chứng và soạn hướng dẫn.

## 2. Công cụ AI đã sử dụng

| Công cụ | Model | Mục đích | Đóng góp ước tính |
| --- | --- | --- | --- |
| ChatGPT / Codex | Chưa xác định từ thông tin phiên | Hỗ trợ E-01 | Chưa ước tính thành tỷ lệ phần trăm |

## 3. Quá trình sử dụng AI

### 3.1. E-01 — Flaky API test

**Phần AI hỗ trợ:** Đọc yêu cầu và repo; viết API test bằng Jest/Supertest, cấu hình chạy riêng, workflow chạy tay và hướng dẫn. Phiên bản cuối cho A chờ 60 hoặc 160 ms rồi thêm sản phẩm; B đọc giỏ sau 100 ms.

**Human Oversight:** Ban đầu làm rõ định nghĩa flaky test, cách A/B chạy và lý do chọn luồng giỏ hàng. Sau khi test, tiếp tục kiểm tra sampled, ý nghĩa của 10 lượt chạy và cách đối chiếu case với log. Khi đọc hướng dẫn, yêu cầu bỏ cách cộng 60 ms với độ trễ bổ sung, đổi thành chờ trực tiếp 60/160 ms; bỏ phần nói sang E-09 và xóa log/snapshot cũ. Các lượt giải thích và chỉnh sửa được giữ trong [chatlog](chatlog.md).

**Kết quả:** AI chạy lại 10 lượt sampled độc lập: 4 pass, 6 fail; các lượt fast pass và slow fail khớp log timing. Lint/build và kiểm tra isolation đạt; bộ test chính giữ baseline 39 test, 29 pass/10 lỗi SUT đã biết, không handle mở và database gốc không đổi.

## 4. Chatlog và minh chứng

- **Hội thoại và diễn biến:** [chatlog.md](chatlog.md).
- **Sản phẩm:** [test](../../../../backend/tests/experiments/cart-timing.flaky.js), [cấu hình Jest](../../../../backend/jest.flaky.config.cjs), [workflow](../../../../.github/workflows/flaky-experiment.yml), [hướng dẫn](../../../../backend/tests/experiments/README.md).
- **Bằng chứng local:** [raw log](../../../evidence/E-01/local-verification.log), [snapshot mã](../../../evidence/E-01/source.patch).

## 5. Cam kết

Khai báo đúng phần AI hỗ trợ và phần tham gia qua trao đổi, kiểm tra, yêu cầu chỉnh sửa; phân biệt kết quả local với CI/review. Người khai báo chịu trách nhiệm kiểm tra nội dung trước khi nộp.

**Người khai báo:** Trần Quốc Vỹ

*Ngày lập:* 19/10/2026.
