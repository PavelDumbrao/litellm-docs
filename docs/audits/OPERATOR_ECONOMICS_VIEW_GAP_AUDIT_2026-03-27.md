# Operator Economics View Gap Audit

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Статус:** Gap audit завершён

---

## 1. Что economics information существует только в docs

На момент аудита economics truth уже был собран в markdown-слое:

- `PROVIDER_ECONOMICS_GAP_AUDIT_2026-03-27.md`
- `PROVIDER_ECONOMICS_SOURCE_MAP.md`
- `PROVIDER_ECONOMICS_REPORT.md`
- `PROVIDER_ECONOMICS_CONFIDENCE_MATRIX.md`
- `PROVIDER_ECONOMICS_IMPLEMENTATION_2026-03-27.md`

То есть знания уже есть, но они доступны только через ручное чтение md-файлов.

Оператор пока не может открыть `/usage?operator=1` и сразу увидеть:

- margin по модели,
- margin по категории,
- confidence split,
- incomplete models,
- special-unit caveats.

---

## 2. Что оператор пока не может inspect быстро

Без нового internal economics view оператору неудобно быстро ответить на вопросы:

1. какая модель даёт высокий / низкий margin;
2. какие категории near-50% proxy-layer, а какие сильно более маржинальны;
3. какие модели Exact, какие Estimated, какие Incomplete;
4. где incomplete coverage и почему;
5. какой primary provider path используется как basis.

Сейчас это требует:

- открыть несколько md-файлов,
- сверять таблицы руками,
- вручную склеивать category picture.

---

## 3. Минимально полезный economics view

Минимальный operator economics view должен показывать:

### Model-level

- `model`
- `category`
- `billing_unit`
- `primary provider`
- `retail rate` (proxy USD/1M)
- `provider cost basis` (USD/1M)
- `estimated gross margin %`
- `confidence` = Exact / Estimated / Incomplete
- `proxy caveat`, если applicable

### Category-level

- `category`
- `total_models`
- `Exact / Estimated / Incomplete counts`
- `avg input margin %`
- `avg output margin %`
- short note: `Token-based exact view` / `Proxy economics only` / `Coverage incomplete`

### Header-level summary

- total models
- exact count
- estimated count
- incomplete count

---

## 4. Что можно безопасно показывать internally, но нельзя клиентам

| Поле | Customer UI | Operator economics view |
|---|---|---|
| margin % | ❌ | ✅ |
| provider cost basis | ❌ | ✅ |
| provider label / api base | ❌ | ✅ |
| confidence status | ❌ | ✅ |
| incomplete coverage note | ❌ | ✅ |
| category margin rollup | ❌ | ✅ |
| exact/estimated/incomplete split | ❌ | ✅ |

Это безопасно показывать **только** в operator-only режиме, потому что эти данные раскрывают:

- коммерческую маржу,
- vendor mix,
- качество покрытия pricing/provider layer,
- слабые места в catalog/provider alignment.

---

## 5. Минимальный безопасный access path

Самый дешёвый и безопасный путь — **не создавать customer route**, а использовать уже существующий internal режим:

```text
/usage?operator=1
```

С тем же барьером:

- JWT сессия
- `X-Operator-Secret`

То есть economics view должен жить внутри существующего operator mode, а не как customer-facing экран.

---

## Финальный вывод

Gap подтверждён:

- economics knowledge уже есть,
- operator-friendly internal view ещё нет,
- минимально полезное решение — operator-only economics snapshot по моделям и категориям внутри `/usage?operator=1`.
