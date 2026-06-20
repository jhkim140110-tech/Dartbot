# DartBOT — DART 공시 모니터 (SK 중심)

간단한 DART(OpenAPI) 폴링 후 텔레그램으로 알림을 보내는 에이전트입니다.

로컬 실행

1. `.env.example`을 복사해 `.env`를 만들고 값 입력:

```powershell
copy .env.example .env
# 편집: DART_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DART_CORP_CODE
```

2. 의존성 설치 및 실행:

```powershell
python -m pip install -r requirements.txt
$env:PYTHONPATH='src'
C:/Users/HP/AppData/Local/Programs/Python/Python314/python.exe -m dartbot.cli
```

Railway 배포 (스케줄러 사용)

1. Railway에서 새 프로젝트를 만들고 GitHub 리포지토리를 연결합니다.
2. `Environment`에 다음 환경변수를 등록합니다: `DART_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `DART_CORP_CODE`.
3. UI에서 `Jobs` 또는 `Scheduler`(Railway 이름에 따라 다름)를 사용해 주기적인 실행을 만듭니다.
   - 명령: `python -m dartbot.cli`
   - 또는 `worker` 프로세스를 사용할 경우 `Procfile`이 사용됩니다.

참고: 비밀값은 절대 커밋하지 마세요. `.env.example`만 커밋되어 있습니다.
