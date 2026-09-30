# pytest-embedded-wireskein

[English README](https://github.com/Open-Embedded-Probe/pytest-embedded-wireskein/blob/main/README.md)

[pytest-embedded](https://github.com/espressif/pytest-embedded) のプラグインです。test ごとに、[WireSkein](https://github.com/Open-Embedded-Probe/wireskein) の記録器 `ws_run` を渡します。

- test は、送ったコマンド、ロジックアナライザのキャプチャ、各ステップの線の上であるべき姿を記録します。
- test の本体が終わると、プラグインがキャプチャを期待と照らし合わせます。
- 検査が NG なら、その test を失敗にします。

状態: **β 版**です。

## 入れ方

```sh
pip install pytest-embedded-wireskein
```

Python 3.11 以上が要ります。`wireskein` と `pytest-embedded` も一緒に入ります。

## 使い方

```python
from wireskein.runlog import square, level, only_moving

def test_pwm(dut, ws_run, probe):              # probe は、ロジックアナライザを動かす何かの fixture
    with ws_run.section(1, "pwm"):
        for duty in (64, 128, 0):
            want = [square("PA1", 1000, duty / 255), only_moving(["PA1"])] if duty else [level("PA1", 0)]
            with ws_run.section(2, f"duty={duty}", expect=want):
                ws_run.command(f"PWM {duty}")
                dut.write(f"PWM {duty}")
                ws_run.reply(dut.expect(r"PWM duty=\d+").group(0).decode())
                t = ws_run.armed()               # キャプチャを開始した直後の time.monotonic()
                data, rate = probe.capture()     # bytes。1 サンプル 1 バイト、ビット k がピン k
                ws_run.capture(t, rate, interleaved=data, names=["PA1", "PA0"])
```

`test_pwm` が戻ると、プラグインは記録を閉じて照合します。NG があれば、test は call の段で失敗します（ERROR ではなく FAILED）。

```text
FAILED test_pwm.py::test_pwm - wireskein: 1 NG (5 ok, 1 ng, 0 unchecked (4 segments, 3 captures))
NG  pwm/duty=128  square  c0002.bin  duty 0.6999 vs 0.5020
report: /tmp/pytest-embedded/2026-09-29_12-00-00-000000/test_pwm/wireskein/report.json
```

検査の一覧（`square`、`level`、`starts`、`ends`、`only_moving`、`pulses`、`i2c`、`spi`、`uart`）と見出しの規則は、[WireSkein の README](https://github.com/Open-Embedded-Probe/wireskein/blob/main/README.ja.md) にあります。

### 記録の置き場所

`ws_run` は、pytest-embedded の `dut.log` の隣の `<test_case_tempdir>/wireskein/` に書きます。フルパスは `<root-logdir>/pytest-embedded/<時刻>/<test 名>/wireskein/` です。

| ファイル | 中身 |
| --- | --- |
| `run.json` | 見出し、コマンド、応答、メモ、キャプチャ、期待（WireSkein の記録の形式） |
| `c0001.wireskein` など | キャプチャ。各チャンネルを自分のレートで持つ（`wireskein info` で中身、`wireskein convert c0001.wireskein c0001.sr` で PulseView 用） |
| `report.json` | すべての結果と測定値、ログ |
| `report.xml` | 結果の JUnit XML |

同じディレクトリは、後から `wireskein verify <ディレクトリ>` で照合し直せます。

- test の `user_properties` には、`wireskein_report`（`report.json` のパス）が入ります。
- 結果の行は、test の報告に `wireskein` の節として付きます（`-rA` や失敗のときに表示されます）。

### 照合する条件

- test が、キャプチャか期待を 1 つでも記録したときだけ照合します。
- NG の検査があれば、test を失敗にします。
- ピンがキャプチャにない検査は未検査で、失敗にはしません。
- test の本体がすでに失敗していた場合も、記録と照合は行います。ただし、test 自身の失敗の内容はそのまま残します。

### 設定

| オプション | ini | 既定 | 意味 |
| --- | --- | --- | --- |
| `--wireskein-verify=fail\|report\|off` | `wireskein_verify` | `fail` | `fail`: 照合して、NG なら失敗。`report`: 照合して報告だけ残す（失敗にしない）。`off`: 記録だけ |
| `--wireskein-unchecked=fail\|pass` | `wireskein_unchecked` | `fail` | 検査できなかったもの（ピンがキャプチャにない、電圧への換算がない、など）。`fail`: 失敗にする（多くは試験の書き間違いか配線の抜けだから）。`pass`: 報告だけ。測るだけと頼んだもの（`uart(baud=None)`）は、どちらでも失敗にしない |

`ws_run` は `wireskein.runlog.Recorder` です。その公開のメソッド（`section`、`heading`、`command`、`reply`、`note`、`armed`、`capture`、`close`、`is_empty`）が、このプラグインの API です。記録の形式と結果の状態は、WireSkein の docs/run-format.ja.md にあります。

### プローブとのつなぎ方

このプラグインは、プローブもターゲットも知りません。ロジックアナライザを動かす fixture（例: ボードの家系ごとのプラグイン）が、両方入っているときに `ws_run` へつなぎます。

- キャプチャを開始した直後に `t = ws_run.armed()`（`time.monotonic()` の値。キャプチャのクライアントが同じ時計で付けた時刻でもよい）
- 読み終えたら `ws_run.capture(t, rate, interleaved=data, names=[...], width=8, positions=None, start_ns=..., start_uncertainty_ns=..., time_base_slipped=True)`
  - `data` はプローブのサンプルの並び（1 サンプル `width` ビット、チャンネル k はビット `positions[k]`）です。
  - `names` は、チャンネルの順に並べたターゲットのピン名です。
  - `time_base_slipped` は、プローブが報告したときだけ渡します。
- レートの違うチャンネルは `ws_run.capture(t, tick_hz, channels=[wireskein.fileformat.Channel(name, bits, n, step=...)])`
- キャプチャについてのほかの情報は `attachments={"probe.json": {...}}`
- コンソールの送受信は `ws_run.command(text)` と `ws_run.reply(text)`

## 開発

```sh
uv sync
uv run pytest
```

## リリース

[pytest-embedded-arduino-cli](https://github.com/tanakamasayuki/pytest-embedded-arduino-cli/blob/main/README.ja.md) と同じ手順です。`CHANGELOG.md` の `## Unreleased` を更新し、`Release` の workflow を版（例 `0.0.2`）を入れて実行します。PyPI への公開は Trusted Publishing で行います。

## ライセンス

MIT
