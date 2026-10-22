# F-01 — Flaky test: lý thuyết và minh họa trên EShop

Ngày biên soạn: 22/10/2026. Phạm vi: phần flaky test của F-01, dùng cho báo cáo, User Guide, slide và thuyết minh demo. Tài liệu này có giải thích nguyên nhân thí nghiệm; không đưa vào bộ dữ liệu phân tích độc lập E-04/E-08.

## 1. Flaky test là gì?

**Flaky test là test có thể cho cả kết quả PASS và FAIL khi chạy lại trên cùng phiên bản mã, dù không chủ động sửa test hoặc chức năng đang kiểm tra.** Google dùng việc xuất hiện cả pass và fail với cùng mã để mô tả kết quả flaky. Thất bại không ổn định làm giảm độ tin cậy của tín hiệu kiểm thử. [1]

“Cùng phiên bản” không có nghĩa mọi yếu tố thực thi giống nhau tuyệt đối. Lịch chạy tác vụ, thời điểm hoàn tất I/O hoặc trạng thái dùng chung có thể khác giữa các lượt. Cần điều tra các yếu tố đó, không kết luận rằng test tự nhiên thay đổi kết quả mà không có nguyên nhân. [2]

Flaky mô tả **đặc tính kết quả**, không phải một cấp kiểm thử riêng. Ví dụ EShop dùng API test viết bằng JavaScript, Jest và Supertest; test này có đặc tính flaky. Tên file hoặc tên lệnh có chữ `flaky` không tự chứng minh đặc tính đó: phải đối chiếu các lần thực thi và điều kiện chạy.

## 2. Phân biệt với các tình huống dễ nhầm

| Tình huống | Có thể kết luận gì? |
| --- | --- |
| Cùng test và phiên bản, có lượt pass và fail | Có dấu hiệu không ổn định; cần điều tra nguyên nhân và điều kiện thực thi |
| Test luôn fail vì expected khác actual | Là lỗi cần phân tích; chưa có bằng chứng biến thiên để gọi flaky |
| Sửa mã rồi test từ fail chuyển pass | Có thay đổi phiên bản, không tự chứng minh flakiness |
| Một test dữ liệu hợp lệ pass, test dữ liệu không hợp lệ fail đúng expected | Hai ca kiểm tra khác nhau; không phải một test thay đổi kết quả |
| Bước cài dependency fail, test chưa chạy | Lỗi pipeline/setup; không ghi thành assertion test fail |
| Rerun một lần chuyển xanh | Một quan sát bổ sung, chưa chứng minh nguyên nhân hoặc việc sửa đã thành công |

Đây là hướng đọc bằng chứng cho thí nghiệm nhóm. Đặc biệt, cùng SHA là điều kiện quan trọng nhưng chưa đủ: cần so môi trường, dữ liệu, lệnh chạy và lịch sử retry. Các trường này được lưu trong [protocol E-02](../../../experiments/flaky-test-protocol.md) và [bằng chứng E-03](../../E-03/20261021-b252db4-01/README.md).

## 3. Các nhóm nguyên nhân thường gặp

Các nhóm sau được tổng hợp từ tài liệu về kiểm thử không xác định và flaky tests. [2][3]

| Nhóm | Ví dụ minh họa | Điểm cần kiểm tra |
| --- | --- | --- |
| Bất đồng bộ, timing | Đọc dữ liệu trước khi thao tác ghi hoàn tất | Test đợi tín hiệu hoàn tất hay chỉ đợi một khoảng thời gian? |
| Trạng thái và thứ tự test | Test trước để lại dữ liệu làm test sau thay đổi kết quả | Fixture có độc lập, reset và cleanup đầy đủ không? |
| Chạy đồng thời | Hai tác vụ cùng sửa một tài nguyên | Thứ tự truy cập và cơ chế đồng bộ có rõ không? |
| Dịch vụ ngoài, tài nguyên | I/O chậm hoặc dịch vụ phụ thuộc không ổn định | Có log dependency, timeout và điều kiện runner không? |
| Thời gian, dữ liệu ngẫu nhiên | Test phụ thuộc giờ hệ thống hoặc dữ liệu không tái hiện được | Có thể kiểm soát đồng hồ hoặc lưu dữ liệu/seed không? |

Flake có thể bắt nguồn từ test, harness, môi trường hoặc lỗi đồng thời trong sản phẩm. Vì vậy không được tự coi mọi lỗi không ổn định là lỗi test rồi bỏ qua. [2][3]

## 4. Vì sao sleep cố định dễ gây lỗi?

Đợi đủ một khoảng thời gian không bảo đảm công việc cần đợi đã xong. Tài liệu Android minh họa rủi ro của việc dùng sleep tùy ý thay cho đồng bộ: tác vụ có thể cần thời gian khác nhau trong các môi trường. [4]

Trong ví dụ EShop, hai luồng bất đồng bộ cùng nằm trong một tiến trình Node.js; cách gọi A/B dưới đây không có nghĩa là tạo hai tiến trình hệ điều hành:

- **A:** đợi 60 hoặc 160 ms, rồi gửi `POST /api/cart` để thêm sản phẩm.
- **B:** đợi 100 ms, rồi gửi `GET /api/cart` và kiểm tra giỏ có một sản phẩm, quantity bằng 1.
- **Sai sót được tạo:** B không đợi A hoàn tất; B dùng mốc 100 ms thay cho điều kiện “thêm sản phẩm đã xong”.

Ở đây `sleep` dùng timer bất đồng bộ: nó tạm hoãn phần tiếp theo của tác vụ đang `await`, không khóa toàn bộ tiến trình trong 60/160 ms. Hai tác vụ có thể tiến triển xen kẽ. Mốc timer là thời gian yêu cầu chờ; mốc thực tế được ghi trong log để đối chiếu.

```text
Minh họa luồng nhanh — thời gian gần đúng, không phải cam kết thực thi:
0 ms       60 ms          ~65 ms              100 ms
A bắt đầu ─ gửi POST ──── thêm hoàn tất
B bắt đầu ─────────────────────────────────── gửi GET → thấy sản phẩm → PASS

Minh họa luồng chậm:
0 ms                    100 ms                     160 ms
A bắt đầu ──────────────────────────────────────── gửi POST → thêm hoàn tất
B bắt đầu ───────────── gửi GET → giỏ rỗng → FAIL
```

Các mốc ở sơ đồ giải thích cơ chế, không thay cho số liệu từng run. Đọc trước khi POST được gửi là bằng chứng rõ hơn việc chỉ nhìn nhãn fast/slow.

## 5. Tạo flake có chủ đích trong thí nghiệm khác gì thực tế?

Thực tế, độ trễ có thể biến thiên vì nhiều yếu tố thực thi. Trong test của nhóm, chế độ `sampled` chủ động chọn độ trễ 60 hoặc 160 ms với xác suất bằng nhau để mô phỏng sự biến thiên. Test giữ nguyên assertion và gọi API thật; không random trực tiếp PASS/FAIL.

Vì vậy đây là **thí nghiệm flake có chủ đích**, không phải bằng chứng rằng API giỏ hàng ngoài thực tế đang có lỗi timing hoặc mạng chậm. Hai chế độ ép `fast` và `slow` giúp kiểm tra cơ chế; đợt đo chính dùng cùng một chế độ sampled cho mọi lượt. Không bắt buộc số mẫu fast và slow bằng nhau.

Nguồn triển khai: [test E-01](../../../../backend/tests/experiments/cart-timing.flaky.js). Mỗi lượt có fixture riêng, login, gọi POST/GET và assertion thật; sau đó đợi tác vụ thêm kết thúc rồi đóng harness, kể cả khi assertion fail.

## 6. Bằng chứng thực tế của nhóm

Đợt E-03 gồm 10 dispatch mới trên cùng SHA `b252db4aa9e236b78879dfbbf7b882cdadb8580c`, giữ cùng môi trường và không retry test. Kết quả: 5 PASS, 5 FAIL ở assertion giỏ có một phần tử. [Bảng 10 run và file gốc](../../E-03/20261021-b252db4-01/README.md).

| Quan sát | Run 02 — PASS | Run 01 — FAIL |
| --- | --- | --- |
| POST được gửi | 60.359 ms | 161.179 ms |
| POST hoàn tất | 64.486 ms | 164.156 ms |
| GET được gửi | 100.395 ms | 100.610 ms |
| GET hoàn tất | 102.889 ms | 105.484 ms |
| HTTP của POST và GET | Đều 200 | Đều 200 |
| Giỏ quan sát được | Một sản phẩm, quantity 1 | Rỗng; expected length 1, actual 0 |

Nguồn: [console run 02](../../E-03/20261021-b252db4-01/02-39624265758/console.log) và [console run 01](../../E-03/20261021-b252db4-01/01-39623369899/console.log). Thời gian tính tương đối từ lúc bắt đầu tác vụ, không phải duration toàn job.

Run 01 cho thấy GET hoàn tất tại 105.484 ms, trước khi POST được gửi tại 161.179 ms. Điều này khớp cơ chế đọc giỏ quá sớm. Đây là giải thích dựa trên mã và log đã biết; việc so sánh phân tích độc lập và chạy xác nhận bản sửa thuộc E-08/E-09, không được tính là đã thực hiện chỉ bằng tài liệu này.

Tỷ lệ fail quan sát là 5/10 = 50%. Đây là tỷ lệ của đợt đo, không chứng minh tỷ lệ lỗi thực tế của EShop hay bảo đảm đợt sampled tiếp theo cũng có đúng 5 pass/5 fail. Mười lượt là số đo của thí nghiệm T07, không phải quy tắc phổ quát để chứng minh mọi test đều ổn định.

## 7. Cách điều tra và xử lý

Quy trình áp dụng cho bộ dữ liệu nhóm:

1. Xác định bước fail: cài đặt, setup, HTTP hay assertion; đọc expected/actual.
2. So các lượt ở cùng revision: môi trường, fixture, thời gian và retry. Giữ cả log pass lẫn fail.
3. Lập giả thuyết có dẫn chứng. Với ví dụ này, so thời điểm GET với thời điểm gửi/hoàn tất POST; không chỉ dựa vào màu job.
4. Thực hiện thay đổi có mục tiêu rồi chạy xác nhận trên điều kiện đã ghi. Lưu cả kết quả chưa đạt, không chỉ lượt xanh.

Với test EShop này, hướng sửa minh họa là đợi thao tác thêm thực sự hoàn tất trước khi đọc giỏ:

```javascript
// Minh họa hướng sửa, không phải bằng chứng đã triển khai E-09.
const added = await request(app).post('/api/cart').send(payload);
expect(added.status).toBe(200);
const cart = await request(app).get('/api/cart');
expect(cart.body).toHaveLength(1);
```

Đoạn trên lược bỏ auth và fixture để minh họa thứ tự. Nếu hệ thống xử lý nền và phản hồi POST chưa bảo đảm dữ liệu đã sẵn sàng, cần đợi trạng thái hoàn tất phù hợp; có thể polling với timeout hữu hạn. Không thay yêu cầu nghiệp vụ “đã thêm thành công” bằng một khoảng đợi dài hơn. Đồng bộ theo điều kiện hoàn tất là hướng xử lý vấn đề bất đồng bộ được thảo luận trong [2][4].

Retry và tăng sleep có thể làm ít thấy lỗi hơn nhưng không tự chứng minh nguyên nhân đã được sửa. Nếu tạm tách test không ổn định khỏi quality gate, vẫn phải theo dõi, có người phụ trách và kế hoạch sửa; không để lần pass sau che lần fail trước. [1][2]

## 8. Vai trò trong CI và phân tích người–AI

Một lần CI đỏ cần dẫn tới hành động có căn cứ. Khi kết quả không ổn định, nhóm dễ mất thời gian chạy lại hoặc bỏ qua cảnh báo thật. Google mô tả việc flake tạo thêm công việc điều tra và làm chậm phát hiện lỗi. [1]

Trong thí nghiệm nhóm, người và ChatGPT nhận cùng [bộ dữ liệu E-05](../../E-05/README.md). AI giúp tổ chức giả thuyết và đề xuất bước kiểm tra; câu trả lời phải được đối chiếu log và chạy kiểm chứng. AI không biến một dự đoán thành nguyên nhân đã xác nhận. Giữ tài liệu lý thuyết có đáp án này ngoài gói đầu vào phân tích độc lập.

## 9. Nội dung dùng nhanh khi thuyết trình

### Đoạn thuyết minh khoảng một phút

“Flaky test là test có lúc pass, lúc fail dù không sửa mã giữa các lượt. Vấn đề thường nằm ở điều kiện thực thi chưa được kiểm soát. Trong ví dụ giỏ hàng của nhóm, thao tác thêm sản phẩm và đọc giỏ chạy bất đồng bộ. Test đợi 100 ms rồi đọc, trong khi thao tác thêm có thể bắt đầu sau 60 hoặc 160 ms. Khi đọc trước lúc thêm, giỏ rỗng và assertion fail. Bộ 10 lượt ghi nhận cả pass và fail với cùng phiên bản. Bài học là phải đợi điều kiện công việc hoàn tất, giữ bằng chứng của mọi lượt và kiểm chứng giả thuyết thay vì chạy lại đến khi xanh.”

Đây là lời thuyết minh gợi ý, chưa phải kết quả đo thời gian trình bày.

### Bố cục hai slide

- **Slide 1 — Khái niệm:** định nghĩa; phân biệt test luôn fail; nhóm nguyên nhân; tác động tới độ tin cậy CI.
- **Slide 2 — EShop:** sơ đồ A/B; hai dòng timing của run 01; kết quả 5/10 fail; hướng sửa bằng đồng bộ hoàn tất.

Khi demo, mở một log PASS và một log FAIL ở mục 6, chỉ assertion và mốc GET/POST. Không dùng riêng nhãn fast/slow làm bằng chứng. Nếu người xem đang làm bài phân tích độc lập, chỉ công bố phần giải thích sau khi họ lưu câu trả lời.

## 10. Nguồn tham khảo

[1] John Micco, Google Testing Blog (2016), [Flaky Tests at Google and How We Mitigate Them](https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html). Nguồn định nghĩa theo kết quả và tác động trong CI.

[2] Martin Fowler (2011), [Eradicating Non-Determinism in Tests](https://martinfowler.com/articles/nonDeterminism.html). Nguồn về nguyên nhân và xử lý kiểm thử không xác định.

[3] pytest documentation, [Flaky tests](https://docs.pytest.org/en/stable/explanation/flaky.html). Nguồn về trạng thái không kiểm soát, isolation và các hướng điều tra.

[4] Android Developers, [Big test stability](https://developer.android.com/training/testing/instrumented-tests/stability). Nguồn minh họa đồng bộ và rủi ro sleep cố định; nguyên tắc được liên hệ với API test, không coi EShop là ứng dụng Android.

Các nguồn web được đối chiếu ngày 22/10/2026. Các ví dụ giả định, hướng sửa và số liệu thực tế đã được phân biệt trong từng mục.
