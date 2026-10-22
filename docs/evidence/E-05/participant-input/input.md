# Bộ dữ liệu phân tích test giỏ hàng

Có 10 lượt chạy độc lập của cùng một API test trên cùng revision-01. Mỗi lượt dùng fixture/database riêng. Test kiểm tra giỏ hàng chứa sản phẩm vừa thêm, quantity bằng 1. Log chứa quan sát thao tác thêm và đọc giỏ; các mốc *Ms là mili giây tương đối từ lúc hai thao tác bắt đầu, không phải thời gian toàn job.

Môi trường chung: Node v24.14.0, npm 11.9.0, Ubuntu 22.04 image 20261018.327.1, runner 2.338.0. Không sửa mã giữa các lượt. Lịch sử thực thi và retry nằm trong history.json.

Đây là bản dữ liệu đã chuẩn hóa: tên test, đường dẫn, lệnh và mã định danh được thay bằng bí danh; bỏ nhãn thiết kế và tham số điều khiển mô phỏng. Giữ thời gian quan sát, thứ tự log, HTTP status, dữ liệu giỏ hàng, assertion, stack frame với số dòng, kết quả và retry. Tên/lệnh trong bản này chỉ là bí danh, không phải hướng dẫn chạy.

Đọc input.md (console có số dòng), history.json và results.json của cả 10 lượt. Không cần mở repo hoặc tra cứu nguồn bên ngoài gói dữ liệu này. Phân biệt bằng chứng trong log với suy đoán; có thể kết luận chưa đủ dữ liệu.

## Lịch sử chạy

```json
[
  {
    "run": "run-01",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:10:57Z",
    "test_status": "failed",
    "test_duration_ms": 339,
    "test_exit_code": 1,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-02",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:17:24Z",
    "test_status": "passed",
    "test_duration_ms": 214,
    "test_exit_code": 0,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-03",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:20:02Z",
    "test_status": "failed",
    "test_duration_ms": 353,
    "test_exit_code": 1,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-04",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:21:54Z",
    "test_status": "passed",
    "test_duration_ms": 319,
    "test_exit_code": 0,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-05",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:24:12Z",
    "test_status": "failed",
    "test_duration_ms": 298,
    "test_exit_code": 1,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-06",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:25:45Z",
    "test_status": "passed",
    "test_duration_ms": 298,
    "test_exit_code": 0,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-07",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:27:43Z",
    "test_status": "failed",
    "test_duration_ms": 362,
    "test_exit_code": 1,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-08",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:29:24Z",
    "test_status": "passed",
    "test_duration_ms": 312,
    "test_exit_code": 0,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-09",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:49:41Z",
    "test_status": "passed",
    "test_duration_ms": 311,
    "test_exit_code": 0,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  },
  {
    "run": "run-10",
    "revision": "revision-01",
    "run_attempt": 1,
    "started_at_utc": "2026-10-21T15:52:07Z",
    "test_status": "failed",
    "test_duration_ms": 302,
    "test_exit_code": 1,
    "jest_invocations": 1,
    "test_retry_count": 0,
    "retry_messages": [],
    "retry_reasons": []
  }
]
```

## run-01

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Cart observation {"readSentMs":100.61,"readCompletedMs":105.484,"httpStatus":200,"cart":[]}
L017
L018       at Object.info (tests/api/cart.test.js:47:13)
L019
L020   console.info
L021     Add completed {"readSentMs":100.61,"readCompletedMs":105.484,"addSentMs":161.179,"addCompletedMs":164.156,"httpStatus":200}
L022
L023       at info (tests/api/cart.test.js:37:15)
L024
L025 FAIL tests/api/cart.test.js
L026   ✕ Cart contains the added product (339 ms)
L027
L028   ● Cart contains the added product
L029
L030     expect(received).toHaveLength(expected)
L031
L032     Expected length: 1
L033     Received length: 0
L034     Received array:  []
L035
L036     [0m [90m 51 |[39m     }))[33m;[39m
L037      [90m 52 |[39m     expect(cart[33m.[39mstatus)[33m.[39mtoBe([35m200[39m)[33m;[39m
L038     [31m[1m>[22m[39m[90m 53 |[39m     expect(cart[33m.[39mbody)[33m.[39mtoHaveLength([35m1[39m)[33m;[39m
L039      [90m    |[39m                       [31m[1m^[22m[39m
L040      [90m 54 |[39m     expect(cart[33m.[39mbody[[35m0[39m])[33m.[39mtoMatchObject({ id[33m:[39m product[33m.[39mid[33m,[39m quantity[33m:[39m [35m1[39m })[33m;[39m
L041      [90m 55 |[39m   } [36mfinally[39m {
L042      [90m 56 |[39m     [90m// Even a failed assertion must drain A before closing its isolated fixture.[39m[0m
L043
L044       at Object.toHaveLength (tests/api/cart.test.js:53:23)
L045
L046 Test Suites: 1 failed, 1 total
L047 Tests:       1 failed, 1 total
L048 Snapshots:   0 total
L049 Time:        0.724 s
L050 Ran all test suites.
L051 Test results written to: test-results/case/results.json
```

## run-02

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Add completed {"addSentMs":60.359,"addCompletedMs":64.486,"httpStatus":200}
L017
L018       at info (tests/api/cart.test.js:37:15)
L019
L020   console.info
L021     Cart observation {"addSentMs":60.359,"addCompletedMs":64.486,"readSentMs":100.395,"readCompletedMs":102.889,"httpStatus":200,"cart":[{"id":1,"name":"iPhone 15 Pro Max","price":30000000,"description":"Điện thoại cao cấp của Apple","imageUrl":"https://placehold.co/300x300/png?text=iPhone+15","category_id":1,"quantity":1}]}
L022
L023       at Object.info (tests/api/cart.test.js:47:13)
L024
L025 PASS tests/api/cart.test.js
L026   ✓ Cart contains the added product (214 ms)
L027
L028 Test Suites: 1 passed, 1 total
L029 Tests:       1 passed, 1 total
L030 Snapshots:   0 total
L031 Time:        0.476 s
L032 Ran all test suites.
L033 Test results written to: test-results/case/results.json
```

## run-03

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Cart observation {"readSentMs":100.371,"readCompletedMs":105.837,"httpStatus":200,"cart":[]}
L017
L018       at Object.info (tests/api/cart.test.js:47:13)
L019
L020   console.info
L021     Add completed {"readSentMs":100.371,"readCompletedMs":105.837,"addSentMs":159.927,"addCompletedMs":162.624,"httpStatus":200}
L022
L023       at info (tests/api/cart.test.js:37:15)
L024
L025 FAIL tests/api/cart.test.js
L026   ✕ Cart contains the added product (353 ms)
L027
L028   ● Cart contains the added product
L029
L030     expect(received).toHaveLength(expected)
L031
L032     Expected length: 1
L033     Received length: 0
L034     Received array:  []
L035
L036     [0m [90m 51 |[39m     }))[33m;[39m
L037      [90m 52 |[39m     expect(cart[33m.[39mstatus)[33m.[39mtoBe([35m200[39m)[33m;[39m
L038     [31m[1m>[22m[39m[90m 53 |[39m     expect(cart[33m.[39mbody)[33m.[39mtoHaveLength([35m1[39m)[33m;[39m
L039      [90m    |[39m                       [31m[1m^[22m[39m
L040      [90m 54 |[39m     expect(cart[33m.[39mbody[[35m0[39m])[33m.[39mtoMatchObject({ id[33m:[39m product[33m.[39mid[33m,[39m quantity[33m:[39m [35m1[39m })[33m;[39m
L041      [90m 55 |[39m   } [36mfinally[39m {
L042      [90m 56 |[39m     [90m// Even a failed assertion must drain A before closing its isolated fixture.[39m[0m
L043
L044       at Object.toHaveLength (tests/api/cart.test.js:53:23)
L045
L046 Test Suites: 1 failed, 1 total
L047 Tests:       1 failed, 1 total
L048 Snapshots:   0 total
L049 Time:        0.802 s
L050 Ran all test suites.
L051 Test results written to: test-results/case/results.json
```

## run-04

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Add completed {"addSentMs":60.476,"addCompletedMs":66.618,"httpStatus":200}
L017
L018       at info (tests/api/cart.test.js:37:15)
L019
L020   console.info
L021     Cart observation {"addSentMs":60.476,"addCompletedMs":66.618,"readSentMs":100.748,"readCompletedMs":104.083,"httpStatus":200,"cart":[{"id":1,"name":"iPhone 15 Pro Max","price":30000000,"description":"Điện thoại cao cấp của Apple","imageUrl":"https://placehold.co/300x300/png?text=iPhone+15","category_id":1,"quantity":1}]}
L022
L023       at Object.info (tests/api/cart.test.js:47:13)
L024
L025 PASS tests/api/cart.test.js
L026   ✓ Cart contains the added product (319 ms)
L027
L028 Test Suites: 1 passed, 1 total
L029 Tests:       1 passed, 1 total
L030 Snapshots:   0 total
L031 Time:        0.799 s
L032 Ran all test suites.
L033 Test results written to: test-results/case/results.json
```

## run-05

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Cart observation {"readSentMs":99.752,"readCompletedMs":103.829,"httpStatus":200,"cart":[]}
L017
L018       at Object.info (tests/api/cart.test.js:47:13)
L019
L020   console.info
L021     Add completed {"readSentMs":99.752,"readCompletedMs":103.829,"addSentMs":160.076,"addCompletedMs":162.817,"httpStatus":200}
L022
L023       at info (tests/api/cart.test.js:37:15)
L024
L025 FAIL tests/api/cart.test.js
L026   ✕ Cart contains the added product (298 ms)
L027
L028   ● Cart contains the added product
L029
L030     expect(received).toHaveLength(expected)
L031
L032     Expected length: 1
L033     Received length: 0
L034     Received array:  []
L035
L036     [0m [90m 51 |[39m     }))[33m;[39m
L037      [90m 52 |[39m     expect(cart[33m.[39mstatus)[33m.[39mtoBe([35m200[39m)[33m;[39m
L038     [31m[1m>[22m[39m[90m 53 |[39m     expect(cart[33m.[39mbody)[33m.[39mtoHaveLength([35m1[39m)[33m;[39m
L039      [90m    |[39m                       [31m[1m^[22m[39m
L040      [90m 54 |[39m     expect(cart[33m.[39mbody[[35m0[39m])[33m.[39mtoMatchObject({ id[33m:[39m product[33m.[39mid[33m,[39m quantity[33m:[39m [35m1[39m })[33m;[39m
L041      [90m 55 |[39m   } [36mfinally[39m {
L042      [90m 56 |[39m     [90m// Even a failed assertion must drain A before closing its isolated fixture.[39m[0m
L043
L044       at Object.toHaveLength (tests/api/cart.test.js:53:23)
L045
L046 Test Suites: 1 failed, 1 total
L047 Tests:       1 failed, 1 total
L048 Snapshots:   0 total
L049 Time:        0.56 s
L050 Ran all test suites.
L051 Test results written to: test-results/case/results.json
```

## run-06

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Add completed {"addSentMs":60.515,"addCompletedMs":66.321,"httpStatus":200}
L017
L018       at info (tests/api/cart.test.js:37:15)
L019
L020   console.info
L021     Cart observation {"addSentMs":60.515,"addCompletedMs":66.321,"readSentMs":100.361,"readCompletedMs":103.469,"httpStatus":200,"cart":[{"id":1,"name":"iPhone 15 Pro Max","price":30000000,"description":"Điện thoại cao cấp của Apple","imageUrl":"https://placehold.co/300x300/png?text=iPhone+15","category_id":1,"quantity":1}]}
L022
L023       at Object.info (tests/api/cart.test.js:47:13)
L024
L025 PASS tests/api/cart.test.js
L026   ✓ Cart contains the added product (298 ms)
L027
L028 Test Suites: 1 passed, 1 total
L029 Tests:       1 passed, 1 total
L030 Snapshots:   0 total
L031 Time:        0.747 s
L032 Ran all test suites.
L033 Test results written to: test-results/case/results.json
```

## run-07

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Cart observation {"readSentMs":100.521,"readCompletedMs":106.37,"httpStatus":200,"cart":[]}
L017
L018       at Object.info (tests/api/cart.test.js:47:13)
L019
L020   console.info
L021     Add completed {"readSentMs":100.521,"readCompletedMs":106.37,"addSentMs":159.552,"addCompletedMs":163.068,"httpStatus":200}
L022
L023       at info (tests/api/cart.test.js:37:15)
L024
L025 FAIL tests/api/cart.test.js
L026   ✕ Cart contains the added product (362 ms)
L027
L028   ● Cart contains the added product
L029
L030     expect(received).toHaveLength(expected)
L031
L032     Expected length: 1
L033     Received length: 0
L034     Received array:  []
L035
L036     [0m [90m 51 |[39m     }))[33m;[39m
L037      [90m 52 |[39m     expect(cart[33m.[39mstatus)[33m.[39mtoBe([35m200[39m)[33m;[39m
L038     [31m[1m>[22m[39m[90m 53 |[39m     expect(cart[33m.[39mbody)[33m.[39mtoHaveLength([35m1[39m)[33m;[39m
L039      [90m    |[39m                       [31m[1m^[22m[39m
L040      [90m 54 |[39m     expect(cart[33m.[39mbody[[35m0[39m])[33m.[39mtoMatchObject({ id[33m:[39m product[33m.[39mid[33m,[39m quantity[33m:[39m [35m1[39m })[33m;[39m
L041      [90m 55 |[39m   } [36mfinally[39m {
L042      [90m 56 |[39m     [90m// Even a failed assertion must drain A before closing its isolated fixture.[39m[0m
L043
L044       at Object.toHaveLength (tests/api/cart.test.js:53:23)
L045
L046 Test Suites: 1 failed, 1 total
L047 Tests:       1 failed, 1 total
L048 Snapshots:   0 total
L049 Time:        0.815 s
L050 Ran all test suites.
L051 Test results written to: test-results/case/results.json
```

## run-08

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Add completed {"addSentMs":60.336,"addCompletedMs":65.492,"httpStatus":200}
L017
L018       at info (tests/api/cart.test.js:37:15)
L019
L020   console.info
L021     Cart observation {"addSentMs":60.336,"addCompletedMs":65.492,"readSentMs":100.593,"readCompletedMs":103.131,"httpStatus":200,"cart":[{"id":1,"name":"iPhone 15 Pro Max","price":30000000,"description":"Điện thoại cao cấp của Apple","imageUrl":"https://placehold.co/300x300/png?text=iPhone+15","category_id":1,"quantity":1}]}
L022
L023       at Object.info (tests/api/cart.test.js:47:13)
L024
L025 PASS tests/api/cart.test.js
L026   ✓ Cart contains the added product (312 ms)
L027
L028 Test Suites: 1 passed, 1 total
L029 Tests:       1 passed, 1 total
L030 Snapshots:   0 total
L031 Time:        0.766 s
L032 Ran all test suites.
L033 Test results written to: test-results/case/results.json
```

## run-09

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Add completed {"addSentMs":60.604,"addCompletedMs":66.993,"httpStatus":200}
L017
L018       at info (tests/api/cart.test.js:37:15)
L019
L020   console.info
L021     Cart observation {"addSentMs":60.604,"addCompletedMs":66.993,"readSentMs":100.13,"readCompletedMs":103.392,"httpStatus":200,"cart":[{"id":1,"name":"iPhone 15 Pro Max","price":30000000,"description":"Điện thoại cao cấp của Apple","imageUrl":"https://placehold.co/300x300/png?text=iPhone+15","category_id":1,"quantity":1}]}
L022
L023       at Object.info (tests/api/cart.test.js:47:13)
L024
L025 PASS tests/api/cart.test.js
L026   ✓ Cart contains the added product (311 ms)
L027
L028 Test Suites: 1 passed, 1 total
L029 Tests:       1 passed, 1 total
L030 Snapshots:   0 total
L031 Time:        0.764 s
L032 Ran all test suites.
L033 Test results written to: test-results/case/results.json
```

## run-10

```text
L001
L002 > backend@1.0.0 test:case
L003 > jest --config jest.case.config.cjs --runInBand --json --outputFile=test-results/case/results.json
L004
L005   console.log
L006     Database initialized and seeded (Phase 2).
L007
L008       at Database.log (database.js:113:17)
L009
L010   console.log
L011     Connected to database
L012
L013       at Database.log (database.js:9:17)
L014
L015   console.info
L016     Cart observation {"readSentMs":100.525,"readCompletedMs":105.381,"httpStatus":200,"cart":[]}
L017
L018       at Object.info (tests/api/cart.test.js:47:13)
L019
L020   console.info
L021     Add completed {"readSentMs":100.525,"readCompletedMs":105.381,"addSentMs":160.184,"addCompletedMs":162.903,"httpStatus":200}
L022
L023       at info (tests/api/cart.test.js:37:15)
L024
L025 FAIL tests/api/cart.test.js
L026   ✕ Cart contains the added product (302 ms)
L027
L028   ● Cart contains the added product
L029
L030     expect(received).toHaveLength(expected)
L031
L032     Expected length: 1
L033     Received length: 0
L034     Received array:  []
L035
L036     [0m [90m 51 |[39m     }))[33m;[39m
L037      [90m 52 |[39m     expect(cart[33m.[39mstatus)[33m.[39mtoBe([35m200[39m)[33m;[39m
L038     [31m[1m>[22m[39m[90m 53 |[39m     expect(cart[33m.[39mbody)[33m.[39mtoHaveLength([35m1[39m)[33m;[39m
L039      [90m    |[39m                       [31m[1m^[22m[39m
L040      [90m 54 |[39m     expect(cart[33m.[39mbody[[35m0[39m])[33m.[39mtoMatchObject({ id[33m:[39m product[33m.[39mid[33m,[39m quantity[33m:[39m [35m1[39m })[33m;[39m
L041      [90m 55 |[39m   } [36mfinally[39m {
L042      [90m 56 |[39m     [90m// Even a failed assertion must drain A before closing its isolated fixture.[39m[0m
L043
L044       at Object.toHaveLength (tests/api/cart.test.js:53:23)
L045
L046 Test Suites: 1 failed, 1 total
L047 Tests:       1 failed, 1 total
L048 Snapshots:   0 total
L049 Time:        0.642 s
L050 Ran all test suites.
L051 Test results written to: test-results/case/results.json
```
