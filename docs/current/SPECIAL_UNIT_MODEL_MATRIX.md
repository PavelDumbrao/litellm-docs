# SPECIAL UNIT MODEL MATRIX

Date: 2026-03-26.

## Audio (P1)
gpt-4o-audio-preview(audio_token, proxy, desired:audio tokens), gpt-audio(audio_token, proxy, desired:audio tokens), gpt-audio-mini(chars_token, proxy, desired:chars), gpt-4o-transcribe(audio_token, proxy, desired:audio minutes), gpt-4o-mini-transcribe(audio_token, proxy, desired:audio minutes)

## TTS (P1)
tts-1(chars_token, ❌ REMOVED from public surface — inert chars billing, legacy model), tts-hd-1(chars_token, ✅ branch active, ⚠️ chars NOT in metadata), gpt-4o-mini-tts(chars_token, ✅ branch active, ⚠️ chars NOT in metadata)

## Search (P2)
gpt-4o-search-preview(search_token, proxy, desired:per query), gpt-4o-mini-search-preview(search_token, proxy, desired:per query), gpt-5-search-api(search_token, proxy, desired:per query)

## Realtime (P2)
gpt-4o-realtime-preview(realtime_token, proxy, desired:realtime tokens), gpt-4o-mini-realtime-preview(realtime_token, proxy, desired:realtime tokens)

## Research (P2)
o4-mini-deep-research(research_token, proxy, desired:per query)

## Summary
14 models, all proxy via token. P1: audio/TTS (8, metadata available). P2: search/realtime/research (6, no reliable unit data).

## Implementation Status (2026-03-26)
- TTS: 2/2 public models have chars_token branch (tts-hd-1, gpt-4o-mini-tts). tts-1 removed from public surface.
- Audio: 0/5 models implemented (pending TTS validation first)
- Search: P2
- Realtime: P2
- Research: P2
- **Blocker CONFIRMED:** LiteLLM does NOT expose character counts in spend log metadata. Chars-token billing is INERT — always falls back to token proxy.
- **Next:** Either patch LiteLLM upstream, or use input text length as char proxy in worker.
