"""Contract checks for evidence loss, hidden retries and participant disclosure."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SPEC = importlib.util.spec_from_file_location("order_history_runner", Path(__file__).with_name("run-order-history.py"))
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)
BATCH_ID = "20260101T000000Z-0123abcd"


def sample(statuses):
    events, attempts = [], []
    def event(attempt, name, **fields):
        events.append({"schema_version": 1, "run_id": "run-01", "attempt": attempt,
                       "sequence": len(events) + 1, "elapsed_ms": float(len(events)),
                       "time_utc": "2026-01-01T00:00:00.000Z", "event": name, **fields})
    for number, status in enumerate(statuses, 1):
        fixture = f"fixture-{number}"
        count = 0 if status == "failed" else 1
        event(number, "attempt.started", fixture_id=fixture)
        event(number, "fixture.ready", fixture_id=fixture, initial_order_count=0)
        for operation in ("submit", "history", "confirmation"):
            request_id = f"run-01.a{number}.{operation}"
            for stage in ("http.client.sent", "http.server.received", "http.server.completed", "http.client.received"):
                response = {"order_count": count if operation == "history" else 1}
                event(number, stage, request_id=request_id, operation=operation, status_code=200, response=response)
        failure = None
        if status == "failed":
            failure = {"category": "assertion", "code": "HISTORY_ORDER_COUNT", "expected": 1, "actual": 0}
            event(number, "assertion.completed", assertion_id="HISTORY_ORDER_COUNT", status="failed", expected=1, actual=0)
        event(number, "fixture.closed", fixture_id=fixture)
        event(number, "attempt.finished", status=status)
        attempts.append({"run_id": "run-01", "attempt": number, "retry_of_attempt": number - 1 or None,
                         "fixture_id": fixture, "status": status, "failure": failure, "additional_failure": None,
                         "observed_order_count": count, "confirmation_order_count": 1})
    native = {"numTotalTests": 1, "numPendingTests": 0, "success": statuses[-1] == "passed",
              "testResults": [{"assertionResults": [{"fullName": RUNNER.TEST_TITLE,
                  "invocations": len(statuses), "retryReasons": ["original failure"] * (len(statuses) - 1),
                  "status": statuses[-1]}]}]}
    return native, attempts, events


class EvidenceContracts(unittest.TestCase):
    def test_accepts_recovery_and_exhausted_budget(self):
        for statuses in (["passed"], ["failed", "passed"], ["failed"] * 3):
            native, attempts, events = sample(statuses)
            RUNNER.validate_run(native, attempts, events, 2, 0 if statuses[-1] == "passed" else 1)

    def test_rejects_hidden_native_retry(self):
        native, attempts, events = sample(["failed", "passed"])
        native["testResults"][0]["assertionResults"][0]["invocations"] = 1
        with self.assertRaisesRegex(ValueError, "invocation count"):
            RUNNER.validate_run(native, attempts, events, 2, 0)

    def test_rejects_lost_server_event(self):
        native, attempts, events = sample(["passed"])
        events = [event for event in events if not (event["event"] == "http.server.received" and event["operation"] == "history")]
        for sequence, event in enumerate(events, 1):
            event["sequence"] = sequence
        with self.assertRaisesRegex(ValueError, "HTTP request lifecycle"):
            RUNNER.validate_run(native, attempts, events, 2, 0)

    def test_rejects_early_stop_or_retry_after_pass(self):
        native, attempts, events = sample(["failed"])
        with self.assertRaisesRegex(ValueError, "exhausting"):
            RUNNER.validate_run(native, attempts, events, 2, 1)
        native, attempts, events = sample(["passed", "passed"])
        with self.assertRaisesRegex(ValueError, "passed test"):
            RUNNER.validate_run(native, attempts, events, 2, 0)

    def test_rejects_verdict_rewrite(self):
        native, attempts, events = sample(["failed", "passed"])
        attempts[0]["observed_order_count"] = 1
        with self.assertRaisesRegex(ValueError, "Snapshot counts"):
            RUNNER.validate_run(native, attempts, events, 2, 0)

    def prepare_packet(self, root, leak=False):
        raw = root / "raw/run-01"
        raw.mkdir(parents=True)
        _, attempts, events = sample(["failed", "passed"])
        if leak:
            events[0]["unexpected"] = "Bearer forbidden-fixture-value"
        original = "".join(json.dumps(event) + "\n" for event in events)
        (raw / "events.jsonl").write_text(original, encoding="utf-8")
        (raw / "attempts.jsonl").write_text("".join(json.dumps(attempt) + "\n" for attempt in attempts), encoding="utf-8")
        (raw / "controls.jsonl").write_text('{"variant":"timed","transport_delay_ms":200}', encoding="utf-8")
        record = {key: None for key in ("runner_started_at_utc", "runner_completed_at_utc", "process_duration_ms",
                                       "jest_test_duration_ms", "jest_started_at_epoch_ms")}
        record.update({"run_id": "run-01", "revision": "revision-01", "status": "passed", "initial_status": "failed",
                       "invocations": 2, "test_retries_used": 1, "retry_limit": 2, "process_exit_code": 0,
                       "validation_error": None, "private_source_path": "not-for-participants"})
        return original, record

    def test_public_zip_preserves_events_and_excludes_controls(self):
        with tempfile.TemporaryDirectory(prefix="eshop-packet-contract-") as directory:
            root = Path(directory)
            original, record = self.prepare_packet(root)
            packet = RUNNER.build_packet(root, [record], {"node": "v24", "jest": "30", "system": "fixture"}, 1, 2, BATCH_ID)
            with zipfile.ZipFile(packet) as archive:
                self.assertEqual(archive.read("run-01/events.jsonl"), (root / "raw/run-01/events.jsonl").read_bytes())
                text = "".join(archive.read(name).decode() for name in archive.namelist())
                self.assertNotIn("transport_delay_ms", text)
                self.assertNotIn("not-for-participants", text)
                self.assertFalse(any(name.startswith(("raw/", "source/")) for name in archive.namelist()))
                self.assertEqual(json.loads(archive.read("history.json"))["packet_id"], BATCH_ID)
            self.assertEqual(json.loads((root / "participant/run-01/attempts.json").read_text()),
                             [json.loads(line) for line in (root / "raw/run-01/attempts.jsonl").read_text().splitlines()])

    def test_leaking_packet_is_not_released(self):
        with tempfile.TemporaryDirectory(prefix="eshop-packet-contract-") as directory:
            root = Path(directory)
            _, record = self.prepare_packet(root, leak=True)
            with self.assertRaisesRegex(ValueError, "release guard"):
                RUNNER.build_packet(root, [copy.deepcopy(record)], {"node": "v24", "jest": "30", "system": "fixture"}, 1, 2, BATCH_ID)
            self.assertFalse((root / RUNNER.archive_names(BATCH_ID)["analysis"]).exists())

    def test_existing_archive_is_never_overwritten(self):
        with tempfile.TemporaryDirectory(prefix="eshop-packet-contract-") as directory:
            root = Path(directory)
            _, record = self.prepare_packet(root)
            destination = root / RUNNER.archive_names(BATCH_ID)["analysis"]
            destination.write_bytes(b"previous-evidence")
            with self.assertRaises(FileExistsError):
                RUNNER.build_packet(root, [record], {"node": "v24", "jest": "30", "system": "fixture"}, 1, 2, BATCH_ID)
            self.assertEqual(destination.read_bytes(), b"previous-evidence")


if __name__ == "__main__":
    unittest.main()
