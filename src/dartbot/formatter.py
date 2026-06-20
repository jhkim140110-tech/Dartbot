from typing import Any, Dict


def format_disclosure_4part(disclosure: Dict[str, Any]) -> str:
    """Create a 4-part human-readable message for a single disclosure.

    Parts:
    1) Header: company and report title
    2) When & type
    3) Short summary / remark
    4) Link or receipt number
    """
    # Heuristic field extraction with safe fallbacks
    company = disclosure.get("corp_name") or disclosure.get("corp", "Unknown Company")
    title = disclosure.get("report_nm") or disclosure.get("rcept_no") or "공시"
    date = disclosure.get("rcept_dt") or disclosure.get("report_dt") or disclosure.get("business_dt") or "날짜 미상"
    doc_type = disclosure.get("stock_code") or disclosure.get("flr_nm") or disclosure.get("pblntf_dt") or "타입 미상"

    # Summary: prefer 'summary' or 'remark' style fields when available
    summary = disclosure.get("summary") or disclosure.get("remark") or disclosure.get("contents") or "요약 없음"

    # Link: DART often exposes receipt number (rcept_no) used to build viewer links
    rcept_no = disclosure.get("rcept_no") or disclosure.get("receipt_no")
    link = None
    if rcept_no:
        link = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
    else:
        link = disclosure.get("url") or disclosure.get("link") or "링크 없음"

    parts = [
        f"1) {company} — {title}",
        f"2) 날짜: {date} | 종류: {doc_type}",
        f"3) 요약: {summary}",
        f"4) 보기: {link}",
    ]

    return "\n".join(parts)


def build_v1_message(disclosure: Dict[str, Any], pblntf_ty: str, matched_keyword: str | None = None) -> str:
    """Build the v1 Telegram message (1·2단 + 원문 링크) per spec.

    matched_keyword is used to produce a one-line PR impact hint.
    """
    company = disclosure.get("corp_name") or disclosure.get("corp", "Unknown Company")
    title = disclosure.get("report_nm") or disclosure.get("rcept_no") or "공시"
    date = disclosure.get("rcept_dt") or disclosure.get("report_dt") or "날짜 미상"
    rcept_no = disclosure.get("rcept_no") or disclosure.get("receipt_no") or ""
    link = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}" if rcept_no else disclosure.get("url") or "링크 없음"

    type_map = {
        "B": "주요사항보고",
        "D": "지분공시",
        "I": "거래소공시",
        "A": "정기공시",
    }
    type_ko = type_map.get(pblntf_ty, pblntf_ty)

    impact = "키워드 기반 영향도 미정"
    if matched_keyword:
        impact = f"관련 키워드: {matched_keyword} — PR 영향도 검토 필요"
    else:
        if pblntf_ty == "D":
            impact = "지분 이동/행동주의 가능성 검토"
        elif pblntf_ty == "B":
            impact = "중대 의사결정 관련 — 영향 검토"
        elif pblntf_ty == "I":
            impact = "거래소 조회·해명 관련 — 즉각 대응 필요 여부 확인"

    lines = [
        f"🔴 [공시 포착] {company}",
        "",
        "1) 무엇이 공시됐나",
        f"   · 제목: {title}",
        f"   · 유형: {type_ko} | 접수: {date}",
        f"   · 원문: {link}",
        "",
        "2) PR 영향도",
        f"   · {impact}",
    ]

    return "\n".join(lines)
