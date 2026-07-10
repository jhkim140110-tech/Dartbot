import os
import sys
from pathlib import Path

# Bootstrap: make src/ and repo root importable regardless of how this
# script is invoked (python -m, direct execution, Railway Nixpacks, etc.)
_HERE = Path(__file__).resolve()
_SRC = str(_HERE.parents[1])   # .../src
_REPO = str(_HERE.parents[2])  # repo root
for _p in (_SRC, _REPO):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dotenv import load_dotenv


def main() -> None:
    # Load .env from repository root if present to ease local testing
    repo_root = Path(__file__).resolve().parents[2]
    env_path = repo_root / ".env"
    load_dotenv(env_path)

    from dartbot.dart_api import DartClient
    from dartbot.telegram import TelegramClient

    dart_client = DartClient()
    telegram_client = TelegramClient()
    from dartbot.formatter import format_disclosure_4part
    import json

    print("Running DartBOT local smoke test...")
    print("DART API key loaded:", bool(dart_client.api_key))
    print("Telegram chat loaded:", bool(telegram_client.chat_id))

    company_code = os.getenv("DART_CORP_CODE")
    if not company_code:
        raise SystemExit("Set DART_CORP_CODE in environment for local DART company query")

    disclosures = dart_client.get_company_disclosures(corp_code=company_code)
    print("DART disclosure response keys:", list(disclosures.keys()))

    # Print a safe, pretty-printed snippet of the DART response
    try:
        pretty = json.dumps(disclosures, ensure_ascii=False, indent=2)
        print("Raw DART response (truncated 1000 chars):")
        print(pretty[:1000])
    except Exception:
        print("Could not pretty-print DART response")

    # If disclosures contain a 'list' of items, format the first one
    first_item = None
    if isinstance(disclosures, dict):
        if "list" in disclosures and disclosures.get("list"):
            first_item = disclosures["list"][0]
        # Some DART endpoints return data under 'message' as nested JSON string
        elif isinstance(disclosures.get("message"), list) and disclosures.get("message"):
            first_item = disclosures.get("message")[0]

    if first_item:
        print("\nFormatted 4-part message for first disclosure:\n")
        print(format_disclosure_4part(first_item))
    else:
        print("No disclosure items to format from DART response.")

    # Use monitor to detect new disclosures vs local state
    from dartbot.monitor import get_new_disclosures

    state_file = repo_root / ".dartbot_state.json"
    new_items = get_new_disclosures(disclosures, company_code, state_file)
    print(f"New disclosures detected: {len(new_items)}")

    # --- Begin full v1 monitoring run per spec 8 ---
    print("\nStarting full v1 monitoring run...")
    from config.companies import WATCH_COMPANIES
    from config.keywords import TRIGGER_KEYWORDS
    from dartbot.formatter import build_v1_message
    from dartbot.monitor import get_new_disclosures
    from datetime import datetime, timedelta, timezone

    # determine seen.json location (Railway: /data/seen.json via env)
    seen_path = Path(os.getenv("SEEN_PATH") or repo_root / "state" / "seen.json")
    seen_path.parent.mkdir(parents=True, exist_ok=True)

    # compute KST today and the lookback range (KST = UTC+9)
    KST = timezone(timedelta(hours=9))
    now_kst = datetime.now(KST)
    today = now_kst.strftime("%Y%m%d")
    lookback_days = int(os.getenv("LOOKBACK_DAYS") or 2)
    start_date = (now_kst - timedelta(days=lookback_days - 1)).strftime("%Y%m%d")

    types = ["B", "D", "I"]
    type_counts = {"B": 0, "D": 0, "I": 0}
    total_new = 0

    for company_name, corp_code in WATCH_COMPANIES.items():
        print(f"Checking {company_name} ({corp_code}) from {start_date} to {today}")
        for pblntf_ty in types:
            try:
                resp = dart_client.get_company_disclosures(
                    corp_code=corp_code,
                    pblntf_ty=pblntf_ty,
                    bgn_de=start_date,
                    end_de=today,
                    page_count=100,
                    sort_mth="desc",
                )
            except Exception as e:
                print(f"DART API error for {corp_code} type {pblntf_ty}: {e}")
                continue

            status = resp.get("status")
            if status == "013":
                # no data
                continue
            if status != "000":
                print(f"DART returned status {status} for {corp_code} type {pblntf_ty}")
                continue

            # filter by keywords for this type
            keywords = TRIGGER_KEYWORDS.get(pblntf_ty, [])
            new_items = get_new_disclosures(resp, corp_code, seen_path, include_keywords=keywords)
            print(f"  type {pblntf_ty}: found {len(new_items)} new trigger items")

            for item in new_items:
                # find first matching keyword
                title = str(item.get("report_nm") or "")
                matched = None
                norm = title.replace(" ", "")
                for kw in keywords:
                    if kw.replace(" ", "") in norm:
                        matched = kw
                        break

                text = build_v1_message(item, pblntf_ty, matched)
                try:
                    print("    Sending Telegram alert...")
                    send_resp = telegram_client.send_telegram(text)
                    print("    Telegram sent, ok=", send_resp.get("ok"))
                    total_new += 1
                    if pblntf_ty in type_counts:
                        type_counts[pblntf_ty] += 1
                except Exception as e:
                    print("    Telegram send failed:", e)

    heartbeat_text = (
        f"📡 실행 완료 | 조회 B {type_counts['B']}·D {type_counts['D']}·I {type_counts['I']} | 신규 알림 {total_new}건"
    )
    try:
        print("    Sending heartbeat Telegram message...")
        heartbeat_resp = telegram_client.send_telegram(heartbeat_text)
        print("Heartbeat sent, ok=", heartbeat_resp.get("ok"))
    except Exception as e:
        print("Heartbeat send failed:", e)

    print(f"Full run complete — total new alerts sent: {total_new}")


if __name__ == "__main__":
    main()
