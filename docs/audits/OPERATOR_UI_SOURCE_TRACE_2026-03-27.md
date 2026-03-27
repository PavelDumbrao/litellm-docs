# OPERATOR_UI_SOURCE_TRACE_2026-03-27

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Задача:** определить, где именно лежит исходный код operator UI/backend и насколько текущий VPS deploy привязан к git.

---

## 1. Итог в одном абзаце

На текущий момент **единственный подтверждённый git-репозиторий**, содержащий исходники operator UI и operator backend endpoint, — это:

- **Repo:** `PavelDumbrao/litellm-docs`
- **Remote:** `https://github.com/PavelDumbrao/litellm-docs.git`
- **Branch:** `main`
- **HEAD:** `ef6bfae10ad06bf1abc79e5f49176a9f68392990`

Frontend operator UI **коммитнут** и **совпадает по sha256** с файлом на VPS в `/opt/billing-portal/frontend/src/pages/Usage.tsx`.  
Backend operator endpoint **коммитнут** и **совпадает по sha256** с файлом в running container и с `/opt/billing-portal/app/api/billing.py`.

Но VPS директории `/opt/billing-portal` и `/docker/billing-portal` **не являются git-репозиториями**, а `/docker/billing-portal/app/api/billing.py` **не совпадает** с running backend. Поэтому общий вердикт: **partially traceable**.

---

## 2. Где живёт frontend source code

### Подтверждённый git-tracked source

- **Repo:** `PavelDumbrao/litellm-docs`
- **Branch:** `main`
- **File path:** `billing-portal-src/frontend/src/pages/Usage.tsx`
- **Last commit touching file:**
  - **Commit:** `ef6bfae10ad06bf1abc79e5f49176a9f68392990`
  - **Message:** `feat: add operator UI for usage debit troubleshooting`

### Доказательство

- Local git file sha256:
  - `f798e95083f606d1587f9c1ccc2227a00cf08e2efb31abafb5c2213c711c1583`
- VPS `/opt/billing-portal/frontend/src/pages/Usage.tsx` sha256:
  - `f798e95083f606d1587f9c1ccc2227a00cf08e2efb31abafb5c2213c711c1583`

**Вывод:** deployed frontend source на VPS (`/opt/.../Usage.tsx`) совпадает с git-tracked source из `litellm-docs` commit `ef6bfae`.

---

## 3. Где живёт backend source code

### Подтверждённый git-tracked source

- **Repo:** `PavelDumbrao/litellm-docs`
- **Branch:** `main`
- **File path:** `billing-portal-src/app/api/billing.py`
- **Last commit touching file:**
  - **Commit:** `d441fbc9914d6b700b47a987402a64c6122d14de`
  - **Message:** `feat: operator troubleshooting layer — gap audit, source map, API endpoint, implementation report`

### Доказательство

- Local git file sha256:
  - `7dd429e1b44449f92378fbb1b6c69bf9331cea8f841dd519cdc0c74dd6946181`
- Running container `/app/app/api/billing.py` sha256:
  - `7dd429e1b44449f92378fbb1b6c69bf9331cea8f841dd519cdc0c74dd6946181`
- VPS `/opt/billing-portal/app/api/billing.py` sha256:
  - `7dd429e1b44449f92378fbb1b6c69bf9331cea8f841dd519cdc0c74dd6946181`

**Вывод:** активный backend operator endpoint в контейнере и `/opt/billing-portal` совпадает с git-tracked source из commit `d441fbc`.

---

## 4. Related auth / config changes

### Что реально изменялось

Для operator endpoint используется runtime secret:

- **Runtime config path on VPS:** `/docker/billing-portal/.env`
- **Variable:** `OPERATOR_SECRET=...`

### Traceability статус

- `.env` **не должен** коммититься в git целиком из-за секретов
- но факт изменения runtime config есть только на VPS
- отдельного git-tracked config artifact с non-secret trace на текущий момент нет

### Что НЕ менялось как код

Дополнительный auth code file для operator UI отдельно не создавался.
Использованы:

- existing JWT auth для customer session
- `X-Operator-Secret` проверка в `billing.py`
- localStorage secret handling внутри `Usage.tsx`

**Вывод:** operator auth/config частично traceable:
- code path — traceable
- runtime secret config on VPS — not git-traceable by design

---

## 5. Что именно задеплоено на VPS сейчас

### Frontend

#### Source file on VPS
- `/opt/billing-portal/frontend/src/pages/Usage.tsx`
- sha256 = `f798e95083f606d1587f9c1ccc2227a00cf08e2efb31abafb5c2213c711c1583`

#### Built bundle
- `/opt/billing-portal/static/assets/index-rHmRLop1.js`
- sha256 = `2fe03f1e508511da4f8f498f7dd7d652ab047d330be5bf5c4e3e4282e1550671`
- bundle markers:
  - `Operator details` → present
  - `billing_operator_secret` → present
  - `operator/usage-detail` → present

**Вывод:** собранный frontend bundle действительно содержит operator UI код.

### Backend

#### Running container
- `billing-portal:/app/app/api/billing.py`
- sha256 = `7dd429e1b44449f92378fbb1b6c69bf9331cea8f841dd519cdc0c74dd6946181`

#### VPS source copy
- `/opt/billing-portal/app/api/billing.py`
- sha256 = `7dd429e1b44449f92378fbb1b6c69bf9331cea8f841dd519cdc0c74dd6946181`

**Вывод:** backend operator endpoint в running deploy совпадает с git source (`d441fbc`).

---

## 6. Где traceability ломается

### VPS directories are not git repos

Проверка показала:

- `/opt/billing-portal/.git` → **absent**
- `/docker/billing-portal/.git` → **absent**

То есть VPS не хранит commit hash как git metadata.

### Drift between `/opt` and `/docker`

Проверка backend source:

- `/opt/billing-portal/app/api/billing.py`
  - `7dd429e1b44449f92378fbb1b6c69bf9331cea8f841dd519cdc0c74dd6946181`
- `/docker/billing-portal/app/api/billing.py`
  - `3609940d4a39019b32be6da39a76382fc7aa819a3db09d012b7f5357d338ad30`

**Это критичный traceability gap.**

Значит:

1. Running backend совпадает с git-tracked source
2. Но build/deploy directory `/docker/billing-portal` уже дрейфовал
3. При следующем rebuild из `/docker/billing-portal` feature может откатиться или стать непредсказуемой, если `/docker` не синхронизирован с git source

---

## 7. Привязка артефактов к commit hash

### Frontend artifact

| Artifact | Repo | File | Commit |
|---|---|---|---|
| Operator UI source | `PavelDumbrao/litellm-docs` | `billing-portal-src/frontend/src/pages/Usage.tsx` | `ef6bfae10ad06bf1abc79e5f49176a9f68392990` |

### Backend artifact

| Artifact | Repo | File | Commit |
|---|---|---|---|
| Operator endpoint source | `PavelDumbrao/litellm-docs` | `billing-portal-src/app/api/billing.py` | `d441fbc9914d6b700b47a987402a64c6122d14de` |

### Related config

| Artifact | Location | Git commit |
|---|---|---|
| `OPERATOR_SECRET` runtime config | `/docker/billing-portal/.env` | missing by design / not committed |

---

## 8. Remediation plan (только для traceability)

Так как текущий deploy **не полностью** привязан к git metadata, нужен короткий remediation plan:

### Must fix

1. **Назначить один canonical code repo для billing-portal app**
   - либо отдельный app repo,
   - либо официально признать `litellm-docs/billing-portal-src` canonical source.

2. **Убрать drift между `/opt` и `/docker`**
   - `/docker/billing-portal/app/api/billing.py` должен быть синхронизирован с git-tracked backend source
   - source-of-build directory не должен расходиться с running code

3. **Добавить deploy revision marker**
   - например `DEPLOYED_GIT_REV` env
   - или `version.json` / `build-meta.json` в static bundle
   - или startup log with git SHA

4. **Документировать deploy source-of-truth**
   - что именно buildится: `/opt`, `/docker`, container copy, or git checkout

### Что не нужно делать

- не переписывать operator UI
- не менять billing logic
- не переделывать auth
- не менять pricing/catalog

---

## 9. Final verdict

### Verdict: **PARTIALLY TRACEABLE**

Почему не fully traceable:

- frontend source → traceable to git ✅
- backend running code → traceable to git ✅
- deployed VPS directories themselves are git repos ❌
- `/docker` build source drifted from running/git version ❌
- built frontend bundle не содержит commit SHA как явный deployment stamp ❌

### Практическая интерпретация

Сейчас мы **знаем**, где лежит исходный код operator UI/backend и **можем связать** активный frontend source + active backend source с конкретными commit hash.

Но deploy pipeline всё ещё недостаточно жёстко привязан к git, поэтому traceability не считается полной.

