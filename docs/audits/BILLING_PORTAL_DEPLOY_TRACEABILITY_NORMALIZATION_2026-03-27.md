# BILLING_PORTAL_DEPLOY_TRACEABILITY_NORMALIZATION_2026-03-27

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Цель:** убрать неоднозначность между `/opt/billing-portal` и `/docker/billing-portal`, зафиксировать один канонический deploy path и сделать будущие деплои воспроизводимыми.

---

## 1. Current VPS deploy topology (до нормализации)

На VPS одновременно существовали две директории с кодом billing-portal:

1. `/opt/billing-portal`
2. `/docker/billing-portal`

Именно это создавало ambiguity: непонятно, какая директория является source-of-build, какая — просто старой копией, а какая реально соответствует running container.

### Что было подтверждено до нормализации

- running container backend совпадал с `/opt/billing-portal/app/api/billing.py`
- frontend source на VPS совпадал с `/opt/billing-portal/frontend/src/pages/Usage.tsx`
- но `/docker/billing-portal/app/api/billing.py` **дрейфовал** от running container и git source
- `/opt/billing-portal` и `/docker/billing-portal` не были git repos

### Практическая проблема

При следующем ручном rebuild через `/docker/billing-portal` можно было случайно собрать старую/дрейфующую версию backend.

---

## 2. Current deploy topology (после нормализации)

После нормализации выбран **один канонический VPS deploy path**:

- **Canonical VPS path:** `/opt/billing-portal`

А `/docker/billing-portal` теперь больше не является отдельным source tree.

### Новая схема

```text
Git source of record:
  /Users/anastasiadumbrao/Desktop/litellm-docs/
    billing-portal-src/

Canonical VPS working copy / deploy path:
  /opt/billing-portal

Compatibility alias:
  /docker/billing-portal -> /opt/billing-portal

Archived old drifting tree:
  /docker/billing-portal_archive_20260327_205918

Running container:
  billing-portal
    uses image/container built from canonical source path workflow
```

---

## 3. What each path means now

### `/opt/billing-portal`
**Роль:** канонический VPS deploy path  
**Назначение:**
- здесь должен жить актуальный source tree для ручного deploy/build на VPS
- здесь же находится frontend source, backend source, static build output, `.env`, `docker-compose.yml`

### `/docker/billing-portal`
**Роль:** compatibility symlink  
**Фактическое состояние:**
- это больше не самостоятельная директория
- теперь это symlink:

```text
/docker/billing-portal -> /opt/billing-portal
```

**Назначение:**
- не ломать старые команды/привычки, если где-то ещё используются пути через `/docker/billing-portal`
- убрать дрейф за счёт того, что оба пути теперь указывают на один и тот же tree

### `/docker/billing-portal_archive_20260327_205918`
**Роль:** backup/archive старой drifting копии  
**Назначение:**
- сохранён как безопасный архив
- ничего деструктивно не удалялось
- использовать только для forensic review, не для deploy

---

## 4. Что именно дрейфовало

До нормализации были подтверждены расхождения между `/opt` и `/docker`:

| Файл | Статус до нормализации |
|---|---|
| `docker-compose.yml` | совпадал |
| `Dockerfile` | drift |
| `requirements.txt` | drift |
| `.env` | drift |
| `app/api/billing.py` | drift |
| `static/index.html` | в `/docker` отсутствовал |

Особенно опасный drift:

- `/docker/billing-portal/app/api/billing.py` ≠ running backend
- `/docker/billing-portal/app/api/billing.py` ≠ git-tracked backend source

Это означало, что `/docker/billing-portal` нельзя было считать надёжным source-of-build.

---

## 5. Что было сделано в рамках нормализации

### Safe normalization steps

1. **Старая drifting директория не удалялась**
2. Она была **переименована в архив**:

```text
/docker/billing-portal_archive_20260327_205918
```

3. Создан symlink:

```text
/docker/billing-portal -> /opt/billing-portal
```

### Результат

После этого проверки показали:

- `docker-compose.yml` → `/opt` == `/docker`
- `Dockerfile` → `/opt` == `/docker`
- `requirements.txt` → `/opt` == `/docker`
- `.env` → `/opt` == `/docker`
- `app/api/billing.py` → `/opt` == `/docker`
- `static/index.html` → `/opt` == `/docker`

То есть ambiguity между `/opt` и `/docker` устранена без удаления данных.

---

## 6. Canonical deploy model (целевой и практичный)

### Chosen minimal deploy model

#### Source of code (canonical source of record)
- Git repo: `PavelDumbrao/litellm-docs`
- Relevant subtree:
  - `billing-portal-src/frontend/...`
  - `billing-portal-src/app/...`

#### Canonical VPS deploy path
- `/opt/billing-portal`

#### Build artifacts
- frontend build output:
  - `/opt/billing-portal/static`

#### Compatibility path
- `/docker/billing-portal` → symlink to `/opt/billing-portal`

#### Running container
- `billing-portal`
- service defined by `/opt/billing-portal/docker-compose.yml`

### Why this model was chosen

Это минимальный practical вариант без redesign CI/CD:

- не требует полной миграции инфраструктуры
- не требует новой репы прямо сейчас
- убирает дрейф немедленно
- сохраняет обратную совместимость со старыми путями `/docker/...`

---

## 7. Which paths should no longer be edited manually

### Больше НЕ использовать как самостоятельный source tree

- `/docker/billing-portal_archive_20260327_205918`

### Разрешённый рабочий путь

- `/opt/billing-portal`

### Что это означает practically

Если кто-то хочет:
- менять backend source
- менять frontend source
- пересобирать static
- запускать `docker compose up -d --build`

то делать это нужно, начиная с:

```text
/opt/billing-portal
```

Путь `/docker/billing-portal` теперь безопасен только потому, что это symlink на `/opt/billing-portal`.

---

## 8. How future deploys should be performed

### Minimal future deploy workflow

1. Источник изменений — git (`PavelDumbrao/litellm-docs`)
2. Обновляем canonical VPS path `/opt/billing-portal`
3. Если менялся frontend:

```bash
cd /opt/billing-portal/frontend
npm run build
```

4. Если менялся backend/container image:

```bash
cd /opt/billing-portal
docker compose up -d --build
```

5. Проверяем, что container работает:

```bash
docker ps | grep billing-portal
docker logs billing-portal --tail 50
```

### Rule for future operators

- **Source edits** → `/opt/billing-portal`
- **Never edit archive path**
- **Never create a second independent copy under `/docker/billing-portal` again**

---

## 9. What remains not fully solved

Несмотря на нормализацию, deploy traceability всё ещё не идеальна.

### Still missing for full traceability

1. `/opt/billing-portal` не является git checkout
2. running deploy не хранит явный deploy revision marker (`git sha`) внутри app/static/env
3. build bundle всё ещё не содержит явный revision stamp
4. deploy process остаётся manual

### Что это значит

Мы устранили ambiguity и drift, но ещё не сделали deploy mathematically provable к конкретному git SHA изнутри VPS без внешнего audit.

---

## 10. Final verdict

### Verdict: **IMPROVED BUT STILL PARTIAL**

Почему не blocked:
- canonical VPS deploy path теперь определён ✅
- drifting duplicate source tree больше не активен ✅
- старый drift безопасно архивирован ✅
- `/docker/billing-portal` больше не расходится с `/opt/billing-portal` ✅
- future deploy path стал понятным и воспроизводимым ✅

Почему ещё не fully traceable:
- VPS path всё ещё не git checkout ❌
- deploy revision stamp не внедрён ❌
- ручной deploy всё ещё может быть выполнен без фиксации commit SHA ❌

### Practical conclusion

Для billing-portal ambiguity между deploy paths устранена.  
С этого момента **единственный canonical VPS deploy path — `/opt/billing-portal`**, а `/docker/billing-portal` — только symlink-совместимость.  
Это существенно улучшает reproducibility и делает дальнейшую traceability-работу намного проще.

