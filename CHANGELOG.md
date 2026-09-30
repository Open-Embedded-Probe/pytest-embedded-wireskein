# Changelog / 変更履歴

## Unreleased
- (EN) **Breaking:** requires wireskein 0.1.0 (the run format `wireskein-run/3` and check statuses). A check that could not be made fails the test by default: `--wireskein-unchecked=pass` (ini `wireskein_unchecked`) reports it only; measure-only checks never fail. The plugin uses only `Recorder`'s public API (`is_empty`) and the report's `status` fields. Python 3.11 or newer (was 3.13).
- (JA) **互換のない変更:** wireskein 0.1.0 が要る（記録の形式 `wireskein-run/3` と結果の状態）。検査できなかったものは、既定でテストを失敗にする: `--wireskein-unchecked=pass`（ini `wireskein_unchecked`）で報告だけにできる。測るだけの検査は失敗にしない。プラグインは `Recorder` の公開の API（`is_empty`）と、報告の `status` だけを使う。Python 3.11 以上（以前は 3.13）。

## 0.0.3
- (EN) Requires wireskein 0.0.8: captures are `.wireskein` files (was `.wsc`), runs are `wireskein-run/2`, and channels for `ws_run.capture(..., channels=[...])` come from `wireskein.fileformat` (was `wireskein.wsc`). The README shows the new names.
- (JA) wireskein 0.0.8 が要る。キャプチャは `.wireskein`（旧 `.wsc`）、記録は `wireskein-run/2`、`ws_run.capture(..., channels=[...])` のチャンネルは `wireskein.fileformat`（旧 `wireskein.wsc`）から作る。README を新しい名前にした。

## 0.0.2
- (EN) Requires wireskein 0.0.2: captures are `.wsc` files (each channel at its own rate) and `ws_run.capture(armed, tick_hz, interleaved=..., names=...)` / `capture(armed, tick_hz, channels=[...])`, `ws_run.armed()` returns `time.monotonic()`. The README shows the new calls.
- (JA) wireskein 0.0.2 が要る。キャプチャは `.wsc`（各チャンネルを自分のレートで持つ）、`ws_run.capture(armed, tick_hz, interleaved=..., names=...)` / `capture(armed, tick_hz, channels=[...])`、`ws_run.armed()` は `time.monotonic()` を返す。README を新しい呼び方にした。

## 0.0.1
- (EN) First beta. The `ws_run` fixture gives each test a `wireskein.runlog.Recorder` writing into `<test_case_tempdir>/wireskein/`, next to `dut.log`. When the test body ends the run is verified: a failing check fails the test in its call phase (FAILED), `report.json` and `report.xml` are written, and the result lines are attached to the test report. `--wireskein-verify` / `wireskein_verify` = `fail` (default), `report` or `off`.
- (JA) 最初のβ版。`ws_run` fixture が test ごとに `wireskein.runlog.Recorder` を渡し、`dut.log` の隣の `<test_case_tempdir>/wireskein/` に記録する。test の本体が終わると照合する。検査が NG なら call の段で test を失敗（FAILED）にし、`report.json` と `report.xml` を書き、結果の行を test の報告に付ける。`--wireskein-verify` / `wireskein_verify` は `fail`（既定）、`report`、`off`。
