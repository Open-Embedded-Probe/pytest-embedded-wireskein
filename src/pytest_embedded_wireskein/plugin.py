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


def pytest_configure(config: pytest.Config) -> None:
    _mode(config)       # a wrong value is a usage error before any test runs


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
    if mode == "off" or not (rec.doc["expect"] or rec.doc["captures"]):
        return
    report = ws_verify.verify(path.parent)
    (path.parent / "report.json").write_text(ws_verify.dumps(report))
    (path.parent / "report.xml").write_text(ws_verify.junit(report))
    item.user_properties.append(("wireskein_report", str(path.parent / "report.json")))
    text = "\n".join([ws_verify.summary_line(report), *ws_verify.lines(report), f"report: {path.parent / 'report.json'}"])
    item.add_report_section("call", "wireskein", text)
    if verdict and mode == "fail" and report["summary"]["ng"]:
        ng = [line for line in ws_verify.lines(report) if line.startswith("NG")]
        pytest.fail(f"wireskein: {report['summary']['ng']} NG ({ws_verify.summary_line(report)})\n"
                    + "\n".join(ng) + f"\nreport: {path.parent / 'report.json'}", pytrace=False)
