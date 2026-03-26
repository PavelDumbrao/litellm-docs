# GIT DOCS HARDENING REPORT

**Date:** 2026-03-26

## 1. Files Updated

README.md — added WARNING about legacy VPS docs being outdated
docs/INDEX.md — added explicit sections: Current, Audits, Legacy/Historical, Live Sources of Truth
docs/historical/LEGACY_DOCS_MIGRATION_PLAN.md — NEW, 3-bucket classification of 56 legacy docs

## 2. Links Checked

All 9 relative links in docs/INDEX.md verified correct:
current/CURRENT_SOURCE_OF_TRUTH.md, LIVE_DOC_INDEX.md, LIVE_PUBLIC_MODEL_CATALOG.md, LIVE_PUBLIC_ALIAS_MAP.md, LIVE_PRICING_REFERENCE.md, LIVE_ROUTING_AND_FALLBACK_REFERENCE.md, audits/CURRENT_STATE_AUDIT_2026-03-26.md, GIT_CANONICALIZATION_REPORT_2026-03-26.md, historical/LEGACY_DOCS_MIGRATION_PLAN.md

## 3. What Changed

README.md: Added WARNING block about legacy VPS docs
INDEX.md: Added 4 explicit sections with clear trust rules and override warnings

## 4. Legacy Migration Plan

3 buckets: Historical only (~25 files, leave on VPS), Superseded (~12 files, already replaced), Migrate later (~13 files, review individually)

## 5. BLOCK C — Current Doc Quality

Reviewed all 6 current docs. All factually accurate, properly labeled, correctly distinguish safe vs proxy-billed. No changes needed.

## 6. Final Verdict

Entrypoint: docs/INDEX.md in PavelDumbrao/litellm-docs
Trustworthy set: 6 current docs + 2 audits
Next task: re-run audit when config/DB changes, review Bucket 3 legacy docs individually