import os
from typing import Any

import requests

from .config import settings


class DartClient:
    BASE_URL = "https://opendart.fss.or.kr/api"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.dart_api_key
        if not self.api_key:
            raise ValueError("DART_API_KEY is required")

    def get_company_disclosures(self, corp_code: str, page_no: int = 1, page_count: int = 10, **kwargs) -> dict[str, Any]:
        """Query the DART 공시 목록 for a single company using its corp_code.

        Supports filtering by pblntf_ty and date range.
        """
        endpoint = f"{self.BASE_URL}/list.json"
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code,
            "page_no": page_no,
            "page_count": page_count,
        }
        # Merge optional params (pblntf_ty, bgn_de, end_de, sort_mth, etc.)
        for k, v in kwargs.items():
            if v is not None:
                params[k] = v

        response = requests.get(endpoint, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_corp_code_by_name(self, company_name: str) -> dict[str, Any]:
        """Resolve the DART corp_code for a company name."""
        endpoint = f"{self.BASE_URL}/corpCode.xml"
        response = requests.get(endpoint, timeout=15)
        response.raise_for_status()
        return {"status": "ok", "data": response.text}
