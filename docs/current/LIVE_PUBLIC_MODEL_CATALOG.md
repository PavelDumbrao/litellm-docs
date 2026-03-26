# LIVE PUBLIC MODEL CATALOG

**Date audited:** 2026-03-26
**Source:** config.yaml model_list (hide!=true entries)
**Note:** Hidden -tools aliases EXCLUDED. Billing via billing.public_model_tariff.

## General Chat (token billing)
gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, gpt-5.3-codex, gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano

## Claude (token billing)
claude-haiku-4-5, claude-haiku-4-5-thinking, claude-sonnet-4-6, claude-sonnet-4-5-thinking, claude-opus-4-6, claude-opus-4-5-thinking, claude-opus-4-6-thinking

## Gemini (token billing)
gemini-3-flash-preview, gemini-3-flash-preview-nothinking, gemini-3-flash-preview-thinking, gemini-3.1-pro-preview, gemini-3.1-pro-preview-high/low/medium, gemini-2.5-flash, gemini-2.5-flash-thinking, gemini-2.5-flash-lite

## Other (token billing)
deepseek-v3.2

## Audio/Speech (special billing unit — PROXY via token)
gpt-4o-audio-preview, gpt-audio, gpt-audio-mini, gpt-4o-mini-tts, tts-1, tts-hd-1

## Realtime (special billing unit — PROXY via token)
gpt-4o-realtime-preview, gpt-4o-mini-realtime-preview

## Search/Research (special billing unit — PROXY via token)
gpt-4o-search-preview, gpt-4o-mini-search-preview, gpt-5-search-api, o4-mini-deep-research

## Transcription (special billing unit — PROXY via token)
gpt-4o-transcribe, gpt-4o-mini-transcribe

## Embeddings (no billing)
text-embedding-3-large, text-embedding-3-small, text-embedding-ada-002

## I7DC Relay (separate provider)
i7dc-claude-haiku-4-5, i7dc-claude-sonnet-4-6, i7dc-claude-opus-4-6

## EXCLUDED (hidden internal aliases — NOT customer-facing)
gpt-5.4-tools, gpt-5.4-mini-tools, gpt-5.4-nano-tools, gpt-4o-tools, gpt-4o-mini-tools, gpt-4.1-mini-tools, gpt-4.1-nano-tools, claude-haiku-4-5-tools, claude-sonnet-4-6-tools, claude-opus-4-6-tools, gemini-2.5-flash-tools, gemini-3-flash-tools, gemini-3.1-pro-preview-tools

## PROXY-BILLED NOTE
Audio/search/realtime/transcribe/TTS models use billing_unit labels but worker currently has NO special-unit logic. Billed via token proxy approximation. Functional but not fully accurate per actual unit.
