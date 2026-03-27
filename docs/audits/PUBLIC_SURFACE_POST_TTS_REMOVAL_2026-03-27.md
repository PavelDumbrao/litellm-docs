# PUBLIC SURFACE SUMMARY — POST TTS REMOVAL

Date: 2026-03-27. State after full TTS removal from public catalog.

## Status

Public surface is now **text-first**.
TTS removed pending reliable unit-aware billing.

## Active Public Models (billing.public_model_tariff is_active=true)

### Token-billed (30 models — clean billing)
claude-haiku-4-5, claude-haiku-4-5-thinking, claude-opus-4-5-thinking, claude-opus-4-6, claude-opus-4-6-thinking, claude-sonnet-4-5-thinking, claude-sonnet-4-6, deepseek-v3.2, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-flash-thinking, gemini-3-flash-preview, gemini-3-flash-preview-nothinking, gemini-3-flash-preview-thinking, gemini-3.1-pro-preview, gemini-3.1-pro-preview-high, gemini-3.1-pro-preview-low, gemini-3.1-pro-preview-medium, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, gpt-5.3-codex, gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, text-embedding-3-large, text-embedding-3-small, text-embedding-ada-002

### Proxy-billed special-unit (11 models — approximate billing)
gpt-4o-audio-preview (audio_token), gpt-audio (audio_token), gpt-audio-mini (chars_token ⚠️), gpt-4o-transcribe (audio_token), gpt-4o-mini-transcribe (audio_token), gpt-4o-search-preview (search_token), gpt-4o-mini-search-preview (search_token), gpt-5-search-api (search_token), gpt-4o-realtime-preview (realtime_token), gpt-4o-mini-realtime-preview (realtime_token), o4-mini-deep-research (research_token)

⚠️ gpt-audio-mini uses chars_token — same billing_unit as removed TTS models. Currently proxy-billed via token. Needs review (see SPECIAL_MODEL_KEEP_REMOVE_AUDIT).

## Counts

| Category | Count |
|---|---|
| Active public models total | 41 |
| Token-billed (clean) | 30 |
| Proxy-billed special-unit | 11 |
| Proxy-billed chars_token (ambiguous) | 1 (gpt-audio-mini) |
| Removed TTS models | 3 |

## Removed (TTS — chars_token billing inert)

| model | id | reason |
|---|---|---|
| tts-1 | 67 | legacy, chars_token billing path inert |
| gpt-4o-mini-tts | 64 | chars NOT in spend log metadata, blocker confirmed |
| tts-hd-1 | 68 | chars NOT in spend log metadata, blocker confirmed |

All 3 set is_active=false in billing.public_model_tariff on 2026-03-27.

## Notes

- Public surface is now text-first: plain token billing covers 30/41 active models
- Special-unit proxy billing covers 11 models without billing ambiguity (token proxy is approximate but not inert)
- TTS removed as billing path is completely inert — chars_token never reaches worker calculation
- gpt-audio-mini has same billing_unit concern — flagged for review
- TTS re-enable requires: tts_billing_events table + worker integration