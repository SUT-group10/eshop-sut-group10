# E-09 — Sửa đồng bộ và kiểm chứng trước/sau

Ngày chạy: 22/10/2026. AI thực hiện kiểm chứng local trên Windows, Node v24.14.0, npm 11.21.0. Base revision: `f057ac453c3221eb7aba4f238b96e40e2e3af078`; các lượt sau sửa chạy với thay đổi local được lưu trong [fix.patch](fix.patch). Không gán kết quả này cho bản mã cũ hoặc cho CI.

Commit chứa bản sửa test: `3a6290defb626f4bd41c53620c2a253d27e235c5`. Kết quả đã được chạy trước khi commit; nội dung test trong commit khớp bản đã kiểm chứng.

## Nguyên nhân và thay đổi

Bản cũ khởi chạy thao tác thêm sau độ trễ 60/160 ms, rồi chỉ đợi 100 ms trước khi đọc giỏ. Test dùng thời gian đã trôi qua thay cho điều kiện thêm hoàn tất. Điều này khớp giả thuyết chính trong [so sánh E-08](../E-08/AI_vs_Human_Triage.md).

Bản sửa đợi `pendingAdd`, kiểm tra không có lỗi và HTTP POST 200 rồi mới gửi GET. Bỏ mốc đợi đọc 100 ms; giữ độ trễ thêm 60/160 ms, sampled và assertion HTTP/độ dài giỏ/quantity. Cleanup vẫn đợi tác vụ thêm kết thúc trước khi đóng fixture. Không sửa nghiệp vụ API, database hoặc helper dùng chung.

## Kiểm chứng trước sửa

Chạy chế độ slow trên mã chưa sửa: exit 1, đúng một test fail ở expected length 1, actual 0. Nguồn: [console](before-slow.console.log), [Jest JSON](before-slow.results.json), [mã trước sửa](before-source.js). Đây là một lượt tái hiện riêng, không thêm vào mẫu E-03.

## Kiểm chứng sau sửa

Đã chạy **12 lượt độc lập, 12 PASS**: một fast, một slow và 10 sampled. Sampled thực tế chọn 6 fast, 4 slow; không ép tỷ lệ. Mỗi lượt mở tiến trình Jest mới, một invocation, không retry.

| Lượt | Mode | Case chọn | Kết quả | Thêm hoàn tất (ms) | Đọc được gửi (ms) | Nguồn |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | fast | fast | PASS | 78.693 | 80.688 | [log](after-01-fast.console.log), [JSON](after-01-fast.results.json) |
| 02 | slow | slow | PASS | 171.024 | 172.547 | [log](after-02-slow.console.log), [JSON](after-02-slow.results.json) |
| 03 | sampled | fast | PASS | 69.382 | 70.819 | [log](after-03-sampled.console.log), [JSON](after-03-sampled.results.json) |
| 04 | sampled | fast | PASS | 74.425 | 75.769 | [log](after-04-sampled.console.log), [JSON](after-04-sampled.results.json) |
| 05 | sampled | slow | PASS | 172.348 | 173.591 | [log](after-05-sampled.console.log), [JSON](after-05-sampled.results.json) |
| 06 | sampled | fast | PASS | 68.013 | 69.315 | [log](after-06-sampled.console.log), [JSON](after-06-sampled.results.json) |
| 07 | sampled | fast | PASS | 81.051 | 82.443 | [log](after-07-sampled.console.log), [JSON](after-07-sampled.results.json) |
| 08 | sampled | slow | PASS | 171.745 | 173.127 | [log](after-08-sampled.console.log), [JSON](after-08-sampled.results.json) |
| 09 | sampled | fast | PASS | 76.757 | 78.182 | [log](after-09-sampled.console.log), [JSON](after-09-sampled.results.json) |
| 10 | sampled | slow | PASS | 177.08 | 178.409 | [log](after-10-sampled.console.log), [JSON](after-10-sampled.results.json) |
| 11 | sampled | slow | PASS | 174.502 | 176.05 | [log](after-11-sampled.console.log), [JSON](after-11-sampled.results.json) |
| 12 | sampled | fast | PASS | 70.663 | 71.954 | [log](after-12-sampled.console.log), [JSON](after-12-sampled.results.json) |

Cả 12 lượt có `addCompletedMs <= readSentMs`, GET 200, giỏ có một sản phẩm quantity 1; assertion POST 200 đạt trước khi đọc. Đây là kiểm tra quan hệ hoàn tất thực tế trong log, không chỉ nhìn nhãn PASS. Lint và build sau sửa đều exit 0: [lint.log](lint.log), [build.log](build.log).

[verification.json](verification.json) lưu lệnh thực thi, mode, case, timing, kết quả, invocation và môi trường. Console lưu stdout rồi stderr của cùng tiến trình; không dùng vị trí tương đối giữa hai stream để suy thứ tự thực thi. Thứ tự thêm/đọc được đối chiếu bằng timing trong observation.

## Cách kiểm tra lại

Từ repo root, chạy trong PowerShell:

```powershell
cd backend
$env:FLAKE_LATENCY_MODE = 'slow'
npm run test:flaky
$LASTEXITCODE
Remove-Item Env:FLAKE_LATENCY_MODE
```

Đổi slow thành fast hoặc sampled để thử chế độ khác. Xem log `E-09 add completed` và `E-09 observation`. Cả fast và slow giờ đều phải pass khi API đúng; sampled không còn dùng mốc chờ đọc cố định để tạo race.

Muốn tái hiện flake trước sửa, dùng revision E-03 trên checkout riêng. Không ghi đè dữ liệu E-03, E-04, E-05 hoặc các output phân tích đã có.

## Kết luận

Tái hiện được lỗi trước sửa, loại bỏ quan hệ đọc-trước-thêm bằng cách đợi hoàn tất, rồi quan sát cả fast/slow sau sửa đều pass. Kết quả hỗ trợ nguyên nhân nằm ở cách đồng bộ của test như hai bản phân tích đã dự đoán. Đây là xác nhận trên các lượt local nêu trên; số mẫu hữu hạn không chứng minh mọi điều kiện thực thi đều không còn bất kỳ lỗi nào. Môi trường npm/OS local khác đợt CI E-03 nên không dùng duration để so tốc độ trước/sau CI.
