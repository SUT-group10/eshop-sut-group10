# E-10 — Kết luận về giá trị và failure modes của AI

> Nội dung bên dưới giữ kết luận **thí nghiệm v1 — cart**. Bản hiện hành nằm tại [E-10 v2 — giá trị, nhiễu và ba failure modes](order-history-v2-39860438568/README.md), dựa trên batch CI order history và output GPT-6.1 Sol v2. [Protocol v2](../../experiments/order-history-protocol.md).

Ngày chốt: 22/10/2026. Nhóm quyết định đóng task với kết quả quan sát hiện có, không tạo thêm trường hợp lỗi hoặc bịa failure mode để đủ số lượng.

## Kết quả trong ca đã thực hiện

[Output Codex GPT-6.1 Sol](../E-08/ai-sol/response.md) và [phân tích của Vượng](../E-04/phan-tich-vuong.md) cùng xác định vấn đề thứ tự thêm/đọc. [E-09](../E-09/README.md) tái hiện được lỗi trước sửa và có 12/12 lượt sau sửa pass khi đợi thêm hoàn tất trước khi đọc. Kết quả này hỗ trợ giả thuyết chính mà AI nêu.

**Chưa ghi nhận failure chẩn đoán được xác nhận trong output AI đã bàn giao.** Không biến kết luận đó thành “AI không bao giờ sai”, “AI tốt hơn người” hoặc “mọi nhận định phụ đều đúng”. Đây là một ca có log timing đầy đủ và một output AI được cung cấp.

## Giá trị và điểm cần review

AI tổng hợp đúng 10 lượt, trích các mốc timing và đề xuất cách xác minh phù hợp; không tự nhận đã tái hiện hay sửa lỗi. Giá trị quan sát được là hỗ trợ tổ chức bằng chứng và cung cấp một bản phân tích thứ hai.

[Báo cáo E-08](../E-08/AI_vs_Human_Triage.md) vẫn ghi hai điểm cần làm rõ: cách giữ revision khi thay đổi thứ tự thao tác và ý nghĩa timestamp workflow/Jest. Không xóa các nhận xét này chỉ vì giả thuyết chính đúng. Chúng là điểm review về diễn đạt/metadata, chưa được tính thành ba failure modes thực tế riêng biệt.

Biện pháp kiểm chứng áp dụng trong ca này: đối chiếu số liệu với log gốc, phân biệt quan sát với giả thuyết và kiểm chứng thay đổi đồng bộ ở E-09. Thời lượng Vượng là 20 phút, Sol là 1 phút 30 giây; chênh lệch này chưa tính toàn bộ công sức review và xác minh nên không tự chứng minh năng suất tổng thể.

## Ranh giới kết luận và trạng thái

Task được **đóng theo quyết định nhóm**, không phải nghiệm thu đã tìm đủ ít nhất ba failure modes thực tế theo dòng checklist ban đầu. Bộ dữ liệu hiện tại chưa chứng minh tiêu chí số lượng đó. Không thực hiện thêm ba prompt patterns hoặc dựng ba lỗi AI giả định rồi gọi là quan sát thực tế.

Brief T07 còn yêu cầu User Guide nêu ba cách công cụ thực tế có thể gây hiểu nhầm. Việc đóng task nội bộ này không tự thay đổi yêu cầu sản phẩm nộp; khi tổng hợp User Guide phải kiểm tra bằng chứng phù hợp, không dùng kết quả “chưa quan sát failure trong một ca” để tuyên bố đã đáp ứng mục đó.
