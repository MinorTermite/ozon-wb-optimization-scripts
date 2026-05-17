# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fetch_ozon_apis import H_OZON_1 as H  # noqa: E402


API_BASE = "https://api-seller.ozon.ru"
STORE_ID = 3292967
PRODUCT_ID = 2664332710
OFFER_ID = "\u0431\u0440\u0430\u0441\u0448\u0438\u044051.2"
SKU = 2818026387
RICH_ATTR_ID = 11254

ASSET_ROOT = "public/ozon_3292967_rich_bras51_2_20260517"
DESKTOP_BY_BLOCK = {
    1: "desktop/01.png",
    2: "mobile/02.png",  # desktop macro is absent in source folder
    3: "desktop/03.png",
    4: "desktop/04.png",
    5: "desktop/05.png",
    6: "desktop/06.png",
    7: "desktop/07.png",
    8: "desktop/08.png",
}
MOBILE_BY_BLOCK = {
    1: "mobile/01.png",
    2: "mobile/02.png",
    3: "mobile/03.png",
    4: "mobile/04.png",
    5: "mobile/05.png",
    6: "mobile/06.png",
    7: "mobile/07.png",
    8: "mobile/08.png",
}

ANALYTICS_DIR = ROOT / "analytics"
ANALYTICS_DIR.mkdir(exist_ok=True)
STAMP = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
BACKUP_PATH = ANALYTICS_DIR / f"ozon_3292967_bras51_2_rich_content_{STAMP}_backup.json"
DRAFT_PATH = ANALYTICS_DIR / f"ozon_3292967_bras51_2_rich_content_{STAMP}_draft.json"
REPORT_PATH = ANALYTICS_DIR / f"ozon_3292967_bras51_2_rich_content_{STAMP}_report.json"


def normalize(value: Any) -> str:
    return " ".join(str(value or "").replace("\n", " ").replace("\r", " ").split())


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def post(path: str, body: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
    response = requests.post(f"{API_BASE}{path}", headers=H, json=body, timeout=timeout)
    response.raise_for_status()
    if response.headers.get("content-type", "").startswith("application/json"):
        data = response.json()
        return data if isinstance(data, dict) else {}
    return {}


def fetch_attrs() -> dict[str, Any]:
    data = post(
        "/v4/product/info/attributes",
        {"filter": {"product_id": [PRODUCT_ID]}, "limit": 1},
        timeout=180,
    )
    rows = data.get("result") or []
    if not rows:
        raise RuntimeError(f"Product attributes not found: {PRODUCT_ID}")
    return rows[0]


def attr_text(attr_row: dict[str, Any], attr_id: int) -> str:
    for attr in attr_row.get("attributes") or []:
        if int(attr.get("id") or 0) != attr_id:
            continue
        values = attr.get("values") or []
        if not values:
            return ""
        first = values[0]
        return normalize(first.get("value") if isinstance(first, dict) else first)
    return ""


def fetch_task(task_id: int) -> dict[str, Any]:
    data = post("/v1/product/import/info", {"task_id": task_id}, timeout=180)
    result = data.get("result") or {}
    items = result.get("items") or []
    counts = Counter(str(item.get("status") or "") for item in items)
    errors = Counter()
    for item in items:
        for error in item.get("errors") or []:
            errors[str(error.get("code") or "")] += 1
    return {
        "task_id": task_id,
        "counts": dict(counts),
        "error_codes": dict(errors),
        "items": items,
    }


def public_url(base_url: str, rel_path: str) -> str:
    return f"{base_url.rstrip('/')}/{ASSET_ROOT}/{rel_path}"


def build_rich_content(base_url: str) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for index in range(1, 9):
        blocks.append(
            {
                "imgLink": "",
                "img": {
                    "src": public_url(base_url, DESKTOP_BY_BLOCK[index]),
                    "srcMobile": public_url(base_url, MOBILE_BY_BLOCK[index]),
                    "alt": "",
                    "position": "width_full",
                    "positionMobile": "width_full",
                    "widthMobile": 640,
                    "heightMobile": 640,
                },
            }
        )
    return {"content": [{"widgetName": "raShowcase", "type": "roll", "blocks": blocks}], "version": 0.3}


def check_local_assets() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel_path in sorted(set(DESKTOP_BY_BLOCK.values()) | set(MOBILE_BY_BLOCK.values())):
        path = ROOT / ASSET_ROOT / rel_path
        rows.append(
            {
                "relative_path": f"{ASSET_ROOT}/{rel_path}",
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    missing = [row for row in rows if not row["exists"] or row["bytes"] <= 0]
    if missing:
        raise RuntimeError(f"Missing local rich-content assets: {missing}")
    return rows


def check_public_urls(urls: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for url in urls:
        response = requests.get(url, timeout=45, stream=True)
        ok = response.status_code == 200 and (response.headers.get("content-type") or "").startswith("image/")
        rows.append(
            {
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "ok": ok,
            }
        )
        response.close()
        if not ok:
            raise RuntimeError(f"Public asset is not available: {rows[-1]}")
    return rows


def build_draft(base_url: str, check_urls: bool) -> dict[str, Any]:
    local_assets = check_local_assets()
    attrs = fetch_attrs()
    live_offer_id = normalize(attrs.get("offer_id"))
    if live_offer_id != OFFER_ID:
        raise RuntimeError(f"Refusing: expected offer_id {OFFER_ID!r}, got {live_offer_id!r}")

    rich_content = build_rich_content(base_url)
    rich_value = json.dumps(rich_content, ensure_ascii=False, separators=(",", ":"))
    urls = []
    for block in rich_content["content"][0]["blocks"]:
        image = block["img"]
        urls.extend([image["src"], image["srcMobile"]])
    urls = list(dict.fromkeys(urls))
    public_checks = check_public_urls(urls) if check_urls else []

    old_rich = attr_text(attrs, RICH_ATTR_ID)
    update = {
        "offer_id": live_offer_id,
        "description_category_id": attrs.get("description_category_id"),
        "type_id": attrs.get("type_id"),
        "attributes": [{"id": RICH_ATTR_ID, "values": [{"value": rich_value}]}],
    }

    backup = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "store_id": STORE_ID,
        "product_id": PRODUCT_ID,
        "offer_id": live_offer_id,
        "sku": SKU,
        "rich_attr_id": RICH_ATTR_ID,
        "old_rich_len": len(old_rich),
        "old_rich_value": old_rich,
        "attr_row": attrs,
    }
    draft = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "store_id": STORE_ID,
        "product_id": PRODUCT_ID,
        "offer_id": live_offer_id,
        "sku": SKU,
        "base_url": base_url.rstrip("/"),
        "asset_root": ASSET_ROOT,
        "desktop_block_2_fallback": "mobile/02.png",
        "old_rich_len": len(old_rich),
        "new_rich_len": len(rich_value),
        "already_same": old_rich == rich_value,
        "local_assets": local_assets,
        "public_checks": public_checks,
        "update": update,
        "rich_content": rich_content,
        "rich_value": rich_value,
        "backup_path": str(BACKUP_PATH),
    }
    save_json(BACKUP_PATH, backup)
    save_json(DRAFT_PATH, draft)
    return draft


def apply_draft(draft: dict[str, Any]) -> dict[str, Any]:
    payload = {"items": [draft["update"]]}
    data = post("/v1/product/attributes/update", payload, timeout=180)
    task_id = int(data.get("task_id") or 0)
    task_info = {}
    if task_id:
        time.sleep(3)
        task_info = fetch_task(task_id)

    verified_attrs = fetch_attrs()
    verified_rich = attr_text(verified_attrs, RICH_ATTR_ID)
    report = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "draft_path": str(DRAFT_PATH),
        "backup_path": str(BACKUP_PATH),
        "store_id": STORE_ID,
        "product_id": PRODUCT_ID,
        "offer_id": OFFER_ID,
        "sku": SKU,
        "apply_response": data,
        "task_info": task_info,
        "verification": {
            "rich_len": len(verified_rich),
            "matches": verified_rich == draft["rich_value"],
        },
    }
    save_json(REPORT_PATH, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--skip-public-url-check", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    draft = build_draft(base_url=args.base_url, check_urls=not args.skip_public_url_check)
    if not args.apply:
        print(
            json.dumps(
                {
                    "draft_path": str(DRAFT_PATH),
                    "backup_path": str(BACKUP_PATH),
                    "summary": {
                        "offer_id": draft["offer_id"],
                        "product_id": draft["product_id"],
                        "old_rich_len": draft["old_rich_len"],
                        "new_rich_len": draft["new_rich_len"],
                        "already_same": draft["already_same"],
                        "public_checks": len(draft["public_checks"]),
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    report = apply_draft(draft)
    print(
        json.dumps(
            {
                "draft_path": str(DRAFT_PATH),
                "backup_path": str(BACKUP_PATH),
                "report_path": str(REPORT_PATH),
                "summary": {
                    "offer_id": OFFER_ID,
                    "product_id": PRODUCT_ID,
                    "task_id": report.get("apply_response", {}).get("task_id"),
                    "task_counts": (report.get("task_info") or {}).get("counts", {}),
                    "task_error_codes": (report.get("task_info") or {}).get("error_codes", {}),
                    "verification": report["verification"],
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
