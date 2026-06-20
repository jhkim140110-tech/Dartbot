import os

# WATCH_COMPANIES maps display name -> corp_code (8자리)
# For v1 we populate SK주식회사 from environment or a default placeholder.
WATCH_COMPANIES = {
    "SK주식회사": os.getenv("DART_CORP_CODE", "034730"),
}
