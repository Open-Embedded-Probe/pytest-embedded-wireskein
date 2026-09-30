import json
from pathlib import Path

import pytest

# A test file using ws_run with a synthetic capture: P0 low for 1000 samples.
TEST_FILE = '''
from wireskein.runlog import level

def test_{name}(ws_run):
    with ws_run.section(1, "t", expect=[level("P0", {want})]):
        ws_run.command("PING")
        ws_run.reply("PONG")
        t = ws_run.armed()
        ws_run.capture(t, 1e6, interleaved=bytes(1000), names=["P0"])
'''


def run(pytester: pytest.Pytester, *args, name="x", want=0, body=None):
    pytester.makepyfile(body or TEST_FILE.format(name=name, want=want))
    logdir = pytester.path / "logs"
    return pytester.runpytest("--root-logdir", str(logdir), *args), logdir


def run_dir(logdir: Path, name: str) -> Path:
    (d,) = logdir.glob(f"pytest-embedded/*/test_{name}/wireskein")
    return d


def test_ok_run_is_recorded_next_to_the_dut_log(pytester):
    result, logdir = run(pytester)
    result.assert_outcomes(passed=1)
    d = run_dir(logdir, "x")
    assert {p.name for p in d.iterdir()} == {"run.json", "c0001.wireskein", "report.json", "report.xml"}
    doc = json.loads((d / "run.json").read_text())
    assert doc["meta"]["test"].endswith("::test_x")
    assert [e["src"] for e in doc["log"]] == ["marker", "host", "dut", "marker"]
    assert json.loads((d / "report.json").read_text())["summary"]["ok"] == 1


def test_ng_fails_the_call_phase(pytester):
    result, logdir = run(pytester, want=1)
    result.assert_outcomes(failed=1)                     # FAILED, not ERROR
    result.stdout.fnmatch_lines(["*wireskein: 1 NG*", "*NG  t  level  c0001.wireskein  not constant 1*", "*report: *report.json*"])


def test_report_mode_keeps_the_reports_without_failing(pytester):
    result, logdir = run(pytester, "--wireskein-verify=report", want=1)
    result.assert_outcomes(passed=1)
    assert json.loads((run_dir(logdir, "x") / "report.json").read_text())["summary"]["ng"] == 1


def test_off_mode_only_records(pytester):
    pytester.makeini("[pytest]\nwireskein_verify = off\n")
    result, logdir = run(pytester, want=1)
    result.assert_outcomes(passed=1)
    assert {p.name for p in run_dir(logdir, "x").iterdir()} == {"run.json", "c0001.wireskein"}


def test_a_failing_test_body_is_not_overridden(pytester):
    body = TEST_FILE.format(name="x", want=1) + "        assert False, 'the body failed'\n"
    result, logdir = run(pytester, body=body)
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*the body failed*"])
    result.stdout.no_fnmatch_line("*wireskein: 1 NG*")
    assert (run_dir(logdir, "x") / "report.json").exists()   # still verified and recorded


def test_unchecked_does_not_fail(pytester):
    body = TEST_FILE.format(name="x", want=0).replace('level("P0", 0)', 'level("NOT_CAPTURED", 0)')
    result, _ = run(pytester, body=body)
    result.assert_outcomes(passed=1)


def test_unused_recorder_writes_no_report(pytester):
    body = "def test_x(ws_run):\n    pass\n"
    result, logdir = run(pytester, body=body)
    result.assert_outcomes(passed=1)
    assert {p.name for p in run_dir(logdir, "x").iterdir()} == {"run.json"}


def test_bad_mode_is_a_usage_error(pytester):
    pytester.makeini("[pytest]\nwireskein_verify = maybe\n")
    result, _ = run(pytester)
    assert result.ret != 0
    result.stderr.fnmatch_lines(["*wireskein_verify must be one of fail, report, off*"])
