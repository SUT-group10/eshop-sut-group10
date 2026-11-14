# Thí nghiệm hiện tại — Order history, retry và evidence v2

Đọc [protocol v2.0](../../../docs/experiments/order-history-protocol.md) để chạy thí nghiệm mới, xem từng attempt và lấy ZIP cho người/AI. Từ `backend`, chạy `npm run experiment:orders -- --runs 10 --retries 2`. Bản mới dùng order API và SQLite thật, retry của Jest tối đa 2 lần; `npm run test:flaky` hiện chọn ca mới này.

Mỗi batch chọn một chế độ: `timed` để quan sát flake, `awaited` để kiểm chứng sửa đồng bộ. Retry giữ nguyên chế độ. Mặc định batch chính có 10 tiến trình Jest độc lập, mỗi tiến trình tối đa ba attempt; đây không phải 10 test case khác nhau hoặc 10 dispatch.

```powershell
cd backend
npm run experiment:orders -- --runs 10 --retries 2
$LASTEXITCODE
```

Lệnh trên chạy từ repo root, sau khi cài dependency backend và có Python 3. Bàn giao `analysis-input-<batch-id>.zip` được in cuối lệnh; giữ `organizer-evidence-<batch-id>.zip` cho người tổ chức. Các ZIP lưu từ đợt kiểm chứng trước khi đổi tên vẫn mang tên lịch sử.

[Kiểm chứng local v2](../../../docs/evidence/E-03/order-history-v2-local-20261023/README.md) lưu sáu batch, trace từng attempt và gói phân tích mới. Đây là dữ liệu mới, không thay thế kết quả người–AI trước đây.

**Trạng thái v2:** đã có implementation, protocol và kiểm chứng local. Run CI, phân tích thủ công/AI và so sánh v2 cần bằng chứng riêng khi thực hiện. Thời lượng 20 phút/90 giây và các kết luận E-08–E-10 cũ thuộc v1.

Phần cart bên dưới là tài liệu **v1 lịch sử**. Các lệnh ở phần này áp dụng revision v1 tương ứng, không phải hành vi hiện tại của `test:flaky`. Bản cart sau sửa nằm ở commit `3a6290defb626f4bd41c53620c2a253d27e235c5`; bản trước sửa dùng revision ghi trong E-03 v1.

---

# Lịch sử v1 — E-09, kiểm chứng sau khi sửa timing flake

Phiên bản hiện tại đợi `POST /api/cart` hoàn tất và kiểm tra HTTP 200 trước khi gửi `GET /api/cart`. Không dùng mốc chờ cố định 100 ms nữa. Vẫn giữ độ trễ mô phỏng 60/160 ms, lựa chọn sampled và assertion giỏ hàng. Cả fast và slow đều phải pass khi API xử lý đúng.

Chạy từ repo root, bằng PowerShell:

```powershell
cd backend
$env:FLAKE_LATENCY_MODE = 'slow'
npm run test:flaky
$LASTEXITCODE
Remove-Item Env:FLAKE_LATENCY_MODE
```

Đổi slow thành fast hoặc sampled để thử chế độ khác. Log `E-09 observation` cần có `addCompletedMs <= readSentMs`, HTTP 200, một sản phẩm và quantity 1. Trường `readAfterAdd: true` chỉ mô tả bản sửa; timing và assertion là bằng chứng. Tên file `.flaky.js` và lệnh giữ nguyên để dùng cấu hình chạy riêng, không có nghĩa bản sửa phải fail ngẫu nhiên.

Bằng chứng trước/sau ở [E-09](../../../docs/evidence/E-09/README.md). Dữ liệu E-03/E-05 giữ nguyên phiên bản cũ. Muốn tái hiện flake cũ, dùng revision ghi trong E-03 trên checkout riêng.

---

# Tài liệu lịch sử E-01 — trước bản sửa E-09

**Nội dung bên dưới mô tả phiên bản cũ. Các nhận định slow fail và log E-01 chỉ áp dụng trước bản sửa.**

# E-01 — API test có sleep-based flake

Đây là test thí nghiệm được chủ động tạo, không phải lỗi timing đã phát hiện sẵn trong EShop. Chạy bằng JavaScript/Jest và Supertest qua route Express thật. Dùng fixture SQLite trong bộ nhớ; không cần mở server hoặc database riêng.

Khi thu dữ liệu chính thức, dùng [protocol E-02](../../../docs/experiments/flaky-test-protocol.md). Các lệnh và kết quả bên dưới phục vụ hướng dẫn/kiểm chứng E-01, không thay cho đợt đo được chốt trước theo protocol.

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

