import { Fragment, useEffect, useState, type ReactNode } from "react"
import { usageApi } from "../lib/api"

interface UsageSummary {
    total_requests: number
    total_debit: number
    standard_debit: number
    estimated_debit: number
    has_estimated: boolean
    estimated_caveat: string | null
    models: Array<{
        model: string
        requests: number
        debit: number
        billing_type_label: string
        proxy_billed: boolean
    }>
}

interface UsageLog {
    id: string
    created_at: string
    model: string
    api_key_prefix: string
    input_tokens: number
    output_tokens: number
    charged_credits: number
    loyalty_discount_percent: number
    billing_type_label: string
    proxy_billed: boolean
    caveat_text: string | null
}

interface LogsResponse {
    logs: UsageLog[]
    total: number
    page: number
    per_page: number
    pages: number
}

interface OperatorTariff {
    input_rate_credits: number | null
    output_rate_credits: number | null
    billing_unit: string | null
    active_from: string | null
    notes: string | null
}

interface OperatorLedgerEntry {
    amount_credits: number | null
    balance_after: number | null
    created_at: string | null
}

interface OperatorDetail {
    snapshot_id: string
    litellm_spend_log_id: string
    created_at: string | null
    user_id: string
    api_key_hash: string | null
    model: string
    provider: string | null
    billing_type_label: string
    billing_unit: string | null
    proxy_billed: boolean
    input_tokens: number
    output_tokens: number
    charged_credits: number
    loyalty_discount_percent: number
    raw_provider_cost_usd: number | null
    tariff: OperatorTariff | null
    calculated_expected_credits: number | null
    formula_note: string | null
    ledger_entry: OperatorLedgerEntry | null
    caveat_text: string | null
    operator_verdict: string
}

interface OperatorEconomicsSummary {
    total_models: number
    exact_count: number
    estimated_count: number
    incomplete_count: number
}

interface OperatorEconomicsCategoryRow {
    category: string
    total_models: number
    exact_count: number
    estimated_count: number
    incomplete_count: number
    avg_input_margin_pct: number | null
    avg_output_margin_pct: number | null
    note: string
}

interface OperatorEconomicsModelRow {
    model: string
    category: string
    billing_unit: string | null
    confidence: string
    provider_label: string | null
    provider_api_base: string | null
    primary_provider_order: number | null
    provider_paths_count: number
    retail_input_usd_per_1m: number | null
    retail_output_usd_per_1m: number | null
    provider_input_cost_usd_per_1m: number | null
    provider_output_cost_usd_per_1m: number | null
    input_margin_pct: number | null
    output_margin_pct: number | null
    proxy_caveat: string | null
}

interface OperatorEconomicsView {
    snapshot_date: string
    visibility: string
    calculation_mode: string
    calculation_basis: {
        fixed_rub_per_credit: number
        fx_rub_per_usd_proxy: number
        retail_formula: string
        provider_formula: string
        note: string
    }
    summary: OperatorEconomicsSummary
    category_rows: OperatorEconomicsCategoryRow[]
    model_rows: OperatorEconomicsModelRow[]
    source_docs: string[]
}

const OPERATOR_SECRET_STORAGE_KEY = "billing_operator_secret"

function formatDateTime(value?: string | null) {
    if (!value) return "—"
    return new Date(value).toLocaleString("ru-RU", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    })
}

function formatNumber(value?: number | null, digits = 6) {
    if (value === null || value === undefined) return "—"
    return value.toFixed(digits)
}

function formatUsdPer1M(value?: number | null) {
    if (value === null || value === undefined) return "—"
    return `$${value.toFixed(3)}`
}

function formatPercent(value?: number | null) {
    if (value === null || value === undefined) return "—"
    return `${value.toFixed(2)}%`
}

function BillingTypeLabel({ label, proxyBilled }: { label: string; proxyBilled: boolean }) {
    if (proxyBilled) {
        return (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-amber-900/40 text-amber-400 border border-amber-800/50">
                ~{label}
            </span>
        )
    }
    return (
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-800 text-gray-400">
            {label}
        </span>
    )
}

function ConfidenceBadge({ confidence }: { confidence: string }) {
    if (confidence === "Exact") {
        return (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-emerald-900/40 text-emerald-300 border border-emerald-800/50">
                Exact
            </span>
        )
    }
    if (confidence === "Estimated") {
        return (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-amber-900/40 text-amber-300 border border-amber-800/50">
                Estimated
            </span>
        )
    }
    return (
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-rose-900/40 text-rose-300 border border-rose-800/50">
            Incomplete
        </span>
    )
}

function SectionCard({ title, children }: { title: string; children: ReactNode }) {
    return (
        <div className="card space-y-2">
            <p className="text-gray-400 text-sm font-medium">{title}</p>
            {children}
        </div>
    )
}

function DetailField({ label, value, mono = false }: { label: string; value?: ReactNode; mono?: boolean }) {
    return (
        <div className="flex items-start justify-between gap-4 border-b border-gray-800/50 pb-2 last:border-b-0 last:pb-0">
            <span className="text-gray-500 text-xs">{label}</span>
            <span className={`text-right text-xs ${mono ? "font-mono text-gray-300" : "text-white"}`}>
                {value ?? "—"}
            </span>
        </div>
    )
}

function OperatorModeCard({
    enabled,
    hasSecret,
    onEnable,
    onClear,
}: {
    enabled: boolean
    hasSecret: boolean
    onEnable: () => void
    onClear: () => void
}) {
    if (!enabled) return null

    return (
        <div className="mb-4 px-4 py-3 rounded border border-cyan-800/40 bg-cyan-950/20">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                    <p className="text-cyan-300 text-sm font-medium">Operator mode</p>
                    <p className="text-cyan-100/70 text-xs mt-1">
                        Internal troubleshooting скрыт от обычного customer flow и работает только с X-Operator-Secret.
                    </p>
                </div>
                <div className="flex gap-2">
                    <button className="px-3 py-1.5 text-xs border border-cyan-700 rounded text-cyan-300 hover:text-white hover:border-cyan-500" onClick={onEnable}>
                        {hasSecret ? "Обновить secret" : "Ввести secret"}
                    </button>
                    {hasSecret && (
                        <button className="px-3 py-1.5 text-xs border border-gray-700 rounded text-gray-400 hover:text-white" onClick={onClear}>
                            Очистить secret
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}

function OperatorHeaderCards({ detail }: { detail: OperatorDetail }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card">
                <p className="text-gray-500 text-xs mb-1">Модель</p>
                <p className="text-white font-mono text-sm">{detail.model}</p>
            </div>
            <div className="card">
                <p className="text-gray-500 text-xs mb-1">Списано</p>
                <p className="text-white font-semibold text-sm">{formatNumber(detail.charged_credits, 6)}</p>
            </div>
            <div className="card">
                <p className="text-gray-500 text-xs mb-1">Тип</p>
                <BillingTypeLabel label={detail.billing_type_label} proxyBilled={detail.proxy_billed} />
            </div>
        </div>
    )
}

function OperatorBillingContextCard({ detail }: { detail: OperatorDetail }) {
    return (
        <SectionCard title="Billing context">
            <DetailField label="billing_unit" value={detail.billing_unit} mono />
            <DetailField label="provider" value={detail.provider} mono />
            <DetailField label="raw_provider_cost_usd" value={formatNumber(detail.raw_provider_cost_usd, 8)} mono />
            <DetailField label="created_at" value={formatDateTime(detail.created_at)} />
            <DetailField label="snapshot_id" value={detail.snapshot_id} mono />
            <DetailField label="litellm_spend_log_id" value={detail.litellm_spend_log_id} mono />
            <DetailField label="api_key_hash" value={detail.api_key_hash} mono />
        </SectionCard>
    )
}

function OperatorTariffCard({ detail }: { detail: OperatorDetail }) {
    return (
        <SectionCard title="Tariff + formula">
            <DetailField label="input_rate_credits" value={formatNumber(detail.tariff?.input_rate_credits, 8)} mono />
            <DetailField label="output_rate_credits" value={formatNumber(detail.tariff?.output_rate_credits, 8)} mono />
            <DetailField label="calculated_expected" value={formatNumber(detail.calculated_expected_credits, 6)} mono />
            <DetailField label="discount" value={detail.loyalty_discount_percent ? `${detail.loyalty_discount_percent}%` : "0%"} />
            <DetailField label="input_tokens" value={detail.input_tokens.toLocaleString()} />
            <DetailField label="output_tokens" value={detail.output_tokens.toLocaleString()} />
            <DetailField label="tariff_active_from" value={formatDateTime(detail.tariff?.active_from)} />
            <DetailField label="tariff_notes" value={detail.tariff?.notes} />
        </SectionCard>
    )
}

function OperatorFormulaCard({ detail }: { detail: OperatorDetail }) {
    return (
        <SectionCard title="Formula note">
            <p className="text-xs text-gray-300 font-mono break-all">{detail.formula_note || "—"}</p>
        </SectionCard>
    )
}

function OperatorLedgerCard({ detail }: { detail: OperatorDetail }) {
    return (
        <SectionCard title="Ledger reference">
            <DetailField label="amount_credits" value={formatNumber(detail.ledger_entry?.amount_credits, 6)} mono />
            <DetailField label="balance_after" value={formatNumber(detail.ledger_entry?.balance_after, 4)} mono />
            <DetailField label="created_at" value={formatDateTime(detail.ledger_entry?.created_at)} />
            <DetailField label="user_id" value={detail.user_id} mono />
        </SectionCard>
    )
}

function OperatorVerdictCard({ detail }: { detail: OperatorDetail }) {
    return (
        <SectionCard title="Operator verdict">
            <p className="text-sm text-white leading-6">{detail.operator_verdict}</p>
            {detail.caveat_text && (
                <div className="rounded border border-amber-800/40 bg-amber-900/10 px-3 py-2">
                    <p className="text-amber-400 text-xs italic">{detail.caveat_text}</p>
                </div>
            )}
        </SectionCard>
    )
}

function OperatorDetailContent({ detail }: { detail: OperatorDetail }) {
    return (
        <div className="space-y-4">
            <OperatorHeaderCards detail={detail} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <OperatorBillingContextCard detail={detail} />
                <OperatorTariffCard detail={detail} />
            </div>
            <OperatorFormulaCard detail={detail} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <OperatorLedgerCard detail={detail} />
                <OperatorVerdictCard detail={detail} />
            </div>
        </div>
    )
}

function OperatorDetailModal({
    open,
    loading,
    error,
    detail,
    onClose,
}: {
    open: boolean
    loading: boolean
    error: string | null
    detail: OperatorDetail | null
    onClose: () => void
}) {
    if (!open) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
            <div className="w-full max-w-4xl rounded-xl border border-gray-800 bg-gray-950 shadow-2xl">
                <div className="flex items-center justify-between border-b border-gray-800 px-5 py-4">
                    <div>
                        <h3 className="text-lg font-semibold text-white">Operator details</h3>
                        <p className="text-xs text-gray-500 mt-1">Internal troubleshooting view. Не показывать клиенту.</p>
                    </div>
                    <button className="text-gray-400 hover:text-white" onClick={onClose}>✕</button>
                </div>
                <div className="max-h-[80vh] overflow-y-auto px-5 py-4">
                    {loading && <p className="text-gray-400 text-sm">Загрузка operator details...</p>}
                    {error && !loading && <p className="text-red-400 text-sm">{error}</p>}
                    {detail && !loading && <OperatorDetailContent detail={detail} />}
                </div>
            </div>
        </div>
    )
}

function OperatorEconomicsSummaryCards({ summary }: { summary: OperatorEconomicsSummary }) {
    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="card">
                <p className="text-gray-500 text-xs mb-1">Всего моделей</p>
                <p className="text-white text-lg font-semibold">{summary.total_models}</p>
            </div>
            <div className="card">
                <p className="text-gray-500 text-xs mb-1">Exact</p>
                <p className="text-emerald-300 text-lg font-semibold">{summary.exact_count}</p>
            </div>
            <div className="card">
                <p className="text-gray-500 text-xs mb-1">Estimated</p>
                <p className="text-amber-300 text-lg font-semibold">{summary.estimated_count}</p>
            </div>
            <div className="card">
                <p className="text-gray-500 text-xs mb-1">Incomplete</p>
                <p className="text-rose-300 text-lg font-semibold">{summary.incomplete_count}</p>
            </div>
        </div>
    )
}

function OperatorEconomicsCategoryTable({ rows }: { rows: OperatorEconomicsCategoryRow[] }) {
    return (
        <SectionCard title="Category view">
            <div className="overflow-x-auto">
                <table className="w-full text-xs">
                    <thead>
                        <tr className="text-gray-500 text-left border-b border-gray-800">
                            <th className="pb-2 pr-3">Категория</th>
                            <th className="pb-2 pr-3">Моделей</th>
                            <th className="pb-2 pr-3">Exact</th>
                            <th className="pb-2 pr-3">Estimated</th>
                            <th className="pb-2 pr-3">Incomplete</th>
                            <th className="pb-2 pr-3">Avg in margin</th>
                            <th className="pb-2">Avg out margin</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row) => (
                            <Fragment key={row.category}>
                                <tr className="border-b border-gray-800/40">
                                    <td className="py-2 pr-3 text-white">{row.category}</td>
                                    <td className="py-2 pr-3 text-gray-300">{row.total_models}</td>
                                    <td className="py-2 pr-3 text-emerald-300">{row.exact_count}</td>
                                    <td className="py-2 pr-3 text-amber-300">{row.estimated_count}</td>
                                    <td className="py-2 pr-3 text-rose-300">{row.incomplete_count}</td>
                                    <td className="py-2 pr-3 text-gray-300">{formatPercent(row.avg_input_margin_pct)}</td>
                                    <td className="py-2 text-gray-300">{formatPercent(row.avg_output_margin_pct)}</td>
                                </tr>
                                <tr className="border-b border-gray-800/20">
                                    <td colSpan={7} className="pb-2 pt-0 text-gray-500 italic">{row.note}</td>
                                </tr>
                            </Fragment>
                        ))}
                    </tbody>
                </table>
            </div>
        </SectionCard>
    )
}

function OperatorEconomicsModelTable({ rows }: { rows: OperatorEconomicsModelRow[] }) {
    return (
        <SectionCard title="Model view">
            <div className="max-h-[420px] overflow-auto">
                <table className="w-full text-xs">
                    <thead>
                        <tr className="text-gray-500 text-left border-b border-gray-800 sticky top-0 bg-gray-950">
                            <th className="pb-2 pr-3">Модель</th>
                            <th className="pb-2 pr-3">Категория</th>
                            <th className="pb-2 pr-3">Confidence</th>
                            <th className="pb-2 pr-3">Retail in/out</th>
                            <th className="pb-2 pr-3">Cost in/out</th>
                            <th className="pb-2 pr-3">Margin in/out</th>
                            <th className="pb-2">Provider</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row) => (
                            <Fragment key={row.model}>
                                <tr className="border-b border-gray-800/40 align-top">
                                    <td className="py-2 pr-3 text-white font-mono">{row.model}</td>
                                    <td className="py-2 pr-3 text-gray-300">{row.category}</td>
                                    <td className="py-2 pr-3"><ConfidenceBadge confidence={row.confidence} /></td>
                                    <td className="py-2 pr-3 text-gray-300">
                                        <div>{formatUsdPer1M(row.retail_input_usd_per_1m)}</div>
                                        <div className="text-gray-500">{formatUsdPer1M(row.retail_output_usd_per_1m)}</div>
                                    </td>
                                    <td className="py-2 pr-3 text-gray-300">
                                        <div>{formatUsdPer1M(row.provider_input_cost_usd_per_1m)}</div>
                                        <div className="text-gray-500">{formatUsdPer1M(row.provider_output_cost_usd_per_1m)}</div>
                                    </td>
                                    <td className="py-2 pr-3 text-gray-300">
                                        <div>{formatPercent(row.input_margin_pct)}</div>
                                        <div className="text-gray-500">{formatPercent(row.output_margin_pct)}</div>
                                    </td>
                                    <td className="py-2 text-gray-300">
                                        <div>{row.provider_label || "—"}</div>
                                        <div className="text-gray-500 text-[11px]">
                                            {row.billing_unit || "—"} · paths: {row.provider_paths_count}
                                        </div>
                                    </td>
                                </tr>
                                {row.proxy_caveat && (
                                    <tr className="border-b border-gray-800/20">
                                        <td colSpan={7} className="pb-2 pt-0 text-amber-500/80 italic">
                                            {row.proxy_caveat}
                                        </td>
                                    </tr>
                                )}
                            </Fragment>
                        ))}
                    </tbody>
                </table>
            </div>
        </SectionCard>
    )
}

function OperatorEconomicsPanel({
    enabled,
    hasSecret,
    loading,
    error,
    data,
    onReload,
}: {
    enabled: boolean
    hasSecret: boolean
    loading: boolean
    error: string | null
    data: OperatorEconomicsView | null
    onReload: () => void
}) {
    if (!enabled) return null

    return (
        <div className="card mb-4 space-y-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <p className="text-white text-sm font-medium">Operator economics view</p>
                    <p className="text-gray-500 text-xs mt-1">Margin picture по моделям и категориям. Только для internal operator mode.</p>
                </div>
                <button className="px-3 py-1.5 text-xs border border-cyan-800 rounded text-cyan-300 hover:text-white hover:border-cyan-500" onClick={onReload}>
                    Обновить economics
                </button>
            </div>

            {!hasSecret && <p className="text-gray-500 text-sm">Сначала введи X-Operator-Secret, чтобы загрузить internal economics view.</p>}
            {loading && <p className="text-gray-400 text-sm">Загрузка economics snapshot...</p>}
            {error && !loading && <p className="text-red-400 text-sm">{error}</p>}

            {data && !loading && (
                <div className="space-y-4">
                    <div className="rounded border border-gray-800/60 px-3 py-2">
                        <p className="text-gray-500 text-xs">Snapshot</p>
                        <p className="text-white text-sm mt-1">{data.snapshot_date} · {data.calculation_mode}</p>
                        <p className="text-gray-500 text-xs mt-1">{data.calculation_basis.note}</p>
                    </div>

                    <OperatorEconomicsSummaryCards summary={data.summary} />
                    <OperatorEconomicsCategoryTable rows={data.category_rows} />
                    <OperatorEconomicsModelTable rows={data.model_rows} />
                </div>
            )}
        </div>
    )
}

function SummaryCards({ summary }: { summary: UsageSummary | null }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="card">
                <p className="text-gray-400 text-sm">Запросов</p>
                <p className="text-2xl font-bold text-white">{summary?.total_requests ?? "—"}</p>
            </div>
            <div className="card">
                <p className="text-gray-400 text-sm">Списано всего</p>
                <p className="text-2xl font-bold text-white">{summary ? summary.total_debit.toFixed(4) : "—"}</p>
            </div>
            <div className="card">
                <p className="text-gray-400 text-sm">Standard</p>
                <p className="text-2xl font-bold text-white">{summary ? summary.standard_debit.toFixed(4) : "—"}</p>
                <p className="text-gray-600 text-xs mt-0.5">Точный биллинг</p>
            </div>
            <div className="card">
                <p className="text-gray-400 text-sm">Estimated</p>
                <p className={`text-2xl font-bold ${summary && summary.estimated_debit > 0 ? "text-amber-400" : "text-gray-500"}`}>
                    {summary ? summary.estimated_debit.toFixed(4) : "—"}
                </p>
                <p className="text-gray-600 text-xs mt-0.5">~Приближённый</p>
            </div>
        </div>
    )
}

function FiltersCard({
    dateFrom,
    dateTo,
    modelFilter,
    onDateFromChange,
    onDateToChange,
    onModelChange,
    onReset,
}: {
    dateFrom: string
    dateTo: string
    modelFilter: string
    onDateFromChange: (value: string) => void
    onDateToChange: (value: string) => void
    onModelChange: (value: string) => void
    onReset: () => void
}) {
    return (
        <div className="card mb-4">
            <p className="text-gray-400 text-sm font-medium mb-3">Фильтры</p>
            <div className="flex flex-wrap gap-3">
                <div>
                    <label className="text-gray-500 text-xs block mb-1">От</label>
                    <input type="date" className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-white" value={dateFrom} onChange={e => onDateFromChange(e.target.value)} />
                </div>
                <div>
                    <label className="text-gray-500 text-xs block mb-1">До</label>
                    <input type="date" className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-white" value={dateTo} onChange={e => onDateToChange(e.target.value)} />
                </div>
                <div>
                    <label className="text-gray-500 text-xs block mb-1">Модель</label>
                    <input className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-white w-48" placeholder="gpt-4o-mini..." value={modelFilter} onChange={e => onModelChange(e.target.value)} />
                </div>
                <div className="flex items-end">
                    <button className="px-3 py-1 text-sm text-gray-400 hover:text-white border border-gray-700 rounded" onClick={onReset}>Сбросить</button>
                </div>
            </div>
        </div>
    )
}

function LogsTable({
    logsData,
    loading,
    page,
    operatorRequested,
    onPrev,
    onNext,
    onDetails,
}: {
    logsData: LogsResponse
    loading: boolean
    page: number
    operatorRequested: boolean
    onPrev: () => void
    onNext: () => void
    onDetails: (snapshotId: string) => void
}) {
    return (
        <div className="card overflow-x-auto">
            <div className="flex justify-between items-center mb-3">
                <p className="text-gray-400 text-sm font-medium">Детальные списания</p>
                <span className="text-gray-500 text-xs">Всего: {logsData.total}</span>
            </div>

            {loading ? (
                <p className="text-gray-500 text-sm py-4">Загрузка...</p>
            ) : logsData.logs.length === 0 ? (
                <div className="text-center py-8">
                    <p className="text-gray-500 text-sm">Записей нет.</p>
                    <p className="text-gray-600 text-xs mt-1">Usage sync работает каждые 10 минут после использования API ключей.</p>
                </div>
            ) : (
                <table className="w-full text-xs">
                    <thead>
                        <tr className="text-gray-500 text-left border-b border-gray-800">
                            <th className="pb-2 pr-3">Дата/время</th>
                            <th className="pb-2 pr-3">Модель</th>
                            <th className="pb-2 pr-3">Тип</th>
                            <th className="pb-2 pr-3">API ключ</th>
                            <th className="pb-2 pr-3">Input tok</th>
                            <th className="pb-2 pr-3">Output tok</th>
                            <th className="pb-2 pr-3">Кредиты</th>
                            <th className="pb-2">Скидка</th>
                            {operatorRequested && <th className="pb-2 text-right">Operator</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {logsData.logs.map((log) => (
                            <Fragment key={log.id}>
                                <tr className="border-b border-gray-800/40 hover:bg-gray-800/20">
                                    <td className="py-2 pr-3 text-gray-400 whitespace-nowrap">{new Date(log.created_at).toLocaleString("ru-RU", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}</td>
                                    <td className="py-2 pr-3 text-gray-300 font-mono">{log.model || "—"}</td>
                                    <td className="py-2 pr-3">
                                        <BillingTypeLabel label={log.billing_type_label || "Standard"} proxyBilled={log.proxy_billed || false} />
                                    </td>
                                    <td className="py-2 pr-3 text-gray-500 font-mono">{log.api_key_prefix}</td>
                                    <td className="py-2 pr-3 text-gray-400">{log.input_tokens.toLocaleString()}</td>
                                    <td className="py-2 pr-3 text-gray-400">{log.output_tokens.toLocaleString()}</td>
                                    <td className="py-2 pr-3 text-white font-medium">{log.charged_credits.toFixed(4)}</td>
                                    <td className="py-2 text-gray-500">{log.loyalty_discount_percent > 0 ? `${log.loyalty_discount_percent}%` : "—"}</td>
                                    {operatorRequested && (
                                        <td className="py-2 text-right">
                                            <button className="px-2 py-1 text-xs border border-cyan-800 rounded text-cyan-300 hover:text-white hover:border-cyan-500" onClick={() => onDetails(log.id)}>
                                                Details
                                            </button>
                                        </td>
                                    )}
                                </tr>
                                {log.proxy_billed && log.caveat_text && (
                                    <tr className="border-b border-gray-800/20">
                                        <td colSpan={operatorRequested ? 9 : 8} className="pb-2 pt-0 pr-3">
                                            <p className="text-amber-600/70 text-xs pl-0 italic">{log.caveat_text}</p>
                                        </td>
                                    </tr>
                                )}
                            </Fragment>
                        ))}
                    </tbody>
                </table>
            )}

            {logsData.pages > 1 && (
                <div className="flex justify-center gap-2 mt-4">
                    <button disabled={page <= 1} onClick={onPrev} className="px-3 py-1 text-sm border border-gray-700 rounded text-gray-400 hover:text-white disabled:opacity-40">←</button>
                    <span className="text-gray-500 text-sm py-1">{page} / {logsData.pages}</span>
                    <button disabled={page >= logsData.pages} onClick={onNext} className="px-3 py-1 text-sm border border-gray-700 rounded text-gray-400 hover:text-white disabled:opacity-40">→</button>
                </div>
            )}
        </div>
    )
}

export default function Usage() {
    const [summary, setSummary] = useState<UsageSummary | null>(null)
    const [logsData, setLogsData] = useState<LogsResponse>({ logs: [], total: 0, page: 1, per_page: 50, pages: 1 })
    const [loading, setLoading] = useState(false)
    const [page, setPage] = useState(1)
    const [dateFrom, setDateFrom] = useState("")
    const [dateTo, setDateTo] = useState("")
    const [modelFilter, setModelFilter] = useState("")
    const [detailOpen, setDetailOpen] = useState(false)
    const [detailLoading, setDetailLoading] = useState(false)
    const [detailError, setDetailError] = useState<string | null>(null)
    const [detailData, setDetailData] = useState<OperatorDetail | null>(null)
    const [economicsLoading, setEconomicsLoading] = useState(false)
    const [economicsError, setEconomicsError] = useState<string | null>(null)
    const [economicsData, setEconomicsData] = useState<OperatorEconomicsView | null>(null)
    const [operatorSecret, setOperatorSecret] = useState("")

    const operatorRequested = typeof window !== "undefined"
        && new URLSearchParams(window.location.search).get("operator") === "1"

    const loadSummary = () => {
        usageApi.summary().then((r: { data: UsageSummary | null }) => setSummary(r.data)).catch(() => setSummary(null))
    }

    useEffect(() => {
        loadSummary()
        if (typeof window !== "undefined") {
            setOperatorSecret(localStorage.getItem(OPERATOR_SECRET_STORAGE_KEY) || "")
        }
    }, [])

    useEffect(() => {
        if (!operatorRequested || !operatorSecret) {
            setEconomicsData(null)
            setEconomicsError(null)
            return
        }
        void loadOperatorEconomics(operatorSecret)
    }, [operatorRequested, operatorSecret])

    useEffect(() => {
        setLoading(true)
        usageApi.logs({
            date_from: dateFrom || undefined,
            date_to: dateTo || undefined,
            model: modelFilter || undefined,
            page,
            per_page: 50,
        }).then((r: { data: LogsResponse }) => {
            setLogsData(r.data || { logs: [], total: 0, page: 1, per_page: 50, pages: 1 })
        }).finally(() => setLoading(false))
    }, [page, dateFrom, dateTo, modelFilter])

    const promptOperatorSecret = () => {
        const nextSecret = window.prompt("Введите X-Operator-Secret для internal troubleshooting", operatorSecret || "")?.trim() || ""
        if (!nextSecret) return ""
        localStorage.setItem(OPERATOR_SECRET_STORAGE_KEY, nextSecret)
        setOperatorSecret(nextSecret)
        return nextSecret
    }

    const clearOperatorSecret = () => {
        localStorage.removeItem(OPERATOR_SECRET_STORAGE_KEY)
        setOperatorSecret("")
        setDetailData(null)
        setDetailError(null)
        setDetailOpen(false)
        setEconomicsData(null)
        setEconomicsError(null)
    }

    const loadOperatorDetail = async (snapshotId: string) => {
        const secret = operatorSecret || promptOperatorSecret()
        if (!secret) return

        setDetailOpen(true)
        setDetailLoading(true)
        setDetailError(null)

        try {
            const response = await fetch(`/api/billing/operator/usage-detail/${snapshotId}`, {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
                    "X-Operator-Secret": secret,
                },
            })
            const payload = await response.json().catch(() => ({}))
            if (!response.ok) throw new Error(payload.detail || `HTTP ${response.status}`)
            setDetailData(payload as OperatorDetail)
        } catch (error) {
            setDetailData(null)
            setDetailError(error instanceof Error ? error.message : "Не удалось загрузить operator details")
        } finally {
            setDetailLoading(false)
        }
    }

    const loadOperatorEconomics = async (secretOverride?: string) => {
        const secret = secretOverride || operatorSecret || promptOperatorSecret()
        if (!secret) return

        setEconomicsLoading(true)
        setEconomicsError(null)

        try {
            const response = await fetch("/api/billing/operator/economics-view", {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
                    "X-Operator-Secret": secret,
                },
            })
            const payload = await response.json().catch(() => ({}))
            if (!response.ok) throw new Error(payload.detail || `HTTP ${response.status}`)
            setEconomicsData(payload as OperatorEconomicsView)
        } catch (error) {
            setEconomicsData(null)
            setEconomicsError(error instanceof Error ? error.message : "Не удалось загрузить economics view")
        } finally {
            setEconomicsLoading(false)
        }
    }

    const resetFilters = () => {
        setDateFrom("")
        setDateTo("")
        setModelFilter("")
        setPage(1)
        loadSummary()
    }

    return (
        <div>
            <h2 className="text-2xl font-bold text-white mb-6">Использование</h2>

            <OperatorModeCard
                enabled={operatorRequested}
                hasSecret={operatorSecret.length > 0}
                onEnable={promptOperatorSecret}
                onClear={clearOperatorSecret}
            />

            <OperatorEconomicsPanel
                enabled={operatorRequested}
                hasSecret={operatorSecret.length > 0}
                loading={economicsLoading}
                error={economicsError}
                data={economicsData}
                onReload={() => { void loadOperatorEconomics() }}
            />

            <SummaryCards summary={summary} />

            {summary?.has_estimated && summary.estimated_caveat && (
                <div className="mb-4 px-4 py-2 rounded border border-amber-800/40 bg-amber-900/10">
                    <p className="text-amber-500/80 text-xs italic">{summary.estimated_caveat}</p>
                </div>
            )}

            <FiltersCard
                dateFrom={dateFrom}
                dateTo={dateTo}
                modelFilter={modelFilter}
                onDateFromChange={(value) => { setDateFrom(value); setPage(1) }}
                onDateToChange={(value) => { setDateTo(value); setPage(1) }}
                onModelChange={(value) => { setModelFilter(value); setPage(1) }}
                onReset={resetFilters}
            />

            <LogsTable
                logsData={logsData}
                loading={loading}
                page={page}
                operatorRequested={operatorRequested}
                onPrev={() => setPage((prev: number) => prev - 1)}
                onNext={() => setPage((prev: number) => prev + 1)}
                onDetails={loadOperatorDetail}
            />

            <OperatorDetailModal
                open={detailOpen}
                loading={detailLoading}
                error={detailError}
                detail={detailData}
                onClose={() => setDetailOpen(false)}
            />
        </div>
    )
}
