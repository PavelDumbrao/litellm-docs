# LIVE PRICING REFERENCE

Date: 2026-03-26. Source: billing.public_model_tariff (live DB).
Formula: retail_$1M = seb_$1M x 2. retail_RUB1M = seb_$1M x 2 x 90.

## Token-billed (Safe — accurate billing)

gpt-5.4-nano: $0.04/$0.40 per 1M
gpt-5.4-mini: $0.12/$0.72 per 1M
gemini-3-flash-preview: $0.14/$0.82 per 1M
gemini-3-flash-nothinking: $0.14/$0.82 per 1M
gemini-3-flash-thinking: $0.14/$0.82 per 1M
claude-haiku-4-5: $0.22/$1.10 per 1M
claude-haiku-4-5-thinking: $0.22/$1.10 per 1M
gpt-5.3-codex: $0.37/$2.99 per 1M
gemini-3.1-pro-preview: $0.55/$3.29 per 1M
gemini-3.1-pro-low: $0.55/$3.29 per 1M
gemini-3.1-pro-medium: $0.55/$3.29 per 1M
gemini-3.1-pro-high: $0.55/$3.29 per 1M
claude-sonnet-4-5-thinking: $0.66/$3.29 per 1M
claude-sonnet-4-6: $0.66/$3.29 per 1M
claude-opus-4-5-thinking: $1.10/$5.48 per 1M
claude-opus-4-6: $1.10/$5.48 per 1M
claude-opus-4-6-thinking: $1.10/$5.48 per 1M
gpt-5.4: $1.03/$8.22 per 1M
gpt-5-search-api: $1.03/$8.22 per 1M

## Proxy-billed special-unit (token approximation)

gpt-4o-mini-search-preview: $0.06/$0.23 per 1M (search_token proxy)
gpt-4o-mini-realtime-preview: $0.25/$0.99 per 1M (realtime_token proxy)
gpt-4o-mini-transcribe: $0.51/$2.05 per 1M (audio_token proxy)
gpt-4o-audio-preview: $1.03/$4.11 per 1M (audio_token proxy)
gpt-4o-search-preview: $1.03/$4.11 per 1M (search_token proxy)
gpt-4o-transcribe: $1.03/$4.11 per 1M (audio_token proxy)
gpt-audio: $1.03/$2.05 per 1M (audio_token proxy)
gpt-4o-realtime-preview: $2.05/$8.22 per 1M (realtime_token proxy)
o4-mini-deep-research: $0.82/$3.29 per 1M (research_token proxy)
gpt-audio-mini: $30.82/$61.64 per 1M (audio_token proxy — reclassified from chars_token 2026-03-27)
## Removed from public surface (2026-03-27)
gpt-4o-mini-tts: REMOVED — is_active=false (chars_token billing inert)
tts-hd-1: REMOVED — is_active=false (chars_token billing inert)
tts-1: REMOVED — is_active=false (legacy, chars_token billing inert)

## Important
proxy-billed = NOT fully accurate. Worker has no special-unit logic. billing_unit stored but not used for calculation. Functional but approximate.

## Verify any price
SELECT input_rate_credits, output_rate_credits, billing_unit, is_active FROM billing.public_model_tariff WHERE public_model_name = MODEL_NAME;
