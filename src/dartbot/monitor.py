from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _extract_items(disclosures: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(disclosures, dict):
        return []
    if "list" in disclosures and isinstance(disclosures["list"], list):
        return disclosures["list"]
    msg = disclosures.get("message")
    if isinstance(msg, list):
        return msg
    return []


def _item_id(item: Dict[str, Any]) -> Optional[str]:
    for k in ("rcept_no", "rceptNo", "rcpNo", "receipt_no", "doc_id"):
        if k in item and item[k]:
            return str(item[k])
    # fallback: compose from available fields
    if "report_nm" in item and "rcept_dt" in item:
        return f"{item.get('report_nm')}|{item.get('rcept_dt')}"
    return None


def load_state(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(path: Path, state: Dict[str, Any]) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def get_new_disclosures(
    disclosures: Dict[str, Any],
    corp_code: str,
    state_path: Path,
    update_state: bool = True,
    include_keywords: Optional[List[str]] = None,
    exclude_keywords: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:

    """Return a list of disclosures that are new compared to stored state.

    The state file stores seen IDs per `corp_code` under keys.
    """
    items = _extract_items(disclosures)
    if not items:
        return []

    state = load_state(state_path)
    seen = set(state.get(corp_code, []))

    new_items: List[Dict[str, Any]] = []
    new_ids: List[str] = []
    for it in items:
        iid = _item_id(it)
        if not iid:
            continue
        if iid in seen:
            continue
        # apply keyword filters if provided
        title = str(it.get("report_nm") or it.get("rcept_nm") or it.get("title") or "")
        text = title + " " + str(it.get("summary") or it.get("remark") or "")
        if include_keywords:
            if not any(k.lower() in text.lower() for k in include_keywords):
                continue
        if exclude_keywords:
            if any(k.lower() in text.lower() for k in exclude_keywords):
                continue
        new_items.append(it)
        new_ids.append(iid)

    if update_state and new_ids:
        # prepend newest ids to seen list (cap to 500)
        updated = new_ids + list(seen)
        state[corp_code] = updated[:500]
        try:
            save_state(state_path, state)
        except Exception:
            pass

    return new_items
