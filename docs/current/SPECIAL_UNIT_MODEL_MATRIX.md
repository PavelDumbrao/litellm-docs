# SPECIAL UNIT MODEL MATRIX

Date: 2026-03-26.

## Audio (P1)
gpt-4o-audio-preview(audio_token, proxy, desired:audio tokens), gpt-audio(audio_token, proxy, desired:audio tokens), gpt-audio-mini(chars_token, proxy, desired:chars), gpt-4o-transcribe(audio_token, proxy, desired:audio minutes), gpt-4o-mini-transcribe(audio_token, proxy, desired:audio minutes)

## TTS (P1)
gpt-4o-mini-tts(chars_token, proxy, desired:chars), tts-1(chars_token, proxy, desired:chars), tts-hd-1(chars_token, proxy, desired:chars)

## Search (P2)
gpt-4o-search-preview(search_token, proxy, desired:per query), gpt-4o-mini-search-preview(search_token, proxy, desired:per query), gpt-5-search-api(search_token, proxy, desired:per query)

## Realtime (P2)
gpt-4o-realtime-preview(realtime_token, proxy, desired:realtime tokens), gpt-4o-mini-realtime-preview(realtime_token, proxy, desired:realtime tokens)

## Research (P2)
o4-mini-deep-research(research_token, proxy, desired:per query)

## Summary
14 models, all proxy via token. P1: audio/TTS (8, metadata available). P2: search/realtime/research (6, no reliable unit data).
