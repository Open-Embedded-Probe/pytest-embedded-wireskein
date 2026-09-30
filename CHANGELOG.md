# Changelog / 変更履歴

## Unreleased

## 0.0.3
- (EN) Requires wireskein 0.0.8: captures are `.wireskein` files (was `.wsc`), runs are `wireskein-run/2`, and channels for `ws_run.capture(..., channels=[...])` come from `wireskein.fileformat` (was `wireskein.wsc`). The README shows the new names.
- (JA) wireskein 0.0.8 が要る。キャプチャは `.wireskein`（旧 `.wsc`）、記録は `wireskein-run/2`、`ws_run.capture(..., channels=[...])` のチャンネルは `wireskein.fileformat`（旧 `wireskein.wsc`）から作る。README を新しい名前にした。

## 0.0.2
- (EN) Requires wireskein 0.0.2: captures are `.wsc` files (each channel at its own rate) and `ws_run.capture(armed, tick_hz, interleaved=..., names=...)` / `capture(armed, tick_hz, channels=[...])`, `ws_run.armed()` returns `time.monotonic()`. The README shows the new calls.
- (JA) wireskein 0.0.2 が要る。キャプチャは `.wsc`（各チャンネルを自分のレートで持つ）、`ws_run.capture(armed, tick_hz, interleaved=..., names=...)` / `capture(armed, tick_hz, channels=[...])`、`ws_run.armed()` は `time.monotonic()` を返す。README を新しい呼び方にした。

## 0.0.1
- (EN) First beta. The `ws_run` fixture gives each test a `wireskein.runlog.Recorder` writing into `<test_case_tempdir>/wireskein/`, next to `dut.log`. When the test body ends the run is verified: a failing check fails the test in its call phase (FAILED), `report.json` and `report.xml` are written, and the result lines are attached to the test report. `--wireskein-verify` / `wireskein_verify` = `fail` (default), `report` or `off`.
- (JA) 最初のβ版。`ws_run` fixture が test ごとに `wireskein.runlog.Recorder` を渡し、`dut.log` の隣の `<test_case_tempdir>/wireskein/` に記録する。test の本体が終わると照合する。検査が NG なら call の段で test を失敗（FAILED）にし、`report.json` と `report.xml` を書き、結果の行を test の報告に付ける。`--wireskein-verify` / `wireskein_verify` は `fail`（既定）、`report`、`off`。
