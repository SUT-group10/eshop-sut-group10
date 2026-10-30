# Context dự án EShop và CI/CD

## 1. Tổng quan

Repository `eshop-sut-group10` là một monorepo cho hệ thống thương mại điện tử EShop, được dùng trong seminar T07 về software testing, test harness và CI/CD. Hệ thống có bốn phân hệ:

- **Backend API:** Node.js, Express, SQLite, JWT; URL mặc định `http://localhost:3000`.
- **Frontend web khách hàng:** React, Vite, Tailwind CSS; URL mặc định `http://localhost:5173`.
- **Frontend web quản trị:** React, Vite, Tailwind CSS; URL mặc định `http://localhost:5174`.
- **Mobile app:** React Native và Expo; kết nối tới backend qua địa chỉ LAN của máy chạy server.

`README.md` mô tả yêu cầu nghiệp vụ đúng để thiết kế expected result. `api_specification.md` mô tả endpoint, request và response của backend. Khi test phát hiện SUT không đúng đặc tả, phải giữ assertion và exit code thật; không đổi expected, skip test hoặc dùng lệnh giả để làm pipeline xanh.

Phạm vi Task C hiện tập trung vào **backend CI trên GitHub Actions**. Workflow chưa chạy lint/build/test cho web, admin hoặc mobile. Frontend vẫn có package manifest và lệnh `lint`/`build` riêng để chạy khi cần.

## 2. Cấu trúc repository

```text
eshop-sut-group10/
├── .github/
│   └── workflows/
│       └── ci.yml                         # GitHub Actions: Backend CI
├── README.md                              # SRS, expected business behavior
├── api_specification.md                   # Backend endpoint contract
├── setup_guide.md                         # Cài đặt, chạy server và kiểm chứng local
├── run_servers.sh                         # Tiện ích chạy các server; phụ thuộc môi trường tác giả
├── backend/
│   ├── package.json                       # npm scripts, dependency và quality gates
│   ├── package-lock.json                  # Lockfile; đầu vào cho npm ci và npm cache
│   ├── server.js                          # Express app, route, middleware JWT, nghiệp vụ API
│   ├── database.js                        # SQLite schema, seed data và database access
│   ├── test_profile.js                    # Script gọi thử API; không phải test tự động
│   ├── eslint.config.cjs                  # Cấu hình ESLint cho backend và Jest
│   ├── jest.config.cjs                    # Jest environment, test match và coverage
│   ├── scripts/
│   │   ├── check-syntax.cjs               # Build backend bằng node --check
│   │   └── verify-isolation.cjs           # Diagnostic về isolation, order và DB hash
│   ├── tests/
│   │   ├── README.md                      # Cách chạy, mapping test và baseline
│   │   ├── unit/
│   │   │   └── authentication.test.js     # Unit test middleware JWT, không dùng DB thật
│   │   ├── api/
│   │   │   ├── catalog-auth.test.js       # Catalog, login, profile và access control
│   │   │   ├── coupons.test.js             # Coupon, biên và công thức giảm giá
│   │   │   └── cart-orders.test.js         # Cart, checkout và order state
│   │   ├── smoke/
│   │   │   └── purchase.test.js            # Luồng mua hàng nhiều bước qua API
│   │   ├── harness/
│   │   │   └── isolation.test.js           # Kiểm tra cô lập fixture/database/cart
│   │   └── helpers/
│   │       └── harness.js                  # App/SQLite :memory:, seed và cleanup
│   ├── coverage/                           # Output tự sinh, bị Git ignore
│   │   ├── cobertura-coverage.xml          # Coverage XML khi chạy test:ci
│   │   └── coverage-summary.json           # Coverage JSON máy đọc được
│   └── test-results/
│       └── jest-report.json                # Jest JSON report do workflow sinh
├── frontend-web/
│   ├── package.json                        # Vite scripts: dev, build, lint, preview
│   ├── vite.config.js / eslint.config.js   # Build và lint config
│   ├── tailwind.config.js / postcss.config.js
│   ├── index.html                          # Web HTML entry point
│   └── src/                                # App, pages, context, styles và assets
├── frontend-admin/
│   ├── package.json                        # Vite scripts: dev, build, lint, preview
│   ├── vite.config.js / eslint.config.js   # Build và lint config
│   ├── tailwind.config.js / postcss.config.js
│   ├── index.html                          # Admin HTML entry point
│   └── src/                                # Admin App, styles và assets
├── frontend-mobile/
│   ├── package.json                        # Expo start/android/ios/web scripts
│   ├── app.json                            # Expo application config
│   ├── index.js                            # Mobile entry point
│   └── assets/                             # Mobile assets
└── docs/
		├── architecture/
		│   ├── test-harness.md                 # Kiến trúc harness, gate và giới hạn
		│   └── assets/                         # PNG/SVG sơ đồ harness
		├── evidence/
		│   ├── B-01/                           # Log setup và inventory
		│   ├── B-02/                           # Log unit/API/smoke baseline
		│   ├── B-03/                           # Log isolation và cleanup
		│   ├── B-04/                           # Clone sạch và coverage XML
		│   └── Task-C/                         # Evidence GitHub Actions C-01 đến C-07
		├── requirements/
		│   ├── stage1_requirement.md           # Yêu cầu giai đoạn đầu
		│   └── T07_CI-CD_and_Test-Harness_Engineering.docx.md
		├── tasks/
		│   └── checklist.md                    # Checklist A-H, đặc biệt B và C
		├── proposal/
		│   └── Tool_Survey_Proposal.md         # Phạm vi công cụ CI/CD và AI
		└── weekly_report/                      # Nhật ký tiến độ và chatlog theo tuần
```

`coverage/`, `test-results/` và `node_modules/` là thư mục sinh trong lúc chạy, không phải source cần commit. Cây trên liệt kê các file quan trọng cho việc hiểu dự án và CI; các file component/assets còn lại nằm trong `src/` và không phải entry point của Task C.

## 3. Backend và test harness

Backend là CommonJS chạy trực tiếp, không có transpile hoặc bundle. Vì vậy `npm run build` thực chất chạy `scripts/check-syntax.cjs`, dùng `node --check` cho các file `.js` và `.cjs`; nó không chứng minh nghiệp vụ đúng.

`server.js` export Express `app` và middleware `authenticateToken` khi được import, nhưng chỉ mở port 3000 khi chạy trực tiếp. API/smoke test dùng Supertest với route Express thật. `database.js` tạo schema và seed SQLite thật. Helper `tests/helpers/harness.js` chuyển database sang SQLite `:memory:` trong Jest, tạo app/database riêng cho mỗi test, chờ seed sẵn sàng rồi cleanup ở teardown. Unit test mock database vì chỉ kiểm tra middleware JWT.

Các npm script backend là:

| Script | Mục đích |
|---|---|
| `npm run lint` | ESLint với `--max-warnings=0` |
| `npm run build` | Kiểm tra syntax toàn bộ source backend |
| `npm run test:unit` | Chạy `tests/unit` |
| `npm run test:api` | Chạy `tests/api` |
| `npm run test:smoke` | Chạy `tests/smoke` |
| `npm run test:harness` | Chạy test cô lập trong `tests/harness` |
| `npm run test:isolation` | Chạy diagnostic nhiều seed và kiểm tra database gốc |
| `npm run test:coverage` | Full Jest suite với coverage |
| `npm run test:ci` | Jest CI, tuần tự, coverage; giữ exit code thật |

`jest.config.cjs` thu coverage từ `server.js` và `database.js`, tạo Cobertura XML và JSON summary. `verify-isolation.cjs` là diagnostic, không thay thế quality gate: nó kiểm tra tính ổn định, không có open handle, đúng baseline failure và database production không đổi.

## 4. GitHub Actions workflow

File điều khiển CI là [`.github/workflows/ci.yml`](../eshop-sut-group10/.github/workflows/ci.yml). Workflow có tên `Backend CI`, job có tên `Backend quality gates`, và đặt `working-directory` mặc định là `backend`.

Trigger:

- `push` vào `main`.
- `pull_request` hướng vào `main`.

Môi trường và tính tái lập:

- Runner cố định `ubuntu-22.04`.
- Node cố định `22.14.0`; log runtime ghi cả Node, npm, commit SHA và runner OS.
- Dependency cài bằng `npm ci`.
- npm cache dùng `backend/package-lock.json` làm cache dependency path.
- `npm_config_build_from_source: "true"` hỗ trợ native binding `sqlite3` build trên runner.
- Concurrency theo workflow/ref và hủy run cũ cùng nhóm khi có run mới.
- Permission chỉ `contents: read`.
- Job timeout là 15 phút.

Quality gate chạy theo thứ tự:

```text
npm ci
	-> npm run lint
	-> npm run build
	-> npm run test:unit
	-> npm run test:api
	-> npm run test:smoke
```

Không có `continue-on-error`, `|| true`, skip test hoặc thay `test:isolation` cho test nghiệp vụ. Vì các step giữ exit code thật, API fail sẽ làm smoke bị dừng/bỏ qua theo hành vi của GitHub Actions.

Sau các test, khi run chưa bị cancel, workflow chạy `npm run test:ci -- --json --outputFile=test-results/jest-report.json` để sinh report coverage và Jest JSON. Bước upload cũng chỉ bỏ qua khi run bị cancel, upload:

- `backend/coverage/cobertura-coverage.xml`;
- `backend/coverage/coverage-summary.json`;
- `backend/test-results/jest-report.json`.

Artifact có tên `backend-ci-reports-<run_id>`, `if-no-files-found: error` và retention 14 ngày. Upload report không biến test fail thành pass.

## 5. Baseline và cách đọc kết quả

Baseline được ghi nhận trong `backend/tests/README.md` và runbook Task C. Backend hiện có các lỗi nghiệp vụ đã biết ở authentication counter, admin access, coupon, cart, checkout và order state. Expected của test lấy từ `README.md`/`api_specification.md`, không lấy từ implementation hiện tại.

Có hai cách đếm cần phân biệt:

- Các job CI chính gọi unit + API + smoke: 5 unit, 30 API và 1 smoke, tổng 36 test.
- Full `npm test` có thêm 3 harness test: tổng 39 test; baseline ghi nhận 29 pass và 10 fail.

Vì vậy một run API đỏ có thể là kết quả đúng của quality gate khi SUT còn 10 assertion lỗi; không được gọi là run xanh và không được sửa assertion để đạt C-02. C-02 chỉ thật sự đạt theo runbook khi lỗi đã được sửa và xác minh lại, hoặc có quyết định quality gate bằng văn bản của GVTH.

`test:isolation` có thể exit 0 dù full suite vẫn có 10 lỗi, vì nó chỉ xác nhận các lỗi đó ổn định và test được cô lập. Đây là chẩn đoán harness, không phải bằng chứng nghiệp vụ pass.

## 6. Checklist làm Task C trên GitHub

1. Push workflow lên GitHub và tạo run đầu tiên; lưu URL, event, branch, SHA, runner, Node/npm và step fail đầu tiên.
2. Tải artifact từ run, kiểm tra Cobertura XML, coverage summary và Jest JSON nếu job đã chạy đến bước report.
3. Tạo một run đỏ có chủ đích từ commit xanh bằng một assertion sai; không merge branch thử nghiệm, sau đó đóng PR hoặc revert.
4. Cấu hình branch protection/ruleset cho `main`: PR bắt buộc, required check chính xác là `Backend quality gates`, review và chính sách cấm force push/delete nếu nhóm yêu cầu.
5. Tạo PR pass và PR fail để chứng minh status check cho phép/chặn merge đúng cách.
6. Đo cache miss và cache hit trong cùng điều kiện: cùng lockfile, Node, OS và cache key; ghi `npm ci` duration và total job duration.
7. Kiểm tra clone sạch: không dựa vào `node_modules`, coverage, database hoặc biến môi trường cá nhân. Giữ secret, JWT, cookie và dữ liệu cá nhân ngoài log/evidence.
8. Không thêm coverage badge tĩnh. Chỉ thêm badge khi nguồn dữ liệu lấy từ report thật của cùng run; nếu không có endpoint đáng tin cậy thì ghi rõ chưa triển khai.

## 7. Tài liệu và bằng chứng nên dùng

- `docs/tasks/checklist.md`: tiêu chí C-01 đến C-07 và quan hệ với B-01 đến B-05, D/E/F/G/H.
- `Personal/T07-Prompt#1-task-C/Check/github-actions-runbook.md`: quy trình thao tác GitHub, cache, artifact, branch protection và mẫu evidence.
- `docs/evidence/Task-C/Task-C01-02-evidence.md`: mô tả implementation/evidence hiện có cho Task C; cần đối chiếu lại URL và trạng thái thực tế trên GitHub.
- `docs/architecture/test-harness.md`: ranh giới giữa test harness, quality gate, report và CI.
- `backend/tests/README.md`: lệnh chạy, mapping test ID, fixture, cleanup, expected result và baseline.
- `docs/evidence/B-04/clean-clone.log`: bằng chứng clone sạch, lint/build/coverage và trạng thái test tại lần ghi log.

## 8. Giới hạn và lưu ý

- Workflow hiện tại là backend-only; frontend/mobile không tự động được gate bởi `.github/workflows/ci.yml`.
- Backend `build` chỉ là syntax check, không tạo `dist` và không khởi động server.
- `test_profile.js` gọi API và có thể in JWT; không đưa output của file này vào artifact công khai. File cũng không thuộc bộ test Jest.
- `run_servers.sh` có giả định môi trường máy tác giả; không dùng nó làm bước CI.
- Coverage đo mức thực thi `server.js`/`database.js`, không phải tỷ lệ yêu cầu nghiệp vụ đúng.
- Artifact tồn tại không đồng nghĩa test pass; cần đọc exit code và log của từng step.
- Không ghi secret/token/cookie vào screenshot, log, PR comment hoặc evidence.
