"""
ワンバンク利用履歴（CSV）をマネーフォワード ME の家計簿手入力モーダル経由で登録する。

MF 登録ロジックは iccard2mf.py を流用（CSV スキーマ・UI 操作は同一）。
CSV 生成: docs/onebank-ocr-prompt.md
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from iccard2mf import csv2mf, load_records

try:
    load_dotenv()
except OSError:
    logging.warning("Could not load .env file")

DEFAULT_ACCOUNT_NAME = os.getenv("ONEBANK_MF_ACCOUNT_NAME", "ワンバンク")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="One Bank CSV → Money Forward ME (manual entry modal)",
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
