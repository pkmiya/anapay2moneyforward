# anapay2moneyforward

マネーフォワード ME への家計簿登録を自動化する個人向けスクリプト集。

| スクリプト | 用途 |
|---|---|
| `anapay2mf_icloud-mail.py` | ANA Pay 利用通知メール（iCloud）→ Google スプレッドシート → MF |
| `iccard2mf.py` | IC カード利用履歴 CSV → MF |
| `onebank2mf.py` | ワンバンク利用履歴 CSV → MF |
| `daily-info_none-to-anapay.py` | MF 日次一覧で保有金融機関「なし」を「ANA Pay」に一括修正 |

## ディレクトリ構成

```
.
├── anapay2mf_icloud-mail.py   # ANA Pay 同期（メイン）
├── iccard2mf.py               # IC カード CSV 登録
├── onebank2mf.py              # ワンバンク CSV 登録
├── daily-info_none-to-anapay.py
├── scripts/
│   └── gmail-auth.py          # Google OAuth 初回セットアップ
├── legacy/
│   └── anapay2mf.py           # 旧 Gmail 版（非推奨）
├── docs/ic-card/              # IC カード機能の設計・要件
├── data/                      # サンプル CSV など
├── .env                       # 認証情報（git 管理外）
└── credentials.json           # Google OAuth クライアント（git 管理外）
```

## 環境構築

### 1. Python 仮想環境

```bash
python3.11 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 2. 環境変数

`.env.example` をコピーして `.env` を作成し、値を埋める。

```bash
cp .env.example .env
```

| 変数 | 用途 |
|---|---|
| `SHEET_ID`, `SHEET_NAME` | ANA Pay 用 Google スプレッドシート |
| `ICLOUD_EMAIL`, `ICLOUD_APP_PASSWORD` | iCloud メール（アプリ専用パスワード） |
| `MF_EMAIL`, `MF_PASSWORD` | マネーフォワード ME ログイン |

IC カード登録で口座名を変える場合は `MF_ACCOUNT_NAME`（デフォルト: `SUGOCA`）も指定可能。詳細は `docs/ic-card/` を参照。ワンバンクは `ONEBANK_MF_ACCOUNT_NAME`（デフォルト: `ワンバンク`）。

### 3. Google スプレッドシート API

ANA Pay 同期は Google スプレッドシートへ書き込むため、OAuth 認証が必要。

1. [Google Cloud コンソール](https://console.cloud.google.com/) でプロジェクトを作成
2. Google Sheets API を有効化
3. OAuth 同意画面を設定（テストユーザーに自分のアカウントを追加）
4. 認証情報（デスクトップアプリ）をダウンロードし、リポジトリ直下に `credentials.json` として保存
5. 初回認証を実行

```bash
python scripts/gmail-auth.py
```

ブラウザで Google アカウントに **同意** すると、直下に `token.json` が生成される。

## 使い方

### ANA Pay 同期

iCloud メールから ANA Pay 利用通知を取得し、スプレッドシート経由で MF に登録する。

```bash
# メール取得 → スプシ書き込み → MF 登録（すべて実行）
python anapay2mf_icloud-mail.py all

# メール → スプシのみ
python anapay2mf_icloud-mail.py mail

# スプシ → MF のみ
python anapay2mf_icloud-mail.py mf
```

`mode` は環境変数 `ANAPAY2MF_MODE`（`mail` / `mf` / `all`）でも指定できる。

MF ログイン後、**認証コードの手入力**が必要。ブラウザが開いたら画面の指示に従う。

メール取得期間は `anapay2mf_icloud-mail.py` 内の `MAIL_SYNC_START_DATE` / `MAIL_SYNC_END_DATE` で変更する（将来 `.env` 化予定）。

### IC カード CSV 登録

```bash
# 登録待ちレコードの確認（MF には接続しない）
python iccard2mf.py data/sample_sugoca_history.csv --dry-run

# MF に登録（1 回あたり最大 100 件、デフォルト）
python iccard2mf.py path/to/history.csv

# 件数・口座名を指定
python iccard2mf.py path/to/history.csv --limit 50 --account SUGOCA
```

CSV 形式・登録済みフラグの仕様は `docs/ic-card/ic-card-csv-to-mf_design-doc.md` を参照。

### ワンバンク CSV 登録

CSV は `docs/onebank-ocr-prompt.md` の形式（IC カードと同一スキーマ）。MF 登録ロジックは `iccard2mf.py` を流用し、支出元・入金先のデフォルトが `ワンバンク` になる点のみ異なる。

```bash
# 登録待ちレコードの確認（MF には接続しない）
python onebank2mf.py data/sample_onebank_history.csv --dry-run

# MF に登録（1 回あたり最大 100 件、デフォルト）
python onebank2mf.py path/to/onebank_history.csv

# 件数・口座名を指定
python onebank2mf.py path/to/onebank_history.csv --limit 50 --account ワンバンク
```

### 保有金融機関「なし」→「ANA Pay」修正

MF の日次一覧で、保有金融機関が「なし」の行を「ANA Pay」に変更するメンテナンス用スクリプト。

```bash
# デフォルト: 2025/06 〜 2026/03
python daily-info_none-to-anapay.py

# 期間・ドライランを指定
START_YM=2025/06 END_YM=2026/03 DRY_RUN=1 python daily-info_none-to-anapay.py
```

## legacy/

`legacy/anapay2mf.py` は Gmail API 版の旧スクリプト。iCloud 版（`anapay2mf_icloud-mail.py`）を使うこと。旧版を動かす場合は `scripts/gmail-auth.py` で Gmail スコープ付きの `token.json` が必要。
