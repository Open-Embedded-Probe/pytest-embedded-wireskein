# pytest-embedded-wireskein

[日本語 README](https://github.com/Open-Embedded-Probe/pytest-embedded-wireskein/blob/main/README.ja.md)

A [pytest-embedded](https://github.com/espressif/pytest-embedded) plugin that gives each test a [WireSkein](https://github.com/Open-Embedded-Probe/wireskein) recorder, `ws_run`. The test records the commands it sent, the logic-analyzer captures, and what each step should look like on the wire. When the test body ends, the plugin checks the captures against these expectations and fails the test if a check fails.

Status: **beta**.

## Install

```sh
pip install pytest-embedded-wireskein
```

Python 3.13 or newer. This installs `wireskein` and `pytest-embedded`.

## Use

```python
from wireskein.runlog import square, level, only_moving

def test_pwm(dut, ws_run, probe):              # `probe` is whatever drives your logic analyzer
    with ws_run.section(1, "pwm"):
        for duty in (64, 128, 0):
            want = [square("PA1", 1000, duty / 255), only_moving(["PA1"])] if duty else [level("PA1", 0)]
            with ws_run.section(2, f"duty={duty}", expect=want):
                ws_run.command(f"PWM {duty}")
                dut.write(f"PWM {duty}")
                ws_run.reply(dut.expect(r"PWM duty=\d+").group(0).decode())
                t = ws_run.armed()               # time.monotonic() right after arming the capture
                data, rate = probe.capture()     # bytes, one sample per byte, bit k = pin k
                ws_run.capture(t, rate, interleaved=data, names=["PA1", "PA0"])
```

When `test_pwm` returns, the plugin closes the run and verifies it. If a check fails, the test fails in its call phase (FAILED, not ERROR):

```text
FAILED test_pwm.py::test_pwm - wireskein: 1 NG (5 ok, 1 ng, 0 unchecked (4 segments, 3 captures))
NG  pwm/duty=128  square  c0002.bin  duty 0.6999 vs 0.5020
report: /tmp/pytest-embedded/2026-09-29_12-00-00-000000/test_pwm/wireskein/report.json
```

The checks (`square`, `level`, `starts`, `ends`, `only_moving`, `pulses`, `i2c`, `spi`, `uart`) and the heading rules are described in the [WireSkein README](https://github.com/Open-Embedded-Probe/wireskein#checking-a-test-run).

### Where the run is written

`ws_run` writes to `<test_case_tempdir>/wireskein/`, next to pytest-embedded's `dut.log`: `<root-logdir>/pytest-embedded/<time>/<test name>/wireskein/`.

| File | Content |
| --- | --- |
| `run.json` | Headings, commands, replies, notes, captures and expectations (WireSkein run format) |
| `c0001.wsc`, ... | The captures, each channel at its own rate (`wireskein info`, `wireskein convert c0001.wsc c0001.sr` for PulseView) |
| `report.json` | Every result with measured values, and the log |
| `report.xml` | The results as JUnit XML |

The same directory can be checked again later with `wireskein verify <dir>`. The test's `user_properties` carry `wireskein_report` (the path of `report.json`), and the result lines are added to the test report as a `wireskein` section (shown with `-rA` or on failure).

### When the plugin verifies

- The run is verified after the test body, only if the test recorded a capture or an expectation.
- A check that fails makes the test fail.
- A check whose pins were not captured is unchecked and does not fail the test.
- If the test body already failed, the run is still recorded and verified, but the test's own failure is kept.

### Options

| Option | ini | Default | Meaning |
| --- | --- | --- | --- |
| `--wireskein-verify=fail\|report\|off` | `wireskein_verify` | `fail` | `fail`: verify and fail on NG. `report`: verify and write the reports, never fail. `off`: record only |

### Connecting a probe

This plugin knows nothing about probes or targets. A fixture that drives the logic analyzer (for example the one of a board-family plugin) connects to `ws_run` when both are installed:

- right after arming a capture: `t = ws_run.armed()` (`time.monotonic()`; a capture client's own stamp of the same clock works too)
- when the samples are read: `ws_run.capture(t, rate, interleaved=data, names=[...], width=8, positions=None, start_us=..., time_base_slipped=True)`. `data` is the probe's sample stream (`width` bits per sample, channel k at bit `positions[k]`), `names` the target's pin names in channel order. Pass `time_base_slipped` only when the probe reports it.
- channels at different rates: `ws_run.capture(t, tick_hz, channels=[wireskein.wsc.Channel(name, bits, n, step=...)])`
- anything else about the capture: `attachments={"probe.json": {...}}`
- the console traffic: `ws_run.command(text)`, `ws_run.reply(text)`

## Development

```sh
uv sync
uv run pytest
```

## Release

The release works the same way as in [pytest-embedded-arduino-cli](https://github.com/tanakamasayuki/pytest-embedded-arduino-cli#release). Update `## Unreleased` in `CHANGELOG.md`, then run the `Release` workflow with the version (for example `0.0.2`). PyPI publishing uses Trusted Publishing.

## License

MIT
