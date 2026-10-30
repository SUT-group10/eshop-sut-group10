# Remind: 

Để một môi trường mới (clean clone) hoặc máy của thành viên khác (như Vỹ) tự động nhận diện và cấp quyền cho các script này mà không cần gõ lệnh thủ công, giải pháp cốt lõi nằm ở việc lưu trữ cấu hình phê duyệt vào file `package.json` và đồng bộ nó qua Git.

Khi bạn chạy lệnh `npm install-scripts approve <pkg>`, npm không lưu cấu hình này ở hệ điều hành, mà nó sẽ tự động chỉnh sửa file `package.json` của dự án (thêm vào trường `"allowScripts"` hoặc cấu hình tương đương).

Dưới đây là quy trình 3 bước để "đóng gói" quyền này vào mã nguồn, đáp ứng đúng tiêu chuẩn Tính tất định (Determinism) của hệ thống Test Harness:

1. **Phê duyệt và ghi cấu hình vào package.json (Tại local hiện tại):**
Chạy các lệnh approve để npm cập nhật file `package.json`:
```bash
npm install-scripts approve sqlite3
npm install-scripts approve @parcel/watcher
npm install-scripts approve unrs-resolver

```


2. **Kiểm tra và Commit cấu hình:**
Bạn gõ lệnh `git status`, bạn sẽ thấy file `package.json` (và có thể cả `package-lock.json`) ở trạng thái *modified*. Bạn thực hiện commit sự thay đổi này:
```bash
git add package.json package-lock.json
git commit -m "build: whitelist install-scripts for sqlite3 and native bindings"
git push origin main

```


*(Lưu ý: Thay `main` bằng tên nhánh `github-ci` nếu bạn đang làm việc trên nhánh đó).*
3. **Nguyên lý hoạt động ở môi trường mới (Clean Clone):**
Lần tới khi Vỹ (hoặc CI/CD runner) thực hiện lệnh `git clone` ra một thư mục trắng hoàn toàn và chạy `npm ci`, npm sẽ đọc file `package.json` đã được cập nhật. Nhờ danh sách whitelist đã nằm sẵn trong code, npm sẽ tự động thực thi ngầm `node-gyp rebuild` cho `sqlite3` mà không hiện lại cảnh báo hay chặn tiến trình.



Điều này giải quyết triệt để yêu cầu của Task C-07: đảm bảo mã nguồn chạy được từ clone sạch mà không dựa vào bất kỳ cấu hình ngầm hay thao tác thủ công nào trên máy cá nhân. Bạn có thể thực hiện commit này, sau đó tiếp tục chạy `npm run lint` và `npm run build` trên thư mục clean-clone hiện tại để lấy log minh chứng cuối cùng.

# Task C

## C03


Lần chạy đầu tiên: https://github.com/SUT-group10/eshop-sut-group10/actions/runs/38856327913
Chạy thứ hai: https://github.com/SUT-group10/eshop-sut-group10/actions/runs/38871782770
Chạy thứ ba: https://github.com/SUT-group10/eshop-sut-group10/actions/runs/38873579380
- Tại sao cả 3 lần chạy trước đó đều không cache được ? (message "npm not found" ở step "Set up Node.js 22" trong job "ci: add backend quality gateway)
+ Theo mặc định, cơ chế Post Set up Node.js chỉ lưu cache khi Job THÀNH CÔNG => Nhưng bởi vì có 10 lỗi nghiệp vụ (API Tests) bị failed => Job này bị failed. Dẫn đến cuối Job sẽ tự động bỏ qua việc lưu cache (nằm tránh lưu phải cache bẩn/lỗi).

- Vậy tại sao có sự chênh lệch số lượng giữa 3 lần chạy ? 
+ Lần 1 (added 135 packages in 2s): Lúc này backend/package-lock.json chưa có bộ devDependencies của Jest/ESLint/Supertest (chỉ có 135 gói cơ bản của Express/SQLite), nên bước Lint ngay sau đó bị lỗi luôn.

+ Lần 2 (added 483 packages in 5s) vs. Lần 3 (added 483 packages in 1m): Sang lần 2 và 3, code đã có đủ 483 packages (gồm cả Jest, ESLint, Supertest). Cùng là Cache Miss nhưng Lần 2 mất 5s còn Lần 3 vọt lên 1m (1 phút) là do biến môi trường `npm_config_build_from_source`: "`true`" trong ci.yml **bắt buộc runner phải tải mã nguồn C/C++ của sqlite3** về và biên dịch trực tiếp (compile from source) bằng node-gyp. Tốc độ tải tarball từ mạng và xung nhịp CPU của máy ảo Ubuntu tại thời điểm cấp phát ở Lần 3 bị nghẽn, làm quá trình compile C++ kéo dài tới 1 phút.

+ ci.yml đặt npm_config_build_from_source: "true", nên ngay cả khi đạt trạng thái Cache Hit, lệnh npm ci vẫn phải bung mã nguồn C++ của sqlite3 ra và gọi trình biên dịch C++ (g++ / make) để build lại native addon từ đầu.
+ Do đó, khi bạn đo được số liệu Cache Hit ở bước trên, nếu thấy thời gian chạy npm ci chỉ giảm nhẹ hoặc vẫn mất vài chục giây (do thời gian CPU biên dịch C++ chiếm đa số chứ không phải thời gian tải mạng), hãy đưa ngay phân tích này vào báo cáo C-03 và mục giới hạn F-05 ("Giới hạn của npm cache khi dự án sử dụng native bindings như sqlite3 với cờ build_from_source").

**Giải pháp**: sử dụng phương án "Phương án 1: Tách riêng bước Cache bằng actions/cache@v4 với cờ save-always: true"
    Thay vì dùng tính năng cache: npm tích hợp sẵn trong setup-node (vốn bị khóa cứng điều kiện chỉ lưu khi Job xanh), bạn chuyển sang dùng trực tiếp action chính thức của GitHub là actions/cache@v4. Từ phiên bản v4, GitHub cung cấp thuộc tính save-always: true, cho phép lưu cache của /home/runner/.npm ngay cả khi bước API tests phía sau bị đỏ do lỗi của SUT!
Lần chạy thứ 4: https://github.com/SUT-group10/eshop-sut-group10/actions/runs/39724696841/job/119645830423

**=> Giải pháp trên đã thất bại, vì sao ?**

Từ phần log của step: "Cache npm dependencies" ta nhận ra được: GitHub đã vô hiệu hóa (deprecate) cờ `save-always` trong `actions/cache@v4` vì bản chất kiến trúc của các bước `Post ...` trong GitHub Actions là luôn bị Runner tự động `Skipped` nếu có **bất kỳ step nào trước đó trong Job thất bại** (ở đây là API tests fail 10 assertions của SUT)

**Giải pháp** sửa ci.yml: "Khi bạn dùng actions/cache/save@v4 như một step thông thường (thay vì phụ thuộc vào Post hook ngầm), bạn có toàn quyền gắn if: ${{ !cancelled() }} — giống hệt cách file ci.yml gốc đang làm rất thành công với bước Upload coverage and test report!"


---

## Mô tả lại vấn đề ở task C03

Dưới đây là bản tổng hợp ngắn gọn, mang tính học thuật cao để bạn đưa vào **Báo cáo chi tiết (G-03)**, **AI Audit Report [AI-02]**, và **Reflective Statement [AI-04]**. Việc trình bày quá trình gỡ lỗi này sẽ chứng minh tư duy phản biện của nhóm thay vì chỉ copy-paste code.

### 1. Vấn đề (The Problem)

* Nhiệm vụ C-03 yêu cầu thiết lập bộ nhớ đệm (cache) cho npm và đo lường thời gian chênh lệch giữa hai lần chạy (cache miss và cache hit).


* Tuy nhiên, hệ thống EShop (SUT) đang chứa sẵn 10 lỗi nghiệp vụ (baseline errors), khiến bước kiểm thử API (`npm run test:api`) luôn trả về kết quả thất bại (exit code 1).
* Khi sử dụng tham số mặc định `cache: npm` của action `actions/setup-node@v4`, GitHub Actions sẽ tạo một bước ẩn có tên `Post Set up Node.js` ở cuối Job để lưu cache.
* Theo thiết kế của GitHub Actions, các bước `Post` sẽ tự động bị bỏ qua (skipped) nếu có bất kỳ bước nào trước đó trong Job bị lỗi. Hậu quả là dù đã cấu hình đúng, cache vẫn không bao giờ được lưu lên server, dẫn đến việc mọi lần chạy đều báo "Cache not found".

### 2. Giải pháp 1 và Vấn đề không giải quyết được (AI Hallucination / Deprecated Feature)

* **Ý tưởng:** Loại bỏ tính năng cache mặc định của `setup-node`, chuyển sang dùng action chuyên dụng `actions/cache@v4` với tham số `save-always: true` do AI đề xuất để ép hệ thống lưu cache bất chấp trạng thái Job.
* **Vấn đề gặp phải:** Tham số `save-always` đã bị GitHub đưa vào danh sách lỗi thời (deprecated) với cảnh báo: *"save-always does not work as intended and will be removed in a future release"*.
* **Nguyên nhân gốc rễ:** Bước lưu cache vẫn được thực thi dưới dạng một hook `Post Cache npm dependencies` ở cuối Job. Khi bước `API tests` thất bại, hook này vẫn bị hệ thống tự động bỏ qua. Giải pháp này chứng tỏ AI đã đề xuất một tham số không còn hoạt động trên thực tế, cung cấp một "Artifact Vàng" với trạng thái INVALID để nhóm đưa vào báo cáo AI Audit Report.



### 3. Giải pháp 2 (Giải pháp triệt để - Decoupled Cache)

* **Ý tưởng:** Tách rời hoàn toàn quá trình phục hồi (restore) và lưu (save) bộ nhớ đệm thành hai bước độc lập, không sử dụng cơ chế `Post` hook ở cuối Job nữa.
* **Cách triển khai:**
* Đặt bước `actions/cache/restore@v4` trước lệnh `npm ci` để tải cache cũ (nếu có).
* Đặt bước `actions/cache/save@v4` **ngay lập tức sau lệnh `npm ci**`, với điều kiện kiểm tra `if: ${{ !cancelled() && steps.npm-cache.outputs.cache-hit != 'true' }}`.


* **Tại sao giải pháp này thành công 100%:** Ngay khi `npm ci` tải xong các thư viện, luồng CI vẫn đang ở trạng thái thành công (màu xanh). Bước `Save` sẽ được kích hoạt và đẩy cache lên server ngay lập tức. Những thất bại ở bước `API tests` xảy ra sau đó không còn ảnh hưởng đến việc lưu cache, giúp nhóm hoàn thành trọn vẹn yêu cầu đo lường của Task C-03.


## C04

