# GPT-AUDIO-MINI CLASSIFICATION DECISION

Date: 2026-03-27.

## Question
gpt-audio-mini was labelled billing_unit=chars_token in billing.public_model_tariff. Is this correct?

## Evidence

### config.yaml (live)
```yaml
- model_name: gpt-audio-mini
  litellm_params:
    model: openai/gpt-audio-mini
    api_base: https://poloai.top/v1
  model_info:
    input_cost_per_token: 1.5411e-05
    output_cost_per_token: 3.0822e-05
```
LiteLLM is billing this model **per token** (input_cost_per_token), not per character.

### DB state before reclassification
```
billing_unit: chars_token
notes: "Audio mini, chars proxied as tokens"
input_rate_credits: 0.00003264
output_rate_credits: 0.00006528
is_active: true
```

### Model nature
gpt-audio-mini is an audio output generation model (not legacy TTS). OpenAI prices audio output models per audio token, not per character. The chars_token label was carried over from an incorrect initial classification — the notes themselves say "chars proxied as tokens" confirming billing was always token-based in practice.

## Decision: RECLASSIFY → audio_token

**Reasoning:**
1. LiteLLM config uses `input_cost_per_token` — billing is per token, not per char
2. Notes confirm chars were proxied as tokens — meaning chars_token label was never functional
3. No TTS chars-path blocker applies — this model has no chars extraction issue
4. audio_token is the correct semantic category for audio output models
5. Reclassification has zero operational impact — billing behavior unchanged (was already token proxy)

**Risk:** None. Billing calculation is unchanged. Only the label is corrected.

## Changes Applied

### billing.public_model_tariff
- billing_unit: `chars_token` → `audio_token`
- notes updated with reclassification reason
- is_active: remains true
- rates: unchanged

### Docs updated
- SPECIAL_UNIT_MODEL_MATRIX.md — gpt-audio-mini moved to Audio section, label corrected
- LIVE_PRICING_REFERENCE.md — ⚠️ flag removed
- SPECIAL_MODEL_KEEP_REMOVE_AUDIT — status AMBIGUOUS → KEEP AS PROXY
- PUBLIC_SURFACE_POST_TTS_REMOVAL — ambiguous count 0, note updated

## Result
No ambiguous chars_token models remain in public surface.
All active billing_unit=chars_token entries are now is_active=false (tts-1, gpt-4o-mini-tts, tts-hd-1).