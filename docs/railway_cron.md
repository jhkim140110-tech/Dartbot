Railway cron schedule

Set up a recurring job in Railway to run the monitoring CLI on weekdays at KST 17:30.

Cron (Railway uses UTC):

```
30 8 * * 1-5
```

Notes:
- Ensure environment variables are configured in Railway: `DART_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `DART_CORP_CODE`.
- Persist seen.json to Railway volume by setting `SEEN_PATH` env var to `/data/seen.json` and adding a persistent volume mounted at `/data`.
- Command to run in the job: `python -m dartbot.cli` (or use the `worker` Procfile process).
