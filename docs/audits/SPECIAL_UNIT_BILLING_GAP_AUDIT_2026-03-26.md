# SPECIAL UNIT BILLING GAP AUDIT

Date: 2026-03-26

## Worker Current Behavior
_calc_credits(tariff, input_tokens, output_tokens, discount) — ALWAYS token-based. Does NOT read billing_unit. Fallback: raw_cost_usd x 90 / 85. No special-unit logic exists.

## 14 Proxy-Billed Models

gpt-4o-audio-preview (audio_token), gpt-4o-realtime-preview (realtime_token), gpt-4o-mini-realtime-preview (realtime_token), gpt-4o-search-preview (search_token), gpt-4o-mini-search-preview (search_token), gpt-5-search-api (search_token), o4-mini-deep-research (research_token), gpt-4o-transcribe (audio_token), gpt-4o-mini-transcribe (audio_token), gpt-4o-mini-tts (chars_token), gpt-audio (audio_token), gpt-audio-mini (chars_token), tts-1 (chars_token), tts-hd-1 (chars_token)

## What Prevents Accuracy
1. Worker does NOT branch on billing_unit
2. Spend logs provide only tokens + USD spend
3. No audio_minutes/char_count/search_query_count in logs
4. Provider usage normalized to tokens by LiteLLM

## What IS Available
prompt_tokens, completion_tokens, spend USD, model name, metadata (sometimes provider-specific)

## Gap
14 models billed as tokens via proxy. Desired: per-actual-unit. Blocker: LiteLLM doesn't expose unit metrics. Workaround: raw spend USD as ground truth.
