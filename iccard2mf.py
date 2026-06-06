"""
ICカード利用履歴（CSV）をマネーフォワード ME の家計簿手入力モーダル経由で登録する。

設計: ic-card-csv-to-mf_design-doc.md
要件: ic-card-csv-to-mf_requirements.md
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import tempfile
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv

try:
    load_dotenv()
except OSError:
    logging.warning("Could not load .env file")

MF_LOGIN_URL = os.getenv("MF_LOGIN_URL", "https://moneyforward.com/login")
MF_CF_URL = os.getenv("MF_CF_URL", "https://moneyforward.com/cf")
DEFAULT_ACCOUNT_NAME = os.getenv("MF_ACCOUNT_NAME", "SUGOCA")

CSV_COLUMNS = ("利用日", "利用内容", "利用金額", "大分類", "小分類", "マネフォ登録日")

format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=format, level=logging.INFO)


@dataclass
class ICRecord:
    row_index: int
    use_date: date
    description: str
    amount: int
    large_category: str
    small_category: str
    mf_registered_at: date | None = None

    @property
    def is_income(self) -> bool:
        return self.large_category == "収入"


def _parse_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_amount(value: str) -> int | None:
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _read_csv_rows(csv_path: Path) -> tuple[list[str], list[list[str]]]:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            with csv_path.open(encoding=encoding, newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
            if not rows:
                raise ValueError("CSV is empty")
            return rows[0], rows[1:]
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Failed to decode CSV: {csv_path}")


def load_records(csv_path: Path, limit: int = 100) -> list[ICRecord]:
    header, data_rows = _read_csv_rows(csv_path)
    missing = [col for col in CSV_COLUMNS if col not in header]
    if missing:
        raise ValueError(f"CSV header missing columns: {missing}")

    col = {name: header.index(name) for name in CSV_COLUMNS}
    records: list[ICRecord] = []

    for i, row in enumerate(data_rows):
        if len(records) >= limit:
            break

        padded = row + [""] * (len(header) - len(row))
        registered = _parse_date(padded[col["マネフォ登録日"]])
        if registered is not None:
            continue

        use_date = _parse_date(padded[col["利用日"]])
        amount = _parse_amount(padded[col["利用金額"]])
        description = padded[col["利用内容"]].strip()
        large_category = padded[col["大分類"]].strip()
        small_category = padded[col["小分類"]].strip()

        if not use_date or amount is None or not description:
            logging.warning("Skip row %d due to missing/invalid fields: %s", i + 2, row)
            continue

        if amount == 0:
            logging.warning(
                "Skip row %d due to zero amount: %s %s",
                i + 2,
                padded[col["利用日"]],
                description,
            )
            continue

        records.append(
            ICRecord(
                row_index=i,
                use_date=use_date,
                description=description,
                amount=amount,
                large_category=large_category,
                small_category=small_category,
            )
        )

    return records


def mark_registered(csv_path: Path, row_index: int, registered_at: date) -> None:
    header, data_rows = _read_csv_rows(csv_path)
    col_registered = header.index("マネフォ登録日")
    registered_str = f"{registered_at:%Y/%m/%d}"

    if row_index < 0 or row_index >= len(data_rows):
        raise IndexError(f"Invalid row_index: {row_index}")

    row = data_rows[row_index]
    if len(row) < len(header):
        row.extend([""] * (len(header) - len(row)))
    row[col_registered] = registered_str

    fd, tmp_path = tempfile.mkstemp(
        suffix=".csv",
        dir=csv_path.parent,
        text=True,
    )
    os.close(fd)
    try:
        with open(tmp_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data_rows)
        os.replace(tmp_path, csv_path)
    except Exception:
        os.unlink(tmp_path)
        raise

    logging.info("Updated CSV row %d: マネフォ登録日=%s", row_index + 2, registered_str)


def _import_browser_deps():
    import helium
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import Select

    return helium, By, Select


def _driver():
    return _import_browser_deps()[0].get_driver()


def login_mf() -> None:
    """Login to Money Forward ME (based on anapay2mf_icloud-mail.py)."""
    helium, _, _ = _import_browser_deps()
    email_addr = os.getenv("MF_EMAIL")
    password = os.getenv("MF_PASSWORD")
    if not email_addr:
        raise ValueError("MF_EMAIL is not set")

    logging.info("Login to moneyforward")
    helium.start_chrome(MF_LOGIN_URL)
    try:
        helium.wait_until(helium.Link("ログイン").exists, timeout_secs=20)
        helium.click(helium.Link("ログイン"))
    except Exception:
        helium.wait_until(helium.Button("ログイン").exists, timeout_secs=20)
        helium.click(helium.Button("ログイン"))

    helium.wait_until(helium.TextField("メールアドレス").exists, timeout_secs=15)
    helium.write(email_addr, into="メールアドレス")
    helium.click(helium.Button("ログインする"))

    def on_auth_page_or_password_page():
        return helium.Button("ログインする").exists() or helium.TextField("パスワード").exists()

    helium.wait_until(on_auth_page_or_password_page, timeout_secs=15)
    if helium.TextField("パスワード").exists():
        if not password:
            raise ValueError("MF_PASSWORD is not set")
        logging.info("Password page detected, entering password")
        helium.write(password, into="パスワード")
        helium.click(helium.Button("ログインする"))
        helium.wait_until(helium.Button("認証する").exists, timeout_secs=15)

    logging.info(
        "Please enter the authentication code in the browser and click 認証する"
    )

    def login_complete():
        driver = helium.get_driver()
        url = driver.current_url
        if "login" in url or helium.Button("認証する").exists():
            return False
        return True

    helium.wait_until(login_complete, timeout_secs=120)


def navigate_to_cf() -> None:
    helium, _, _ = _import_browser_deps()
    driver = helium.get_driver()
    driver.get(MF_CF_URL)
    helium.wait_until(helium.Button("手入力").exists, timeout_secs=30)
    logging.info("Navigated to %s", MF_CF_URL)


def switch_payment_tab(is_income: bool) -> None:
    _, By, _ = _import_browser_deps()
    driver = _driver()
    css = "input.plus-payment" if is_income else "input.minus-payment"
    radio = driver.find_element(By.CSS_SELECTOR, css)
    radio.find_element(By.XPATH, "./..").click()
    time.sleep(0.3)


def set_date(use_date: date) -> None:
    _, By, _ = _import_browser_deps()
    date_str = f"{use_date:%Y/%m/%d}"
    driver = _driver()
    el = driver.find_element(By.ID, "updated-at")
    driver.execute_script("arguments[0].value = arguments[1];", el, date_str)


def set_amount(amount: int) -> None:
    _, By, _ = _import_browser_deps()
    driver = _driver()
    el = driver.find_element(By.ID, "appendedPrependedInput")
    el.clear()
    el.send_keys(str(amount))


def select_account(account_name: str) -> None:
    _, By, Select = _import_browser_deps()
    driver = _driver()
    select_el = driver.find_element(By.ID, "user_asset_act_sub_account_id_hash")
    sel = Select(select_el)
    for option in sel.options:
        if option.text.startswith(account_name):
            sel.select_by_visible_text(option.text)
            return
    raise ValueError(f"Account not found: {account_name}")


def select_category(large: str, small: str) -> bool:
    if not large or not small:
        return False

    _, By, _ = _import_browser_deps()
    driver = _driver()
    try:
        driver.find_element(By.ID, "js-large-category-selected").click()
        time.sleep(0.3)

        found_large = None
        for link in driver.find_elements(By.CSS_SELECTOR, "a.l_c_name"):
            if link.text.strip() == large:
                found_large = link
                break
        if not found_large:
            logging.warning("Category not found: 大分類=%s", large)
            return False

        found_large.click()
        time.sleep(0.3)

        driver.find_element(By.ID, "js-middle-category-selected").click()
        time.sleep(0.3)

        for link in driver.find_elements(By.CSS_SELECTOR, "a.m_c_name"):
            if link.text.strip() == small:
                link.click()
                return True

        logging.warning("Category not found: 小分類=%s (大分類=%s)", small, large)
        return False
    except Exception as exc:
        logging.warning("Failed to select category: %s", exc)
        return False


def set_content(description: str) -> None:
    _, By, _ = _import_browser_deps()
    driver = _driver()
    el = driver.find_element(By.ID, "js-content-field")
    el.clear()
    el.send_keys(description)


def open_manual_entry_modal(is_first: bool) -> None:
    helium, _, _ = _import_browser_deps()
    if is_first:
        helium.click(helium.Button("手入力"))
        helium.wait_until(helium.S("#user_asset_act_new").exists, timeout_secs=10)
    else:
        helium.click(helium.S("#confirmation-button"))
        time.sleep(0.5)


def fill_record(record: ICRecord, account_name: str) -> None:
    switch_payment_tab(record.is_income)
    set_date(record.use_date)
    set_amount(record.amount)
    select_account(account_name)
    select_category(record.large_category, record.small_category)
    set_content(record.description)


def save_and_wait() -> None:
    helium, By, _ = _import_browser_deps()
    driver = helium.get_driver()
    driver.find_element(By.ID, "submit-button").click()

    def save_confirmed():
        try:
            alert = driver.find_element(By.ID, "alert-area")
            return "入力を保存しました" in alert.text
        except Exception:
            return False

    helium.wait_until(save_confirmed, timeout_secs=10)


def continue_or_close(has_more: bool) -> None:
    helium, _, _ = _import_browser_deps()
    if has_more:
        helium.click(helium.S("#confirmation-button"))
        time.sleep(0.5)
    else:
        helium.click(helium.S("#cancel-button"))
        time.sleep(0.3)


def csv2mf(
    csv_path: Path,
    records: list[ICRecord],
    account_name: str = DEFAULT_ACCOUNT_NAME,
) -> int:
    if not records:
        logging.info("No pending records to process")
        return 0

    login_mf()
    navigate_to_cf()

    added = 0
    today = date.today()
    total = len(records)

    for idx, record in enumerate(records):
        kind = "income" if record.is_income else "expense"
        logging.info(
            "Adding record [%d/%d]: %s %s %d円 (%s)",
            idx + 1,
            total,
            record.use_date,
            record.description,
            record.amount,
            kind,
        )

        open_manual_entry_modal(is_first=(idx == 0))
        fill_record(record, account_name)
        save_and_wait()
        mark_registered(csv_path, record.row_index, today)
        added += 1
        logging.info(
            "Record saved: %s, %d, %s",
            f"{record.use_date:%Y/%m/%d}",
            record.amount,
            record.description,
        )
        continue_or_close(has_more=(idx < total - 1))

    helium, _, _ = _import_browser_deps()
    helium.kill_browser()
    return added


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="IC card CSV → Money Forward ME (manual entry modal)",
    )
    parser.add_argument("csv_path", type=Path, help="Path to input CSV")
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Max records per run (default: 100)",
    )
    parser.add_argument(
        "--account",
        default=DEFAULT_ACCOUNT_NAME,
        help=f"Expense source / income destination (default: {DEFAULT_ACCOUNT_NAME})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load CSV and list pending records without MF automation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = args.csv_path.resolve()

    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    records = load_records(csv_path, limit=args.limit)
    logging.info(
        "Loaded %d pending records (processing up to %d)",
        len(records),
        args.limit,
    )

    if args.dry_run:
        for i, record in enumerate(records, start=1):
            kind = "収入" if record.is_income else "支出"
            logging.info(
                "[%d] row=%d %s %s %d円 大=%s 小=%s (%s)",
                i,
                record.row_index + 2,
                record.use_date,
                record.description,
                record.amount,
                record.large_category or "-",
                record.small_category or "-",
                kind,
            )
        return

    added = csv2mf(csv_path, records, account_name=args.account)
    logging.info("Records added to moneyforward: %d", added)


if __name__ == "__main__":
    main()
