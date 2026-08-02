import argparse
import email
import imaplib
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime

import gspread
import helium
from dateutil import parser
from dotenv import load_dotenv
from gspread.exceptions import APIError
from selenium.webdriver.support.select import Select

load_dotenv()

# Google Spreadsheet ID and Sheet name
SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

# mail2spreadsheet の取得期間（None のときは従来どおり）
# 形式: "YYYY/MM/DD"
MAIL_SYNC_START_DATE: str | None = "2026/03/17"
MAIL_SYNC_END_DATE: str | None = None

# MF_URL = "https://ssnb.x.moneyforward.com/cf"
MF_URL = "https://moneyforward.com/login"

format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=format, level=logging.INFO)

ICLOUD_IMAP_HOST = "imap.mail.me.com"
ICLOUD_IMAP_PORT = 993


def _is_rate_limit_error(exc: APIError) -> bool:
    msg = str(exc)
    return (
        "Rate Limit Exceeded" in msg
        or "rateLimitExceeded" in msg
        or "userRateLimitExceeded" in msg
        or "RESOURCE_EXHAUSTED" in msg
    )


def append_row_with_retry(worksheet, values, value_input_option="USER_ENTERED", max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            worksheet.append_row(values, value_input_option=value_input_option)
            return
        except APIError as e:
            if not _is_rate_limit_error(e) or attempt == max_retries - 1:
                raise
            sleep_sec = 2 ** attempt
            logging.warning("Google Sheets rate limit on append_row, retry in %s sec (attempt %s/%s)",
                            sleep_sec, attempt + 1, max_retries)
            time.sleep(sleep_sec)


def append_rows_with_retry(worksheet, values_list, value_input_option="USER_ENTERED", max_retries: int = 5):
    """
    複数行をまとめて append するためのラッパー。
    values_list: [[row1_col1, row1_col2, ...], [row2_col1, ...], ...]
    """
    if not values_list:
        return

    for attempt in range(max_retries):
        try:
            # gspread の append_rows を利用してバッチで書き込む
            worksheet.append_rows(
                values_list, value_input_option=value_input_option)
            return
        except APIError as e:
            if not _is_rate_limit_error(e) or attempt == max_retries - 1:
                raise
            sleep_sec = 2 ** attempt
            logging.warning("Google Sheets rate limit on append_rows, retry in %s sec (attempt %s/%s)",
                            sleep_sec, attempt + 1, max_retries)
            time.sleep(sleep_sec)


def update_cell_with_retry(worksheet, row: int, col: int, value, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            worksheet.update_cell(row, col, value)
            return
        except APIError as e:
            if not _is_rate_limit_error(e) or attempt == max_retries - 1:
                raise
            sleep_sec = 2 ** attempt
            logging.warning("Google Sheets rate limit on update_cell, retry in %s sec (attempt %s/%s)",
                            sleep_sec, attempt + 1, max_retries)
            time.sleep(sleep_sec)


@dataclass
class ANAPay:
    """ANA Pay information"""

    email_date: datetime = None
    date_of_use: datetime = None
    amount: int = 0
    store: str = ""

    def values(self) -> tuple[str, str, int, str]:
        return (
            self.email_date_str,
            self.date_of_use_str,
            self.amount,
            self.store,
        )

    @property
    def email_date_str(self) -> str:
        return f"{self.email_date:%Y-%m-%d %H:%M:%S}"

    @property
    def date_of_use_str(self) -> str:
        return f"{self.date_of_use:%Y-%m-%d %H:%M:%S}"


def decode_mime_header(value: str | None) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    decoded = []
    for part, encoding in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(encoding or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def extract_text_body(msg: Message) -> str:
    """メール本文の text/plain を優先して取得"""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                if payload:
                    return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or "utf-8"
        if payload:
            return payload.decode(charset, errors="replace")

    return ""


def get_mail_info_from_message(msg: Message) -> ANAPay | None:
    """
    1件のメールからANA Payの利用情報を取得して返す
    """
    ana_pay = ANAPay()

    date_header = msg.get("Date")
    if date_header:
        ana_pay.email_date = parsedate_to_datetime(date_header)
        if ana_pay.email_date.tzinfo is not None:
            ana_pay.email_date = ana_pay.email_date.astimezone().replace(tzinfo=None)

    body = extract_text_body(msg)

    # 例:
    # ご利用日時：2023-06-28 22:46:19
    # ご利用金額：44,308円
    # ご利用店舗：SMOKEBEERFACTORY OTSUKATE
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line.startswith("ご利用"):
            continue

        if "：" not in line:
            continue

        key, value = line.split("：", 1)
        value = value.strip()

        if key == "ご利用日時":
            ana_pay.date_of_use = parser.parse(value)
        elif key == "ご利用金額":
            amount_text = re.sub(r"[^\d]", "", value)
            ana_pay.amount = int(amount_text) if amount_text else 0
        elif key == "ご利用店舗":
            ana_pay.store = value

    if not ana_pay.email_date or not ana_pay.date_of_use or not ana_pay.amount:
        logging.warning("Failed to parse ANA Pay mail")
        return None

    return ana_pay


def _parse_ymd(date_str: str) -> datetime:
    """YYYY/MM/DD を日付の先頭 00:00:00 として返す"""
    return datetime.strptime(date_str, "%Y/%m/%d")


def get_anapay_info(after: str, before: str | None = None) -> list[ANAPay]:
    """
    iCloud Mail (IMAP) からANA Payの利用履歴を取得する
    after: YYYY/MM/DD（この日を含む）
    before: YYYY/MM/DD（この日を含む。None のときは上限なし）
    """
    ana_pay_list: list[ANAPay] = []

    icloud_email = os.getenv("ICLOUD_EMAIL")
    icloud_app_password = os.getenv("ICLOUD_APP_PASSWORD")

    if not icloud_email or not icloud_app_password:
        raise ValueError("ICLOUD_EMAIL または ICLOUD_APP_PASSWORD が設定されていません")

    after_dt = _parse_ymd(after)
    before_end: datetime | None = None
    if before:
        before_end = _parse_ymd(before).replace(hour=23, minute=59, second=59)

    # IMAPのSINCE / BEFORE は '01-Jan-2026' 形式（BEFORE は指定日未満）
    imap_since = after_dt.strftime("%d-%b-%Y")
    search_criteria = ['FROM', '"payinfo@121.ana.co.jp"', 'SINCE', imap_since]
    if before:
        imap_before = (_parse_ymd(before) + timedelta(days=1)
                       ).strftime("%d-%b-%Y")
        search_criteria.extend(['BEFORE', imap_before])

    logging.info("Connecting to iCloud IMAP %s:%s",
                 ICLOUD_IMAP_HOST, ICLOUD_IMAP_PORT)
    with imaplib.IMAP4_SSL(ICLOUD_IMAP_HOST, ICLOUD_IMAP_PORT) as mail:
        mail.login(icloud_email, icloud_app_password)
        mail.select("INBOX")

        # From / Subject / 日付で絞る
        # 件名の日本語検索はサーバ依存で不安定なことがあるため、
        # まずFROM + SINCE (+ BEFORE) で拾って、あとでPython側で件名・日付判定する。
        status, data = mail.search(None, *search_criteria)
        if status != "OK":
            logging.warning("IMAP search failed")
            return []

        message_ids = data[0].split()
        search_range = f"SINCE={imap_since}"
        if before:
            search_range += f", BEFORE={imap_before}"
        logging.info("IMAP search OK, %s, message count=%d",
                     search_range, len(message_ids))

        for msg_id in message_ids:
            # iCloud は (RFC822) で本文を返さないことがあるため BODY.PEEK[] を利用
            status, msg_data = mail.fetch(msg_id, "(BODY.PEEK[])")
            if status != "OK":
                continue

            # msg_data から生メール本文を取り出す（iCloud は [b'ID (BODY[] {N}', b'...本文...'), b')'] など）
            raw_email = None
            for part in msg_data:
                if isinstance(part, tuple) and len(part) >= 2:
                    candidate = part[1]
                    if isinstance(candidate, (bytes, bytearray)) and len(candidate) > 100:
                        raw_email = candidate
                        break
                if isinstance(part, (bytes, bytearray)) and len(part) > 100 and b"From:" in part:
                    raw_email = part
                    break

            if raw_email is None:
                logging.warning(
                    "Failed to get raw email bytes for msg_id %s, msg_data len=%s",
                    msg_id, [len(p) if isinstance(p, (bytes, bytearray))
                             else repr(p)[:80] for p in msg_data],
                )
                continue

            msg = email.message_from_bytes(raw_email)

            subject = decode_mime_header(msg.get("Subject"))
            from_ = decode_mime_header(msg.get("From"))

            if "payinfo@121.ana.co.jp" not in from_:
                continue
            if "ご利用のお知らせ" not in subject:
                continue

            ana_pay = get_mail_info_from_message(msg)
            if not ana_pay or not ana_pay.email_date:
                continue
            if ana_pay.email_date < after_dt:
                continue
            if before_end and ana_pay.email_date > before_end:
                continue
            ana_pay_list.append(ana_pay)

    ana_pay_list.sort(key=lambda x: x.email_date)
    return ana_pay_list


def get_last_email_date(records: list[dict[str, str]]) -> str:
    """get last email date for mail search"""
    after = "2023/06/28"
    if records:
        # 下から見て、email_date を持つ最後の行だけを対象にする
        for r in reversed(records):
            value = r.get("email_date")
            if not value:
                continue
            try:
                last_email_date = parser.parse(value)
            except (ValueError, TypeError):
                continue
            after = f"{last_email_date:%Y/%m/%d}"
            break
    return after


def mail2spreadsheet(
    worksheet,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """
    iCloud MailからANA Payの利用履歴を取得しスプレッドシートに書き込む

    start_date: YYYY/MM/DD。指定時はスプレッドシート最終日ではなくこの日から取得
    end_date: YYYY/MM/DD。指定時はこの日まで取得（この日を含む）
    """
    records = worksheet.get_all_records()
    logging.info("Records in spreadsheet: %d", len(records))

    if start_date:
        after = start_date
        logging.info("Mail search start (specified): %s", after)
    else:
        after = get_last_email_date(records)
        logging.info("Mail search start (from spreadsheet): %s", after)
    if end_date:
        logging.info("Mail search end (specified): %s", end_date)
    # 既存レコードの重複判定用キー
    # - 文字列のまま比較することで、日付パース失敗による漏れや重複を防ぐ
    # - email_date / date_of_use / amount の3つを組み合わせてユニークキーとする
    existing_keys = set(
        (
            str(r.get("email_date") or ""),
            str(r.get("date_of_use") or ""),
            str(r.get("amount") or ""),
        )
        for r in records
    )

    ana_pay_list = get_anapay_info(after, before=end_date)
    logging.info("ANA Pay emails: %d", len(ana_pay_list))

    count = 0
    rows_to_append: list[list] = []
    for ana_pay in ana_pay_list:
        key = (
            ana_pay.email_date_str,
            ana_pay.date_of_use_str,
            str(ana_pay.amount),
        )
        if key not in existing_keys:
            rows_to_append.append(list(ana_pay.values()))
            existing_keys.add(key)
            count += 1
            logging.info("Record queued for append: %s", ana_pay.values())

    if rows_to_append:
        # まとめて Sheets API を叩くことでレート制限にかかりにくくする
        append_rows_with_retry(
            worksheet, rows_to_append, value_input_option="USER_ENTERED"
        )
        logging.info("Records actually appended to spreadsheet: %d",
                     len(rows_to_append))

    logging.info("Records added to spreadsheet: %d", count)


def login_mf():
    """Login to Money Forward ME.
    流れ:
    1. moneyforward.com/login の「ログイン」リンクで ME ログイン画面へ遷移
    2. メールアドレスのみ入力し「ログインする」をクリック
    3a. 認証コードページに直行する場合: そのまま 4 へ
    3b. パスワード入力ページが挟まる場合: パスワード入力 → ログイン → 認証コードページへ
    4. 認証コード入力ページでユーザーが手入力でコードを入れ「認証する」をクリック
    5. ログイン完了後カンタン入力フォームが表示されるまで待つ
    """

    email_addr = os.getenv("MF_EMAIL")
    password = os.getenv("MF_PASSWORD")

    logging.info("Login to moneyforward")
    # Firefox 未インストール時は Selenium Manager が応答せずハングするため Chrome を使用
    helium.start_chrome(MF_URL)
    # 1. トップの「ログイン」リンクで ME ログイン画面へ
    try:
        helium.wait_until(helium.Link("ログイン").exists, timeout_secs=20)
        helium.click(helium.Link("ログイン"))
    except Exception:
        helium.wait_until(helium.Button("ログイン").exists, timeout_secs=20)
        helium.click(helium.Button("ログイン"))
    # 2. メールアドレスだけ入力し「ログインする」をクリック
    helium.wait_until(helium.TextField("メールアドレス").exists, timeout_secs=15)
    helium.write(email_addr, into="メールアドレス")
    helium.click(helium.Button("ログインする"))

    # 3. 次の画面: 認証コード直行 or パスワード入力が挟まる
    def on_auth_page_or_password_page():
        return helium.Button("ログインする").exists() or helium.TextField("パスワード").exists()

    helium.wait_until(on_auth_page_or_password_page, timeout_secs=15)
    if helium.TextField("パスワード").exists():
        logging.info("Password page detected, entering password")
        helium.write(password, into="パスワード")
        helium.click(helium.Button("ログインする"))
        helium.wait_until(helium.Button("認証する").exists, timeout_secs=15)

    # 4. 認証コードページ → ユーザーが手入力でコード入力・「認証する」クリック
    logging.info(
        "Please enter the authentication code in the browser and click 認証する"
    )
    # 5. ログイン完了（家計簿画面）でカンタン入力フォームが表示されるまで待つ（最大2分）
    helium.wait_until(
        helium.TextField("金額を入力してください").exists,
        timeout_secs=120,
    )


def _amount_field_value(driver) -> str:
    """カンタン入力の金額欄の現在値を返す。"""
    return driver.execute_script(
        "var el = document.querySelector("
        "  'input[placeholder=\"金額を入力してください\"]'"
        ");"
        "return el ? (el.value || '') : '';"
    ) or ""


def _select_expense_source(
    driver,
    preferred: str = "ANA Pay",
    fallback: str = "なし",
) -> str:
    """カンタン入力の支出元を選択。preferred が無ければ fallback。戻り値は選んだ表示名。"""
    select_el = driver.find_element("id", "user_asset_act_sub_account_id_hash")
    sel = Select(select_el)

    def find_option(prefix: str):
        for opt in sel.options:
            label = (opt.text or "").strip()
            if label.startswith(prefix):
                return opt.get_attribute("value"), label
        return None, None

    value, label = find_option(preferred)
    if value is None:
        value, label = find_option(fallback)
        if value is None:
            raise RuntimeError(
                f"支出元に '{preferred}' も '{fallback}' も見つかりません"
            )
        logging.warning(
            "支出元 '%s' がないため '%s' にフォールバック", preferred, label
        )

    sel.select_by_value(value)
    return label


def add_mf_record(
    dt: datetime,
    amount: int,
    store: str,
    store_info: dict | None,
    *,
    expense_source: str = "ANA Pay",
):
    """カンタン入力フォームに日付・金額・内容を入力し保存。

    支出元は expense_source（デフォルト ANA Pay）。無ければ「なし」へフォールバック。
    """
    # カンタン入力フォームが表示されていることを確認
    helium.wait_until(helium.TextField("金額を入力してください").exists, timeout_secs=10)
    # 日付: hidden と表示用 label を JS で設定（カレンダーウィジェットのため）
    date_str = f"{dt:%Y/%m/%d}"
    driver = helium.get_driver()
    driver.execute_script(
        "var d = arguments[0];"
        "var el = document.getElementById('js-cf-manual-payment-entry-updated-at');"
        "var label = document.getElementById('js-cf-manual-payment-entry-updated-at-label');"
        "if(el) el.value = d; if(label) label.textContent = d;"
        "var p = document.getElementById('js-cf-manual-payment-entry-calendar');"
        "if(p) p.setAttribute('data-date', d);",
        date_str,
    )
    # 金額（placeholder「金額を入力してください」の input）
    helium.write(str(amount), into="金額を入力してください")
    # 支出元
    source = _select_expense_source(driver, preferred=expense_source)
    # 内容（placeholder「内容を入力してください(任意)」の input）
    helium.write(store, into="内容を入力してください(任意)")

    # 保存する（ID 指定。文言マッチだと別要素を掴むことがある）
    submit = driver.find_element(
        "id", "js-cf-manual-payment-entry-submit-button"
    )
    submit.click()

    def save_confirmed():
        # 保存成功後は金額欄がクリアされる想定。失敗時は入力値が残る。
        return _amount_field_value(driver) == ""

    try:
        helium.wait_until(save_confirmed, timeout_secs=10)
    except Exception as exc:
        raise RuntimeError(
            f"MF save not confirmed for {date_str}, {amount}, {store}"
        ) from exc

    logging.info(
        "Record added to moneyforward: %s, %s, %s (支出元=%s)",
        date_str,
        amount,
        store,
        source,
    )
    time.sleep(0.3)


def spreadsheet2mf(
    worksheet,
    store_dict: dict[str, dict[str, str]],
    limit: int | None = None,
) -> None:
    """スプレッドシートからmoneyforwardに書き込む。

    limit: 処理する未登録件数の上限（検証用）。None なら全件。
    """

    records = worksheet.get_all_records()

    login_mf()
    added = 0
    for count, record in enumerate(records):
        if limit is not None and added >= limit:
            logging.info("Reached limit=%d, stopping", limit)
            break

        # 'mf' 列がない／空の場合でも KeyError にならないようにしつつ、
        # 'done' 以外を「未処理」とみなす
        mf_status = (record.get("mf") or "").lower()
        if mf_status == "done":
            continue

        date_text = record.get("date_of_use")
        amount_text = record.get("amount")
        store = record.get("store")

        # 必須カラムが欠けている行はスキップ
        if not date_text or not amount_text or not store:
            logging.warning("Skip record due to missing fields: %s", record)
            continue

        try:
            date_of_use = parser.parse(str(date_text))
        except (ValueError, TypeError) as e:
            logging.warning(
                "Failed to parse date_of_use '%s': %s", date_text, e)
            continue

        try:
            amount = int(str(amount_text))
        except (ValueError, TypeError) as e:
            logging.warning("Failed to parse amount '%s': %s", amount_text, e)
            continue

        try:
            add_mf_record(date_of_use, amount, store, store_dict.get(store))
        except RuntimeError as e:
            logging.error("%s", e)
            logging.error(
                "Stop without marking spreadsheet done "
                "(row %d). Fix UI/save then retry.",
                count + 2,
            )
            break

        # 先頭行がヘッダなので +2
        update_cell_with_retry(worksheet, count + 2, 5, "done")
        time.sleep(0.2)
        added += 1

    helium.kill_browser()
    logging.info("Records added to moneyforward: %d", added)


def parse_args():
    parser = argparse.ArgumentParser(
        description="ANA Pay: iCloud Mail → Spreadsheet → Money Forward",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["mail", "mf", "all"],
        default=os.getenv("ANAPAY2MF_MODE", "all"),
        help="mail=メール→スプシ, mf=スプシ→MF (default), all=両方。環境変数 ANAPAY2MF_MODE でも指定可",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="mf/all 時に処理する未登録件数の上限（検証用）",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.info("Starting anapay2mf_icloud-mail (mode=%s)", args.mode)
    gc = gspread.oauth(
        credentials_filename="credentials.json",
        authorized_user_filename="token.json",
    )

    sheet = gc.open_by_key(SHEET_ID)
    anapay_sheet = sheet.worksheet("ANAPay")

    if args.mode in ("mail", "all"):
        logging.info("Running mail2spreadsheet")
        mail2spreadsheet(
            anapay_sheet,
            start_date=MAIL_SYNC_START_DATE,
            end_date=MAIL_SYNC_END_DATE,
        )

    if args.mode in ("mf", "all"):
        store_sheet = sheet.worksheet("ANAPayStore")
        store_dict = {store["store"]                      : store for store in store_sheet.get_all_records()}
        logging.info("Running spreadsheet2mf (limit=%s)", args.limit)
        spreadsheet2mf(anapay_sheet, store_dict, limit=args.limit)


if __name__ == "__main__":
    main()
