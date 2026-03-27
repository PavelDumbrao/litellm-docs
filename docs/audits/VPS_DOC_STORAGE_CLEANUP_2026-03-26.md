# VPS DOC STORAGE CLEANUP

Date: 2026-03-26. Consolidation of docs storage on VPS.

## WHAT WAS ON VPS BEFORE

### /docker/litellm-xne6/docs/
141 files — legacy corpus from pre-Git era. Contained outdated audits, baseline JSONs, planning docs, test evidence. Most marked as OUTDATED in CURRENT_SOURCE_OF_TRUTH.md.

### /docker/litellm-xne6/docs-current/
Did not exist.

## WHAT WAS DONE

### 1. Legacy archived
```
mv /docker/litellm-xne6/docs → /docker/litellm-xne6/docs-legacy-archive-2026-03-26/
```
- 141 files preserved (not deleted)
- Contains all pre-Git documentation artifacts

### 2. Git repo cloned
```
git clone https://github.com/PavelDumbrao/litellm-docs.git /docker/litellm-xne6/docs-current/
```
- Full canonical doc set from GitHub
- README.md present
- docs/INDEX.md present
- docs/current/ (12 canonical files)
- docs/audits/ (14 audit files + sql/)
- docs/historical/ (migration plan)

## CURRENT VPS DOC STRUCTURE

```
/docker/litellm-xne6/
├── config.yaml                  ← LIVE TRUTH (routing)
├── custom_callbacks.py          ← LIVE TRUTH (callbacks)
├── docs-current/                ← CANONICAL DOCS (from Git)
│   ├── README.md
│   └── docs/
│       ├── INDEX.md
│       ├── current/             (12 files)
│       ├── audits/              (14 files + sql/)
│       └── historical/
└── docs-legacy-archive-2026-03-26/  ← LEGACY ARCHIVE (141 files)
```

## WHAT NOW COUNTS AS

| Layer | Location | Status |
|---|---|---|
| Canonical docs | GitHub: PavelDumbrao/litellm-docs | PRIMARY — edit here, push, pull on VPS |
| Runtime truth | /docker/litellm-xne6/config.yaml + billing DB | ALWAYS overrides any doc |
| Local docs copy | /docker/litellm-xne6/docs-current/ | Mirror of Git — run git pull to update |
| Legacy archive | /docker/litellm-xne6/docs-legacy-archive-2026-03-26/ | DO NOT USE as source — historical only |

## DESKTOP/MAC ARTIFACTS

Desktop has many .md files from pre-Git era (20+ files). These are legacy copies of docs that are now in Git. Examples: AUDIT_REPORT.md, BACKEND_*.md, CAPABILITY_*.md, CHATGPT_READPACK.md, CLAUDE_TOOLS_ROUTER_*.md, CLEANUP-PLAN.md, LITELLM_*.md, and many more.

**Recommendation:** These can be deleted from Desktop since all canonical docs are now in GitHub repo. Not urgent — they don't create confusion as long as docs/current/* in Git is trusted.

## VERIFICATION

- README.md in docs-current: YES
- docs/INDEX.md: YES
- docs/current/: 12 canonical files present
- docs/audits/: 14 audit files + sql/ present
- docs/historical/: migration plan present
- Legacy archive: 141 files preserved
- No config.yaml changes
- No billing DB changes