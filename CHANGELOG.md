# Changelog / 変更履歴

## Unreleased
- (EN) Pin `wireskein==0.0.2` (0.0.2 required `>=0.0.2`): wireskein 0.0.x may break its API in any release, so each plugin release follows one wireskein release.
- (JA) `wireskein==0.0.2` に固定する（0.0.2 は `>=0.0.2` だった）。wireskein は 0.0.x の間どの版でも互換のない変更がありうるので、プラグインのリリースは wireskein の 1 つの版に合わせる。

## 0.0.2
- (EN) Requires wireskein 0.0.2: captures are `.wsc` files (each channel at its own rate) and `ws_run.capture(armed, tick_hz, interleaved=..., names=...)` / `capture(armed, tick_hz, channels=[...])`, `ws_run.armed()` returns `time.monotonic()`. The README shows the new calls.
- (JA) wireskein 0.0.2 が要る。キャプチャは `.wsc`（各チャンネルを自分のレートで持つ）、`ws_run.capture(armed, tick_hz, interleaved=..., names=...)` / `capture(armed, tick_hz, channels=[...])`、`ws_run.armed()` は `time.monotonic()` を返す。README を新しい呼び方にした。

## 0.0.1
- (EN) First beta. The `ws_run` fixture gives each test a `wireskein.runlog.Recorder` writing into `<test_case_tempdir>/wireskein/`, next to `dut.log`. When the test body ends the run is verified: a failing check fails the test in its call phase (FAILED), `report.json` and `report.xml` are written, and the result lines are attached to the test report. `--wireskein-verify` / `wireskein_verify` = `fail` (default), `report` or `off`.
- (JA) 最初のβ版。`ws_run` fixture が test ごとに `wireskein.runlog.Recorder` を渡し、`dut.log` の隣の `<test_case_tempdir>/wireskein/` に記録する。test の本体が終わると照合する。検査が NG なら call の段で test を失敗（FAILED）にし、`report.json` と `report.xml` を書き、結果の行を test の報告に付ける。`--wireskein-verify` / `wireskein_verify` は `fail`（既定）、`report`、`off`。
