Railway 배포 체크리스트 (단계별)

이 문서는 레일웨이에 `DartBOT`을 배포하고, 볼륨에 `seen.json`을 영속화하고, 스케줄(크론)을 설정하는 단계별 가이드입니다.

1) GitHub 레포 준비
- 현재 레포를 GitHub에 푸시합니다. (기존 레포가 없다면 새로 생성)
- `.env`는 절대 커밋하지 마세요. `.env.example`만 보관합니다.

2) Railway에서 새 프로젝트 생성 및 GitHub 연결
- Railway에 로그인 → New Project → Deploy from GitHub → 해당 레포 선택

3) 환경변수 설정
- Railway Project Settings → Environment → Add Variables
  - `DART_API_KEY` = <your dart api key>
  - `TELEGRAM_BOT_TOKEN` = <bot token>
  - `TELEGRAM_CHAT_ID` = <chat id>
  - `DART_CORP_CODE` = <SK corp_code, e.g. 034730>
  - `SEEN_PATH` = `/data/seen.json`  # Railway에서 영속 볼륨을 `/data`에 마운트할 예정일 때

4) Persistent Volume(볼륨) 추가
- Railway에서 Project → Environments → Storage (Volumes) 또는 Plugins에서 Volume을 추가합니다.
- Mount point를 `/data`로 설정합니다.

5) Procfile / 커맨드 확인
- 이미 `Procfile`에 `worker: python -m dartbot.cli`가 있습니다. Railway는 이 프로세스 타입을 사용하거나, Job을 별도로 만들 수 있습니다.

6) Scheduler(Job) 설정 (Cron)
- Railway UI에서 Jobs / Scheduler 추가
  - Command: `python -m dartbot.cli`
  - Schedule (UTC): `0 9 * * 1-5`  # KST 평일 18:00

7) Deploy 및 로그 확인
- 처음 배포 후 Logs에서 실행 결과를 확인하세요. `telegram` 전송 성공 여부와 `seen.json` 파일 생성 여부를 확인합니다.
- 예상 로그 패턴:
  - `Running DartBOT local smoke test...`
  - `DART API key loaded: True`
  - `Telegram chat loaded: True`
  - `Starting full v1 monitoring run...`
  - `Checking SK주식회사 (034730) from YYYYMMDD to YYYYMMDD`
  - `Full run complete — total new alerts sent: X`
- `status == 013`은 데이터가 없는 정상 상태입니다. 이 경우 알림은 없지만 실행 자체는 정상입니다.
- 실제 메시지 전송이 정상인지 확인하려면 `Telegram api` 로그에서 `send_hello` 또는 `Telegram sent, ok=` 항목이 있는지 확인합니다.

8) SEEN_PATH와 권한
- Railway 컨테이너에서 `SEEN_PATH`로 지정한 경로(`/data/seen.json`)에 쓰기 권한이 있어야 합니다. `state/seen.json` 로컬 샘플은 개발용이며, 배포 시에는 `/data/seen.json`을 사용하세요.

9) 롤백/업데이트
- 코드를 수정하면 GitHub에 푸시 → Railway가 자동 배포합니다. 테스트는 스테이징 브랜치에서 먼저 실행하세요.

문제 발생 시
- DART 호출 에러: API 키·쿼리 파라미터 확인 및 DART 호출 로그(응답 status) 확인
- Telegram 전송 에러: 봇이 채팅에 참여했는지, chat_id와 토큰 유효성 확인
