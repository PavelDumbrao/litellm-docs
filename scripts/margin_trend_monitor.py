#!/usr/bin/env python3
"""Генерирует внутренний trend-отчёт по economics snapshot без изменения retail."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FILE_REL = "billing-portal-src/app/api/billing.py"
DATE_RE = re.compile(r'OPERATOR_ECONOMICS_SNAPSHOT_DATE\s*=\s*"([^\"]+)"')
TSV_RE = re.compile(r'OPERATOR_ECONOMICS_MODEL_MATRIX_TSV\s*=\s*"""(.*?)"""', re.S)


def run_git(repo: Path, args: list[str]) -> str:
    """Выполняет git-команду и возвращает stdout, иначе выбрасывает ошибку."""
    cmd = ["git", "-C", str(repo), *args]
    return subprocess.check_output(cmd, text=True)


def parse_float(raw: str) -> float | None:
    """Преобразует строку в float, пустое значение оставляет None."""
    return None if raw == "" else float(raw)


def parse_snapshot(content: str, commit_sha: str) -> dict[str, Any]:
    """Извлекает snapshot economics из версии billing.py в конкретном коммите."""
    m_date = DATE_RE.search(content)
    m_tsv = TSV_RE.search(content)
    if not m_tsv:
        raise ValueError(f"TSV не найден в коммите {commit_sha}")

    models: dict[str, dict[str, Any]] = {}
    for line in m_tsv.group(1).strip("\n").splitlines():
        cols = line.split("\t")
        (
            model, category, billing_unit, confidence, api_base, order,
            retail_input, retail_output, cost_input, cost_output,
            margin_input, margin_output, provider_paths_count,
        ) = cols
        models[model] = {
            "model": model,
            "category": category,
            "billing_unit": billing_unit or None,
            "confidence": confidence,
            "api_base": api_base or None,
            "order": None if order == "" else int(order),
            "retail_input_usd_per_1m": parse_float(retail_input),
            "retail_output_usd_per_1m": parse_float(retail_output),
            "cost_input_usd_per_1m": parse_float(cost_input),
            "cost_output_usd_per_1m": parse_float(cost_output),
            "input_margin_pct": parse_float(margin_input),
            "output_margin_pct": parse_float(margin_output),
            "provider_paths_count": int(provider_paths_count),
        }

    return {
        "commit": commit_sha,
        "snapshot_date": m_date.group(1) if m_date else None,
        "models": models,
    }


def load_two_snapshots(repo: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Возвращает текущий и предыдущий snapshot economics из git history."""
    log = run_git(repo, ["log", "--format=%H", "--", FILE_REL]).strip().splitlines()
    if len(log) < 2:
        raise RuntimeError("Недостаточно history для trend-сравнения (нужны минимум 2 коммита).")

    snapshots: list[dict[str, Any]] = []
    for sha in log[:8]:
        content = run_git(repo, ["show", f"{sha}:{FILE_REL}"])
        try:
            snapshots.append(parse_snapshot(content, sha))
        except ValueError:
            continue
        if len(snapshots) == 2:
            break

    if len(snapshots) < 2:
        raise RuntimeError("Не удалось извлечь 2 валидных snapshot из history.")
    return snapshots[0], snapshots[1]


def lowest_margin(row: dict[str, Any] | None) -> float | None:
    """Возвращает минимальную маржу (input/output) для модели."""
    if not row:
        return None
    vals = [v for v in (row.get("input_margin_pct"), row.get("output_margin_pct")) if v is not None]
    return min(vals) if vals else None


def margin_band(row: dict[str, Any] | None) -> str:
    """Классифицирует модель по band на основе минимальной маржи."""
    lm = lowest_margin(row)
    if lm is None:
        return "unknown"
    if lm < 0:
        return "negative"
    if lm < 30:
        return "critical"
    if lm < 50:
        return "warning"
    return "ok"


def band_score(band: str) -> int:
    """Возвращает score риска: больше значение = хуже."""
    return {"negative": 4, "critical": 3, "warning": 2, "ok": 1, "unknown": 0}.get(band, 0)


def confidence_score(conf: str | None) -> int:
    """Возвращает score качества confidence: больше значение = лучше."""
    return {"Exact": 3, "Estimated": 2, "Incomplete": 1}.get(conf or "", 0)


def classify_model_trend(current: dict[str, Any] | None, previous: dict[str, Any] | None) -> tuple[str, str]:
    """Классифицирует тренд модели: worsening / stable / improving."""
    current_band = margin_band(current)
    previous_band = margin_band(previous)
    current_conf = (current or {}).get("confidence")
    previous_conf = (previous or {}).get("confidence")
    current_lm = lowest_margin(current)
    previous_lm = lowest_margin(previous)

    if previous is None and current is not None:
        return "stable", "new_in_current_snapshot"
    if current is None and previous is not None:
        return "stable", "missing_in_current_snapshot"

    # unknown-band трактуем отдельно, чтобы не искажать тренд.
    if previous_band == "unknown" and current_band != "unknown":
        return "improving", f"margin_band:{previous_band}->{current_band}"
    if previous_band != "unknown" and current_band == "unknown":
        return "worsening", f"margin_band:{previous_band}->{current_band}"

    if band_score(current_band) > band_score(previous_band):
        return "worsening", f"margin_band:{previous_band}->{current_band}"
    if band_score(current_band) < band_score(previous_band):
        return "improving", f"margin_band:{previous_band}->{current_band}"

    if confidence_score(current_conf) < confidence_score(previous_conf):
        return "worsening", f"confidence:{previous_conf}->{current_conf}"
    if confidence_score(current_conf) > confidence_score(previous_conf):
        return "improving", f"confidence:{previous_conf}->{current_conf}"

    if current_lm is not None and previous_lm is not None:
        delta = round(current_lm - previous_lm, 2)
        if delta <= -0.5:
            return "worsening", f"lowest_margin_delta:{delta}"
        if delta >= 0.5:
            return "improving", f"lowest_margin_delta:+{delta}"

    return "stable", "no_material_change"


def build_category_metrics(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Строит агрегаты по категориям для одного snapshot."""
    buckets: dict[str, dict[str, Any]] = {}
    for row in snapshot["models"].values():
        cat = row["category"]
        item = buckets.setdefault(cat, {
            "category": cat,
            "total_models": 0,
            "warning_or_worse": 0,
            "avg_lowest_margin": None,
            "_margins": [],
            "confidence": {"Exact": 0, "Estimated": 0, "Incomplete": 0},
        })
        item["total_models"] += 1
        conf = row["confidence"]
        if conf in item["confidence"]:
            item["confidence"][conf] += 1
        if margin_band(row) in {"warning", "critical", "negative"}:
            item["warning_or_worse"] += 1
        lm = lowest_margin(row)
        if lm is not None:
            item["_margins"].append(lm)

    for item in buckets.values():
        if item["_margins"]:
            item["avg_lowest_margin"] = round(sum(item["_margins"]) / len(item["_margins"]), 2)
        del item["_margins"]
    return buckets


def classify_category_trend(current: dict[str, Any], previous: dict[str, Any]) -> tuple[str, str]:
    """Определяет тренд категории по warning-count и средней марже."""
    cw = current["warning_or_worse"]
    pw = previous["warning_or_worse"]
    ca = current["avg_lowest_margin"]
    pa = previous["avg_lowest_margin"]

    if cw > pw:
        return "worsening", f"warning_or_worse:{pw}->{cw}"
    if cw < pw:
        return "improving", f"warning_or_worse:{pw}->{cw}"

    if ca is not None and pa is not None:
        delta = round(ca - pa, 2)
        if delta <= -0.5:
            return "worsening", f"avg_margin_delta:{delta}"
        if delta >= 0.5:
            return "improving", f"avg_margin_delta:+{delta}"

    return "stable", "no_material_change"


def build_trend_report(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    """Формирует итоговый trend report в JSON-формате."""
    current_models = current["models"]
    previous_models = previous["models"]
    all_model_names = sorted(set(current_models) | set(previous_models))

    model_trend: list[dict[str, Any]] = []
    for name in all_model_names:
        cur = current_models.get(name)
        prev = previous_models.get(name)
        cur_band = margin_band(cur)
        prev_band = margin_band(prev)
        status, reason = classify_model_trend(cur, prev)
        model_trend.append({
            "model": name,
            "category_current": (cur or prev or {}).get("category"),
            "confidence_current": (cur or {}).get("confidence"),
            "confidence_previous": (prev or {}).get("confidence"),
            "lowest_margin_current": lowest_margin(cur),
            "lowest_margin_previous": lowest_margin(prev),
            "margin_band_current": cur_band,
            "margin_band_previous": prev_band,
            "trend_status": status,
            "trend_reason": reason,
        })

    cur_low = {x["model"] for x in model_trend if x["margin_band_current"] == "warning"}
    prev_low = {x["model"] for x in model_trend if x["margin_band_previous"] == "warning"}
    repeated_low = sorted(cur_low & prev_low)

    cur_cats = build_category_metrics(current)
    prev_cats = build_category_metrics(previous)
    all_cats = sorted(set(cur_cats) | set(prev_cats))
    category_trend: list[dict[str, Any]] = []
    for cat in all_cats:
        cur = cur_cats.get(cat, {"category": cat, "total_models": 0, "warning_or_worse": 0, "avg_lowest_margin": None, "confidence": {"Exact": 0, "Estimated": 0, "Incomplete": 0}})
        prev = prev_cats.get(cat, {"category": cat, "total_models": 0, "warning_or_worse": 0, "avg_lowest_margin": None, "confidence": {"Exact": 0, "Estimated": 0, "Incomplete": 0}})
        status, reason = classify_category_trend(cur, prev)
        category_trend.append({
            "category": cat,
            "warning_or_worse_current": cur["warning_or_worse"],
            "warning_or_worse_previous": prev["warning_or_worse"],
            "avg_lowest_margin_current": cur["avg_lowest_margin"],
            "avg_lowest_margin_previous": prev["avg_lowest_margin"],
            "confidence_current": cur["confidence"],
            "confidence_previous": prev["confidence"],
            "trend_status": status,
            "trend_reason": reason,
        })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_sources": {
            "economics_matrix": FILE_REL,
            "window_basis": "git revisions affecting OPERATOR_ECONOMICS_MODEL_MATRIX_TSV",
        },
        "observation_window": {
            "current_commit": current["commit"],
            "previous_commit": previous["commit"],
            "current_snapshot_date": current["snapshot_date"],
            "previous_snapshot_date": previous["snapshot_date"],
        },
        "summary": {
            "models_current": len(current_models),
            "models_previous": len(previous_models),
            "low_margin_warning_current": len(cur_low),
            "low_margin_warning_previous": len(prev_low),
            "repeated_low_margin_models": len(repeated_low),
            "worsening_models": sum(1 for x in model_trend if x["trend_status"] == "worsening"),
            "improving_models": sum(1 for x in model_trend if x["trend_status"] == "improving"),
            "stable_models": sum(1 for x in model_trend if x["trend_status"] == "stable"),
        },
        "confidence_caveat": {
            "Exact": "Точные economics значения, приоритетный сигнал для действий.",
            "Estimated": "Прокси-оценка себестоимости, требует осторожной интерпретации тренда.",
            "Incomplete": "Неполные economics данные, тренд ограниченно интерпретируем.",
        },
        "category_trend": category_trend,
        "model_trend": model_trend,
        "low_margin_model_trend": [x for x in model_trend if x["margin_band_current"] == "warning" or x["margin_band_previous"] == "warning"],
        "repeated_low_margin_models": repeated_low,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Строит markdown-версию trend report для операторского review."""
    lines: list[str] = []
    lines.append("# Margin Trend Report (Latest)")
    lines.append("")
    lines.append(f"**Generated at:** {report['generated_at']}  ")
    lines.append(f"**Window:** `{report['observation_window']['previous_commit'][:7]}` -> `{report['observation_window']['current_commit'][:7]}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for k, v in report["summary"].items():
        lines.append(f"- `{k}`: **{v}**")
    lines.append("")
    lines.append("## Category Trend")
    lines.append("")
    lines.append("| Category | Warning<=Current | Warning<=Previous | Avg margin current | Avg margin previous | Trend | Reason |")
    lines.append("|---|---:|---:|---:|---:|---|---|")
    for row in sorted(report["category_trend"], key=lambda x: x["category"]):
        lines.append(
            f"| {row['category']} | {row['warning_or_worse_current']} | {row['warning_or_worse_previous']} | "
            f"{row['avg_lowest_margin_current']} | {row['avg_lowest_margin_previous']} | {row['trend_status']} | {row['trend_reason']} |"
        )
    lines.append("")
    lines.append("## Low-Margin Model Trend")
    lines.append("")
    lines.append("| Model | Category | Confidence prev->curr | Lowest margin prev->curr | Band prev->curr | Trend |")
    lines.append("|---|---|---|---|---|---|")
    for row in sorted(report["low_margin_model_trend"], key=lambda x: x["model"]):
        conf = f"{row['confidence_previous']} -> {row['confidence_current']}"
        marg = f"{row['lowest_margin_previous']} -> {row['lowest_margin_current']}"
        band = f"{row['margin_band_previous']} -> {row['margin_band_current']}"
        lines.append(f"| `{row['model']}` | {row['category_current']} | {conf} | {marg} | {band} | {row['trend_status']} |")
    lines.append("")
    lines.append("## Repeated LOW_MARGIN_WARNING")
    lines.append("")
    if report["repeated_low_margin_models"]:
        for model in report["repeated_low_margin_models"]:
            lines.append(f"- `{model}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Confidence Caveat")
    lines.append("")
    for k, v in report["confidence_caveat"].items():
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Точка входа: строит latest JSON + Markdown trend report."""
    parser = argparse.ArgumentParser(description="Generate margin trend monitoring report")
    parser.add_argument("--repo", default=".", help="Путь до git-репозитория")
    parser.add_argument("--json-out", default="docs/current/MARGIN_TREND_REPORT_LATEST.json")
    parser.add_argument("--md-out", default="docs/current/MARGIN_TREND_REPORT_LATEST.md")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    current, previous = load_two_snapshots(repo)
    report = build_trend_report(current, previous)

    json_path = repo / args.json_out
    md_path = repo / args.md_out
    json_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    md_path.write_text(render_markdown(report) + "\n")

    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")


if __name__ == "__main__":
    main()
