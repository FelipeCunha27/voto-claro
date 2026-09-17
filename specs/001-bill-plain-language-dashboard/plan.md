# Implementation Plan: Tradução de Projetos Políticos para Linguagem Acessível com Painel Público

**Branch**: `001-bill-plain-language-dashboard` | **Date**: 2026-09-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-bill-plain-language-dashboard/spec.md`

## Summary

Authenticated users submit the text of a bill (pasted, or extracted from PDF/DOCX). A background worker sends it to an LLM, which returns a fixed four-part plain-language version plus a suggested theme. Nothing reaches the public panel without an administrator approving it. Anonymous visitors browse, search and filter the approved versions, always seeing an AI-generated label and a route to the original text, and can flag inaccuracies.

Technically this is one server-rendered Django 6.1 monolith with three apps, a database-backed task queue, and a single adapter module isolating the LLM provider. The architectural load is carried by two spec decisions rather than by any technology choice: mandatory human approval (FR-015) makes the curation queue MVP scope and decouples generation latency from reader-facing latency, and append-only storage (FR-010, FR-011, FR-026) makes the audit trail a property of the schema instead of something code must remember to write.

## Technical Context

**Language/Version**: Python 3.14.7 (`.python-version`), verified in `.venv`

**Primary Dependencies**: Django 6.1.1; openai 3.10.0; pydantic 2.13.5 (transitive via openai); python-dotenv 1.2.3. Added by this feature: `django-tasks-db` 0.13.0 (durable task backend), `pypdf` 6.18.1 (PDF extraction), `python-docx` 1.2.0 (DOCX extraction)

**Storage**: SQLite in development; PostgreSQL in production. Uploaded originals via Django `STORAGES`, local filesystem in development

**Testing**: Django's built-in test runner — `uv run manage.py test`. No pytest; adding a second test framework is out of scope

**Target Platform**: Linux server, server-rendered HTML, responsive down to mobile widths (FR-029)

**Project Type**: Web application — single Django project, no separate frontend build

**Performance Goals**: Plain-language version available to the submitter within 3 minutes for 90% of valid submissions (SC-001); panel sustains 200 submissions/day and 5,000 reads/day (SC-010)

**Constraints**: WCAG 2.1 AA on listing and reading pages (SC-009); LGPD — submitter identity never public, personal data in source text screened before publication; no submission may be lost to LLM downtime (SC-007); per-submitter cap of 5 submissions/24h and 500–50,000 usable characters (FR-004, FR-006)

**Scale/Scope**: Small. ~7 models, ~15 routes, one LLM adapter, one worker process. Curation throughput — not server capacity — is the real ceiling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status: no enforceable gates.** `.specify/memory/constitution.md` is still the unmodified scaffold — every principle is a `[PRINCIPLE_N_NAME]` placeholder. There is nothing to check against, so this gate passes vacuously rather than substantively, and that distinction matters: the design below was reviewed against the spec and against ordinary Django practice, not against ratified project principles.

Two conventions this plan adopts that a future constitution would most plausibly want a say in, recorded now so they are visible rather than implicit:

| Convention adopted | Where it is decided |
|---|---|
| Apps live under `src/voto_claro/`, registered as `voto_claro.<app>` | D2 — user decision, resolves the open question in `CLAUDE.md` |
| Append-only for source text, versions, and audit entries | D8 — forced by FR-010/FR-011/FR-026 |

**Post-design re-check**: unchanged. No new violations, because there is still no standard to violate. Recommend running `/speckit-constitution` before this feature merges.

## Project Structure

### Documentation (this feature)

```text
specs/001-bill-plain-language-dashboard/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── http-routes.md
│   └── ai-generation.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
core/                              # Django project package (settings, root urls, wsgi/asgi)
├── settings.py                    # dotenv load, MAILERS, TASKS, STORAGES
└── urls.py

src/voto_claro/                    # Distribution package; all apps live here
├── __init__.py                    # existing console-script entry point
├── accounts/                      # identity and the curator role
│   ├── apps.py                    # name = "voto_claro.accounts"
│   ├── models.py                  # Profile.is_curator
│   └── tests/
├── bills/                         # domain core
│   ├── apps.py                    # name = "voto_claro.bills"
│   ├── models.py                  # Submission, Bill, Theme, AccessibleVersion, Flag, AuditEntry
│   ├── forms.py                   # submission form, flag form, curation actions
│   ├── views.py                   # submit, my-submissions, curation queue
│   ├── tasks.py                   # @task generate_accessible_version
│   ├── services/
│   │   ├── extraction.py          # pypdf / python-docx -> text
│   │   ├── screening.py           # deterministic checks + moderations
│   │   ├── dedupe.py              # normalisation + content hash
│   │   └── generation.py          # orchestration, retries, audit writes
│   ├── adapters/
│   │   └── openai_adapter.py      # the ONLY module importing openai
│   ├── migrations/
│   └── tests/
├── panel/                         # public read-only surface
│   ├── apps.py                    # name = "voto_claro.panel"
│   ├── views.py                   # list, detail, original text, flag submit
│   ├── search.py                  # single query function; SQLite/Postgres diverge here
│   └── tests/
├── templates/
└── static/
```

**Structure Decision**: Single Django project with three apps under `src/voto_claro/`, registered as `voto_claro.<app>` (D2). `panel` depends on `bills`; `bills` depends on `accounts`; nothing depends on `panel`. Giving the public read path its own app with no write access makes "the public cannot mutate anything" a structural property rather than a rule to remember. No separate frontend project: the spec needs server-rendered pages that are keyboard-navigable and screen-reader compatible (FR-028), which Django templates deliver without a build step.

## Complexity Tracking

> Filled despite no constitution violations, because two items cost more than their line count suggests and should be visible before `/speckit-tasks` expands them.

| Item | Why needed | Simpler alternative rejected because |
|------|------------|--------------------------------------|
| `django-tasks-db` + a long-running `db_worker` process | FR-013, FR-014 and SC-007 require that a submission survive a process restart and be retried. Django 6.1 ships only `ImmediateBackend` and `DummyBackend`, both of which run in-process | `ImmediateBackend` blocks the HTTP request on a multi-second LLM call and loses queued work on restart, directly failing SC-007. Celery + Redis was rejected separately as disproportionate infrastructure for 200 submissions/day |
| Append-only `AccessibleVersion` and `AuditEntry` instead of in-place updates | FR-026 requires reconstructing what was publicly visible and when, which is impossible once rows are overwritten | Updating rows and writing a separate log drifts from the data exactly when the log is most needed — during an incident |
