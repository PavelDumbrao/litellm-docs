# LIVE PUBLIC ALIAS MAP

Date: 2026-03-26. Source: config.yaml model_list + router_settings.

## Public Alias -> Routes

gpt-5.4 -> jeniya-codex (order:1), polo-codex (order:2)
gpt-5.4-mini -> jeniya-default (order:1), jeniya-az15 (order:2)
gpt-5.4-nano -> jeniya-default (order:1), jeniya-az15 (order:2)
gpt-5.3-codex -> jeniya-codex (order:1), polo-codex (order:2)
gpt-4o -> polo-az (order:1), gpt-4o-mini (fallback)
gpt-4o-mini -> polo-az (order:1), gpt-4.1-mini (fallback)
gpt-4.1 -> polo-az (order:1), gpt-4.1-mini (fallback)
gpt-4.1-mini -> polo-az (order:1), jeniya-az15 (order:2)
gpt-4.1-nano -> polo-az (order:1), jeniya-az15 (order:2)
claude-haiku-4-5 -> anideaai (order:1), polo-claude (order:3)
claude-sonnet-4-6 -> anideaai (order:1), polo-claude (order:3)
claude-opus-4-6 -> anideaai (order:1), polo-claude (order:3)
gemini-3-flash-preview -> jeniya-gemini (order:1), polo-fastgemini (order:2)
gemini-3.1-pro-preview -> polo-fastgemini (order:1), gemini-3-flash (fallback)
gemini-2.5-flash -> jeniya-gemini (order:1), polo-gemini (order:2)
deepseek-v3.2 -> jeniya-skidka (order:1), jeniya-az15 (order:2)
i7dc-claude-* -> i7dc.com relay (separate provider)

## Thinking Variants -> Same base pricing
claude-haiku-4-5-thinking, claude-sonnet-4-5-thinking, claude-opus-4-5-thinking, claude-opus-4-6-thinking, gemini-3-flash-nothinking, gemini-3-flash-thinking, gemini-2.5-flash-thinking

## Special-Unit -> Proxy token billing
All audio/search/realtime/transcribe/TTS route through polo-az, billed via token proxy.

## Hidden -tools -> Base model (1:1)
All -tools aliases map to base. Worker fallback handles them. NOT in public_model_tariff.
