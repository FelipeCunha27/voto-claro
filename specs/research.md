# Phase 0 Research: Tradução de Projetos Políticos para Linguagem Acessível

**Feature**: `001-bill-plain-language-dashboard` | **Date**: 2026-09-13 (supersedes the 2026-09-10 pass)

**Method note**: Django facts were fetched from the versioned Django 6.1 documentation through Context7 (`/websites/djangoproject_en_6_1`) — unlike the previous pass, where Context7 was unreachable and everything had to be read out of `.venv`. Package-level claims were additionally verified by running code against the real environment; every verification below can be re-run.

**Verified environment**: Django 6.1.1, Python 3.14.7, openai 3.10.0, pydantic 2.13.5, python-dotenv 1.2.3.

**What changed since the previous pass**: the durable task backend — previously the highest-priority open risk with no known solution — is resolved (D3). Five clarifications recorded in `spec.md` on 2026-09-13 are folded into D5, D6, D10 and D11.

---

## D1. Product scope decisions

**Decision**: Authenticated submission with open registration (FR-002); pasted text plus PDF/DOCX upload (FR-003); mandatory human approval before publication (FR-015).

**Rationale**: Confirmed by the user on 2026-09-10. These three shape the architecture more than any technology pick. Mandatory approval makes the moderation queue MVP scope rather than a later addition, and decouples generation latency from public-facing latency — a slow LLM call delays a curator, never a reader. Authenticated submission makes `django.contrib.auth` load-bearing from day one and lets rate limiting key on user rather than IP, which is both exact and cheap to enforce.

**Alternatives considered**: Anonymous submission (rejected — makes abuse control the dominant engineering problem and leaves LLM spend unbounded); automatic publication (rejected — puts unreviewed machine output about political content in front of the public, the single largest reputational risk in this domain); confidence-triaged publication (rejected for v1 — requires calibrating a "doubtful" threshold, which is an unmade product decision).

---

## D2. Django app layout

**Decision**: Apps live under `src/voto_claro/`, registered in `INSTALLED_APPS` as `voto_claro.<app>`.

**Rationale**: User decision on 2026-09-10, resolving the open question flagged in `CLAUDE.md`. Everything ships inside the single distributable package built by `uv_build`, so there is one import root rather than two competing ones. `src/voto_claro/` is already installed into `.venv` in editable mode, so `voto_claro.bills` imports with no path manipulation.

**Consequences**: `startapp` needs the target directory created first and passed explicitly — `mkdir -p src/voto_claro/bills && uv run manage.py startapp bills src/voto_claro/bills`. The generated `apps.py` will contain `name = "bills"` and **must** be corrected to `name = "voto_claro.bills"`, or app loading fails. This is the most common mistake with this layout; `quickstart.md` calls it out.

**Alternatives considered**: Repo-root apps (rejected by user) — plainer `INSTALLED_APPS` entries and no `apps.py` fixup, but leaves two Python roots with an ambiguous boundary.

---

## D3. Background processing — durable backend (resolves the previous pass's top risk)

**Decision**: Use the built-in `django.tasks` framework with **`django-tasks-db` 0.13.0** (`django_tasks_db.DatabaseBackend`) as the backend, run by a `manage.py db_worker` process. Tests use `DummyBackend` to assert enqueueing, or run the task function directly.

**Verified** — executed against Django 6.1.1 on Python 3.14.7 in an ephemeral environment:

- `manage.py check` passes with `django_tasks_db` in `INSTALLED_APPS`; migrations apply cleanly.
- The backend reports `supports_defer=True`, `supports_get_result=True`, `supports_async_task=True` — strictly more capable than `ImmediateBackend`.
- `add.enqueue(2, 3)` returns status `READY` **and persists a `DBTaskResult` row without executing the task**. That persisted row is the durability property SC-007 needs.
- Management commands `db_worker` and `prune_db_task_results` are both registered.

**Compatibility caveat, stated plainly**: the package's classifiers stop at Django 6.0 and its base requirement is only `django>=5.2`. Django 6.1 is therefore *untested upstream* but works — which is why the probe above exists rather than a citation. Its `compat` extra (`django<6.0` plus the `django-tasks` backport) is for projects on older Django and **must not** be installed here; on Django 6.1 the built-in `django.tasks` is the framework and `django-tasks-db` supplies only the backend. Re-run the probe on any upgrade.

**Rationale**: Django 6.1's own documentation is explicit that the shipped backends are for development and testing and that "production systems should utilize third-party backends that support durable queues and worker processes." An ORM-backed queue needs no broker, no extra service, and no new operational surface — the queue lives in the database that already exists and is already backed up. At 200 submissions/day (SC-010), that is ample.

**Why not `ImmediateBackend` in production**: it runs the task inside the request/response cycle. The HTTP request would block on a multi-second LLM call, which fails FR-014 in substance rather than merely in form, and an in-process task cannot survive a restart, which fails FR-013 and SC-007.

**Alternatives considered**: Celery + Redis (rejected — a broker plus a second service is disproportionate for this volume, and adds an operational dependency to a project with no infrastructure yet); hand-writing a `BaseTaskBackend` subclass (rejected — `BaseTaskBackend` is an ABC needing `enqueue`, plus result storage, worker loop, locking and pruning; that is a library, and one already exists); a `cron` sweep over a status column with no queue (rejected — reimplements the abstraction and hard-codes the choice into every call site).

**Defence in depth for SC-007**: the Submission row, not the queue row, remains the source of truth. A periodic sweep re-enqueues any Submission left in `received`/`processing` past a timeout. Even total loss of the queue table cannot lose a submission.

---

## D4. LLM generation contract

**Decision**: Call the OpenAI Responses API via `client.responses.parse(...)` with a Pydantic model as `text_format`, behind an internal adapter so the provider stays swappable.

**Verified**: `Responses.parse` accepts `text_format`, `input`, `instructions`, `model`, `temperature`, `max_output_tokens`, `timeout`. The SDK exposes `APITimeoutError`, `RateLimitError`, `APIConnectionError`, `APIStatusError`, `LengthFinishReasonError`, and the client defaults to `max_retries=2`.

**Rationale**: Structured parsing removes prompt-fragile free-text scraping. The generated version has a fixed shape — objective, who is affected, what changes in practice, points of attention — mapping directly onto the fields FR-008 requires, plus the theme suggestion FR-008a adds. A schema violation surfaces as a clean validation error that can be retried, rather than as a malformed page.

**Retry split**: the SDK's own `max_retries` handles transport blips within a call. FR-013's retry is a different thing — a task-level retry with `attempt_count` persisted on the Submission, so a retry survives a worker restart. Both exist; do not collapse them.

**Fidelity controls for FR-009** (no invented facts, no value judgement, no recommendation): these are prompt-and-review obligations, not API guarantees. The prompt instructs the model to work only from the supplied text and to refuse rather than speculate; the schema carries no field that invites an opinion; mandatory human approval (D1) is the actual enforcement mechanism. Treat the first two as harm reduction and the third as the control.

**Provider abstraction**: all `openai` imports are confined to `bills/adapters/openai_adapter.py`. Everything else depends on a narrow interface taking source text and returning the structured result, which keeps retry logic and tests free of network concerns — tests use a fake adapter, not HTTP mocking.

**Alternatives considered**: Chat Completions with manual JSON parsing (rejected — hand-written parsing and repair logic for something the SDK does); calling the model from the view (rejected — no retry, no durability, blocks the user).

---

## D5. Content screening and theme suggestion

**Decision**: Three stages — a deterministic pre-check before any paid call, then the OpenAI moderations endpoint, then an "is this actually a legislative text?" judgement folded into the generation call. The same generation call returns the suggested theme (FR-008a).

**Verified**: `Moderations.create` exists in openai 3.10.0.

**Deterministic stage, with the now-concrete thresholds** (FR-004, clarified 2026-09-13): usable text between **500 and 50,000 characters**, Portuguese, and a usable-character ratio above a floor. This stage rejects the most common junk at zero cost, which matters precisely because FR-006 exists to bound spend. The 50,000-character ceiling also bounds the cost of any single call.

**Theme handling**: the generation schema carries a `suggested_theme` constrained to the controlled vocabulary. A value outside the vocabulary is discarded rather than auto-created — FR-008a requires the bill then stay themeless until an administrator sets it, and FR-018 requires a themeless bill still be publishable. This keeps the filter facet from fragmenting while never blocking publication on a classification failure.

**Alternatives considered**: Moderation only after generation (rejected — pays for content that will be discarded); no automated screening at all (rejected — pushes filtering cost onto the curator, whose scarcity is the system's real bottleneck under D1); free-text themes (rejected by clarification — fragments the filter).

---

## D6. Document text extraction (FR-003)

**Decision**: `pypdf` for PDF, `python-docx` for DOCX. Extract synchronously on upload, before enqueueing generation. Reject when extracted text falls below the usable-character threshold, telling the user to paste the text instead.

**Verified**: `pypdf` 6.18.1 and `python-docx` 1.2.0 both import and run on Python 3.14.7, confirmed in an ephemeral 3.14 environment. This check mattered: `python-docx`'s PyPI classifiers stop at Python 3.11, so its support for 3.14 is undeclared rather than absent. Pin deliberately and re-check on upgrade.

**Rationale**: Both are pure Python with no system dependencies, so `uv sync` remains sufficient for setup. Extracting before enqueue means a broken file fails fast with a clear error instead of consuming a queue slot and an LLM call. The threshold check is exactly what catches scanned PDFs, satisfying that edge case without OCR.

**Explicitly out of scope**: OCR. Tesseract would add a system-level dependency and a large accuracy question for a case the user can trivially work around by pasting text.

**Alternatives considered**: `pdfplumber` (richer layout analysis, heavier; unnecessary for linear prose); `PyMuPDF` (fast and excellent, but AGPL — a licensing decision this project should not make implicitly).

---

## D7. Configuration and secrets

**Decision**: Load `.env` via `python-dotenv` at the top of `core/settings.py`; read `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` and `OPENAI_API_KEY` from the environment. Commit `.env.example`, never `.env`.

**Rationale**: `CLAUDE.md` flags that `SECRET_KEY` is still the hardcoded `django-insecure-…` default with `DEBUG = True`, and that both dependencies are declared but unused. Adding a required `OPENAI_API_KEY` is the natural moment to fix this, since the app now genuinely cannot start correctly without external configuration.

**Fail-fast rule**: `SECRET_KEY` gets no default outside `DEBUG`. A missing key must abort startup rather than silently fall back — a fallback default is how insecure keys reach production.

**Also**: `db.sqlite3` is untracked and absent from `.gitignore`. Add it there before the first commit rather than committing the binary.

---

## D8. Data integrity for the audit trail (FR-010, FR-011, FR-026)

**Decision**: Submitted source text is write-once. Regeneration inserts a new `AccessibleVersion` rather than mutating the existing one, and publish/unpublish transitions append to a separate audit table.

**Rationale**: FR-026 requires reconstructing what was publicly visible and when. That is impossible if rows are updated in place. Append-only storage makes the audit trail a consequence of the data model rather than something that depends on remembering to write a log line.

**Alternatives considered**: `django-simple-history` (rejected — a general-purpose dependency for three specific tables); updating rows and logging separately (rejected — the log and the data drift apart, and the log is what you need precisely when something went wrong).

---

## D9. Storage, search and testing

**Decision**: SQLite in development, PostgreSQL as the production target. Keyword search (FR-017) sits behind a single query function in `panel/search.py`. Django's built-in test runner via `uv run manage.py test`.

**Search**: PostgreSQL gets `SearchVector`/`SearchQuery`/`SearchRank` from `django.contrib.postgres.search`, ranked by relevance. SQLite gets a case-insensitive `icontains` fallback over title and summary. Both satisfy FR-017's observable behaviour — matching bills listed, non-matching omitted — and the two implementations must never leak past that one function, or view code silently becomes Postgres-only.

**Uploaded files**: Django's `STORAGES` with local filesystem in development. Originals are retained (FR-010); extracted text alone is not a sufficient source of truth for an audit trail.

**Testing**: no pytest is installed and `CLAUDE.md` documents the Django runner as the project's test command. Adding a second test framework is not this feature's job.

---

## D10. Rate limiting (FR-006, concrete since 2026-09-13)

**Decision**: Enforce 5 submissions per user per rolling 24 hours with a `COUNT` over `Submission(submitter, created_at)` inside the submission transaction. No rate-limiting dependency.

**Rationale**: The index backing this query already exists for other reasons. A database count is exact, survives cache eviction and restarts, and cannot be bypassed by cycling cache keys — properties a cache-based limiter does not have. Since D1 makes submission authenticated, there is no IP-based fallback to reason about. `django-ratelimit` was considered and rejected: a cache-based approximation is the wrong trade when the quantity being limited directly maps to money spent on LLM calls.

**Message**: on refusal, tell the submitter when they may try again — FR-006 requires it, which means the window start must be read, not just counted.

---

## D11. Flag abuse and the public review notice (FR-022, FR-024, clarified 2026-09-13)

**Decision**: Anyone may flag, including anonymous readers. Only flags from authenticated accounts count toward the automatic public "revisão pendente" notice. Administrators can force the notice on or off manually, independent of the threshold.

**Rationale**: This splits the open reporting channel from its only automatic public consequence. Anonymous reports still reach the curation queue, so no signal is lost, but no unauthenticated party can unilaterally stamp a bill as suspect — which in political content is a defacement vector, not a hypothetical.

**Implementation note**: the threshold query filters on open flags whose reporter is non-null, over the *current* version only. The manual override is tri-state on `Bill` — auto, forced on, forced off — because a two-state boolean cannot express "administrator has decided this is fine despite the count."

**Residual gap, not resolved by the clarification**: nothing yet bounds how many anonymous flags reach the queue. The public consequence is neutralised; queue spam is not. Carried as a risk below.

---

## Resolved unknowns summary

| # | Unknown | Resolution | Basis |
|---|---------|------------|-------|
| 1 | Who may submit | Authenticated users, open registration | User decision |
| 2 | Input format | Pasted text + PDF/DOCX, no OCR | User decision |
| 3 | Publication gate | Mandatory human approval | User decision |
| 4 | App layout | `src/voto_claro/<app>` as `voto_claro.<app>` | User decision |
| 5 | Durable async execution | `django-tasks-db` `DatabaseBackend` + `db_worker` | Probe against Django 6.1.1 / Python 3.14.7 |
| 6 | LLM call shape | `responses.parse` + Pydantic schema behind an adapter | Signature inspected in openai 3.10.0 |
| 7 | Document extraction | `pypdf` + `python-docx`, threshold check for scanned files | Import probe on Python 3.14.7 |
| 8 | Secrets handling | `python-dotenv`, fail fast, no insecure fallback | Existing `CLAUDE.md` warning |
| 9 | Duplicate criterion | Normalised-text hash only; metadata never decides | Clarification 2026-09-13 |
| 10 | Theme provenance | LLM suggests from controlled vocabulary, curator confirms | Clarification 2026-09-13 |
| 11 | Submission limits | 5 per 24h; 500–50,000 characters | Clarification 2026-09-13 |
| 12 | Submitter notification | Pull-only; no transactional email in this version | Clarification 2026-09-13 |
| 13 | Anonymous flag weight | Recorded, but never triggers the public notice alone | Clarification 2026-09-13 |

## Open risks carried into implementation

1. **Curation throughput is the scaling limit.** SC-010's 200 submissions/day is a curator workload question, not a server capacity question. If the queue is not drained the panel silently stops growing while submitters wait — and because notification is pull-only (FR-012), they wait without being told.
2. **Translation fidelity is not automatically verifiable.** SC-002 and SC-005 need human evaluation. No automated test proves a simplification is not misleading, so the curation UI must make original and generated text easy to compare side by side, or approval degrades into rubber-stamping.
3. **Anonymous flag spam reaches the curation queue.** D11 removed the public consequence but not the queue load. Needs a limit before launch; the shape of that limit is an open product question.
4. **`django-tasks-db` is unverified upstream against Django 6.1.** It works here (D3) but sits one minor version ahead of its declared support. Re-run the probe on any Django or package upgrade, and watch the project for a 6.1 release.
5. **Missed rejections.** With pull-only status (FR-012), a submitter whose bill was rejected may never learn it. Accepted deliberately; revisit if submission volume makes it visible.
