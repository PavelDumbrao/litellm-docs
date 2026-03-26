# LIVE PUBLIC ALIAS MAP EXPANDED
Date: 2026-03-26. Source: config.yaml + billing.public_model_tariff.

## GPT-5.x
gpt-5.4 -> jeniya-codex(order:1), polo-codex(order:2). Fallback: gpt-4o->gpt-4o-mini. Exact: YES. $1.03/$8.22
gpt-5.4-mini -> jeniya-default(order:1), jeniya-az15(order:2). Fallback: gpt-4o-mini->gpt-4.1-mini. Exact: YES. $0.12/$0.72
gpt-5.4-nano -> jeniya-default(order:1), jeniya-az15(order:2). Fallback: gpt-4.1-nano->gpt-4o-mini. Exact: YES. $0.04/$0.40
gpt-5.3-codex -> jeniya-codex(order:1), polo-codex(order:2). Fallback: gpt-5.4->gpt-4o. Exact: YES. $0.37/$2.99

## GPT-4.x
gpt-4o -> polo-az(order:1). Fallback: gpt-4o-mini->gpt-4.1-mini. Exact: YES
gpt-4o-mini -> polo-az(order:1). Fallback: gpt-4.1-mini->gpt-4.1-nano. Exact: YES
gpt-4.1 -> polo-az(order:1). Fallback: gpt-4.1-mini->gpt-4o-mini. Exact: YES
gpt-4.1-mini -> polo-az(order:1), jeniya-az15(order:2). Fallback: gpt-4o-mini->gpt-4.1-nano. Exact: YES
gpt-4.1-nano -> polo-az(order:1), jeniya-az15(order:2). Fallback: gpt-4.1-mini->gpt-4o-mini. Exact: YES

## Claude
claude-haiku-4-5 -> anideaai(order:1), polo-claude(order:3). Fallback: gpt-4o-mini->gpt-4.1-mini. Exact: YES. $0.22/$1.10
claude-sonnet-4-6 -> anideaai(order:1), polo-claude(order:3). Fallback: claude-haiku-4-5->gpt-4o. Exact: YES. $0.66/$3.29
claude-opus-4-6 -> anideaai(order:1), polo-claude(order:3). Fallback: claude-sonnet-4-6->claude-haiku-4-5. Exact: YES. $1.10/$5.48

## Thinking Variants (same pricing as base)
claude-haiku-4-5-thinking, claude-sonnet-4-5-thinking, claude-opus-4-5-thinking, claude-opus-4-6-thinking
gemini-3-flash-preview-nothinking, gemini-3-flash-preview-thinking, gemini-2.5-flash-thinking

## Gemini
gemini-3-flash-preview -> jeniya-gemini(order:1), polo-fastgemini(order:2). Fallback: gemini-2.5-flash->gpt-4o-mini. Exact: YES. $0.14/$0.82
gemini-3.1-pro-preview -> polo-fastgemini(order:1). Fallback: gemini-3-flash->gemini-2.5-flash. Exact: YES. $0.55/$3.29
gemini-3.1-pro-preview-high/low/medium -> same provider, same pricing, same fallback
gemini-2.5-flash -> jeniya-gemini(order:1), polo-gemini(order:2). Fallback: gemini-3-flash->gpt-4o-mini. Exact: YES
gemini-2.5-flash-lite -> polo-gemini. Fallback: gemini-2.5-flash->gemini-3-flash. Exact: YES

## Other
deepseek-v3.2 -> jeniya-skidka(order:1), jeniya-az15(order:2). Fallback: gpt-4o->gpt-4o-mini. Exact: YES

## Proxy-Billed Special-Unit (token proxy, NOT fully accurate)
gpt-4o-audio-preview(audio_token), gpt-4o-realtime-preview(realtime_token), gpt-4o-mini-realtime-preview(realtime_token)
gpt-4o-search-preview(search_token), gpt-4o-mini-search-preview(search_token), gpt-5-search-api(search_token)
o4-mini-deep-research(research_token), gpt-4o-transcribe(audio_token), gpt-4o-mini-transcribe(audio_token)
gpt-4o-mini-tts(chars_token), gpt-audio(audio_token), gpt-audio-mini(chars_token), tts-1(chars_token), tts-hd-1(chars_token)

## Embeddings (passthrough)
text-embedding-3-large, text-embedding-3-small, text-embedding-ada-002

## I7DC Relay (separate provider, not exact-name critical)
i7dc-claude-haiku-4-5, i7dc-claude-sonnet-4-6, i7dc-claude-opus-4-6

## Hidden -tools Aliases (NOT PUBLIC)
gpt-5.4-tools, gpt-5.4-mini-tools, gpt-5.4-nano-tools, gpt-4o-tools, gpt-4o-mini-tools
gpt-4.1-mini-tools, gpt-4.1-nano-tools, claude-haiku-4-5-tools, claude-sonnet-4-6-tools
claude-opus-4-6-tools, gemini-2.5-flash-tools, gemini-3-flash-tools, gemini-3.1-pro-preview-tools
