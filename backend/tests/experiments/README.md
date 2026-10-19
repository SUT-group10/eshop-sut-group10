# E-01 — API test có sleep-based flake

Đây là test thí nghiệm được chủ động tạo, không phải lỗi timing đã phát hiện sẵn trong EShop. Chạy bằng JavaScript/Jest và Supertest qua route Express thật. Dùng fixture SQLite trong bộ nhớ; không cần mở server hoặc database riêng.

## Cơ chế và nguyên nhân đã biết

- A đợi **60 hoặc 160 ms**, rồi gửi `POST /api/cart`.
- Ở chế độ mặc định `sampled`, mỗi lượt chọn ngẫu nhiên một trong hai mức chờ trên, xác suất bằng nhau. Chỉ thời gian chờ được chọn ngẫu nhiên; assertion và kết quả API đều là thật.
- B bắt đầu chờ cùng lúc với A, đợi cố định 100 ms rồi gửi `GET /api/cart`, kiểm tra đúng một sản phẩm và số lượng 1.
- Nếu B đọc trước khi A cập nhật giỏ, assertion fail. Nếu A hoàn tất trước khi B đọc, assertion pass. Thời gian thực tế phụ thuộc thêm tải máy/lập lịch; hai mức trễ không bảo đảm tuyệt đối kết quả trên mọi máy.

Root cause nằm ở test: B đọc sau thời gian cố định 100 ms mà không đợi A thêm sản phẩm xong. Độ trễ chỉ được thêm trong file thí nghiệm, không sửa nghiệp vụ SUT hay helper dùng chung.

`E-01 observation` ghi case đã chọn (`selectedCase`), thời gian chờ của A (`delayMs`), thời điểm đọc và giỏ thực tế. `E-01 add completed` ghi thời điểm thao tác thêm hoàn tất. Thời gian là ms tính từ lúc khởi chạy A/B sau khi fixture đã sẵn sàng. Khi assertion fail, cleanup vẫn chờ A kết thúc rồi đóng database.

## Chạy một lượt trong terminal PowerShell

Mở terminal tại thư mục gốc repo, rồi chạy:

```powershell
cd backend
npm ci
npm run test:flaky
$LASTEXITCODE
```

Mặc định là `sampled` khi chưa đặt `FLAKE_LATENCY_MODE`. Toàn bộ ví dụ dưới đây dùng **PowerShell**, phù hợp với terminal có dấu nhắc `PS`. Tiếp tục chạy từ thư mục `backend`.

Exit 0 nghĩa là test pass; exit 1 kèm assertion giỏ rỗng là kết quả fail dự kiến của thí nghiệm. Lỗi cài đặt, fixture, HTTP hoặc timeout cần được phân biệt với timing flake; không coi mọi exit 1 là kết quả thí nghiệm hợp lệ.

Không cần chạy `npm ci` mỗi lượt nếu dependency đã được cài đúng lockfile.

## Thử hai điều kiện để hiểu cơ chế

```powershell
$env:FLAKE_LATENCY_MODE = 'fast'
npm run test:flaky
$LASTEXITCODE

$env:FLAKE_LATENCY_MODE = 'slow'
npm run test:flaky
$LASTEXITCODE

Remove-Item Env:FLAKE_LATENCY_MODE
```

`Remove-Item` xóa biến chế độ khỏi phiên terminal để các lượt tiếp theo trở về mặc định `sampled`.

`fast` cho A chờ 60 ms, thường pass; `slow` cho A chờ 160 ms, thường fail. Đây là hai lượt chẩn đoán riêng; `sampled` tự chọn giữa hai case này mỗi lượt.

## Tự quan sát nhiều lượt sampled

```powershell
$env:FLAKE_LATENCY_MODE = 'sampled'

foreach ($attempt in 1..10) {
    Write-Host "Attempt ${attempt}"
    npm run test:flaky
    $testExit = $LASTEXITCODE
    Write-Host "Attempt ${attempt}: exit code $testExit"
}

Remove-Item Env:FLAKE_LATENCY_MODE
```

Mỗi lệnh mở một tiến trình Jest mới, không retry bên trong lượt. Không bảo đảm đúng 5 pass/5 fail; đối chiếu `selectedCase`, `delayMs` và timing trong log để hiểu từng kết quả.

Để xuất report Jest của một lượt:

```powershell
New-Item -ItemType Directory -Force 'test-results/flaky' | Out-Null
npm run test:flaky -- --json --outputFile=test-results/flaky/results.json
$LASTEXITCODE
```

## Cô lập và CI

- File kết thúc bằng `.flaky.js`, chỉ cấu hình `jest.flaky.config.cjs` chọn nó. `npm test`, các test theo tầng và `test:ci` tiếp tục chỉ chọn `.test.js` như trước.
- Workflow `Flaky experiment (manual only)` chỉ nhận `workflow_dispatch`, không tự chạy khi push/PR. Mỗi dispatch chạy một lượt sampled và upload report/log kể cả assertion fail, giữ exit code thật. Không thêm workflow này vào required checks của pipeline chính.
- File workflow đang có trong mã nguồn không chứng minh đã chạy CI. Sau khi nhóm đưa workflow lên remote/default branch, mới có thể chạy qua GitHub Actions.

Bằng chứng kiểm chứng local của E-01 được lưu tại `docs/evidence/E-01/`. Checklist E-01 chỉ được chốt khi có commit và các điều kiện nghiệm thu của nhóm; việc có file/test local chưa đồng nghĩa đã hoàn thành toàn bộ task.

## Kết quả kiểm chứng local ngày 19/10/2026

[Raw log](../../../docs/evidence/E-01/local-verification.log) của phiên bản 60/160 ms ghi 10 lượt `sampled` độc lập: **4 pass, 6 fail**, không retry. Cả 4 lượt chọn `fast` (60 ms) đều pass; cả 6 lượt chọn `slow` (160 ms) đều fail vì giỏ còn rỗng khi đọc. Hai lượt chẩn đoán riêng cũng cho `fast` pass/exit 0 và `slow` fail/exit 1.

Lint/build pass; kiểm tra isolation ba seed vẫn có 39 test, 29 pass/10 lỗi SUT đã biết, không handle mở; hash database gốc không đổi. Bộ test mặc định không chọn file `.flaky.js`.

Đây là kiểm chứng local cho E-01, chưa phải kết quả CI. Mã được kiểm chứng là thay đổi chưa commit trên base `b9c76a6`; [source.patch](../../../docs/evidence/E-01/source.patch) giữ snapshot phần thay đổi để tái hiện. Chưa có peer review được ghi nhận trong lần kiểm chứng này.

