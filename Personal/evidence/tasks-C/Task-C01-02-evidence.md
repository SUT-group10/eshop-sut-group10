# Task C Evidence — GitHub Actions (C-01 to C-07)

## 1. Phạm vi báo cáo

Báo cáo này ghi nhận bằng chứng cho toàn bộ Task C-01 đến C-07 của hệ thống GitHub Actions cho backend EShop.

Phạm vi thực hiện:

- Chạy workflow trên Pull Request vào `main` và push vào `main`.
- Cố định runner `ubuntu-22.04` và Node.js `22.14.0`.
- Cài dependency bằng `npm ci`.
- Chạy quality gate theo thứ tự `lint -> build -> unit -> API -> smoke`.
- Giữ nguyên exit code thật của test; không skip, sửa expected hoặc dùng `continue-on-error` để che lỗi.
- Đo npm cache miss/hit và thời lượng tương ứng.
- Sinh, kiểm tra và upload coverage/test report khi runner chưa bị cancel.
- Cấu hình branch protection và kiểm tra PR pass/fail.
- Kiểm tra khả năng tái lập từ clone sạch.

Repository: EShop SUT Group 10  
Workflow: `Backend CI`  
Job: `Backend quality gates`  
Workflow source: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)

> **Lưu ý về trạng thái baseline:** Ứng dụng EShop được thiết kế có chủ đích với một số lỗi nghiệp vụ. Nhóm đóng vai tester và test harness engineer, không tự ý sửa SUT hoặc sửa assertion chỉ để tạo run xanh. Các lỗi API được ghi nhận là kết quả kiểm thử của SUT.

---

## 2. C-01 — Workflow cơ bản

### 2.1. Tiêu chí

C-01 yêu cầu workflow:

- chạy khi có Pull Request vào `main`;
- chạy khi có push vào `main`;
- cố định phiên bản Node.js;
- cài dependency bằng `npm ci`;
- có URL run để truy xuất lại bằng chứng.

### 2.2. Implementation

Workflow hiện tại khai báo:

```yaml
on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main
```

Môi trường CI:

```yaml
runs-on: ubuntu-22.04
node-version: 22.14.0
```

Cài dependency:

```yaml
run: npm ci
```

Do dependency `sqlite3` có native binding, bước cài đặt bổ sung:

```yaml
env:
  npm_config_build_from_source: "true"
```

Việc này giúp native module được build trên chính runner `ubuntu-22.04`, tránh sử dụng binary không tương thích với phiên bản GLIBC của runner.

### 2.3. Evidence run

| Trường | Giá trị |
|---|---|
| Workflow run URL | `https://github.com/SUT-group10/eshop-sut-group10/pull/10` |
| Event | Pull Request vào `main` |
| Branch | `github-ci` |
| Commit SHA | `cf00005` |
| Runner OS | `ubuntu-22.04` |
| Node.js | `22.14.0` |
| npm | `10.9.2` |
| Kết quả tổng thể | Run được kích hoạt; quality gate phản ánh lỗi thật của pipeline |

### 2.4. Hình minh chứng

> **[PLACEHOLDER HÌNH C-01]**  
> Chèn ảnh GitHub Actions hiển thị workflow `Backend CI`, event Pull Request, branch `github-ci`, commit SHA và danh sách các step.

### 2.5. Kết luận C-01

Workflow đã được GitHub nhận diện và chạy trên Pull Request. Trigger, runner, Node.js version và lệnh `npm ci` được cấu hình trong source. URL run và ảnh chụp cần được bổ sung vào bảng evidence trước khi nộp báo cáo.

---

## 3. C-02 — Quality gates theo thứ tự

### 3.1. Tiêu chí

C-02 yêu cầu thêm và thể hiện rõ chuỗi:

```text
lint -> build -> unit/API/smoke
```

Mỗi bước phải giữ exit code thật để khi một bước thất bại, các bước sau phản ánh đúng trạng thái bị dừng hoặc bỏ qua.

### 3.2. Các script được sử dụng

Các script nằm trong `backend/package.json`:

| Step CI | Script |
|---|---|
| Lint | `npm run lint` |
| Build và syntax check | `npm run build` |
| Unit tests | `npm run test:unit` |
| API tests | `npm run test:api` |
| Smoke tests | `npm run test:smoke` |
| Coverage và Jest report | `npm run test:ci` |

Workflow không dùng lệnh giả để làm pipeline xanh.

### 3.3. Kết quả run đầu tiên

Kết quả quan sát được sau khi đồng bộ test harness và script từ nhánh `develop`:

| Step | Kết quả | Nhận xét |
|---|---|---|
| Install | Pass | `npm ci` hoàn tất |
| Lint | Pass | ESLint hoàn tất |
| Build and syntax check | Pass | Syntax check hoàn tất |
| Unit tests | Pass | Unit test hoàn tất |
| API tests | Fail | Ban đầu gặp lỗi native `sqlite3`/GLIBC; sau khi build từ source, test chạy và phát hiện lỗi nghiệp vụ của SUT |
| Smoke tests | Skipped | Bị dừng sau khi API test fail |
| Generate coverage and Jest report | Failed/đỏ | `test:ci` chạy lại suite và giữ exit code fail khi assertion API không đạt |
| Upload report | `[BỔ SUNG KẾT QUẢ RUN]` | Kiểm tra artifact thực tế trên GitHub |

### 3.4. Phân biệt lỗi hạ tầng và lỗi SUT

Lỗi ban đầu:

```text
/lib/x86_64-linux-gnu/libm.so.6: version `GLIBC_2.38' not found
```

Đây là lỗi tương thích native binary của `sqlite3`, không phải lỗi assertion. Workflow đã được cập nhật để build native module từ source trên runner.

Sau khi xử lý lỗi này, API tests chạy được và tiếp tục phát hiện các lỗi nghiệp vụ đã ghi nhận trong test harness, ví dụ:

- sản phẩm trùng không được gộp trong giỏ hàng;
- checkout tin tổng tiền do client gửi;
- giỏ hàng không bị xóa sau checkout;
- user thường truy cập được admin API;
- coupon có lỗi ở điều kiện biên và công thức;
- trạng thái đơn hàng có thể bị chuyển trái với đặc tả.

Các test assertion và expected result không được sửa chỉ để làm pipeline xanh.

### 3.5. Hình minh chứng

> **![alt text](C02-pass-failed-run.png)**  
> Ảnh GitHub Actions hiển thị thứ tự step: Lint pass, Build pass, Unit pass, API fail, Smoke skipped và Coverage/report fail hoặc được tạo với trạng thái test fail.

### 3.6. Trạng thái hoàn thành C-02

**Implementation:** Đã triển khai chuỗi quality gate trong workflow.  
**Evidence hiện có:** Có run thể hiện step fail và nguyên nhân được chẩn đoán.  
**Run xanh:** Chưa có do baseline SUT có lỗi nghiệp vụ đã biết.  
**Run đỏ có chủ đích:** Chưa tạo từ một commit xanh.

---

## 4. C-03 — npm cache và đo thời lượng

### 4.1. Tiêu chí

C-03 yêu cầu đo hai run trong cùng điều kiện: một run cache miss và một run cache hit. Lockfile, Node.js version, runner OS và cache key phải được giữ nguyên.

Cache chỉ chứng minh tối ưu hóa bước cài dependency; cache hit không chứng minh test pass.

### 4.2. Cấu hình hiện tại

Workflow dùng cache npm của `actions/setup-node` với:

```yaml
cache: npm
cache-dependency-path: backend/package-lock.json
```

### 4.3. Evidence cần điền

| Trường | Cache miss | Cache hit |
|---|---|---|
| Run URL | `[BỔ SUNG URL]` | `[BỔ SUNG URL]` |
| Event/branch | `[BỔ SUNG]` | `[BỔ SUNG]` |
| Commit SHA | `[BỔ SUNG]` | `[BỔ SUNG]` |
| Cache key | `[BỔ SUNG]` | `[BỔ SUNG]` |
| Cache result | `miss` | `hit` |
| `npm ci` duration | `[BỔ SUNG]` | `[BỔ SUNG]` |
| Total job duration | `[BỔ SUNG]` | `[BỔ SUNG]` |
| Lockfile changed? | `No` | `No` |

### 4.4. Hình minh chứng

> **[PLACEHOLDER HÌNH C-03]**  
> Chèn ảnh log `actions/setup-node` thể hiện cache miss/hit và thời lượng `npm ci` của hai run.

### 4.5. Trạng thái C-03

**Implementation:** Đã bật npm cache trong workflow.  
**Evidence đo lường:** Chưa bổ sung URL, cache key và thời lượng thực tế.

---

## 5. C-04 — Coverage và artifact

### 5.1. Tiêu chí

C-04 yêu cầu sinh coverage XML, Jest JSON report và upload các report dưới dạng artifact. Artifact cần được giữ lại khi test fail nếu runner chưa bị cancel.

### 5.2. Cấu hình hiện tại

Workflow gọi:

```text
npm run test:ci -- --json --outputFile=test-results/jest-report.json
```

Artifact được đặt tên theo run:

```text
backend-ci-reports-<run_id>
```

Các đường dẫn cần kiểm tra:

```text
backend/coverage/cobertura-coverage.xml
backend/coverage/coverage-summary.json
backend/test-results/jest-report.json
```

### 5.3. Evidence cần điền

| Trường | Giá trị |
|---|---|
| Run URL | `[BỔ SUNG URL C-04]` |
| Artifact name | `[BỔ SUNG TÊN ARTIFACT]` |
| Artifact URL | `[BỔ SUNG URL ARTIFACT]` |
| Run status | `[BỔ SUNG]` |
| Coverage XML tồn tại | `[Có/Không]` |
| Coverage summary tồn tại | `[Có/Không]` |
| Jest JSON report tồn tại | `[Có/Không]` |
| Artifact tải được sau test fail | `[Có/Không]` |
| Coverage source/value | `[BỔ SUNG TỪ REPORT THẬT]` |

### 5.4. Hình minh chứng

> **[PLACEHOLDER HÌNH C-04]**  
> Chèn ảnh trang Artifacts và danh sách ba file report đã tải xuống.

### 5.5. Trạng thái C-04

**Implementation:** Đã có bước generate và upload trong workflow.  
**Evidence:** Cần kiểm tra artifact thực tế trên run GitHub, đặc biệt với run API fail. Upload thành công không làm test đỏ thành test xanh.

---

## 6. C-05 — Branch protection và status check

### 6.1. Tiêu chí

C-05 yêu cầu áp dụng branch protection/ruleset cho `main`, yêu cầu Pull Request và yêu cầu status check `Backend quality gates` pass trước khi merge.

### 6.2. Cấu hình cần kiểm tra

- Pull Request bắt buộc trước khi merge.
- Required status check: `Backend quality gates`.
- Review bắt buộc theo chính sách nhóm.
- Không force push/delete `main` theo chính sách nhóm.
- Không chọn một check phụ hoặc check không tồn tại làm required check.

### 6.3. Evidence cần điền

| Trường | PR pass | PR fail |
|---|---|---|
| PR URL | `[BỔ SUNG URL]` | `[BỔ SUNG URL]` |
| Workflow run URL | `[BỔ SUNG URL]` | `[BỔ SUNG URL]` |
| Commit SHA | `[BỔ SUNG]` | `[BỔ SUNG]` |
| Check result | `pass` | `fail` |
| Merge allowed/blocked | `[BỔ SUNG]` | `[BỔ SUNG]` |
| Artifact/log URL | `[BỔ SUNG]` | `[BỔ SUNG]` |

Settings/ruleset URL: `[BỔ SUNG URL SETTINGS]`

### 6.4. Hình minh chứng

> **[PLACEHOLDER HÌNH C-05]**  
> Chèn ảnh ruleset/branch protection và ảnh PR fail bị chặn merge. Không chụp secret hoặc thông tin cá nhân.

### 6.5. Trạng thái C-05

**Implementation:** Chưa có evidence branch protection trong repository.  
**Cần thực hiện trên GitHub:** Cấu hình ruleset cho `main` và kiểm tra cả PR pass lẫn PR fail. Nếu baseline SUT đỏ được giảng viên chấp thuận, phải ghi quyết định đó cùng evidence.

---

## 7. C-06 — Coverage badge

### 7.1. Tiêu chí

Chỉ tạo coverage badge nếu có endpoint đáng tin cậy lấy số liệu từ report thật của cùng run hoặc dịch vụ được nhóm phê duyệt. Không dùng số coverage hard-code.

### 7.2. Trạng thái hiện tại

Chưa triển khai badge tĩnh. Đây là lựa chọn phù hợp khi repository chưa có endpoint coverage được xác nhận.

Kết luận tạm thời: **Không triển khai coverage badge.** Coverage vẫn được lưu trong `coverage/cobertura-coverage.xml` và `coverage/coverage-summary.json` khi report được sinh thành công.

### 7.3. Evidence cần điền nếu triển khai sau

| Trường | Giá trị |
|---|---|
| Badge URL | `[BỔ SUNG NẾU CÓ]` |
| Report endpoint | `[BỔ SUNG NẾU CÓ]` |
| Run/report source | `[BỔ SUNG]` |
| Giá trị badge | `[BỔ SUNG]` |
| Giá trị trong report thật | `[BỔ SUNG]` |
| Đối chiếu khớp? | `[Có/Không]` |

### 7.4. Hình minh chứng

> **[PLACEHOLDER HÌNH C-06 - TÙY CHỌN]**  
> Chỉ chèn ảnh badge và nguồn report nếu nhóm được phê duyệt triển khai. Nếu không triển khai, chèn ảnh report thật hoặc ghi rõ `Not implemented — no trusted endpoint`.

### 7.5. Trạng thái C-06

**Status:** Không triển khai do chưa có endpoint đáng tin cậy. Không dùng badge hard-code để thay thế evidence.

---

## 8. C-07 — Kiểm tra từ clone sạch

### 8.1. Tiêu chí

C-07 yêu cầu kiểm tra pipeline từ clone sạch, không dựa vào `node_modules`, coverage, database hoặc biến môi trường cá nhân có sẵn.

### 8.2. Protocol

```bash
git clone <repository-url> clean-clone
cd clean-clone/backend
node --version
npm --version
npm ci
npm run lint
npm run build
npm run test:unit
npm run test:api
npm run test:smoke
npm run test:ci -- --json --outputFile=test-results/jest-report.json
```

### 8.3. Evidence cần điền

| Trường | Giá trị |
|---|---|
| Clone URL/commit | `[BỔ SUNG]` |
| Clone date and UTC | `[BỔ SUNG]` |
| Node/npm | `[BỔ SUNG]` |
| Pre-existing `node_modules` | `No` |
| Pre-existing coverage | `No` |
| `npm ci` | `[Pass/Fail]` |
| Lint/build | `[Pass/Fail]` |
| Unit | `[Pass/Fail]` |
| API | `[Pass/Fail — ghi rõ SUT baseline nếu có]` |
| Smoke | `[Pass/Fail/Skipped]` |
| Database production changed? | `[No/ghi chú]` |
| Raw log | `[BỔ SUNG LINK FILE/URL]` |

### 8.4. Hình minh chứng

> **[PLACEHOLDER HÌNH C-07]**  
> Chèn ảnh terminal/CI log cho thấy clone sạch, `npm ci`, các lệnh quality gate và trạng thái database/report.

### 8.5. Trạng thái C-07

Đã có bằng chứng local trong [B-04 clean clone verification](../B-04/clean-clone.log). Cần bổ sung commit/URL và ghi rõ kết quả API đỏ là expected baseline của SUT nếu nhóm không có quyền sửa backend.

---

## 9. Tài liệu và source liên quan

- [Workflow Backend CI](../../.github/workflows/ci.yml)
- [Backend package scripts](../../backend/package.json)
- [Test harness guide](../../backend/tests/README.md)
- [B-02 test run](../B-02/test-run.log)
- [B-04 clean clone verification](../B-04/clean-clone.log)
- [B-04 coverage XML](../B-04/cobertura-coverage.xml)
- [Checklist Task C](../../tasks/checklist.md)

## 10. Checklist evidence cần bổ sung

- [ ] URL run C-01.
- [ ] URL run C-02.
- [ ] Commit SHA của từng run.
- [ ] Ảnh minh chứng C-01.
- [ ] Ảnh minh chứng C-02.
- [ ] Kết quả artifact upload.
- [ ] Evidence cache miss/hit và thời lượng C-03.
- [ ] Evidence branch protection, PR pass và PR fail của C-05.
- [ ] Kết luận C-06: badge được triển khai và đối chiếu, hoặc ghi rõ không triển khai.
- [ ] Evidence clone sạch và commit của C-07.
- [ ] Kết luận/review của thành viên review.
- [ ] Quyết định của giảng viên nếu baseline API đỏ được chấp thuận.
