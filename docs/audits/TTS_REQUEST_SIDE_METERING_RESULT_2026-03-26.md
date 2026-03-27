# TTS REQUEST-SIDE METERING RESULT

Date: 2026-03-26. Validation of TtsBillingHandler for gpt-4o-mini-tts.

## WHAT WAS IMPLEMENTED

### TtsBillingHandler (custom_callbacks.py)
- async_pre_call_hook fires for model gpt-4o-mini-tts only
- Captures input text length: len(data["input"])
- Writes to request data["metadata"]["tts_input_characters"]
- Python class introspection: async_pre_call_hook in vars(TtsBillingHandler) = True
- Registered in config.yaml callbacks list
- Compiles OK (py_compile verified)

### Config State After This Session
```
callbacks: [custom_callbacks.proxy_handler_instance, custom_callbacks.tools_routing_handler_instance, custom_callbacks.tts_billing_handler_instance]
```

## TEST RESULTS

### Request
- Model: gpt-4o-mini-tts
- Input: 63 characters
- Response: HTTP 200

### Spend Log
```json
{
  "additional_usage_values": {},
  "usage_object": {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
}
```

## BLOCKER: REQUEST DATA METADATA != SPEND LOG METADATA

### Root Cause
LiteLLM builds spend log `metadata` from a fixed set of internal fields via `StandardLoggingPayloadSetup`. The `additional_usage_values` field in spend log is populated by LiteLLM internal cost calculation logic, NOT from request data["metadata"].

Writing to `data["metadata"]["tts_input_characters"]` in async_pre_call_hook does NOT propagate to spend log additional_usage_values.

### What Would Work
To populate `additional_usage_values.characters` in spend log, the injection must happen in `async_log_success_event(kwargs, response_obj, start_time, end_time)` where kwargs contains the full spend context. However, LiteLLM writes the spend log AFTER callbacks complete — meaning kwargs mutations in async_log_success_event are NOT reflected in the already-written spend log row.

### Confirmed Blockers
1. LiteLLM does NOT expose character counts for TTS models (validated twice)
2. async_pre_call_hook can capture input chars at request time
3. BUT there is no supported path to inject custom fields into spend log additional_usage_values from a callback
4. async_log_success_event fires AFTER spend log is written

## VIABLE PATH FORWARD

### Option 1: Separate TTS Metering Table (recommended)
- TtsBillingHandler captures char count in async_pre_call_hook
- Writes to a SEPARATE billing table (not spend log): tts_billing_events(request_id, model, char_count, timestamp)
- Worker reads from this table for TTS models instead of spend log
- Clean separation, no LiteLLM internals dependency

### Option 2: Spend Log Post-Processing
- After spend log is written, run a background job to UPDATE additional_usage_values
- Source: tts_billing_events table or similar side-channel
- Adds latency but avoids modifying LiteLLM internals

### Option 3: Accept Token Proxy
- Keep current token proxy fallback as TTS billing
- Accurate enough for production: minimum charge per request
- No additional infrastructure needed

## SUMMARY

| Step | Status |
|---|---|
| TtsBillingHandler deployed | YES |
| Callback registered and loaded | YES |
| async_pre_call_hook fires for gpt-4o-mini-tts | YES (verified) |
| char count captured in request data | YES |
| char count in spend log additional_usage_values | NO |
| Blocker identified | YES — spend log sealed before callback can inject |
| Path forward documented | YES |
| Token proxy fallback functional | YES |