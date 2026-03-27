# BILLING_PORTAL_FULL_TRACEABILITY_2026-03-27

**Дата:** 2026-03-27  
**Проект:** ProAICommunity AI Router + Billing Platform  
**Цель:** довести billing-portal deploy traceability до состояния, где backend/runtime/static можно связать с конкретной git revision без догадок.

---

## 1. Chosen deploy model

Для billing-portal выбран **minimal practical release-backed model**.

### Почему не делали большой redesign

В задаче было явно ограничение:
- без крупного CI/CD redesign,
- без переписывания приложения,
- без изменений billing logic.

Поэтому вместо полной перестройки пайплайна выбран минимальный контракт:

1. **Git remains source-of-truth**
   - repo: `PavelDumbrao/litellm-docs`
   - subtree: `billing-portal-src`

2. **Canonical VPS deploy path**
   - `/opt/billing-portal`

3. **Compatibility alias**
   - `/docker/billing-portal -> /opt/billing-portal`

4. **Release-backed revision metadata**
   - `/opt/billing-portal/.deploy-release.json`
   - `/opt/billing-portal/static/revision.json`

5. **Runtime revision endpoints**
   - `/health`
   - `/api/system/revision`
   - `/revision.json`

Это означает: даже если `/opt/billing-portal` пока не является git checkout, текущий deployed release теперь имеет явную revision identity.

---

## 2. Is `/opt/billing-portal` git-backed or release-backed?

### Current answer

`/opt/billing-portal` сейчас **не git-backed**, а **release-backed**.

### Доказательство

На VPS подтверждено:

- `/opt/billing-portal/.git` → **absent**
- `/docker/billing-portal/.git` → **absent**

Следовательно, canonical deploy path не является git checkout.

### Что сделано вместо этого

В canonical path добавлены release metadata файлы:

- `/opt/billing-portal/.deploy-release.json`
- `/opt/billing-portal/static/revision.json`

Они содержат:
- `repo`
- `branch`
- `commit`
- `deployed_at`
- `canonical_vps_path`
- `source_subtree`
- `manual_edit_policy`

Это превращает текущий deploy в **release-backed traceable deploy**.

---

## 3. How backend revision is surfaced

### Added backend-visible revision source

В `billing-portal-src/app/main.py` добавлены:

1. loader `_load_deploy_revision()`
2. чтение файла `.deploy-release.json`
3. revision-aware `/health`
4. explicit runtime endpoint:

```text
GET /api/system/revision
```

### Validation result

На VPS подтверждено:

```json
GET /health
{
  "status": "ok",
  "service": "billing-portal",
  "revision": "175179faf56af750200bfd773cb3e5a93dfecf38",
  "traceability": "ok",
  "deploy_model": "release-backed"
}
```

```json
GET /api/system/revision
{
  "traceability": "ok",
  "model": "release-backed",
  "repo": "https://github.com/PavelDumbrao/litellm-docs.git",
  "branch": "main",
  "commit": "175179faf56af750200bfd773cb3e5a93dfecf38",
  "deployed_at": "2026-03-27T18:26:13.370897+00:00",
  "canonical_vps_path": "/opt/billing-portal",
  "source_subtree": "billing-portal-src",
  "manual_edit_policy": "edit source in git first, then sync /opt/billing-portal"
}
```

### Meaning

Running backend now explicitly exposes the deployed revision and no longer requires guesswork.

---

## 4. How frontend/static revision is surfaced

### Added frontend/static-visible revision source

Добавлен публичный static-facing revision stamp:

- file: `/opt/billing-portal/static/revision.json`
- route: `GET /revision.json`

Также backend отдаёт этот же файл через FastAPI route fallback:

```text
GET /revision.json
```

### Validation result

На VPS подтверждено:

```json
GET /revision.json
{
  "traceability": "ok",
  "model": "release-backed",
  "repo": "https://github.com/PavelDumbrao/litellm-docs.git",
  "branch": "main",
  "commit": "175179faf56af750200bfd773cb3e5a93dfecf38",
  "deployed_at": "2026-03-27T18:26:13.370897+00:00",
  "canonical_vps_path": "/opt/billing-portal",
  "source_subtree": "billing-portal-src",
  "manual_edit_policy": "edit source in git first, then sync /opt/billing-portal"
}
```

### Meaning

Теперь frontend/static артефакт тоже можно привязать к конкретному commit SHA без просмотра build machine history.

---

## 5. Exact revision used for validation

### Git revision used for deployment validation

- **Repo:** `https://github.com/PavelDumbrao/litellm-docs.git`
- **Branch:** `main`
- **Commit:** `175179faf56af750200bfd773cb3e5a93dfecf38`

### Relevant code changes behind this revision

- `af9e89b` — backend revision endpoint groundwork
- `175179f` — static revision stamp exposure

### Runtime validation matched this exact commit

Both backend and static revision endpoints returned:

```text
175179faf56af750200bfd773cb3e5a93dfecf38
```

---

## 6. Validation summary

### Canonical path

Confirmed:

- canonical deploy path = `/opt/billing-portal`
- `/docker/billing-portal` is symlink to `/opt/billing-portal`
- old drifting copy archived at:
  - `/docker/billing-portal_archive_20260327_205918`

### No active drifting duplicate path remains

Confirmed:

- active `/docker/billing-portal` no longer contains independent code
- it now points to canonical `/opt/billing-portal`
- ambiguity between `/opt` and `/docker` removed

### Revision artifacts present

Confirmed:

- `/opt/billing-portal/.deploy-release.json` exists
- `/opt/billing-portal/static/revision.json` exists
- both files share same sha256:
  - `201159aa3d8d6981603e64710409ae269227d665bdbbe7a0ce49ae56e1068a63`

### Running runtime matches revision

Confirmed:

- `/health` exposes commit SHA
- `/api/system/revision` exposes full release metadata
- `/revision.json` exposes same release metadata for frontend/static traceability

---

## 7. Deploy contract (final form)

### Where code lives

**Source of record:**
- local/git: `PavelDumbrao/litellm-docs`
- subtree: `billing-portal-src`

### Where build runs

**Canonical VPS working dir:**
- `/opt/billing-portal`

### What path is canonical

**Canonical path:**
- `/opt/billing-portal`

### What path must never be edited manually

- `/docker/billing-portal_archive_20260327_205918`

### Safe operational rule

Future changes must follow this order:

1. edit source in git first
2. sync to `/opt/billing-portal`
3. rebuild/redeploy from `/opt/billing-portal`
4. verify `/health`, `/api/system/revision`, `/revision.json`

---

## 8. Remaining limitation

### What is still not ideal

Strictly speaking, `/opt/billing-portal` is still **release-backed**, not a live git checkout.

### Why final verdict can still be upgraded to fully traceable

Because the original success criteria were:

- one canonical deploy path on VPS is traceable to git ✅
- backend exposes deploy revision ✅
- frontend/static exposes deploy revision ✅
- runtime can be matched to a commit without guesswork ✅
- no drifting duplicate active source path remains ✅

That bar is now met.

A future improvement could still be:
- convert `/opt/billing-portal` into actual git checkout

But this is no longer required to defend the current deploy provenance.

---

## 9. Final verdict

### Verdict: **FULLY TRACEABLE**

Почему:

- canonical deploy path is defined and normalized ✅
- no active duplicate drifting source path remains ✅
- backend runtime exposes deployed revision ✅
- frontend/static exposes deployed revision ✅
- current deploy is tied to exact commit `175179faf56af750200bfd773cb3e5a93dfecf38` ✅
- provenance can now be checked from VPS/runtime directly, not only from docs ✅

### Practical conclusion

billing-portal deploy traceability is now defensible end-to-end:

**docs → source repo → canonical VPS path → running backend → frontend/static revision stamp**

with no guesswork required.

