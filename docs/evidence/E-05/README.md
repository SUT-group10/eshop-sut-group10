# E-05 — Hướng dẫn chuẩn bị và bàn giao dữ liệu

> Trang này và `participant-input.zip` thuộc **thí nghiệm v1 — cart**. Hướng dẫn bàn giao bên dưới áp dụng gói v1; v2 tự xuất gói `analysis-input-<batch-id>.zip` từ bộ chạy mới. ZIP và dữ liệu chuẩn hóa v1 được giữ nguyên. [Protocol v2 hiện hành](../../experiments/order-history-protocol.md).

Tài liệu này dành cho người chuẩn bị và bàn giao dữ liệu, không gửi cho Vượng hoặc GPT. README nằm bên trong ZIP là tài liệu khác: chỉ cung cấp bối cảnh chung để đọc log, không chứa đáp án.

## File gửi cho Vượng và GPT

Chỉ gửi **[participant-input.zip](participant-input.zip)** cho cả Vượng và GPT. ZIP gồm:

- `README.md`: bối cảnh và quy tắc đọc dữ liệu.
- `input.md`: lịch sử 10 lượt và console đã chuẩn hóa, có số dòng để dẫn chứng.
- `history.json`: revision bí danh, thời gian, pass/fail, exit code, số lần thực thi và retry.
- `run-01` đến `run-10`: mỗi thư mục có `console.log` và `results.json`.
- `prompt.md`: yêu cầu phân tích chung, lưu nguyên bản cho E-04 và làm baseline khi thiết kế prompt ở E-06/E-07.
- `SHA256SUMS`: kiểm tra tính toàn vẹn của bộ đầu vào.

Nếu GPT đọc được ZIP, đính kèm ZIP và dùng nguyên yêu cầu trong `prompt.md`. Nếu giao diện không đọc ZIP, giải nén rồi cung cấp toàn bộ file trong gói; không chỉ đưa một vài log fail. Cả hai bên cần nhận đúng cùng phiên bản dữ liệu. Không gửi README này, bảng ánh xạ, báo cáo E-03, protocol, repo hoặc lịch sử chat thiết kế test.

## Cách dùng cho E-04 và E-06/E-07

1. Chuẩn bị gói này cho Vượng; đề nghị phân tích bằng log, ghi thời gian thực tế, giả thuyết, dẫn chứng và bước kiểm tra. Lưu kết quả trước khi xem output AI. Không thực hiện phân tích thủ công thay Vượng.
2. E-06 nghiên cứu và chọn prompt patterns; bộ dữ liệu đã sẵn sàng nhưng task nghiên cứu đó chưa được thực hiện trong E-05. Prompt chung trong gói chưa phải ba prompt patterns đã được thử nghiệm.
3. Khi đến E-07, dùng chat/ngữ cảnh mới chưa biết nguyên nhân; cung cấp cùng dữ liệu cho các lần thử prompt. Chat đã tạo test hoặc biết đáp án không được coi là phân tích độc lập. Lưu nguyên prompt/output, model nếu biết, thời gian và mọi lần thử.
4. Chỉ đối chiếu hai bản phân tích sau khi bản thủ công đã được lưu. Nếu người phân tích đã biết nguyên nhân hoặc đã đọc báo cáo có đáp án, ghi nhận việc đó; che nhãn không xóa được kiến thức đã biết.

E-05 chỉ chuẩn bị đầu vào, không gửi tin nhắn cho thành viên hay thực hiện lượt GPT triage.

## Những gì đã chuẩn hóa

Giữ nguyên bằng chứng [E-03](../E-03/20261021-b252db4-01/README.md); chỉ tạo bản dẫn xuất:

| Nội dung gốc | Xử lý trong bản gửi |
| --- | --- |
| Tên test có `injected timing flake`, tên file/config/lệnh có `flaky`, thư mục experiments, nhãn E-01 | Thay bằng tên trung tính, nhất quán; giữ số dòng stack frame |
| Đường dẫn workspace trên runner | Thay tiền tố bằng `<workspace>` |
| Run ID, URL, SHA, tên branch/workflow/artifact | Dùng run-01…run-10 và revision-01; không đưa URL/branch vào gói |
| Các trường điều khiển `mode`, `selectedCase`, `delayMs`, `readWaitMs` trong quan sát console | Bỏ khỏi bản gửi; đây là tham số thiết kế, không phải thời điểm quan sát |
| README, batch, nhãn TIMING_FAIL và giải thích nguyên nhân đã có | Không đưa vào gói |
| Thời điểm thêm/đọc thực tế, thứ tự dòng log, HTTP status, giỏ hàng, assertion, pass/fail, duration, timestamp và retry | Giữ nguyên giá trị |

Các giá trị khoảng 60/160/100 ms vẫn có thể suy ra từ thời gian thao tác. Đây là bằng chứng cần để chẩn đoán, không che để làm bài khó hơn. Tên và lệnh trong bản gửi chỉ là bí danh, không phải code/lệnh chạy thực tế. Gói đã được kiểm tra nhãn tiết lộ và các mẫu credential/email/đường dẫn cá nhân thường gặp; dữ liệu sản phẩm fixture được giữ lại.

## Đối chiếu dành cho người tổ chức — không gửi cùng dữ liệu

[organizer-mapping.json](organizer-mapping.json) lưu ánh xạ run, nguồn và SHA256 trước/sau chuẩn hóa, cùng hash ZIP. File ở cùng repo, không phải vùng có kiểm soát truy cập: phải gửi riêng ZIP để tránh người phân tích vô tình đọc đáp án.

Tái tạo và kiểm tra từ repo root bằng PowerShell:

```powershell
python docs/experiments/prepare-triage-input.py
Get-FileHash docs/evidence/E-05/participant-input.zip -Algorithm SHA256
```

Script tạo gói xác định từ nguồn E-03, kiểm tra các quan sát sau chuẩn hóa và quét nhãn tiết lộ trong toàn bộ file gửi. Không chạy lại test, không đổi nguồn E-03.
