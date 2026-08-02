"""支出元 ANA Pay / なし のダミー登録動作確認。

使い方:
  python scripts/verify_expense_source.py

ブラウザで MFA 認証後、今日日付で 1円のダミーを 2 件登録する。
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODULE_PATH = ROOT / "anapay2mf_icloud-mail.py"


def _load_anapay():
    spec = importlib.util.spec_from_file_location("anapay2mf", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    mod = _load_anapay()
    helium = mod.helium

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cases = [
        ("ANA Pay", 1, "[TEST] ANA Pay source"),
        ("なし", 1, "[TEST] none source"),
    ]

    logging.info("Login then register %d dummy expenses", len(cases))
    mod.login_mf()

    for preferred, amount, store in cases:
        logging.info("=== Registering: preferred=%s store=%s ===", preferred, store)
        mod.add_mf_record(
            today,
            amount,
            store,
            None,
            expense_source=preferred,
        )

    logging.info("Done. Check MF daily list for the 2 [TEST] rows.")
    helium.kill_browser()


if __name__ == "__main__":
    main()
