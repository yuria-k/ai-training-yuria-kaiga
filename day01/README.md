# Day 01

## 受講者が実装する場所

- `day01/app.py`（基本はこのファイルを編集）

## 目的

- 開発環境のセットアップができる状態にする
- GitHubのPR提出フローに慣れる
- Pythonで小さなCLIを作り、例外/ログ/READMEの書き方を身につける

## ゴール（完了条件）

- READMEどおりに第三者が実行できる
- 入力不備で終了コード `2` になり、標準エラーに分かりやすいメッセージが出る

## 機能要件

### 機能要件

コマンド

- `python -m day01.app` で起動できること（モジュール名は固定）

必須オプション

- `--name`：表示したい名前（文字列、必須）

任意オプション

- `--repeat`：繰り返し回数（整数、デフォルト `1`、1〜10）
- `--format`：出力形式（`text` / `json`、デフォルト `text`）

出力

- `--format text` の場合：標準出力に、指定回数分のテキストを出す
- `--format json` の場合：標準出力にJSONを出す
  - 例：`{"name":"Taro","repeat":2,"outputs":["Hello, Taro","Hello, Taro"]}`

終了コード

- 正常終了：`0`
- 入力不備（未指定、範囲外など）：`2`

ログ

- 実行開始時に、`name` / `repeat` / `format` をINFOで出す
- 例外発生時はERRORで出す

### 受け入れ基準

- `--name` 未指定で終了コード `2`、標準エラーに分かりやすいメッセージが出る
- `--repeat 2` で2行（または2要素）出る
- `--format json` でJSONとしてパース可能な文字列が出る

## 実装タスク

- `day01/app.py` を編集し、機能要件を満たす
- 例外時は標準エラーへメッセージを出し、終了コードを要件どおりにする

## 実行方法

### セットアップ

```bash
# 仮想環境の作成と有効化
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 実行コマンド例

```bash
# 基本的な実行
python -m day01.app --name "Taro"

# 繰り返し回数を指定
python -m day01.app --name "Taro" --repeat 3

# JSON形式で出力
python -m day01.app --name "Taro" --repeat 2 --format json
```

### 期待する出力例

```
# --name "Taro" の場合
Hello, Taro

# --name "Taro" --repeat 2 --format json の場合
{"name": "Taro", "repeat": 2, "outputs": ["Hello, Taro", "Hello, Taro"]}
```

---

**以下は受講者が記入してください**

- 追加で確認した入力例：python -m day01.app --name "Yuria",python -m day01.app --name "Yuria" --repeat 5
- 発生したエラーと対処：

## 提出物

- `day01/app.py`
- `day01/README.md`

## セルフレビュー

- 正常系：`--name Taro` で期待どおりに表示される:OK
- 異常系：`--name` 未指定でエラーになり、メッセージが分かりやすい
- 境界：`--name` に長い文字列や記号を入れても壊れない
- 再実行：同じ入力で複数回実行しても安定して同じ結果になる

## リサーチメモ（任意）

調べたURLや、理解した要点をメモしてください。

- Python仮想環境（venv等）
venv:virtual environmentの略称。
プロジェクトごとに独立した実行環境を作り、ライブラリやバージョンの衝突を防ぐ仕組み。
・仮想環境に入る
venv\○○\activate
ターミナルの行頭に（venv）と表示される。
・仮想環境を終了する
deactivate

- 依存管理（requirements/pyprojectの考え方）
依存関係：あるソフトウェアが動作するために必要な他のソフトウェアやライブラリの関係
プロジェクトの依存関係をrequirements.txtに記録することで、他の開発者が同じ環境を構築できるようになる。
・pyproject：Pythonパッケージの標準的な設定ファイル

- CLIの引数処理（例：argparse等）
CLI:Command Line Interface　文字コマンドを入力してコンピュータを操作するユーザーインターフェース
CLI引数：プログラム実行時に渡す追加情報

argparse:Pythonのスクリプトに渡すコマンドライン引数を解析し、型変換・必須チェック・ヘルプ表示・エラー表示までを自動で行う標準ライブラリ


- ログ（INFO/ERRORの使い分け）

・INFO：後から読んで何が起きたかわかるための記録
処理開始・終了/節目の出来事/外部との通信結果/状態の変化
開始と終了をセットで残すのが基本形

・5つのログレベル

DEBUG：10：開発中の詳細な記録
INFO：20：正常に進んだことの記録
WARNING：30：問題の予兆
ERROR：40：処理が失敗した
CRITICAL：50：システムが続行できない

・終了コードを確認する方法
実行後に　$LASTEXITCODE

- GitHub：ブランチ作成→PR→修正push

・main 最新化

git checkout main
git pull origin main

・ブランチ作成

git checkout -b feature/add-greeting

・修正後

git add .
git commit -m "挨拶機能追加"

・初回push

git push -u origin feature/add-greeting

・レビュー指摘後

git add .
git commit -m "レビュー指摘対応"

・再push

git push