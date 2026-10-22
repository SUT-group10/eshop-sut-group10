# E-06 — Khảo sát và chọn phương pháp phân tích log CI

Ngày hoàn thiện: 22/10/2026. Đây là phần phương pháp dùng cho báo cáo `AI_vs_Human_Triage`: tìm nguồn, đánh giá độ phù hợp và lưu bản skill đã điều chỉnh. Không coi việc chọn phương pháp là bằng chứng nó tốt nhất về hiệu quả thực nghiệm.

## 1. Phương pháp được chọn

Chọn **systematic debugging**, điều chỉnh thành [ci-log-triage/SKILL.md](ci-log-triage/SKILL.md) để chỉ phân tích dữ liệu được cung cấp. Quy trình: đọc lỗi và kiểm kê dữ liệu → đối chiếu lượt thành công/thất bại → lập giả thuyết có dẫn chứng → đề xuất bước xác minh.

Kỹ thuật chính gồm phân rã nhiệm vụ, phân tích đối chiếu, kiểm chứng giả thuyết và ràng buộc đầu ra theo bằng chứng. Không gọi là Few-Shot vì không có chuỗi ví dụ đầu vào/đáp án hoàn chỉnh; không gọi là Chain-of-Thought chỉ vì quy trình chia nhiều bước.

## 2. Nguồn công khai và ứng viên đã đối chiếu

| Ứng viên | Kỹ thuật và độ phù hợp | Quyết định |
| --- | --- | --- |
| [obra/superpowers — systematic-debugging](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/systematic-debugging/SKILL.md) | Điều tra bằng chứng, so sánh trường hợp hoạt động/lỗi, giả thuyết có thể kiểm tra; bản gốc còn đọc code và sửa lỗi | Chọn làm nguồn phương pháp; bỏ các bước vượt phạm vi log |
| [openai/skills — gh-fix-ci](https://github.com/openai/skills/blob/main/skills/.curated/gh-fix-ci/SKILL.md) | Thu check/log GitHub Actions, trích lỗi và lập kế hoạch sửa; cần gh, repo/PR | Tham khảo cách giữ ngữ cảnh và báo thiếu log; không chọn làm bản chính vì bộ E-05 đã có dữ liệu tĩnh |
| [agent-substrate/substrate — detect-flaky-tests](https://github.com/agent-substrate/substrate/blob/main/.agents/skills/detect-flaky-tests/SKILL.md) | Tách lỗi hạ tầng khỏi lỗi test rồi tổng hợp nhiều lượt; gắn với Go, repo và quy trình issue/PR riêng | Tham khảo cách phân biệt setup/test; không áp nguyên ngưỡng hay tự động mở issue/sửa mã |

Các ứng viên trên đã được đọc để khảo sát phương pháp, chưa thử đối chứng hiệu quả của cả ba. Chỉ nguồn được chọn được cố định commit cho bản điều chỉnh; các liên kết main còn lại là nguồn tham khảo có thể thay đổi.

## 3. Vì sao chọn bản điều chỉnh này?

Đầu vào của nhóm là [bộ E-05](../E-05/README.md) gồm log, Jest JSON và lịch sử 10 lượt. Cần giải thích kết quả bằng dữ liệu, không cần agent tự tải CI hoặc sửa sản phẩm. Phương pháp được chọn có thể dùng để so sánh các lượt và lập giả thuyết mà không mặc định nguyên nhân là flaky hay timing.

Bản gốc có nhiều file vì phục vụ điều tra và sửa lỗi đầy đủ. Bản điều chỉnh chỉ cần ba file: hướng dẫn tự chứa, hồ sơ nguồn/điều chỉnh và giấy phép. Danh mục từng file gốc cùng quyết định giữ/bỏ nằm trong [SOURCES.md](ci-log-triage/SOURCES.md).

| Phần | Xử lý |
| --- | --- |
| Đọc kỹ lỗi, đối chiếu trường hợp pass/fail, truy ngược dấu vết, kiểm tra giả thuyết | Giữ nguyên tắc, viết lại thành quy trình chỉ đọc bằng chứng |
| Đọc source/Git, thêm instrumentation, chạy tái hiện, tạo test, sửa mã và chạy xác nhận | Bỏ khỏi phạm vi thực thi; nếu cần thì chỉ đề xuất cho người xác minh |
| Script tìm test gây nhiễm trạng thái và code ví dụ sửa timing | Không đưa vào bản điều chỉnh |
| Nguồn dữ liệu được phép đọc | Chỉ gói đầu vào; không repo, web, đáp án hoặc output của bên còn lại |
| Báo cáo phân tích | Tối đa ba giả thuyết có dẫn chứng, đúng ba bước kiểm tra, mức chắc chắn và thông tin thiếu |
| Kiểm soát suy diễn | Phân biệt quan sát/giả thuyết; không bịa số dòng, nguyên nhân, phần trăm tin cậy hoặc thời gian |

## 4. Bản lưu và cách bàn giao

- [SKILL.md](ci-log-triage/SKILL.md): bản hướng dẫn dùng để phân tích.
- [SOURCES.md](ci-log-triage/SOURCES.md): nguồn gốc và thay đổi; hồ sơ phương pháp dành cho người tổ chức.
- [LICENSE.txt](ci-log-triage/LICENSE.txt): MIT, giữ thông báo bản quyền của nguồn.
- [SHA256SUMS](SHA256SUMS): kiểm tra toàn vẹn bản lưu.

Bản skill trong evidence được sao chép nguyên byte từ bản đã dùng để chuẩn bị thí nghiệm. Khi chạy độc lập, cung cấp SKILL.md và dữ liệu E-05 trong ngữ cảnh chưa biết đáp án; nếu phân phối skill thì giữ giấy phép. Không đưa README khảo sát hoặc hồ sơ đối chiếu nguồn vào gói dữ liệu phân tích. Không thay ZIP E-05 để tránh đổi đầu vào của những lượt đã thực hiện.

Trong công cụ hỗ trợ skills, gọi skill với gói dữ liệu được giao. Trong chat chỉ nhận văn bản, dùng nội dung SKILL.md như hướng dẫn; không gọi đó là đã chạy tích hợp skill nếu thực tế chỉ dán nội dung.

## 5. Kiểm chứng và ranh giới nghiệm thu

Đã kiểm tra frontmatter/cấu trúc bằng skill validator, các liên kết local và việc bản hướng dẫn không chứa số liệu/đáp án riêng của EShop. Bản lưu khớp byte với bản nguồn local. Đây là kiểm tra cấu trúc và phạm vi, không phải đo hiệu quả chẩn đoán.

Output Codex GPT-6.1 Sol do người dùng cung cấp được giữ riêng tại [E-08](../E-08/ai-sol/README.md). Không dùng một output đó để tuyên bố phương pháp thắng các ứng viên chưa được thử. E-06 hoàn thành ở mức khảo sát, đề xuất một phương pháp và lưu bản điều chỉnh có nguồn; báo cáo so sánh người–AI và đánh giá noise thực hiện riêng.
