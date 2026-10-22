"""Run isolated Jest invocations, verify native retry history and export two ZIPs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import re
import secrets
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
SCHEMA = 1
TEST_TITLE = "Submitted order appears in account history"
SOURCE_FILES = [
    "backend/tests/experiments/order-history.case.js",
    "backend/tests/helpers/order-history-observer.js",
    "backend/tests/helpers/harness.js", "backend/jest.flaky.config.cjs",
    "backend/jest.config.cjs", "backend/package.json", "backend/package-lock.json",
    "backend/server.js", "backend/database.js", ".github/workflows/flaky-experiment.yml",
    "docs/experiments/run-order-history.py", "docs/experiments/order-history-protocol.md",
    "docs/experiments/test_order_history_collector.py",
]


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def capture(command, cwd=ROOT):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=15)
    if result.returncode:
        raise RuntimeError(f"Command failed: {command[0]}")
    return result.stdout.strip()


def fingerprint():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


def validate_run(jest, attempts, events, retry_limit, exit_code):
    """Reject lost retries, duplicate events, setup errors and contradictory verdicts."""
    cases = [case for suite in jest.get("testResults", []) for case in suite.get("assertionResults", [])]
    if len(cases) != 1 or cases[0].get("fullName") != TEST_TITLE:
        raise ValueError("Expected exactly the planned test, not an empty/extra suite")
    case = cases[0]
    if not 1 <= len(attempts) <= retry_limit + 1:
        raise ValueError("Invalid attempt count for configured retry budget")
    if case.get("invocations") != len(attempts):
        raise ValueError("Attempt ledger disagrees with native Jest invocation count")
    if len(case.get("retryReasons", [])) != len(attempts) - 1:
        raise ValueError("Native retry reasons are missing or duplicated")
    if [e["sequence"] for e in events] != list(range(1, len(events) + 1)):
        raise ValueError("Event sequence contains a gap or duplicate")
    if any(a["status"] != "failed" for a in attempts[:-1]):
        raise ValueError("A passed test was executed again as if it were a retry")
    final = attempts[-1]["status"]
    if final not in ("passed", "failed") or case.get("status") != final:
        raise ValueError("Final verdict disagrees with native Jest")
    if exit_code != (0 if final == "passed" else 1) or jest.get("success") != (final == "passed"):
        raise ValueError("Process exit code disagrees with final verdict")
    if final == "failed" and len(attempts) != retry_limit + 1:
        raise ValueError("Failed test stopped before exhausting the configured retries")
    if (jest.get("numTotalTests") != 1 or jest.get("numPendingTests") != 0 or jest.get("wasInterrupted")
            or jest.get("numRuntimeErrorTestSuites", 0)):
        raise ValueError("Unexpected test count, pending test or interrupted execution")
    if jest.get("openHandles"):
        raise ValueError("Jest reported open handles")
    for index, attempt in enumerate(attempts, 1):
        if attempt["attempt"] != index or attempt["retry_of_attempt"] != (index - 1 if index > 1 else None):
            raise ValueError("Broken attempt/retry relationship")
        if attempt["fixture_id"] != f"fixture-{index}" or attempt.get("additional_failure"):
            raise ValueError("Invalid fixture identity or cleanup failure")
        own_events = [event for event in events if event["attempt"] == index]
        starts = [event for event in own_events if event["event"] == "attempt.started"]
        ends = [event for event in own_events if event["event"] == "attempt.finished"]
        closes = [event for event in own_events if event["event"] == "fixture.closed"]
        ready = [event for event in own_events if event["event"] == "fixture.ready"]
        if len(starts) != 1 or len(ends) != 1 or len(closes) != 1 or ends[0]["status"] != attempt["status"]:
            raise ValueError("Incomplete attempt lifecycle or fixture cleanup")
        if len(ready) != 1 or ready[0]["initial_order_count"] != 0:
            raise ValueError("Missing isolated starting state")
        if any(event["fixture_id"] != attempt["fixture_id"] for event in starts + ready + closes):
            raise ValueError("Fixture identifiers do not agree")
        if any(event["run_id"] != attempt["run_id"] for event in own_events):
            raise ValueError("Run identifiers do not agree")
        requests = [event for event in own_events if event["event"] == "http.client.sent"]
        if sorted(request["operation"] for request in requests) != ["confirmation", "history", "submit"]:
            raise ValueError("Missing or duplicate operation in attempt")
        for sent in requests:
            matches = [event for event in own_events if event.get("request_id") == sent["request_id"]]
            stages = [event["event"] for event in matches]
            if stages != ["http.client.sent", "http.server.received", "http.server.completed", "http.client.received"]:
                raise ValueError("Incomplete HTTP request lifecycle")
            if matches[-1]["status_code"] != 200:
                raise ValueError("Non-successful HTTP result")
        responses = {event["operation"]: event for event in own_events if event["event"] == "http.client.received"}
        if (responses["history"]["response"].get("order_count") != attempt["observed_order_count"]
                or responses["confirmation"]["response"].get("order_count") != attempt["confirmation_order_count"]
                or attempt["confirmation_order_count"] != 1):
            raise ValueError("Snapshot counts disagree or post-submit state is invalid")
        assertions = [event for event in own_events if event["event"] == "assertion.completed" and event["status"] == "failed"]
        if len(assertions) != (1 if attempt["status"] == "failed" else 0):
            raise ValueError("Assertion events disagree with attempt verdict")
        if attempt["status"] == "failed" and attempt["failure"]["code"] != "HISTORY_ORDER_COUNT":
            raise ValueError("Non-target failure: keep evidence, investigate before measurement")
        if attempt["status"] == "failed" and (
            assertions[0]["assertion_id"] != "HISTORY_ORDER_COUNT" or
            assertions[0]["expected"] != 1 or assertions[0]["actual"] != 0 or
            attempt["failure"].get("expected") != 1 or attempt["failure"].get("actual") != 0
        ):
            raise ValueError("Target failure does not match the original assertion")
    if any(b["elapsed_ms"] < a["elapsed_ms"] for a, b in zip(events, events[1:])):
        raise ValueError("Monotonic timestamps moved backwards")
    return case


def public_readme(runtime, planned, actual, retry_limit):
    return f"""# API test analysis input

This packet contains {actual} completed test invocations (planned: {planned}) of
`{TEST_TITLE}`, test ID `ORDER-HISTORY-01`, on `revision-01`.
Each run is a fresh Jest process. Failed tests may be retried at most {retry_limit}
times inside that process; the first attempt is not a retry. Every attempt uses
a new application instance and isolated SQLite in-memory fixture with zero orders.
The APIs are the real EShop endpoints, exercised over local HTTP by Supertest.

## Files and clocks

- `history.json`: initial/final verdicts, invocation count and retry relationship.
- `run-NN/events.jsonl`: original structured observations, one event per line.
- `run-NN/console.log`: a line-numbered rendering of those same events, not new runs.
- `run-NN/attempts.json`: original per-attempt verdicts, assertions and observations.
- `run-NN/result.json`: final result checked against the native Jest report.

`elapsed_ms` is milliseconds from a monotonic clock in that run's Jest process.
It includes fixture setup and retries. Compare event times only within the same
run. `time_utc` is wall time for orientation, not the clock used to infer ordering.
`sequence` breaks ties. `process_duration_ms` in history measures the whole Jest
process including startup; it is not test duration. Native Jest test duration is
listed separately. Request IDs connect client send/receive and server receipt/
completion. `history` and `confirmation` identify two separate history requests;
both observations are retained. Assertions determine the test result.

## Scope

Environment: Node {runtime['node']}, Jest {runtime['jest']}, {runtime['system']}.
Run/revision labels are aliases. Original CI IDs, source mapping and experiment
controls are retained by the organizer outside this packet. Source code, runner
stack/code frames, authentication data and design explanations are not supplied.
Event values and attempt results have not been rewritten to suggest a cause.
Use only this packet. An observed pattern is evidence for a hypothesis, not by
itself confirmation of a particular implementation defect.
"""


PROMPT = """# Analysis request

Read the supplied log/report/history only; do not open the repository or other sources.
1. Summarize initial attempts, retries and final results without double-counting files.
2. Give at most three hypotheses ranked by evidence. Cite run/file/line or JSON field,
   distinguish observations from hypotheses, and state missing information/uncertainty.
3. Propose exactly three next checks, explaining which outcomes support or weaken each hypothesis.
Do not claim to have executed those checks or fixed code. Record actual analysis time
if measurable; do not estimate or invent it. Save the answer before seeing another analyst's output.
"""


def archive_names(batch_id):
    return {"analysis": f"analysis-input-{batch_id}.zip",
            "organizer": f"organizer-evidence-{batch_id}.zip"}


def build_packet(batch, runs, runtime, planned, retry_limit, batch_id):
    packet = batch / "participant"
    packet.mkdir()
    history = []
    for run in runs:
        if run.get("validation_error"):
            continue
        source = batch / "raw" / run["run_id"]
        dest = packet / run["run_id"]
        dest.mkdir()
        shutil.copyfile(source / "events.jsonl", dest / "events.jsonl")
        attempts = read_jsonl(source / "attempts.jsonl")
        events = read_jsonl(source / "events.jsonl")
        write_json(dest / "attempts.json", attempts)
        public = {key: run[key] for key in (
            "run_id", "revision", "status", "initial_status", "invocations", "test_retries_used",
            "retry_limit", "process_exit_code", "runner_started_at_utc", "runner_completed_at_utc",
            "process_duration_ms", "jest_test_duration_ms", "jest_started_at_epoch_ms")}
        write_json(dest / "result.json", public)
        history.append(public)
        lines = []
        for event in events:
            fields = {key: value for key, value in event.items() if key not in (
                "schema_version", "run_id", "sequence", "time_utc", "elapsed_ms", "attempt", "event")}
            lines.append(f"L{event['sequence']:04d} {event['time_utc']} t+{event['elapsed_ms']:.3f}ms "
                         f"attempt={event['attempt']} {event['event']} " + json.dumps(fields, ensure_ascii=False))
        (dest / "console.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(packet / "history.json", {
        "schema_version": SCHEMA, "packet_id": batch_id, "planned_runs": planned, "validated_runs": len(history),
        "complete": len(history) == planned, "test_id": "ORDER-HISTORY-01", "runs": history,
    })
    (packet / "README.md").write_text(public_readme(runtime, planned, len(history), retry_limit), encoding="utf-8")
    (packet / "prompt.md").write_text(PROMPT, encoding="utf-8")
    # A release guard, not a search/replace anonymizer. Fail closed on leakage.
    forbidden = re.compile(r"Bearer\s+|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_|[A-Z]:[\\/]Users[\\/]|"
                           r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|transport_delay_ms|observation_wait_ms|"
                           r"\b(?:timed|awaited|injected|flaky|flake)\b", re.I)
    files = sorted(path for path in packet.rglob("*") if path.is_file())
    for path in files:
        if forbidden.search(path.read_text(encoding="utf-8")):
            raise ValueError(f"Participant release guard rejected {path.relative_to(packet)}")
    archive_path = batch / archive_names(batch_id)["analysis"]
    with zipfile.ZipFile(archive_path, "x", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(packet).as_posix())
    return archive_path


def bounded_integer(low, high):
    def parse(value):
        integer = int(value)
        if not low <= integer <= high:
            raise argparse.ArgumentTypeError(f"must be between {low} and {high}")
        return integer
    return parse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=bounded_integer(1, 50), default=10)
    parser.add_argument("--retries", type=int, choices=(0, 1, 2), default=2)
    parser.add_argument("--variant", choices=("timed", "awaited"), default="timed")
    parser.add_argument("--latency-ms", type=bounded_integer(0, 2000), help="constant-latency diagnostic, not sampled measurement")
    parser.add_argument("--seed", type=int, help="replay a recorded pseudo-random latency schedule")
    parser.add_argument("--output", type=Path, help="new batch directory; existing paths are never overwritten")
    parser.add_argument("--detect-open-handles", action="store_true")
    args = parser.parse_args()
    node = shutil.which("node")
    if not node or not (BACKEND / "node_modules/jest/bin/jest.js").is_file():
        parser.error("Install backend dependencies with npm ci; Node and Python 3 are required")
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4)
    names = archive_names(batch_id)
    batch = args.output.resolve() if args.output else BACKEND / "test-results/order-history" / batch_id
    try:
        batch.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error("Output directory already exists; choose a new directory to preserve the previous batch")
    (batch / "raw").mkdir()
    before = fingerprint()
    # Snapshot experiment implementation; identify unchanged SUT modules by SHA/hash.
    for name in SOURCE_FILES:
        if name in ("backend/server.js", "backend/database.js", "backend/package-lock.json"):
            continue
        destination = batch / "source" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    runtime = {
        "node": capture([node, "--version"]),
        "jest": json.loads((BACKEND / "node_modules/jest/package.json").read_text(encoding="utf-8"))["version"],
        "python": platform.python_version(), "system": platform.system(),
        "platform": platform.platform(), "npm_user_agent": os.environ.get("npm_config_user_agent"),
    }
    seed = args.seed if args.seed is not None else secrets.randbits(64)
    generator = random.Random(seed)
    manifest = {
        "schema_version": SCHEMA, "protocol": "order-history-v2.0", "state": "running",
        "batch_id": batch_id, "archives": names,
        "started_at_utc": utc_now(), "planned_runs": args.runs,
        "source_commit": capture(["git", "rev-parse", "HEAD"]),
        "source_worktree_status": capture(["git", "status", "--porcelain", "--", *SOURCE_FILES]),
        "source_sha256": before, "runtime": runtime,
        "variant": args.variant, "retry_limit": args.retries, "seed": seed,
        "latency_profile": "constant-diagnostic" if args.latency_ms is not None else "sampled-integer-20..220-ms",
        "observation_wait_ms": 120, "ci_run_id": os.environ.get("GITHUB_RUN_ID"),
        "ci_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "ci_url": (f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
                   f"{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
                   if os.environ.get("GITHUB_REPOSITORY") and os.environ.get("GITHUB_RUN_ID") else None),
        "runs": [],
    }
    write_json(batch / "organizer.json", manifest)
    print(f"Evidence directory: {batch}", flush=True)
    for number in range(1, args.runs + 1):
        run_id = f"run-{number:02d}"
        raw = batch / "raw" / run_id
        raw.mkdir()
        # Always reserve three slots. With the same seed, initial-attempt latency
        # remains matched across retry=0, retry=2 and the corrected variant.
        delays = [args.latency_ms if args.latency_ms is not None else generator.randint(20, 220)
                  for _ in range(3)]
        command = [node, str(BACKEND / "node_modules/jest/bin/jest.js"),
                   "--config", "jest.flaky.config.cjs", "--runInBand", "--no-cache", "--json",
                   f"--outputFile={raw / 'jest.json'}"]
        if args.detect_open_handles:
            command.append("--detectOpenHandles")
        env = os.environ.copy()
        env.update({"ORDER_TEST_VARIANT": args.variant, "ORDER_TEST_RETRIES": str(args.retries),
                    "ORDER_RUN_ID": run_id, "ORDER_EVIDENCE_DIR": str(raw),
                    "ORDER_TRANSPORT_DELAYS": ",".join(map(str, delays)), "FORCE_COLOR": "0"})
        run = {"run_id": run_id, "revision": "revision-01", "retry_limit": args.retries,
               "runner_started_at_utc": utc_now(), "planned_delays_ms": delays,
               "command": command, "validation_error": None}
        started = time.perf_counter()
        with (raw / "jest.console.log").open("wb") as output:
            try:
                result = subprocess.run(command, cwd=BACKEND, env=env, stdout=output,
                                        stderr=subprocess.STDOUT, timeout=45)
                run["process_exit_code"] = result.returncode
            except subprocess.TimeoutExpired:
                run["process_exit_code"] = None
                run["validation_error"] = "Jest process exceeded 45 seconds"
        run["runner_completed_at_utc"] = utc_now()
        run["process_duration_ms"] = round((time.perf_counter() - started) * 1000, 3)
        try:
            if run["validation_error"]:
                raise ValueError(run["validation_error"])
            if fingerprint() != before:
                raise ValueError("Source/configuration changed during the batch")
            jest = json.loads((raw / "jest.json").read_text(encoding="utf-8"))
            attempts = read_jsonl(raw / "attempts.jsonl")
            events = read_jsonl(raw / "events.jsonl")
            case = validate_run(jest, attempts, events, args.retries, run["process_exit_code"])
            if args.variant == "awaited":
                for attempt in attempts:
                    own = [event for event in events if event["attempt"] == attempt["attempt"]]
                    submitted = next(event for event in own if event["event"] == "http.client.received" and event["operation"] == "submit")
                    read = next(event for event in own if event["event"] == "http.client.sent" and event["operation"] == "history")
                    if submitted["sequence"] >= read["sequence"]:
                        raise ValueError("Corrected variant did not await submission before reading")
            run.update({"status": case["status"], "initial_status": attempts[0]["status"],
                        "invocations": case["invocations"], "test_retries_used": len(attempts) - 1,
                        "jest_test_duration_ms": case["duration"], "jest_started_at_epoch_ms": jest["startTime"]})
            print(f"{run_id}: initial={run['initial_status']} final={run['status']} "
                  f"attempts={run['invocations']} retries={run['test_retries_used']}", flush=True)
        except (OSError, ValueError, KeyError, TypeError) as error:
            run["validation_error"] = str(error)
            run["status"] = "error"
            print(f"{run_id}: EVIDENCE ERROR: {error}", flush=True)
        manifest["runs"].append(run)
        write_json(batch / "organizer.json", manifest)
        if run["validation_error"]:
            # Keep partial raw data. Do not silently drop bad runs and keep sampling.
            break
    runs = manifest["runs"]
    valid = [run for run in runs if not run["validation_error"]]
    manifest["summary"] = {
        "planned_runs": args.runs, "validated_runs": len(valid),
        "first_attempt_pass": sum(run["initial_status"] == "passed" for run in valid),
        "recovered_after_retry": sum(run["initial_status"] == "failed" and run["status"] == "passed" for run in valid),
        "final_fail": sum(run["status"] == "failed" for run in valid),
        "total_attempts": sum(run["invocations"] for run in valid),
        "failed_attempts": sum(run["invocations"] - (run["status"] == "passed") for run in valid),
        "evidence_errors": sum(bool(run["validation_error"]) for run in runs),
    }
    manifest["completed_at_utc"] = utc_now()
    manifest["state"] = "complete" if len(valid) == args.runs else "incomplete"
    try:
        build_packet(batch, runs, runtime, args.runs, args.retries, batch_id)
    except (ValueError, OSError) as error:
        manifest["state"] = "incomplete"
        manifest["packaging_error"] = str(error)
    exit_code = (2 if manifest["state"] != "complete" else
                 1 if manifest["summary"]["final_fail"] else 0)
    manifest["exit_code"] = exit_code
    write_json(batch / "organizer.json", manifest)
    organizer_archive = batch / names["organizer"]
    with zipfile.ZipFile(organizer_archive, "x", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(batch.rglob("*")):
            if path.is_file() and path != organizer_archive and "participant" not in path.relative_to(batch).parts:
                archive.write(path, path.relative_to(batch).as_posix())
    print(json.dumps(manifest["summary"], ensure_ascii=False), flush=True)
    print(f"Batch {manifest['state']}; exit={exit_code}. Share {names['analysis']} only.", flush=True)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as output:
            output.write("## Order-history experiment\n\n| Metric | Count |\n| --- | --- |\n")
            for key, value in manifest["summary"].items():
                output.write(f"| {key} | {value} |\n")
            output.write(f"\nState: **{manifest['state']}**. Retry limit: **{args.retries}**. "
                         "Download **api-analysis-input** for analysis; organizer evidence contains the controls.\n")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
