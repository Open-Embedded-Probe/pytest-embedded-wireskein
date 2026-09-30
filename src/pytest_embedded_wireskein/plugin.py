"""`ws_run`: a WireSkein recorder per test, verified when the test body ends.

The run is written next to pytest-embedded's dut.log, in
<test_case_tempdir>/wireskein/ (run.json, the captures, report.json,
report.xml). A failing check fails the test in its call phase, so pytest
reports FAILED, not ERROR. The plugin knows nothing about the probe or the
target: whatever fixture drives the probe feeds `ws_run` (armed / capture /
command / reply).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from wireskein import verify as ws_verify
from wireskein.runlog import Recorder

MODES = ("fail", "report", "off")
UNCHECKED = ("fail", "pass")
DIR_NAME = "wireskein"

_recorder_key = pytest.StashKey[Recorder]()
_done_key = pytest.StashKey[bool]()


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("embedded-wireskein")
    group.addoption(
        "--wireskein-verify",
        choices=MODES,
        default=None,
        help="after each test using ws_run: fail = verify and fail the test on NG (default), "
             "report = verify and keep the reports only, off = record only",
    )
    parser.addini("wireskein_verify", help="fail | report | off (see --wireskein-verify)", default="fail")
    group.addoption(
        "--wireskein-unchecked",
        choices=UNCHECKED,
        default=None,
        help="a check that could not be made (a pin not captured, ...): fail = fails the test (default), "
             "pass = reported only",
    )
    parser.addini("wireskein_unchecked", help="fail | pass (see --wireskein-unchecked)", default="fail")


def pytest_configure(config: pytest.Config) -> None:
    _mode(config)       # a wrong value is a usage error before any test runs
    _allow_unchecked(config)


def _allow_unchecked(config: pytest.Config) -> bool:
    v = config.getoption("wireskein_unchecked") or config.getini("wireskein_unchecked")
    if v not in UNCHECKED:
        raise pytest.UsageError(f"wireskein_unchecked must be one of {', '.join(UNCHECKED)}, not {v!r}")
    return v == "pass"


def _mode(config: pytest.Config) -> str:
    mode = config.getoption("wireskein_verify") or config.getini("wireskein_verify")
    if mode not in MODES:
        raise pytest.UsageError(f"wireskein_verify must be one of {', '.join(MODES)}, not {mode!r}")
    return mode


@pytest.fixture
def ws_run(request: pytest.FixtureRequest, test_case_tempdir: str) -> Recorder:
    """A wireskein.runlog.Recorder for this test, recording into
    <test_case_tempdir>/wireskein/. Headings (`section`), commands, replies,
    captures and expectations go through it; the plugin verifies the run when
    the test body ends."""
    rec = Recorder(Path(test_case_tempdir) / DIR_NAME, test=request.node.nodeid)
    request.node.stash[_recorder_key] = rec
    yield rec
    # the call phase did not run (a setup error): still leave the record
    _finish(request.node, verdict=False)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item: pytest.Item):
    try:
        result = yield
    except BaseException:
        _finish(item, verdict=False)    # the test failed on its own: record, do not override
        raise
    _finish(item, verdict=True)
    return result


def _finish(item: pytest.Item, verdict: bool) -> None:
    rec = item.stash.get(_recorder_key, None)
    if rec is None or item.stash.get(_done_key, False):
        return
    item.stash[_done_key] = True
    path = rec.close()
    mode = _mode(item.config)
    if mode == "off" or rec.is_empty:
        return
    allow = _allow_unchecked(item.config)
    report = ws_verify.verify(path.parent)
    (path.parent / "report.json").write_text(ws_verify.dumps(report))
    (path.parent / "report.xml").write_text(ws_verify.junit(report, allow))
    item.user_properties.append(("wireskein_report", str(path.parent / "report.json")))
    text = "\n".join([ws_verify.summary_line(report), *ws_verify.lines(report), f"report: {path.parent / 'report.json'}"])
    item.add_report_section("call", "wireskein", text)
    if verdict and mode == "fail" and ws_verify.failed(report, allow):
        bad = [r for r in report["results"] if r["status"] == "ng" or (r["status"] == "unchecked" and not allow)]
        s = report["summary"]
        head = f"{s['ng']} NG" + (f", {s['unchecked']} unchecked" if s["unchecked"] and not allow else "")
        pytest.fail(f"wireskein: {head} ({ws_verify.summary_line(report)})\n"
                    + "\n".join(f"{ws_verify.MARKS[r['status']]}  {r['path']}  {r['check']}  {r['capture'] or ''}  "
                                 f"{r['reason']}".rstrip() for r in bad)
                    + f"\nreport: {path.parent / 'report.json'}", pytrace=False)
