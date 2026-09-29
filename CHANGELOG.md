# Changelog / 変更履歴

## Unreleased
- (EN) `oep_client.config` (oep.probe.config: slots, binds, plan / label / idle items, get / set / save / erase, the live slot and bind state) and the `oep config show | slot | bind | remove | save | erase` command.
- (JA) `oep_client.config`（oep.probe.config: スロット、bind、plan / label / idle の項目、get / set / save / erase、スロットと bind の今の状態）と、`oep config show | slot | bind | remove | save | erase` の命令。

## 0.0.1
- (EN) First beta. The `ws_run` fixture gives each test a `wireskein.runlog.Recorder` writing into `<test_case_tempdir>/wireskein/`, next to `dut.log`. When the test body ends the run is verified: a failing check fails the test in its call phase (FAILED), `report.json` and `report.xml` are written, and the result lines are attached to the test report. `--wireskein-verify` / `wireskein_verify` = `fail` (default), `report` or `off`.
- (JA) 最初のβ版。`ws_run` fixture が test ごとに `wireskein.runlog.Recorder` を渡し、`dut.log` の隣の `<test_case_tempdir>/wireskein/` に記録する。test の本体が終わると照合する。検査が NG なら call の段で test を失敗（FAILED）にし、`report.json` と `report.xml` を書き、結果の行を test の報告に付ける。`--wireskein-verify` / `wireskein_verify` は `fail`（既定）、`report`、`off`。
