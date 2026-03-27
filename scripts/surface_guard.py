#!/usr/bin/env python3
"""
PublicSurfaceGuard v1.0 — 2026-03-27
Проверяет согласованность публичной поверхности AI Router.

Запуск на VPS:
  docker cp /path/to/surface_guard.py billing-portal:/opt/surface_guard.py
  docker exec billing-portal python3 /opt/surface_guard.py

Выход: JSON в stdout, exit code 0=PASS / 1=FAIL
"""

import asyncio
import asyncpg
import json
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Доверенный baseline (зафиксирован 2026-03-27)
# ---------------------------------------------------------------------------
BASELINE = {
    "expected_active_total": 41,
    "expected_token_billed": 30,
    "expected_proxy_billed": 11,
    "expected_chars_token_active": 0,
}

# Модели, УДАЛЁННЫЕ с публичной поверхности — не должны возвращаться активными
REMOVED_MODELS = {
    "tts-1",
    "tts-hd-1",
    "gpt-4o-mini-tts",
}

# Скрытые -tools алиасы — не должны появляться как active в billing table
HIDDEN_TOOLS_ALIASES = {
    "claude-haiku-4-5-tools",
    "claude-sonnet-4-6-tools",
    "gpt-4o-tools",
    "gpt-4o-mini-tools",
    "gpt-5.4-mini-tools",
    "gpt-5.4-tools",
    "gemini-2.5-flash-tools",
    "gemini-3-flash-tools",
}

# Все 11 proxy-billed special-unit моделей
PROXY_BILLED_MODELS = {
    # Audio (5)
    "gpt-4o-audio-preview",
    "gpt-audio",
    "gpt-audio-mini",
    "gpt-4o-transcribe",
    "gpt-4o-mini-transcribe",
    # Search (3)
    "gpt-4o-search-preview",
    "gpt-4o-mini-search-preview",
    "gpt-5-search-api",
    # Realtime (2)
    "gpt-4o-realtime-preview",
    "gpt-4o-mini-realtime-preview",
    # Research (1)
    "o4-mini-deep-research",
}

PROXY_BILLED_UNITS = {"audio_token", "search_token", "realtime_token", "research_token"}

DB_DSN = "postgresql://n8n:uI5lQFcE1C7NGLUmhweZ@n8n-postgres:5432/railway"


async def run_checks() -> dict:
    conn = await asyncpg.connect(DB_DSN)
    rows = await conn.fetch(
        "SELECT public_model_name, billing_unit, is_active "
        "FROM billing.public_model_tariff"
    )
    await conn.close()

    all_rows = [dict(r) for r in rows]
    active = [m for m in all_rows if m["is_active"]]
    active_names = {m["public_model_name"] for m in active}

    failures: list[str] = []
    checks: dict = {}

    # CHECK 1 — общее количество active
    c1 = len(active)
    checks["active_model_count"] = c1
    if c1 != BASELINE["expected_active_total"]:
        failures.append(
            f"CHECK1: active={c1}, expected={BASELINE['expected_active_total']}"
        )

    # CHECK 2 — token-billed
    token_billed = [m for m in active if m["billing_unit"] == "token"]
    c2 = len(token_billed)
    checks["token_billed_count"] = c2
    if c2 != BASELINE["expected_token_billed"]:
        failures.append(
            f"CHECK2: token_billed={c2}, expected={BASELINE['expected_token_billed']}"
        )

    # CHECK 3 — proxy-billed (special-unit)
    proxy_billed = [m for m in active if m["billing_unit"] in PROXY_BILLED_UNITS]
    c3 = len(proxy_billed)
    checks["proxy_billed_count"] = c3
    if c3 != BASELINE["expected_proxy_billed"]:
        failures.append(
            f"CHECK3: proxy_billed={c3}, expected={BASELINE['expected_proxy_billed']}"
        )

    # CHECK 4 — утечка удалённых моделей
    leaked_removed = sorted(active_names & REMOVED_MODELS)
    checks["removed_model_leakage"] = leaked_removed
    if leaked_removed:
        failures.append(f"CHECK4: removed models leaked back into active: {leaked_removed}")

    # CHECK 5 — утечка скрытых -tools алиасов
    leaked_tools = sorted(active_names & HIDDEN_TOOLS_ALIASES)
    checks["hidden_alias_leakage"] = leaked_tools
    if leaked_tools:
        failures.append(f"CHECK5: hidden -tools aliases active: {leaked_tools}")

    # CHECK 6 — дубликаты активных записей
    name_counts: dict[str, int] = {}
    for m in active:
        n = m["public_model_name"]
        name_counts[n] = name_counts.get(n, 0) + 1
    duplicates = {k: v for k, v in name_counts.items() if v > 1}
    checks["duplicate_active_count"] = len(duplicates)
    if duplicates:
        failures.append(f"CHECK6: duplicate active entries: {duplicates}")

    # CHECK 7 — ни одного активного chars_token
    chars_active = [m["public_model_name"] for m in active if m["billing_unit"] == "chars_token"]
    checks["chars_token_active_count"] = len(chars_active)
    if chars_active:
        failures.append(f"CHECK7: chars_token models still active: {chars_active}")

    # CHECK 8 — все 11 proxy-billed моделей присутствуют и активны
    missing_proxy = sorted(PROXY_BILLED_MODELS - active_names)
    checks["missing_proxy_models"] = missing_proxy
    if missing_proxy:
        failures.append(f"CHECK8: expected proxy-billed models missing: {missing_proxy}")

    verdict = "PASS" if not failures else "FAIL"

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "guard_version": "1.0",
        "verdict": verdict,
        "checks": checks,
        "failures": failures,
        "baseline": BASELINE,
    }


if __name__ == "__main__":
    result = asyncio.run(run_checks())
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["verdict"] == "PASS" else 1)
