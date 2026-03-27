# TTS REQUEST-SIDE METERING PLAN

Date: 2026-03-26. Production-safe TTS billing without LiteLLM spend-log metadata dependency.

## PROBLEM

LiteLLM spend logs for TTS models contain EMPTY metadata:
- metadata.additional_usage_values: {}
- metadata.usage_object: {tokens: 0}
- messages: {}
- proxy_server_request: {}
- response: {}

Character counts from OpenAI TTS API are NOT captured by LiteLLM. Worker chars_token branch is inert.

## ARCHITECTURE

### Source of Truth for TTS Billing
Input text length — captured from request body at LiteLLM proxy level.

### Approach: LiteLLM Callback Handler
Add TtsBillingHandler(CustomLogger) to custom_callbacks.py:
- Hook: async_post_call_success_hook(data, user_api_key_dict, response)
- data contains full request body: {"model": "gpt-4o-mini-tts", "input": "...", "voice": "alloy"}
- Extract data["input"], count len(input)
- Inject into spend log via additional_usage_values

### Data Flow
```
Client -> LiteLLM proxy -> TtsBillingHandler (counts input chars)
    -> OpenAI TTS API -> response
    -> spend log written with additional_usage_values.characters
    -> worker reads additional_usage_values.characters
    -> chars_token billing activates
```

### Models Affected
- gpt-4o-mini-tts (public, active)
- tts-hd-1 (public, active)
- tts-1 (inactive, path still works)

### Fallback If Input Missing
- If data.get("input") is empty/missing -> skip injection
- Worker falls back to token proxy (existing behavior)
- No billing failure

### Anti-Double-Charge
- Callback only writes additional_usage_values
- Worker reads it ONCE during process_spend_log
- Idempotency by spend_log_id (existing unique constraint)
- If callback fails -> spend log written with empty additional_usage_values -> token proxy fallback

### Coexistence With Current Worker
- Worker _extract_char_count_from_metadata() currently reads metadata.usage.characters
- Need to also check metadata.additional_usage_values.characters
- Small targeted edit to one function

### Implementation Steps
1. Add TtsBillingHandler class to custom_callbacks.py
2. Register in config.yaml callbacks list
3. Modify worker _extract_char_count_from_metadata() to check additional_usage_values
4. Deploy and test with one TTS request
5. Verify spend log has additional_usage_values.characters populated
6. Verify worker computes correct debit

### Rollback
- Remove TtsBillingHandler from callbacks list
- Redeploy LiteLLM
- Worker falls back to token proxy (existing behavior)
- No data loss, no billing gap

### Risks
- Production config change (requires container restart)
- Callback performance (minimal — string length calculation)
- Spend log schema (additional_usage_values column already exists as JSONB)
- Worker change (small targeted edit)

## VERDICT
Clean architecture. Callback captures input at request time, writes to existing spend log column. Worker reads it. No new infrastructure. Rollback is one config line change.