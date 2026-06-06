# ICカード CSV → マネフォME 自動入力 設計書

要件定義: [ic-card-csv-to-mf_requirements.md](./ic-card-csv-to-mf_requirements.md)

## 1. 概要

| 項目 | 内容 |
|------|------|
| プログラム名 | `iccard2mf.py` |
| 目的 | CSV形式のICカード（SUGOCA）利用履歴を、マネーフォワード ME の**家計簿手入力モーダル**経由で登録する |
| 技術スタック | Python 3.11+, Helium (Selenium), python-dotenv |
| 既存コードとの関係 | ログイン処理は `anapay2mf_icloud-mail.py` を流用。入力UIは `anapay2mf.py` の手入力モーダル操作に近い |

### 既存プログラムとの主な違い

| | `anapay2mf_icloud-mail.py` | 本プログラム |
|---|---|---|
| 入力元 | Google Spreadsheet | **CSVファイル** |
| MF入力UI | トップの**カンタン入力**フォーム | **家計簿タブ → 手入力モーダル** |
| 収入対応 | なし（支出のみ） | **支出・収入両方** |
| 分類 | 設定しない | **大分類・小分類を指定**（存在しなければスキップ） |
| 登録済み管理 | スプシの `mf` 列 | CSVの **`マネフォ登録日` 列** |

---

## 2. 入力データ（CSV）

### スキーマ

| 列名 | 型 | 必須 | 説明 |
|------|-----|------|------|
| 利用日 | 日付 | ○ | `YYYY/MM/DD` 形式 |
| 利用内容 | 文字列 | ○ | モーダルの「項目（内容）」欄へ |
| 利用金額 | 整数 | ○ | 円（カンマなし） |
| 大分類 | 文字列 | △ | 例: `交通費` / `収入`。空なら未分類 |
| 小分類 | 文字列 | △ | 例: `バス` / `その他入金`。大分類とセットで使用 |
| マネフォ登録日 | 日付 | - | 未登録は空。登録成功時にプログラムが書き込む |

### サンプル

```csv
利用日,利用内容,利用金額,大分類,小分類,マネフォ登録日
2026/06/05,バス,330,交通費,バス,
2026/06/05,入場時オートチャージ,1000,収入,その他入金,
```

### パースルール

- **未処理行**: `マネフォ登録日` が空（null / 空白）の行のみ対象
- **収入判定**: `大分類 == "収入"` → 収入タブ、それ以外 → 支出タブ
- **1回の実行上限**: 未処理行のうち先頭から **最大100件**
- **エンコーディング**: UTF-8（BOM付きも許容）
- **ヘッダ行**: 必須（列名でマッピング）

---

## 3. 全体フロー

```mermaid
flowchart TD
    A[CLI起動: CSVパス指定] --> B[CSV読み込み]
    B --> C[未処理行を抽出 最大100件]
    C --> D{対象あり?}
    D -- No --> Z[終了]
    D -- Yes --> E[MFログイン]
    E --> F[/cf 家計簿タブへ遷移]
    F --> G[手入力ボタン押下]
    G --> H[1件目をモーダルに入力]
    H --> I[保存する]
    I --> J[入力を保存しました 待機 max 10秒]
    J --> K[CSVにマネフォ登録日を書き込み]
    K --> L{残りあり?}
    L -- Yes --> M[続けて入力する]
    M --> H
    L -- No --> N[閉じる]
    N --> O[ブラウザ終了]
    O --> Z
```

---

## 4. モジュール構成

初期実装は単一ファイル `iccard2mf.py`。必要になったら以下に分割する。

```
iccard2mf.py          # エントリポイント・CLI
├── models.py         # ICRecord データクラス（任意）
├── csv_io.py         # CSV読み書き
├── mf_auth.py        # ログイン
└── mf_entry.py       # 家計簿モーダル操作
```

---

## 5. 主要関数設計

### 5.1 CSV I/O

```python
@dataclass
class ICRecord:
    row_index: int          # CSV行番号（書き戻し用、0-based data row）
    use_date: date
    description: str
    amount: int
    large_category: str     # 大分類
    small_category: str     # 小分類
    mf_registered_at: date | None

    @property
    def is_income(self) -> bool:
        return self.large_category == "収入"

def load_records(csv_path: Path, limit: int = 100) -> list[ICRecord]:
    """未登録行のみ、最大 limit 件返す"""

def mark_registered(csv_path: Path, row_index: int, registered_at: date) -> None:
    """マネフォ登録日列を更新（都度ファイル書き込み）"""
```

**書き戻し方針**: 1件登録成功ごとにCSVを更新する（途中中断時も再実行で重複登録を防げる）。

### 5.2 ログイン

`anapay2mf_icloud-mail.py` の `login_mf()` をベースに、**ログイン完了判定を変更**する。

| ステップ | 操作 |
|----------|------|
| 1 | `https://moneyforward.com/login` を Chrome で開く |
| 2 | メールアドレス入力 → 「ログインする」 |
| 3 | パスワードページがあれば入力 |
| 4 | ユーザーが認証コードを手入力（既存と同様、最大120秒待機） |
| 5 | ログイン完了を確認（認証ページから離脱） |
| 6 | `/cf` へ遷移し、「手入力」ボタンの出現を待つ |

```python
def login_mf() -> None: ...
def navigate_to_cf() -> None:
    """/cf へ移動し Button('手入力') を待つ"""
```

### 5.3 1件入力

```python
def open_manual_entry_modal(is_first: bool) -> None:
    """初回: 手入力ボタン。2件目以降: 続けて入力する"""

def fill_record(record: ICRecord) -> None:
    """タブ切替 → 各フィールド入力 → 分類選択"""

def save_and_wait() -> None:
    """保存する → '入力を保存しました' 最大10秒待機"""

def continue_or_close(has_more: bool) -> None:
    """続けて入力する / 閉じる"""
```

#### フィールドマッピング

| CSV / 条件 | MFモーダル | セレクタ / 操作 |
|------------|-----------|----------------|
| 支出 | 支出タブ | `input.minus-payment` の親 label |
| 収入 | 収入タブ | `input.plus-payment` の親 label |
| 利用日 | 日付 | `#updated-at` |
| 利用金額 | 支出金額 / 収入金額 | `#appendedPrependedInput` |
| 支出元 / 入金先 | SUGOCA | `#user_asset_act_sub_account_id_hash` で `SUGOCA` を含む option |
| 大分類 | 項目（大） | `#js-large-category-selected` → `a.l_c_name` テキスト一致 |
| 小分類 | 項目（小） | `#js-middle-category-selected` → `a.m_c_name` テキスト一致 |
| 利用内容 | 内容 | `#js-content-field` |

#### 分類選択ロジック

- 大分類ドロップダウンを開き、`a.l_c_name` のテキストが一致する項目をクリック
- サブメニューから `a.m_c_name` で小分類をクリック
- **存在しない場合**: ログに warning を出し、分類は未分類のまま（要件通り）
- 収入タブ選択後に分類選択を行う

#### 保存後のUI状態遷移

| 状態 | submit-box | confirmation | confirmation-button |
|------|-----------|--------------|---------------------|
| 入力中 | 表示 | 非表示 | 非表示 |
| 保存後 | 非表示 | 表示（「入力を保存しました。」） | 表示（「続けて入力する」） |

---

## 6. CLI インターフェース

```bash
python iccard2mf.py /path/to/sugoca_history.csv
python iccard2mf.py /path/to/sugoca_history.csv --limit 100
python iccard2mf.py /path/to/sugoca_history.csv --dry-run
```

| 引数 | 説明 |
|------|------|
| `csv_path` | 必須。入力CSVのパス |
| `--limit` | 1回の最大件数（デフォルト 100） |
| `--account` | 支出元/入金先名（デフォルト `SUGOCA`） |
| `--dry-run` | CSV読み込みのみ（MF操作なし） |

---

## 7. 環境変数

| 変数 | 用途 |
|------|------|
| `MF_EMAIL` | ログインメールアドレス |
| `MF_PASSWORD` | パスワード |

任意:

| 変数 | 用途 | デフォルト |
|------|------|-----------|
| `MF_ACCOUNT_NAME` | 支出元/入金先 | `SUGOCA` |
| `MF_LOGIN_URL` | ログインURL | `https://moneyforward.com/login` |
| `MF_CF_URL` | 家計簿URL | `https://moneyforward.com/cf` |

---

## 8. エラーハンドリング

| 状況 | 対応 |
|------|------|
| CSV必須列欠落 | その行をスキップ、warning ログ |
| 日付・金額パース失敗 | スキップ、warning ログ |
| 分類がMFに存在しない | 分類なしで登録（要件通り） |
| SUGOCA口座が見つからない | 例外で中断 |
| 保存後10秒以内に確認メッセージなし | 例外で中断（CSVは未更新のまま） |
| 認証コード未入力 | 120秒タイムアウトで終了 |
| 途中中断（Ctrl+C等） | 成功分のみCSV更新済み。再実行で続きから |

---

## 9. 待機・タイミング

| 操作 | 待機 |
|------|------|
| 保存ボタン押下後 | 「入力を保存しました」まで **最大10秒** |
| 各フィールド入力間 | 0.2〜0.5秒 |
| タブ切替後 | フォーム表示の `wait_until` |

---

## 10. ログ出力

既存と同様 `logging.INFO` レベル:

```
INFO  Loaded 45 pending records (processing up to 100)
INFO  Login to moneyforward
INFO  Navigated to /cf
INFO  Adding record [1/45]: 2026/06/05 バス 330円 (expense)
WARNING  Category not found: 大分類=xxx 小分類=yyy — registering as 未分類
INFO  Record saved: 2026/06/05, 330, バス
INFO  Updated CSV row 2: マネフォ登録日=2026/06/06
INFO  Records added to moneyforward: 45
```

---

## 11. 実装時の注意点

1. **日付入力**: `#updated-at` へ JS で値設定
2. **初回 vs 2件目以降**: 初回のみ「手入力」ボタン。以降は「続けて入力する」（`#confirmation-button`）
3. **支出→収入の混在**: 連続入力中にタブを毎回切り替える
4. **口座選択**: option テキストは `SUGOCA (238円)` のように残高付き → `startswith("SUGOCA")` でマッチ
5. **CSV書き戻し**: 一時ファイル経由で atomic write

---

## 12. テスト計画

| 段階 | 内容 |
|------|------|
| 単体 | CSVパース（日付形式、収入判定、未処理行フィルタ） |
| 結合 | `--dry-run` で対象行一覧を確認 |
| 手動 | テストCSV 2〜3件（支出1 + 収入1）で実際にMFへ登録 |
| 回帰 | 再実行で登録済み行がスキップされることを確認 |

---

## 13. 将来拡張（スコープ外）

- ICカード履歴のCSV生成部分（別プログラム）
- 複数ICカード口座名の対応
- スプレッドシート連携

---

## 14. ファイル構成

```
anapay2moneyforward/
├── iccard2mf.py
├── ic-card-csv-to-mf_design-doc.md
├── ic-card-csv-to-mf_requirements.md
├── anapay2mf_icloud-mail.py
├── requirements.txt
└── .env                  # MF_EMAIL, MF_PASSWORD
```
