# youtube-shorts-automation4

Daily longform YouTube automation for Korean general health education.

The workflow is based on `youtube-shorts-automation3`, but the topic, narration, and image prompts are focused on health guidance:

- general health knowledge, prevention, body mechanisms, infection routes, and lifestyle risk
- direct educational visuals of affected organs, blood vessels, viruses, bacteria, inflammation, and prevention actions
- non-graphic medical documentary style: no gore, surgery, blood, shocking imagery, labels, logos, or readable text
- narration that avoids personal diagnosis, medication dosing, or treatment instructions
- reminders to consult a clinician for persistent symptoms, danger signs, or personal care decisions

## Daily Workflow

GitHub Actions runs `Daily Health YouTube Upload` every day.

```yaml
cron: "17 20 * * *"
```

This targets 05:17 Asia/Seoul on the next day. GitHub schedules are not exact timers, so execution can start later depending on Actions queue load.

## Narration Voice

The cloud workflow uses ElevenLabs by default:

```yaml
TTS_PROVIDER: elevenlabs
```

GitHub-hosted Ubuntu runners cannot access the macOS system voices installed on a local Mac. To use the same style of voice during unattended GitHub execution, create or select an ElevenLabs voice that matches the Mac voice and set `ELEVENLABS_VOICE_ID` as a repository secret.

For local Mac-only rendering, use:

```bash
TTS_PROVIDER=macos MACOS_SAY_VOICE="Yuna" python longform_automation/daily_longform_upload_v2.py
```

Use `say -v ?` on the Mac to list available voice names.

## Required Secrets

Configure repository secrets with:

```bash
longform_automation/set_github_secrets.sh
```

Required values:

- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `YOUTUBE_TOKEN_JSON`

The script reads API keys from `.env` and YouTube OAuth credentials from `token.json`. Do not commit those files.
