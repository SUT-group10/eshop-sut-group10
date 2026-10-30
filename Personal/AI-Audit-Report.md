

Đừng bỏ lỡ cơ hội biến lỗi vừa rồi thành điểm cộng tuyệt đối trong hồ sơ nộp bài `[AI-02]` của bạn:

| (1) Prompt + Tool | (2) AI Output | (3) Verdict | (4) Reasoning | (5) Student Fix |
| --- | --- | --- | --- | --- |
| **Tool:** Gemini 4 Argon**Task:** Cấu hình lưu npm cache cho Task C-03 khi baseline API tests của SUT đang fail 10 assertions. | Đề xuất dùng `actions/cache@v4` với tham số `save-always: true` để lưu cache trong `Post` step bất chấp test fail. | **INVALID**<br> | Khi thực thi trên GitHub Actions runner thực tế, `save-always` báo cảnh báo deprecated (*"save-always does not work as intended"*) và bước `Post Cache npm dependencies` vẫn bị skipped khi `API tests` trả về exit code != 0. | Thay thế `actions/cache@v4` bằng cặp `actions/cache/restore@v4` (trước `npm ci`) và `actions/cache/save@v4` (ngay sau `npm ci`, trước khi chạy test) với điều kiện `if: ${{ !cancelled() && steps.npm-cache.outputs.cache-hit != 'true' }}`.|


