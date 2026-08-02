"""
対象ページ：家計簿：https://moneyforward.com/cf#daily_info
- 対象月を移動させる。（初期値：2025/06、終了値：2026/03）
- 保有金融機関が「なし」のものを、「ANA Pay」に変更する

# 対象付の移動ボタン
## 前の月へ
<span class="fc-button fc-button-prev fc-state-default fc-corner-left fc-corner-right"><span class="fc-button-inner"><span class="fc-button-content">&nbsp;◄&nbsp;</span><span class="fc-button-effect"><span></span></span></span></span>

## 次の月へ
<span class="fc-button fc-button-next fc-state-default fc-corner-left fc-corner-right"><span class="fc-button-inner"><span class="fc-button-content">&nbsp;►&nbsp;</span><span class="fc-button-effect"><span></span></span></span></span>

# HTML
## 表タイトル
<span class="fc-header-title"><h2>2025/6/1 - 2025/6/30</h2></span>

## ヘッダー
<thead>
<tr>
<th class="calc" style="vertical-align:middle;" title="" data-original-title="チェックを外すと、月々の収支計算の対象外とすることができます。">
計算
<br>
対象
<br>
<i class="icon-question-sign"></i>
</th>
<th class="date table-sortable:string table-sortable                           " style="vertical-align:-30px;" title="Click to sort">日付</th>
<th class="note table-sortable:string table-sortable" style="vertical-align:top;" title="Click to sort">内容</th>
<th class="amnt table-sortable:numeric table-sortable" style="vertical-align:top;" title="Click to sort">金額（円）</th>
<th class="serv table-sortable:string table-sortable table-sorted-desc" style="vertical-align:top;" title="Click to sort">保有金融機関</th>
<th class="lctg table-filterable             " title="" data-original-title="内容よりマネーフォワードが自動分類した大項目が表示されます。ユーザーによる変更が可能です。">
大項目
<i class="icon-question-sign"></i>
<br>
<select onchange="Table.filter(this,this)" onclick="Table.cancelBubble(event)" class="table-autofilter js-table-autofilter-select " style="width:80%;"><option value="">全て</option><option value="/収入/">収入</option><option value="/食費/">食費</option><option value="/日用品/">日用品</option><option value="/趣味・娯楽/">趣味・娯楽</option><option value="/交通費/">交通費</option><option value="/教養・教育/">教養・教育</option><option value="/特別な支出/">特別な支出</option><option value="/現金・カード/">現金・カード</option><option value="/通信費/">通信費</option><option value="/税・社会保障/">税・社会保障</option><option value="/その他/">その他</option><option value="/未分類/">未分類</option></select></th>
<th class="mctg table-filterable" title="" data-original-title="内容よりマネーフォワードが自動分類した中項目が表示されます。ユーザーによる変更が可能です。">
中項目
<i class="icon-question-sign"></i>
<br>
<select onchange="Table.filter(this,this)" onclick="Table.cancelBubble(event)" class="table-autofilter js-table-autofilter-select " style="width:80%;"><option value="">全て</option><option value="/給与/">給与</option><option value="/その他入金/">その他入金</option><option value="/食費/">食費</option><option value="/食料品/">食料品</option><option value="/外食/">外食</option><option value="/カフェ/">カフェ</option><option value="/日用品/">日用品</option><option value="/映画・音楽・ゲーム/">映画・音楽・ゲーム</option><option value="/旅行/">旅行</option><option value="/飛行機/">飛行機</option><option value="/書籍/">書籍</option><option value="/家具・家電/">家具・家電</option><option value="/ATM引き出し/">ATM引き出し</option><option value="/カード引き落とし/">カード引き落とし</option><option value="/電子マネー/">電子マネー</option><option value="/携帯電話/">携帯電話</option><option value="/情報サービス/">情報サービス</option><option value="/その他通信費/">その他通信費</option><option value="/所得税・住民税/">所得税・住民税</option><option value="/その他税・社会保障/">その他税・社会保障</option><option value="/雑費/">雑費</option><option value="/未分類/">未分類</option></select></th>
<th class="memo" style="vertical-align:middle;" title="" data-original-title="内容自由のメモです。例)昼食代, 文房具代">
メモ
<i class="icon-question-sign"></i>
</th>
<th class="calc" style="vertical-align:middle;" title="" data-original-title="収入でも支出でもない、口座間のお金の移動の際に選択ください。振替を選択すると、家計の計算対象外となります。">
振替
<i class="icon-question-sign"></i>
</th>
<th class="delete" style="vertical-align:middle;" title="" data-original-title="手入力した入出金を削除します。">
削除
<i class="icon-question-sign"></i>
</th>
</tr>
</thead>

## 各レコード
<tr class="transaction_list js-cf-edit-container target-active" id="js-transaction-1830826969059557995">
<td class="calc" data-original-title="" title="">
<form accept-charset="UTF-8" action="/cf/update" class="new_user_asset_act" id="new_user_asset_act" method="post">
<input value="1830826969059557995" type="hidden" name="user_asset_act[id]" id="user_asset_act_id">
<input type="hidden" name="original_amount" id="original_amount" value="-480.0">
<input class="h_l_ctg" income="-1" value="0" type="hidden" name="user_asset_act[large_category_id]" id="user_asset_act_large_category_id">
<input class="h_m_ctg" income="-1" value="0" type="hidden" name="user_asset_act[middle_category_id]" id="user_asset_act_middle_category_id">
<input type="hidden" name="user_asset_act[sub_account_id_hash]" id="user_asset_act_sub_account_id_hash">
<input value="user_asset_act" type="hidden" name="user_asset_act[table_name]" id="user_asset_act_table_name">
<input value="0" type="hidden" name="user_asset_act[is_income]" id="user_asset_act_is_income">
<input value="1" type="hidden" name="user_asset_act[is_target]" id="user_asset_act_is_target">
<i class="icon-check icon-large js-v-is-target"></i>
<div class="form hide">
<input class="js-form-field-memo" type="text" name="user_asset_act[memo]" id="user_asset_act_memo">
<input class="js-form-field-updated-at" value="2025/06/15" type="text" name="user_asset_act[updated_at]" id="user_asset_act_updated_at">
<input class="js-form-field-content" value="基山ＰＡ上り／ｉＤ" type="text" name="user_asset_act[content]" id="user_asset_act_content">
<input class="js-form-field-amount" value="-480" type="text" name="user_asset_act[amount]" id="user_asset_act_amount">
<select class="js-form-field-sub-account-id-hash" style="width: 120px;" name="user_asset_act[sub_account_id_hash]" id="user_asset_act_sub_account_id_hash"><option value="BH0jU4fPrd4yURWBiTo6lOP1NLtSA6famnN3av4YPdU">SUGOCA   (836円)</option>
<option value="CbjEnh8DkcrJuJxMVyjrAIHMaq9xtmLvH513-Fwzfc8">PayPay   (-33,800円)</option>
<option value="99-juGc_NqX5XirCki0-o4P8nURQMeonTbtskMBhyC4">ANA Pay   (-10,071円)</option>
<option selected="selected" value="0">なし</option></select>
</div>
</form>
</td>
<td class="date form-switch-td" data-table-sortable-value="2025/06/15-1830826969059557995" data-original-title="クリックして編集し、Enterキーを押せば変更出来ます。">
<div class="noform">
<span>06/15(日)</span>
<i class="icon-pencil pull-right"></i></div>
<div class="form hide">
<input class="v_updated_at" value="2025/06/15" type="text" name="user_asset_act[updated_at]" id="user_asset_act_updated_at">
</div>
</td>
<td class="content form-switch-td" data-original-title="クリックして編集し、Enterキーを押せば変更出来ます。">
<div class="noform">
<span>基山ＰＡ上り／ｉＤ</span>
<i class="icon-pencil pull-right"></i></div>
<div class="form hide">
<input class="v_content" size="8" value="基山ＰＡ上り／ｉＤ" type="text" name="user_asset_act[content]" id="user_asset_act_content">
</div>
</td>
<td class="number amount form-switch-td minus-color" title="" data-original-title="クリックして編集し、Enterキーを押せば変更出来ます。">
<div class="noform">
<span>-480</span>
<i class="icon-pencil"></i>
</div>
<div class="form hide">
<input class="v_amount" size="10" value="-480" type="text" name="user_asset_act[amount]" id="user_asset_act_amount">
</div>
</td>
<td class="sub_account_id_hash form-switch-td calc" style="text-align: left;" title="" data-original-title="クリックして編集し、Enterキーを押せば変更出来ます。">
<div class="noform">
<span>なし</span>
<i class="icon-pencil pull-right"></i></div>
<div class="form hide">
<select class="v_sub_account_id_hash" style="width: 120px;" name="user_asset_act[sub_account_id_hash]" id="user_asset_act_sub_account_id_hash"><option value="BH0jU4fPrd4yURWBiTo6lOP1NLtSA6famnN3av4YPdU">SUGOCA   (836円)</option>
<option value="CbjEnh8DkcrJuJxMVyjrAIHMaq9xtmLvH513-Fwzfc8">PayPay   (-33,800円)</option>
<option value="99-juGc_NqX5XirCki0-o4P8nURQMeonTbtskMBhyC4">ANA Pay   (-10,071円)</option>
<option selected="selected" value="0">なし</option></select>
</div>
</td>
<td class="lctg" data-original-title="" title="">
<div class="btn-group btn_l_ctg">
<a class="btn btn-small dropdown-toggle v_l_ctg btn-danger" data-toggle="dropdown">
未分類
<span class="caret"></span></a>
</div>
</td>
<td class="mctg" data-original-title="" title="">
<div class="btn-group btn_m_ctg">
<a class="btn btn-small dropdown-toggle v_m_ctg" data-toggle="dropdown">
未分類
<span class="caret"></span></a>
</div>
</td>
<td class="memo form-switch-td" data-original-title="クリックして編集し、Enterキーを押せば変更出来ます。" title="">
<div class="noform">
<span></span>
<i class="icon-pencil pull-right"></i></div>
<div class="form hide">
<input class="v_memo" type="text" name="user_asset_act[memo]" id="user_asset_act_memo">
</div>
</td>
<td class="calc" title="" data-original-title="支出元のない収支を振替に切り替えることは出来ません。"></td>
<td class="delete" data-original-title="" title=""><a data-confirm="手入力項目を削除してもよろしいですか？" data-remote="true" rel="nofollow" data-method="delete" href="/cf/1830826969059557995?from=2025/06/15&amp;sorted=serv"><i class="icon-trash icon-large black"></i></a></td>
</tr>


"""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import date

import helium
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from selenium.common.exceptions import (StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()

MF_LOGIN_URL = "https://moneyforward.com/login"
MF_CF_DAILY_INFO_URL = "https://moneyforward.com/cf#daily_info"

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)


@dataclass(frozen=True)
class TargetRange:
    start_ym: str  # YYYY/MM
    end_ym: str  # YYYY/MM (inclusive)

    def months(self) -> list[str]:
        start = _parse_ym(self.start_ym)
        end = _parse_ym(self.end_ym)
        if start > end:
            start, end = end, start
        months: list[str] = []
        cur = start
        while cur <= end:
            months.append(f"{cur.year:04d}/{cur.month:02d}")
            cur = cur + relativedelta(months=1)
        return months


def _parse_ym(ym: str) -> date:
    m = re.fullmatch(r"(\d{4})/(\d{1,2})", ym.strip())
    if not m:
        raise ValueError(f"Invalid ym format (expected YYYY/MM): {ym!r}")
    y = int(m.group(1))
    mo = int(m.group(2))
    return date(y, mo, 1)


def _wait_for_daily_info_loaded(driver, timeout: int = 30) -> None:
    wait = WebDriverWait(driver, timeout)
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "tr.transaction_list")))
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "span.fc-header-title h2")))
    wait.until(lambda d: _try_get_displayed_month_ym(d) is not None)


def _get_displayed_month_ym_with_wait(driver, timeout: int = 30) -> str:
    """
    表タイトルが一時的に不定（Loading/空/DOM更新中）でも落ちないよう、
    パース可能になるまで待って YYYY/MM を返す。
    """
    WebDriverWait(driver, timeout).until(lambda d: _try_get_displayed_month_ym(d) is not None)
    ym = _try_get_displayed_month_ym(driver)
    if ym is None:
        raise TimeoutException("Failed to parse displayed month title")
    return ym


def _get_displayed_month_ym(driver) -> str:
    """
    表タイトル（例: "2025/6/1 - 2025/6/30"）から表示中の年月 (YYYY/MM) を取得する。
    """
    ym = _try_get_displayed_month_ym(driver)
    if ym is None:
        title_el = driver.find_element(By.CSS_SELECTOR, "span.fc-header-title h2")
        title = (title_el.text or "").strip()
        raise ValueError(f"Unexpected title format: {title!r}")
    return ym


def _try_get_displayed_month_ym(driver) -> str | None:
    """
    画面遷移直後などでタイトルが 'Loading...' の場合があるので、
    パースできる状態になるまで待つための安全版。
    """
    try:
        title_el = driver.find_element(By.CSS_SELECTOR, "span.fc-header-title h2")
    except StaleElementReferenceException:
        return None
    except Exception:
        return None

    try:
        title = (title_el.text or "").strip()
    except StaleElementReferenceException:
        return None

    if not title or title.lower() == "loading...":
        return None

    m = re.search(
        r"(\d{4})/(\d{1,2})/(\d{1,2})\s*-\s*(\d{4})/(\d{1,2})/(\d{1,2})",
        title,
    )
    if not m:
        return None
    y = int(m.group(1))
    mo = int(m.group(2))
    return f"{y:04d}/{mo:02d}"


def _click_month_nav(driver, direction: str) -> None:
    """
    direction: "prev" or "next"
    """
    if direction not in {"prev", "next"}:
        raise ValueError("direction must be 'prev' or 'next'")
    btn = driver.find_element(By.CSS_SELECTOR, f"span.fc-button.fc-button-{direction}")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    btn.click()


def goto_month(target_ym: str, *, max_steps: int = 48) -> None:
    """
    HTML上の表示月を見ながら prev/next で target_ym まで移動する。
    """
    driver = helium.get_driver()
    target = _parse_ym(target_ym)
    for _ in range(max_steps):
        _wait_for_daily_info_loaded(driver, timeout=30)
        cur_ym = _get_displayed_month_ym_with_wait(driver, timeout=30)
        cur = _parse_ym(cur_ym)
        if cur == target:
            return

        direction = "prev" if cur > target else "next"
        before = cur_ym
        _click_month_nav(driver, direction)
        WebDriverWait(driver, 30).until(
            lambda d: (
                (ym := _try_get_displayed_month_ym(d)) is not None
                and ym != before
            )
        )

    raise TimeoutException(f"Failed to navigate to {target_ym} within {max_steps} steps")


def login_mf() -> None:
    """
    Money Forward ME にログインする。
    `anapay2mf_icloud-mail.py` の手順に合わせる（認証コードは手動入力）。
    """
    email_addr = os.getenv("MF_EMAIL")
    password = os.getenv("MF_PASSWORD")
    if not email_addr or not password:
        raise ValueError("環境変数 MF_EMAIL / MF_PASSWORD を設定してください")

    logging.info("Login to moneyforward")
    # Firefox 未インストール時は Selenium Manager が失敗するため Chrome を使用
    # （anapay2mf_icloud-mail.py と同じ）
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
        logging.info("Password page detected, entering password")
        helium.write(password, into="パスワード")
        helium.click(helium.Button("ログインする"))
        helium.wait_until(helium.Button("認証する").exists, timeout_secs=15)

    logging.info("ブラウザで認証コードを入力して「認証する」を押してください")


def _ensure_logged_in_ready(timeout_secs: int = 120) -> None:
    """
    ログイン完了後、家計簿画面が使える状態になるまで待つ。
    """
    driver = helium.get_driver()
    wait = WebDriverWait(driver, timeout_secs)
    wait.until(
        EC.any_of(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "tr.transaction_list")),
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#js-cf-manual-payment-entry-updated-at")),
        )
    )


def _visible_account_select(sub_td):
    """編集中の保有金融機関 select が可視なら要素を返し、なければ None。"""
    try:
        selects = sub_td.find_elements(
            By.CSS_SELECTOR, "select.v_sub_account_id_hash"
        )
        for s in selects:
            if s.is_displayed():
                return s
    except StaleElementReferenceException:
        return None
    except Exception:
        return None
    return None


def _select_ana_pay_in_row(
    driver,
    row_el,
    *,
    row_id: str | None = None,
    ana_pay_label: str = "ANA Pay",
) -> bool:
    """
    1レコード行の「保有金融機関」が「なし」なら ANA Pay を選択して保存する。
    成功時 True。
    """
    rid = row_id or (row_el.get_attribute("id") or "")

    try:
        sub_td = row_el.find_element(By.CSS_SELECTOR, "td.sub_account_id_hash")
    except Exception:
        logging.warning("sub_account td not found (id=%s)", rid)
        return False

    # 表示状態（noform）で現在値を確認
    try:
        current = sub_td.find_element(
            By.CSS_SELECTOR, "div.noform span").text.strip()
    except Exception:
        current = ""

    if current != "なし":
        return False

    # 編集状態へ（td 全体より表示中の span / pencil を優先）
    clicked = False
    for css in (
        "div.noform span",
        "div.noform i.icon-pencil",
        "div.noform",
    ):
        try:
            el = sub_td.find_element(By.CSS_SELECTOR, css)
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        try:
            sub_td.click()
            clicked = True
        except Exception as e:
            logging.warning("Failed to open editor (id=%s): %s", rid, e)
            return False

    # select が表示されるまで待つ
    try:
        select_el = WebDriverWait(driver, 5).until(
            lambda d: _visible_account_select(sub_td)
        )
    except Exception:
        try:
            sub_td.click()
            select_el = WebDriverWait(driver, 5).until(
                lambda d: _visible_account_select(sub_td)
            )
        except Exception:
            logging.warning("Account select not visible (id=%s)", rid)
            return False

    sel = Select(select_el)
    target_value = None
    target_label = None
    for opt in sel.options:
        label = (opt.text or "").strip()
        if label.startswith(ana_pay_label):
            target_value = opt.get_attribute("value")
            target_label = label
            break
    if not target_value:
        logging.warning(
            "ANA Pay option not found in select for row id=%s options=%s",
            rid,
            [(o.get_attribute("value"), (o.text or "").strip())
             for o in sel.options],
        )
        return False

    # Selenium Select + change イベントを明示発火（MF のインライン保存用）
    sel.select_by_value(target_value)
    driver.execute_script(
        """
        var el = arguments[0];
        var val = arguments[1];
        el.value = val;
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        if (window.jQuery) {
          try { jQuery(el).val(val).trigger('change'); } catch (e) {}
        }
        """,
        select_el,
        target_value,
    )
    try:
        select_el.send_keys(Keys.ENTER)
    except Exception:
        pass
    try:
        driver.execute_script("arguments[0].blur();", select_el)
    except Exception:
        pass

    # 反映待ち: DOM 再描画で stale になりやすいので ID で取り直す
    def saved(_driver):
        try:
            row = _driver.find_element(By.ID, rid) if rid else row_el
            span = row.find_element(
                By.CSS_SELECTOR, "td.sub_account_id_hash div.noform span"
            )
            return (span.text or "").strip().startswith(ana_pay_label)
        except StaleElementReferenceException:
            return False
        except Exception:
            return False

    try:
        WebDriverWait(driver, 10).until(saved)
        logging.info("Saved ANA Pay for id=%s (%s)", rid, target_label)
        return True
    except Exception:
        try:
            row = driver.find_element(By.ID, rid) if rid else row_el
            final = row.find_element(
                By.CSS_SELECTOR, "td.sub_account_id_hash div.noform span"
            ).text.strip()
        except Exception:
            final = "?"
        logging.warning(
            "Save not confirmed for id=%s (display=%r, selected=%r)",
            rid,
            final,
            target_label,
        )
        return False


def replace_none_to_anapay_for_current_month(*, dry_run: bool = False, max_passes: int = 5) -> int:
    """
    表示中の月の一覧で「なし」→「ANA Pay」をできるだけ置換する。
    `max_passes`: 保存によりDOMが更新されるので、何回か全行スキャンを繰り返す。
    """
    driver = helium.get_driver()
    _wait_for_daily_info_loaded(driver, timeout=30)
    ym = _get_displayed_month_ym_with_wait(driver, timeout=30)

    updated = 0
    for _ in range(max_passes):
        # まず「なし」の行IDをスナップショットとして集める（DOM更新で要素参照が切れやすいのでIDベースにする）
        target_ids: list[str] = []
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "tr.transaction_list[id]")
        except Exception:
            rows = []

        for row in rows:
            try:
                row_id = row.get_attribute("id") or ""
                if not row_id:
                    continue
                sub_tds = row.find_elements(By.CSS_SELECTOR, "td.sub_account_id_hash")
                if not sub_tds:
                    continue
                sub_td = sub_tds[0]
                spans = sub_td.find_elements(By.CSS_SELECTOR, "div.noform span")
                if not spans:
                    continue
                if (spans[0].text or "").strip() == "なし":
                    target_ids.append(row_id)
            except StaleElementReferenceException:
                continue
            except Exception:
                continue

        if not target_ids:
            break

        changed_this_pass = 0
        for row_id in target_ids:
            if dry_run:
                logging.info("[dry-run] would update row id=%s", row_id)
                changed_this_pass += 1
                continue

            # IDで取り直してから編集する（stale対策）
            ok = False
            for attempt in range(3):
                try:
                    row = driver.find_element(By.ID, row_id)
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
                    time.sleep(0.05)
                    ok = _select_ana_pay_in_row(driver, row, row_id=row_id)
                    break
                except StaleElementReferenceException:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                except Exception as e:
                    logging.warning("Row handling error (month=%s, id=%s): %s", ym, row_id, e)
                    break

            if ok:
                updated += 1
                changed_this_pass += 1
                logging.info("Updated row id=%s (month=%s)", row_id, ym)
            else:
                logging.warning("Failed to update row id=%s (month=%s)", row_id, ym)

        if changed_this_pass == 0:
            break

        time.sleep(0.3)

    return updated


def main() -> None:
    """
    実行例:
      START_YM=2025/06 END_YM=2026/03 python daily-info_none-to-anapay.py

    オプション:
      DRY_RUN=1 で変更せずログだけ出す
    """
    start_ym = os.getenv("START_YM", "2025/06")
    end_ym = os.getenv("END_YM", "2026/03")
    dry_run = (os.getenv("DRY_RUN", "") or "").lower() in {
        "1", "true", "yes", "y"}

    target = TargetRange(start_ym=start_ym, end_ym=end_ym)
    months = target.months()
    logging.info("Target months: %s ... %s (%d months)",
                 months[0], months[-1], len(months))

    login_mf()
    _ensure_logged_in_ready(timeout_secs=180)

    driver = helium.get_driver()
    driver.get(MF_CF_DAILY_INFO_URL)
    _wait_for_daily_info_loaded(driver, timeout=60)

    # 開始月へ移動（以降は prev/next で走査）
    goto_month(months[0])

    total = 0
    for ym in months:
        logging.info("Processing month %s", ym)
        try:
            goto_month(ym)
            updated = replace_none_to_anapay_for_current_month(dry_run=dry_run)
            total += updated
            logging.info("Month %s updated rows: %d", ym, updated)
        except TimeoutException:
            logging.warning("Timeout loading month %s, skipping", ym)
        except Exception as e:
            logging.exception("Failed processing month %s: %s", ym, e)

    logging.info("Done. Total updated rows: %d (dry_run=%s)", total, dry_run)
    helium.kill_browser()


if __name__ == "__main__":
    main()
