import { useEffect, useState } from "react"
import { usageApi } from "../lib/api"

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

export default function Usage() {
    const [summary, setSummary] = useState<any>(null)
    const [logsData, setLogsData] = useState<LogsResponse>({ logs: [], total: 0, page: 1, per_page: 50, pages: 1 })
    const [loading, setLoading] = useState(false)
    const [page, setPage] = useState(1)
    const [dateFrom, setDateFrom] = useState("")
    const [dateTo, setDateTo] = useState("")
    const [modelFilter, setModelFilter] = useState("")

    useEffect(() => {
        usageApi.summary().then(r => setSummary(r.data)).catch(() => { })
    }, [])

    useEffect(() => {
        setLoading(true)
        usageApi.logs({
            date_from: dateFrom || undefined,
            date_to: dateTo || undefined,
            model: modelFilter || undefined,
            page,
            per_page: 50,
        }).then(r => {
            setLogsData(r.data || { logs: [], total: 0, page: 1, per_page: 50, pages: 1 })
        }).finally(() => setLoading(false))
    }, [page, dateFrom, dateTo, modelFilter])

    const handleFilterChange = () => setPage(1)

    return (
        <div>
            <h2 className="text-2xl font-bold text-white mb-6">Использование</h2>

            {/* Summary cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div className="card"><p className="text-gray-400 text-sm">Запросов</p><p className="text-2xl font-bold text-white">{summary?.total_requests ?? "—"}</p></div>
                <div className="card"><p className="text-gray-400 text-sm">Успешных</p><p className="text-2xl font-bold text-green-400">{summary?.success_requests ?? "—"}</p></div>
                <div className="card"><p className="text-gray-400 text-sm">Ошибок</p><p className="text-2xl font-bold text-red-400">{summary?.error_requests ?? "—"}</p></div>
                <div className="card"><p className="text-gray-400 text-sm">Списано кредитов</p><p className="text-2xl font-bold text-white">{summary?.total_charged_credits ?? logsData.logs.reduce((s, l) => s + l.charged_credits, 0).toFixed(4)}</p></div>
            </div>

            {/* Filters */}
            <div className="card mb-4">
                <p className="text-gray-400 text-sm font-medium mb-3">Фильтры</p>
                <div className="flex flex-wrap gap-3">
                    <div>
                        <label className="text-gray-500 text-xs block mb-1">От</label>
                        <input type="date" className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-white" value={dateFrom} onChange={e => { setDateFrom(e.target.value); handleFilterChange() }} />
                    </div>
                    <div>
                        <label className="text-gray-500 text-xs block mb-1">До</label>
                        <input type="date" className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-white" value={dateTo} onChange={e => { setDateTo(e.target.value); handleFilterChange() }} />
                    </div>
                    <div>
                        <label className="text-gray-500 text-xs block mb-1">Модель</label>
                        <input className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-white w-48" placeholder="gpt-4o-mini..." value={modelFilter} onChange={e => { setModelFilter(e.target.value); handleFilterChange() }} />
                    </div>
                    <div className="flex items-end">
                        <button className="px-3 py-1 text-sm text-gray-400 hover:text-white border border-gray-700 rounded" onClick={() => { setDateFrom(""); setDateTo(""); setModelFilter(""); setPage(1) }}>Сбросить</button>
                    </div>
                </div>
            </div>

            {/* Logs table */}
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
                            </tr>
                        </thead>
                        <tbody>
                            {logsData.logs.map((log) => (
                                <>
                                    <tr key={log.id} className="border-b border-gray-800/40 hover:bg-gray-800/20">
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
                                    </tr>
                                    {log.proxy_billed && log.caveat_text && (
                                        <tr key={`${log.id}-caveat`} className="border-b border-gray-800/20">
                                            <td colSpan={8} className="pb-2 pt-0 pr-3">
                                                <p className="text-amber-600/70 text-xs pl-0 italic">{log.caveat_text}</p>
                                            </td>
                                        </tr>
                                    )}
                                </>
                            ))}
                        </tbody>
                    </table>
                )}

                {/* Pagination */}
                {logsData.pages > 1 && (
                    <div className="flex justify-center gap-2 mt-4">
                        <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="px-3 py-1 text-sm border border-gray-700 rounded text-gray-400 hover:text-white disabled:opacity-40">←</button>
                        <span className="text-gray-500 text-sm py-1">{page} / {logsData.pages}</span>
                        <button disabled={page >= logsData.pages} onClick={() => setPage(p => p + 1)} className="px-3 py-1 text-sm border border-gray-700 rounded text-gray-400 hover:text-white disabled:opacity-40">→</button>
                    </div>
                )}
            </div>
        </div>
    )
}
