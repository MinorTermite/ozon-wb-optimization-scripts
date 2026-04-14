from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from playwright.sync_api import sync_playwright


CDP_ENDPOINT = "http://127.0.0.1:9224"
PRICES_URL = "https://partner.market.yandex.ru/business/216491430/prices?tld=ru&campaignId=148862812&page=1&pageSize=20"
ROOT_DIR = Path(__file__).resolve().parents[1]
ANALYTICS_DIR = ROOT_DIR / "analytics"
OUTPUT_DIR = ROOT_DIR / "output" / "spreadsheet"
PLAYWRIGHT_DIR = ROOT_DIR / "output" / "playwright"
ANALYTICS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLAYWRIGHT_DIR.mkdir(parents=True, exist_ok=True)


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def find_price_cells(ws) -> tuple[int, int, int]:
    header_row = None
    sku_col = None
    price_col = None
    for row in range(1, min(ws.max_row, 30) + 1):
        values = [ws.cell(row, col).value for col in range(1, ws.max_column + 1)]
        if "Ваш SKU *" in values and "Цена *" in values:
            header_row = row
            sku_col = values.index("Ваш SKU *") + 1
            price_col = values.index("Цена *") + 1
            break
    if header_row is None or sku_col is None or price_col is None:
        raise RuntimeError("Не найдены колонки 'Ваш SKU *' и 'Цена *' в шаблоне цен.")
    data_row = header_row + 2
    return header_row, data_row, sku_col, price_col


def load_prices(path: Path) -> dict[str, int]:
    wb = load_workbook(path)
    ws = wb.active
    _, data_row, sku_col, price_col = find_price_cells(ws)
    prices: dict[str, int] = {}
    for row in range(data_row, ws.max_row + 1):
        sku = ws.cell(row, sku_col).value
        price = ws.cell(row, price_col).value
        if not sku or price in (None, ""):
            continue
        prices[str(sku)] = int(float(price))
    return prices


def build_reduced_file(source_path: Path, target_path: Path) -> dict[str, Any]:
    wb = load_workbook(source_path)
    ws = wb.active
    _, data_row, sku_col, price_col = find_price_cells(ws)

    summary_counter: Counter[str] = Counter()
    rows = 0
    before_prices: dict[str, int] = {}
    after_prices: dict[str, int] = {}
    changed_rows: list[dict[str, Any]] = []

    for row in range(data_row, ws.max_row + 1):
        sku = ws.cell(row, sku_col).value
        current_price = ws.cell(row, price_col).value
        if not sku or current_price in (None, ""):
            continue
        old = int(float(current_price))
        new = max(1, int(math.floor(old * 0.95)))
        ws.cell(row, price_col).value = new
        rows += 1
        before_prices[str(sku)] = old
        after_prices[str(sku)] = new
        summary_counter[f"{old}->{new}"] += 1
        if len(changed_rows) < 20:
            changed_rows.append({"sku": str(sku), "old": old, "new": new})

    wb.save(target_path)
    return {
        "sourcePath": str(source_path),
        "targetPath": str(target_path),
        "rowCount": rows,
        "summary": dict(summary_counter),
        "sample": changed_rows,
        "beforePrices": before_prices,
        "afterPrices": after_prices,
    }


def save_download(download, target_path: Path) -> str:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    download.save_as(str(target_path))
    return str(target_path)


def download_current_template(page, target_path: Path) -> str:
    with page.expect_download(timeout=60_000) as download_info:
        clicked = page.evaluate(
            """
            () => {
              const trigger = document.querySelector('[data-e2e-i18n-key="pidgets.promo-prices:generate-report.button"]');
              const button = trigger?.closest('button');
              if (button) {
                button.click();
                return true;
              }
              const buttons = Array.from(document.querySelectorAll('button'));
              const fallback = buttons.find(btn => (btn.innerText || btn.textContent || '').trim() === 'Скачать');
              if (!fallback) return false;
              fallback.click();
              return true;
            }
            """
        )
        if not clicked:
            raise RuntimeError("Не найдена кнопка скачивания отчета по текущим ценам.")
    download = download_info.value
    return save_download(download, target_path)


def js_click_button_by_text(page, text: str) -> bool:
    return bool(
        page.evaluate(
            """
            ({text}) => {
              const buttons = Array.from(document.querySelectorAll('button'));
              const target = buttons.find(btn => (btn.innerText || btn.textContent || '').trim() === text);
              if (!target) return false;
              target.click();
              return true;
            }
            """,
            {"text": text},
        )
    )


def close_popups(page) -> None:
    page.evaluate(
        """
        () => {
          const closeButtons = Array.from(document.querySelectorAll('button')).filter(btn => {
            const aria = btn.getAttribute('aria-label') || '';
            return aria === 'Закрыть';
          });
          closeButtons.forEach(btn => btn.click());
        }
        """
    )
    page.wait_for_timeout(1000)


def body_has_text(page, text: str) -> bool:
    return bool(page.evaluate("({text}) => document.body.innerText.includes(text)", {"text": text}))


def open_upload_modal(page) -> None:
    close_popups(page)
    if not js_click_button_by_text(page, "Обновить цены"):
        raise RuntimeError("Не найдена кнопка 'Обновить цены' на странице цен.")
    page.wait_for_timeout(4000)
    if not body_has_text(page, "Загрузите обновлённый файл"):
        raise RuntimeError("После клика не открылось окно загрузки файла цен.")
    if page.locator("input[type='file']").count() == 0:
        raise RuntimeError("В окне обновления цен не найден input[type=file].")


def upload_price_file(page, upload_path: Path) -> dict[str, Any]:
    open_upload_modal(page)
    file_input = page.locator("input[type='file']").first
    file_input.set_input_files(str(upload_path))
    page.wait_for_timeout(2_000)
    if not js_click_button_by_text(page, "Обновить"):
        raise RuntimeError("Не найдена кнопка подтверждения 'Обновить' в модальном окне.")
    page.wait_for_timeout(4_000)
    body = page.locator("body").inner_text(timeout=20_000)
    return {
        "url": page.url,
        "title": page.title(),
        "bodyExcerpt": body[:8000],
        "hasUpdate120Marker": "Обновляем данные для 120 товаров" in body,
        "has15to30Marker": "15–30 минут" in body or "15-30 минут" in body,
    }


def compare_prices(expected: dict[str, int], actual: dict[str, int]) -> dict[str, Any]:
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    mismatches: list[dict[str, Any]] = []
    for sku in sorted(set(expected) & set(actual)):
        if expected[sku] != actual[sku]:
            mismatches.append({"sku": sku, "expected": expected[sku], "actual": actual[sku]})
            if len(mismatches) >= 25:
                break
    return {
        "expectedCount": len(expected),
        "actualCount": len(actual),
        "matchedCount": len(expected) - len(missing) - len(mismatches),
        "missingCount": len(missing),
        "extraCount": len(extra),
        "mismatchCount": len(mismatches),
        "missingSample": missing[:25],
        "extraSample": extra[:25],
        "mismatchSample": mismatches,
        "allMatched": not missing and not extra and not mismatches and len(expected) == len(actual),
    }


def wait_for_prices(page, expected: dict[str, int], base_name: str) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    for index in range(1, 10):
        try:
            page.reload(wait_until="domcontentloaded", timeout=90_000)
            page.wait_for_timeout(8_000)
        except Exception:
            page.wait_for_timeout(10_000)
        body = page.locator("body").inner_text(timeout=20_000)
        processing = "Обновляем данные для 120 товаров" in body

        verify_path = ANALYTICS_DIR / f"{base_name}_verify_download_{index}.xlsx"
        try:
            downloaded = download_current_template(page, verify_path)
            actual = load_prices(Path(downloaded))
            comparison = compare_prices(expected, actual)
        except Exception as exc:
            comparison = {
                "allMatched": False,
                "error": str(exc),
            }
            downloaded = None

        attempt = {
            "index": index,
            "processing": processing,
            "downloadPath": downloaded,
            "comparison": comparison,
        }
        attempts.append(attempt)
        if comparison.get("allMatched"):
            return {"attempts": attempts, "final": attempt}
        if not processing and index >= 3:
            break
        time.sleep(45)
    return {"attempts": attempts, "final": attempts[-1] if attempts else None}


def publish_screenshot(page, base_name: str) -> str:
    path = PLAYWRIGHT_DIR / f"{base_name}.png"
    page.screenshot(path=str(path), full_page=True)
    return str(path)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    base_name = f"ym_reduce_prices_5pct_{stamp()}"
    report_path = ANALYTICS_DIR / f"{base_name}.json"
    pre_download_path = ANALYTICS_DIR / f"{base_name}_before.xlsx"
    upload_path = OUTPUT_DIR / f"ym_prices_minus5pct_additional_20260414.xlsx"
    report: dict[str, Any] = {
        "pricesUrl": PRICES_URL,
        "uploadPath": str(upload_path),
    }

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
        context = browser.contexts[0]
        page = next((item for item in context.pages if "partner.market.yandex.ru/business/216491430/prices" in item.url), None)
        if page is None:
            raise RuntimeError("Не найдена уже открытая вкладка с разделом цен Яндекс Маркета.")
        page.bring_to_front()
        page.wait_for_timeout(2_000)
        close_popups(page)

        report["beforeDownloadPath"] = download_current_template(page, pre_download_path)
        build_report = build_reduced_file(Path(report["beforeDownloadPath"]), upload_path)
        report["build"] = {
            k: v for k, v in build_report.items() if k not in {"beforePrices", "afterPrices"}
        }

        report["uploadResult"] = upload_price_file(page, upload_path)
        report["uploadScreenshotPath"] = publish_screenshot(page, f"{base_name}_upload")

        verify = wait_for_prices(page, build_report["afterPrices"], base_name)
        report["verification"] = verify
        report["finalScreenshotPath"] = publish_screenshot(page, f"{base_name}_final")
        page.close()

    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report.get("verification", {}).get("final", {}).get("comparison", {}).get("allMatched"):
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
