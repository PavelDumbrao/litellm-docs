# LIVE ROUTING AND FALLBACK REFERENCE

Date: 2026-03-26. Source: config.yaml.

## Routing
simple-shuffle, 2 retries, 300s timeout, 3 allowed fails, 30s cooldown, pre_call_checks enabled.

## Provider Groups (13 keys)
JENIYA_CODEX -> jeniya.top (GPT-5.4/5.3-codex, order:1)
JENIYA_DEFAULT -> jeniya.top (GPT-5.4-mini/nano, order:1)
JENIYA_GEMINI -> jeniya.top (Gemini, order:1)
JENIYA_SKIDKA -> jeniya.top (DeepSeek, order:1)
JENIYA_AZ15 -> jeniya.top (fallback, order:2)
POLO_CLAUDE -> poloai.top (Claude, order:3)
POLO_CODEX_GPT -> poloai.top (GPT-5.x fallback, order:2)
POLO_AZ -> poloai.top (GPT-4.1/4o/audio/search/TTS, order:1)
POLO_GEMINI -> poloai.top (Gemini fallback)
POLO_FASTGEMINI -> poloai.top (Gemini 3/3.1 fast)
ANIDEAAI -> anideaai.com (Claude native, order:1)
I7DC -> i7dc.com (I7DC relay)

## Fallback Chains
gpt-5.4 -> gpt-4o -> gpt-4o-mini
gpt-5.4-mini -> gpt-4o-mini -> gpt-4.1-mini
gpt-5.4-nano -> gpt-4.1-nano -> gpt-4o-mini
gpt-5.3-codex -> gpt-5.4 -> gpt-4o
gpt-4o -> gpt-4o-mini -> gpt-4.1-mini
gpt-4.1-mini -> gpt-4o-mini -> gpt-4.1-nano
gpt-4.1-nano -> gpt-4.1-mini -> gpt-4o-mini
gpt-4o-mini -> gpt-4.1-mini -> gpt-4.1-nano
claude-opus-4-6 -> claude-sonnet-4-6 -> claude-haiku-4-5
claude-sonnet-4-6 -> claude-haiku-4-5 -> gpt-4o
claude-haiku-4-5 -> gpt-4o-mini -> gpt-4.1-mini
gemini-3.1-pro -> gemini-3-flash -> gemini-2.5-flash
gemini-3-flash -> gemini-2.5-flash -> gpt-4o-mini
gemini-2.5-flash -> gemini-3-flash -> gpt-4o-mini
deepseek-v3.2 -> gpt-4o -> gpt-4o-mini

## Hidden -tools Fallbacks
All -tools aliases -> base model -> base fallback chain. Example: gpt-5.4-tools -> gpt-5.4 -> gpt-4o -> gpt-4o-mini.

## Callbacks
JsonHealingV1Handler (JSON healing), ToolsRoutingHandler (Auto-Tools Router)
