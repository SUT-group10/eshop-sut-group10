# BÁO CÁO TUYÊN BỐ SỬ DỤNG AI (AI USAGE DECLARATION)

- **Môn học:** Kiểm thử phần mềm (Software Testing)
- **Tuần báo cáo:** Tuần 5 (Week 5)
- **Họ và tên sinh viên:** Trần Quốc Vỹ
- **MSSV:** 23120410
- **Nhóm / Đề tài:** Nhóm 10 — T07: CI/CD & Test-Harness Engineering
- **Thời gian:** 19–22/10/2026.
- **Phạm vi:** Triển khai và kiểm chứng E-01; xây dựng protocol và rehearsal E-02; chạy và thu dữ liệu thí nghiệm E-03; chuẩn hóa đầu vào phân tích E-05; khảo sát phương pháp và so sánh người–AI E-06–E-08.

## 1. Trạng thái sử dụng AI trong tuần

- [ ] Không sử dụng AI.
- [x] Có sử dụng AI để làm rõ yêu cầu, viết test/protocol, chạy kiểm chứng và soạn hướng dẫn.

## 2. Công cụ AI đã sử dụng

| Công cụ | Model | Mục đích | Đóng góp ước tính |
| --- | --- | --- | --- |
| ChatGPT / Codex | Chưa xác định từ thông tin phiên | Hỗ trợ E-01, E-02, E-03, E-05 và E-06–E-08 | Chưa ước tính thành tỷ lệ phần trăm |
| Codex | GPT-6.1 Sol, theo xác nhận | Phân tích log bằng skill, output được bàn giao để so sánh E-08 | Chưa ước tính thành tỷ lệ phần trăm |

## 3. Quá trình sử dụng AI

### 3.1. E-01 — Flaky API test

**Phần AI hỗ trợ:** Đọc yêu cầu và repo; viết API test bằng Jest/Supertest, cấu hình chạy riêng, workflow chạy tay và hướng dẫn. Phiên bản cuối cho A chờ 60 hoặc 160 ms rồi thêm sản phẩm; B đọc giỏ sau 100 ms.

**Human Oversight:** Ban đầu làm rõ định nghĩa flaky test, cách A/B chạy và lý do chọn luồng giỏ hàng. Sau khi test, tiếp tục kiểm tra sampled, ý nghĩa của 10 lượt chạy và cách đối chiếu case với log. Khi đọc hướng dẫn, yêu cầu bỏ cách cộng 60 ms với độ trễ bổ sung, đổi thành chờ trực tiếp 60/160 ms; bỏ phần nói sang E-09 và xóa log/snapshot cũ. Các lượt giải thích và chỉnh sửa được giữ trong [chatlog](chatlog.md).

**Kết quả:** AI chạy lại 10 lượt sampled độc lập: 4 pass, 6 fail; các lượt fast pass và slow fail khớp log timing. Lint/build và kiểm tra isolation đạt; bộ test chính giữ baseline 39 test, 29 pass/10 lỗi SUT đã biết, không handle mở và database gốc không đổi.

### 3.2. E-02 — Protocol và rehearsal thí nghiệm

**Phần AI hỗ trợ:** Đối chiếu đề và checklist, viết protocol về cách chạy, phân loại kết quả và dữ liệu cần lưu; bổ sung hướng dẫn GitHub từng bước. Kiểm tra artefact, nâng ba action lên @v6 và chạy lại rehearsal.

**Human Oversight:** Ban đầu làm rõ mục tiêu và cách nghiệm thu E-02. Khi tài liệu dài, tiếp tục hỏi cách kiểm chứng bằng job thật và yêu cầu hướng dẫn cụ thể. Sau khi chạy thử, gửi ảnh để kiểm tra branch, rồi cung cấp artefact của lượt chạy đúng và hỏi cảnh báo Node 20. Yêu cầu nâng action, cân nhắc chuyển sang develop, sau đó đổi quyết định giữ main và chỉ merge YAML. Cuối cùng yêu cầu đối chiếu tiêu chí và đánh dấu hoàn thành.

**Kết quả:** Protocol và hướng dẫn đã có trong repo. Lượt chạy do sinh viên thao tác và rehearsal sau nâng action do AI chạy đều chọn fast và pass; log/report tải được. Rehearsal mới hết cảnh báo Node 20; workflow nâng cấp đã merge vào main qua PR #16. Hai lượt này giữ riêng với đợt 10 lượt E-03.

### 3.3. E-03 — Chạy và thu dữ liệu thí nghiệm

**Phần AI hỗ trợ:** Làm rõ yêu cầu, thực hiện 10 lượt GitHub Actions theo protocol E-02; thu log, artefact, metadata và lập bảng kết quả.

**Human Oversight:** Ban đầu yêu cầu giải thích công việc và checklist nghiệm thu rồi mới triển khai. Khi log báo thành công nhưng GitHub còn hiển thị đang chạy, tiếp tục hỏi cách xử lý và yêu cầu hoàn thiện lượt 09–10. Sau khi trạng thái lượt 08 được cập nhật, yêu cầu kiểm tra lại và sửa báo cáo theo kết quả cuối.

**Kết quả:** Đủ 10 lượt trên cùng SHA và môi trường: 5 PASS, 5 FAIL do timing, không retry test. Bằng chứng gốc, bảng kết quả và checksum được lưu trong repo.

### 3.4. E-05 — Chuẩn hóa đầu vào phân tích

**Phần AI hỗ trợ:** Chuẩn hóa dữ liệu của 10 lượt E-03, viết script tái tạo, prompt chung và hướng dẫn bàn giao.

**Human Oversight:** Yêu cầu che thông tin làm lộ flake để chuẩn bị phân tích người–AI. Sau đó kiểm tra việc giữ bản gốc và làm rõ chỉ gửi ZIP, phân biệt README trong gói với hướng dẫn dành cho người bàn giao.

**Kết quả:** Có bộ đầu vào chung cho Vượng và GPT; bằng chứng E-03 giữ nguyên. Đã kiểm tra nội dung ZIP và checksum.

### 3.5. E-06–E-08 — Phương pháp và so sánh người–AI

**Phần AI hỗ trợ:** Làm rõ phạm vi đề, tìm nguồn và điều chỉnh skill phân tích log; lưu output Codex GPT-6.1 Sol, đối chiếu với phân tích của Vượng và viết báo cáo so sánh.

**Human Oversight:** Yêu cầu giới hạn skill ở việc đọc log, không đọc code hoặc sửa test. Chốt dùng `ci-log-triage`, cung cấp hai bản phân tích, yêu cầu giản lược file phụ và xác nhận Vượng đã review.

**Kết quả:** Đã lưu skill có nguồn và báo cáo người–AI. Hai bên đồng thuận về vấn đề thứ tự thao tác. Phần này ghi nhận một lượt AI đã bàn giao, không ghi thành đã thử ba phương pháp theo E-07.

## 4. Chatlog và minh chứng

- **Hội thoại và diễn biến:** [chatlog.md](chatlog.md).
- **Sản phẩm:** [test](../../../../backend/tests/experiments/cart-timing.flaky.js), [cấu hình Jest](../../../../backend/jest.flaky.config.cjs), [workflow](../../../../.github/workflows/flaky-experiment.yml), [hướng dẫn](../../../../backend/tests/experiments/README.md).
- **Bằng chứng local:** [raw log](../../../evidence/E-01/local-verification.log), [snapshot mã](../../../evidence/E-01/source.patch).

- **Protocol E-02:** [cách chạy và thu dữ liệu](../../../experiments/flaky-test-protocol.md).
- **Rehearsal:** [lượt chạy do sinh viên thao tác](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39612964275), [lượt AI chạy sau nâng action](https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39615233808).
- **Tích hợp workflow:** [PR #13](https://github.com/SUT-group10/eshop-sut-group10/pull/13), [PR #16](https://github.com/SUT-group10/eshop-sut-group10/pull/16).

- **Thí nghiệm E-03:** [bảng 10 lượt và dữ liệu gốc](../../../evidence/E-03/20261021-b252db4-01/README.md), [metadata](../../../evidence/E-03/20261021-b252db4-01/batch.json), [checksum](../../../evidence/E-03/20261021-b252db4-01/SHA256SUMS).

- **Đầu vào E-05:** [ZIP chuẩn hóa](../../../evidence/E-05/participant-input.zip), [hướng dẫn bàn giao](../../../evidence/E-05/README.md), [script tái tạo](../../../experiments/prepare-triage-input.py).

- **E-06–E-08:** [khảo sát phương pháp](../../../evidence/E-06/README.md), [output Sol](../../../evidence/E-08/ai-sol/response.md), [báo cáo so sánh](../../../evidence/E-08/AI_vs_Human_Triage.md).

## 5. Cam kết

Khai báo đúng phần AI hỗ trợ và phần tham gia qua trao đổi, kiểm tra, yêu cầu chỉnh sửa; phân biệt kết quả local với CI/review. Người khai báo chịu trách nhiệm kiểm tra nội dung trước khi nộp.

**Người khai báo:** Trần Quốc Vỹ

*Ngày lập:* 19/10/2026.

*Cập nhật E-02:* 21/10/2026.

*Cập nhật E-03:* 21/10/2026.

*Cập nhật E-05:* 21/10/2026.

*Cập nhật E-06–E-08:* 22/10/2026.
