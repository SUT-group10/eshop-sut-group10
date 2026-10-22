"""Build the E-05 participant packet without changing E-03 evidence. Run from any cwd."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/evidence/E-03/20261021-b252db4-01"
OUT = ROOT / "docs/evidence/E-05"
PACKET = OUT / "participant-input"
TITLE = "Cart contains the added product"
REMOVED = {"mode", "selectedCase", "delayMs", "readWaitMs"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sanitize_text(value):
    replacements = [
        ("E-01 cart contains the product after a fixed wait (injected timing flake)", TITLE),
        ("/home/runner/work/eshop-sut-group10/eshop-sut-group10/backend/", "<workspace>/backend/"),
        ("cart-timing.flaky.js", "cart.test.js"),
        ("jest.flaky.config.cjs", "jest.case.config.cjs"),
        ("test:flaky", "test:case"),
        ("test-results/flaky/", "test-results/case/"),
        ("tests/experiments/", "tests/api/"),
        ("E-01 observation", "Cart observation"),
        ("E-01 add completed", "Add completed"),
    ]
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def normalize(value):
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items() if k not in REMOVED}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    if isinstance(value, str):
        return sanitize_text(value)
    return value


def main():
    batch = json.loads((SOURCE / "batch.json").read_text(encoding="utf-8"))
    PACKET.mkdir(parents=True, exist_ok=True)
    history, mapping, combined = [], [], []
    for run in batch["runs"]:
        label = "run-%02d" % run["sequence"]
        src = SOURCE / run["directory"]
        dest = PACKET / label
        dest.mkdir(exist_ok=True)
        text = (src / "console.log").read_text(encoding="utf-8")
        lines = []
        original_observations = []
        for line in text.splitlines():
            match = re.match(r"^(.*?E-01 (?:observation|add completed) )(\{.*\})$", line)
            if match:
                observation = json.loads(match[2])
                original_observations.append(observation)
                line = match[1] + json.dumps(normalize(observation), ensure_ascii=False, separators=(",", ":"))
            lines.append(sanitize_text(line))
        normalized = "\n".join(lines) + "\n"
        (dest / "console.log").write_text(normalized, encoding="utf-8", newline="\n")
        result = json.loads((src / "results.json").read_text(encoding="utf-8"))
        converted = normalize(result)
        write_json(dest / "results.json", converted)
        # All counts, timestamps, assertions and status survive recursive normalization.
        assert normalize(result) == converted
        observed = []
        for line in normalized.splitlines():
            match = re.match(r"^.*?(?:Cart observation|Add completed) (\{.*\})$", line)
            if match:
                observed.append(json.loads(match[1]))
        assert observed == [normalize(v) for v in original_observations]
        assert result["testResults"][0]["assertionResults"][0]["status"] == run["test_status"]
        history.append({
            "run": label, "revision": "revision-01", "run_attempt": run["run_attempt"],
            "started_at_utc": run["run_started_at_utc"], "test_status": run["test_status"],
            "test_duration_ms": run["test_duration_ms"], "test_exit_code": run["test_exit_code"],
            "jest_invocations": run["jest_invocations"], "test_retry_count": run["test_retry_count"],
            "retry_messages": run["retry_messages"], "retry_reasons": run["retry_reasons"],
        })
        mapping.append({"alias": label, "source_run_id": run["run_id"], "source_directory": run["directory"],
                        "source_url": run["url"], "source_sha": run["head_sha"],
                        "files": {name: {"source_sha256": digest((src/name).read_bytes()),
                                         "normalized_sha256": digest((dest/name).read_bytes())}
                                  for name in ["console.log", "results.json"]}})
        combined.append("## " + label + "\n\n```text\n" +
                        "\n".join(("L%03d %s" % (i, line)).rstrip() for i, line in enumerate(lines, 1)) + "\n```\n")
    context = """# Bộ dữ liệu phân tích test giỏ hàng

Có 10 lượt chạy độc lập của cùng một API test trên cùng revision-01. Mỗi lượt dùng fixture/database riêng. Test kiểm tra giỏ hàng chứa sản phẩm vừa thêm, quantity bằng 1. Log chứa quan sát thao tác thêm và đọc giỏ; các mốc *Ms là mili giây tương đối từ lúc hai thao tác bắt đầu, không phải thời gian toàn job.

Môi trường chung: Node v24.14.0, npm 11.9.0, Ubuntu 22.04 image 20261018.327.1, runner 2.338.0. Không sửa mã giữa các lượt. Lịch sử thực thi và retry nằm trong history.json.

Đây là bản dữ liệu đã chuẩn hóa: tên test, đường dẫn, lệnh và mã định danh được thay bằng bí danh; bỏ nhãn thiết kế và tham số điều khiển mô phỏng. Giữ thời gian quan sát, thứ tự log, HTTP status, dữ liệu giỏ hàng, assertion, stack frame với số dòng, kết quả và retry. Tên/lệnh trong bản này chỉ là bí danh, không phải hướng dẫn chạy.

Đọc input.md (console có số dòng), history.json và results.json của cả 10 lượt. Không cần mở repo hoặc tra cứu nguồn bên ngoài gói dữ liệu này. Phân biệt bằng chứng trong log với suy đoán; có thể kết luận chưa đủ dữ liệu.
"""
    (PACKET / "README.md").write_text(context, encoding="utf-8", newline="\n")
    prompt = """# Yêu cầu phân tích chung

Chỉ dùng dữ liệu trong gói đính kèm để phân tích kết quả API test giỏ hàng qua 10 lượt. Chưa cần sửa mã hoặc chạy lại test.

1. Tóm tắt kết quả và đưa ra tối đa 3 giả thuyết nguyên nhân, xếp theo mức độ được bằng chứng hỗ trợ.
2. Với mỗi giả thuyết, trích đúng run/file/dòng log (số L trong input.md) hoặc đường dẫn trường JSON; nêu bằng chứng hỗ trợ và điểm chưa đủ để kết luận.
3. Đề xuất đúng 3 bước kiểm tra tiếp theo, kèm quan sát nào sẽ xác nhận hoặc bác bỏ giả thuyết.
4. Nêu mức độ chắc chắn và thông tin còn thiếu. Không coi nhận định là nguyên nhân đã xác nhận nếu chưa kiểm chứng.

Ghi thời điểm bắt đầu/kết thúc và thời gian thực hiện thực tế; nếu công cụ không đo được thì ghi không đo được, không tự ước lượng số giây. Lưu bản phân tích trước khi xem câu trả lời của bên còn lại.
"""
    (PACKET / "prompt.md").write_text(prompt, encoding="utf-8", newline="\n")
    write_json(PACKET / "history.json", history)
    history_text = json.dumps(history, ensure_ascii=False, indent=2)
    (PACKET / "input.md").write_text(context + "\n## Lịch sử chạy\n\n```json\n" + history_text + "\n```\n\n" + "\n".join(combined), encoding="utf-8", newline="\n")
    for path in PACKET.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            assert not re.search(r"flaky|flake|E-0[123]|TIMING_FAIL|injected|selectedCase|delayMs|readWaitMs|test/issue|github.com|396[0-9]{8}", text, re.I), path
            assert not re.search(r"github_pat_|gh[pousr]_[A-Za-z0-9]{20,}|Bearer |[A-Z]:[\\/]Users[\\/]|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text), path
    files = sorted(p for p in PACKET.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (PACKET / "SHA256SUMS").write_text("".join(digest(p.read_bytes()) + "  " + p.relative_to(PACKET).as_posix() + "\n" for p in files), encoding="utf-8", newline="\n")
    with zipfile.ZipFile(OUT / "participant-input.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(p for p in PACKET.rglob("*") if p.is_file()):
            info = zipfile.ZipInfo(path.relative_to(PACKET).as_posix(), (2026, 10, 21, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    write_json(OUT / "organizer-mapping.json", {"participant_zip_sha256": digest((OUT / "participant-input.zip").read_bytes()),
        "source_batch": SOURCE.relative_to(ROOT).as_posix(), "removed_observation_fields": sorted(REMOVED), "runs": mapping})
    print("Verified and packaged 10 runs; original observations/results preserved except documented normalization.")


if __name__ == "__main__":
    main()
