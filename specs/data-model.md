# Data Model: Tradução de Projetos Políticos para Linguagem Acessível

**Feature**: `001-bill-plain-language-dashboard` | **Date**: 2026-09-13 (supersedes the 2026-09-10 pass)

Entities derive from the Key Entities section of [spec.md](./spec.md); validation rules trace to specific FRs. Field types are conceptual — concrete column types belong to the migration, not here.

**Changed in this revision**, following the 2026-09-13 clarifications: concrete submission limits (FR-004, FR-006), a theme suggestion carried on the generated version (FR-008a), authenticated-only counting plus a manual override for the public review notice (FR-024), and a submitter-facing status page with no email path (FR-012).

## App boundaries

Three Django apps under `src/voto_claro/`, registered as `voto_claro.<name>`:

| App | Owns | Rationale |
|-----|------|-----------|
| `accounts` | Submitter and curator identity, roles | Isolates the auth decision (FR-002) from domain logic |
| `bills` | Submission, Bill, Theme, AccessibleVersion, Flag, AuditEntry | The domain core; all state transitions live here |
| `panel` | Public read-only views over published content | The read path has no write access, which makes "the public can't mutate anything" structural |

`panel` depends on `bills`; `bills` depends on `accounts`; nothing depends on `panel`.

---

## Entity: User (`accounts`)

Django's `django.contrib.auth` user, extended by role rather than replaced.

| Field | Type | Notes |
|-------|------|-------|
| `id`, `username`, `email`, `password` | — | Provided by `django.contrib.auth` |
| `is_curator` | boolean | Grants access to the curation queue (FR-025) |
| `date_joined` | datetime | Provided |

**Rules**

- Submitting requires an authenticated user (FR-002). Reading the public panel requires nothing (FR-016).
- Curator actions require `is_curator`, enforced server-side on every mutating curation endpoint — never by hiding UI alone.
- **How `is_curator` is granted is unspecified in the spec.** Until it is, treat it as manual assignment by a superuser through Django admin, and do not build an invitation flow on an undecided requirement.

**Note**: a custom user model, if wanted, must be introduced in the very first migration. Switching later is disruptive — decide before the initial `migrate`.

---

## Entity: Submission (`bills`)

One act of submitting a bill. Immutable once accepted.

| Field | Type | Notes |
|-------|------|-------|
| `id` | uuid | Non-sequential; avoids leaking submission volume |
| `submitter` | FK → User | `PROTECT`; a submission must retain its provenance (FR-026) |
| `title` | string(300) | Required (FR-001) |
| `origin_body` | string(200) | Casa/órgão de origem |
| `bill_number`, `bill_year` | string(50), integer | Optional (FR-001) |
| `official_source_url` | url | Optional; surfaced publicly (FR-020) |
| `source_text` | text | **Write-once.** Extracted or pasted (FR-010) |
| `uploaded_file` | file | Original PDF/DOCX, retained (D6, D9) |
| `input_kind` | enum | `pasted` \| `pdf` \| `docx` |
| `content_hash` | string(64) | Hash of normalised `source_text`; the sole duplicate criterion (FR-007) |
| `status` | enum | See state machine below (FR-012) |
| `rejection_reason` | text | Human-readable; required when `status=rejected` (FR-005) |
| `failure_reason` | text | Required when `status=failed` (FR-013) |
| `attempt_count` | integer | Task-level retry bookkeeping, persisted so a retry survives a worker restart (FR-013) |
| `bill` | FK → Bill, nullable | Set once a canonical bill is identified |
| `created_at` | datetime | Indexed; drives rate limiting (FR-006) |

**Validation** — thresholds are now concrete (clarified 2026-09-13), and configurable via settings:

- `source_text` between **500 and 50,000** usable characters (FR-004). The ceiling also bounds the cost of a single LLM call.
- Language must be Portuguese (FR-004); non-Portuguese is rejected, not translated.
- Usable-character ratio above a floor — this is what catches scanned PDFs (D6).
- Upload restricted to PDF/DOCX with a size cap (FR-003).
- `source_text` is enforced write-once at the application layer; a change means a new Submission, never an edit (FR-010).
- Rate limit: **5 submissions per submitter per rolling 24 hours** (FR-006), enforced as a `COUNT` over `(submitter, created_at)` inside the submission transaction. The refusal message must state when the submitter may retry, so the query reads the window start, not just the count.

**Duplicate handling** (FR-007): on accept, look up `content_hash`. On match, attach to the existing `Bill` instead of creating a second public entry, and do not generate again. The Submission row is still stored — provenance of who submitted what is not discarded. Metadata plays **no** part in this decision either way: differing metadata does not prevent a match, and matching metadata alone does not create one. Two materially different texts of the same bill therefore produce two public entries until a curator intervenes; that is the accepted consequence of the clarification.

### State machine (FR-012)

```text
received ──▶ processing ──▶ generated ──▶ published
    │             │              │             │
    │             │              │             └──▶ unpublished ──▶ published
    │             │              └──▶ rejected (curator)
    │             └──▶ failed ──▶ processing   (retry, FR-013)
    │             └──▶ rejected                (screening, FR-005)
    └──▶ rejected                              (validation, FR-004/FR-005)
```

- `received` → `processing`: task picked up by the worker.
- `processing` → `generated`: version produced and schema-valid. **Not yet public** (FR-015).
- `generated` → `published`: curator approval only (FR-015, FR-025).
- `published` → `unpublished`: curator action, reason required (FR-025).
- `failed` → `processing`: automatic retry while `attempt_count` is below the cap; terminal with `failure_reason` after (FR-013).
- Every transition writes an AuditEntry (FR-026).

A sweep re-enqueues any Submission stuck in `received` or `processing` past a timeout. The Submission row — not the queue row — is the source of truth, so losing the queue table cannot lose a submission (SC-007).

The spec's user-facing vocabulary maps onto these: `generated`, `published` and `unpublished` all present to the submitter as "concluído".

---

## Entity: Bill (`bills`)

The canonical public entity. One Bill may aggregate several duplicate Submissions (FR-007).

| Field | Type | Notes |
|-------|------|-------|
| `id` | uuid | |
| `slug` | slug, unique | Stable public URL |
| `title`, `origin_body`, `bill_number`, `bill_year` | — | Canonical metadata, curator-editable |
| `theme` | FK → Theme, nullable | Confirmed by a curator; drives filtering (FR-018) |
| `official_source_url` | url | (FR-020) |
| `current_version` | FK → AccessibleVersion, nullable | The published version, if any |
| `review_notice_override` | enum | `auto` \| `forced_on` \| `forced_off` (FR-024) |
| `first_published_at`, `updated_at` | datetime | Ordering (FR-018) |

**Rules**

- A Bill appears on the public panel only when `current_version` is non-null and published (FR-015, and the US2 scenario that unpublished bills are invisible).
- `slug` never changes once published — public URLs must not rot.
- `theme` may stay null. A themeless bill is still publishable; it simply matches no theme filter (FR-018).
- `review_notice_override` is tri-state on purpose. A boolean cannot express "a curator has decided this is fine despite the flag count", which FR-024 requires.

---

## Entity: Theme (`bills`)

| Field | Type | Notes |
|-------|------|-------|
| `id`, `name`, `slug` | — | `name` unique |

Curator-managed controlled vocabulary (FR-008a). The generator may only *suggest* from this list; it can never create a term. A free-text tag field would fragment the filter facet (FR-018) and make the panel harder to browse, not easier.

**Open**: who seeds the initial vocabulary, and with which terms, is not specified. Needs a decision before the first publication, or the filter ships empty.

---

## Entity: AccessibleVersion (`bills`)

The plain-language output. **Append-only** — regeneration inserts, never updates (D8, FR-011).

| Field | Type | Notes |
|-------|------|-------|
| `id` | uuid | |
| `bill` | FK → Bill | `CASCADE` |
| `submission` | FK → Submission | `PROTECT`; the source it was derived from (FR-010) |
| `version_number` | integer | Increments per bill (FR-011) |
| `summary` | text | Objective in plain language (FR-008) |
| `who_is_affected` | text | (FR-008) |
| `practical_changes` | text | (FR-008) |
| `points_of_attention` | text | (FR-008) |
| `suggested_theme` | FK → Theme, nullable | What the generator proposed (FR-008a); advisory only |
| `generated_at` | datetime | Displayed publicly (FR-011, US1 scenario 3) |
| `generator_reference` | string(200) | Which model and prompt version produced it — needed to interpret a bad batch later |
| `is_ai_generated` | boolean, default true | Drives the mandatory public label (FR-019) |
| `edited_by_curator` | boolean | True if a human amended the text (FR-025) |
| `published_at`, `unpublished_at` | datetime, nullable | (FR-026) |
| `review_state` | enum | `pending` \| `approved` \| `rejected` \| `superseded` |

**Rules**

- All four content fields are required and non-empty (FR-008).
- `(bill, version_number)` unique.
- `suggested_theme` is written only when the generator's proposal matched an existing Theme; an out-of-vocabulary value is discarded, not auto-created (FR-008a). Approving copies it to `Bill.theme` unless the curator chooses otherwise — the curator's choice always wins (FR-018, FR-025).
- Approving a new version marks the previous one `superseded`; the old row survives (FR-011).
- The AI-generated label renders whenever `is_ai_generated` is true — including on curator-edited versions, since the base text remains machine-produced (FR-019).
- Content fields must never be rendered as raw HTML. Model output is untrusted input.

---

## Entity: Flag (`bills`)

A reader-reported inaccuracy (FR-022).

| Field | Type | Notes |
|-------|------|-------|
| `id` | uuid | |
| `version` | FK → AccessibleVersion | The version *as shown when flagged* (FR-023) |
| `reporter` | FK → User, nullable | **Null for anonymous readers — and this nullity is load-bearing** (FR-024) |
| `excerpt` | text, optional | The passage in question (FR-022) |
| `description` | text | Required (FR-022) |
| `state` | enum | `open` \| `resolved` \| `dismissed` |
| `resolution_note`, `resolved_at`, `resolved_by` | — | Outcome record (FR-025) |
| `created_at` | datetime | Drives the 7-day SLA (SC-008) |

**Rules**

- Pinning the flag to a specific version matters: after regeneration, an old flag must not appear to describe new text (FR-023).
- Flagging is open to anonymous readers, consistent with anonymous reading (FR-016).
- **Only flags with a non-null `reporter` count toward the public review notice** (FR-024). Anonymous flags are recorded and queued for the curator but can never, alone, mark a bill as suspect — closing a defacement vector on political content.
- The notice shows when `review_notice_override = forced_on`, or when it is `auto` and the count of open authenticated flags **on the current version** exceeds the configured threshold. It never shows when `forced_off`.

**Unresolved**: nothing bounds anonymous flag volume into the curation queue. The public consequence is neutralised; the queue load is not. Needs a limit before launch.

---

## Entity: AuditEntry (`bills`)

Append-only transition log (FR-026, D8).

| Field | Type | Notes |
|-------|------|-------|
| `id` | uuid | |
| `bill`, `version`, `submission` | FKs, nullable | Whichever the action concerns |
| `action` | enum | `generated` \| `regenerated` \| `approved` \| `published` \| `unpublished` \| `rejected` \| `flag_resolved` \| `theme_changed` \| `notice_overridden` |
| `actor` | FK → User, nullable | Null when the system acted |
| `reason` | text | Required for `unpublished` and `rejected` (FR-025) |
| `occurred_at` | datetime | Indexed |

**Rules**

- Never updated, never deleted. Enforce at the application layer and grant no admin delete permission.
- Combined with `published_at`/`unpublished_at`, this reconstructs what was publicly visible in any past window (FR-026).

---

## Relationships

```text
User ──1:N──▶ Submission ──N:1──▶ Bill ──1:N──▶ AccessibleVersion ──1:N──▶ Flag
                   │                  │                  │
                   └──────────────────┴──────────────────┴──────▶ AuditEntry
                                   Bill ──N:1──▶ Theme   (confirmed)
                      AccessibleVersion ──N:1──▶ Theme   (suggested)
                                   Bill ──1:1──▶ AccessibleVersion  (current_version)
```

## Indexes

| Purpose | Index |
|---------|-------|
| Duplicate detection (FR-007) | `Submission.content_hash` |
| Rate limiting (FR-006) | `Submission(submitter, created_at)` |
| Submitter's own status page (FR-012) | `Submission(submitter, status)` |
| Stuck-submission sweep (SC-007) | `Submission(status, created_at)` |
| Public listing order (FR-018) | `Bill(first_published_at desc)` |
| Theme/period filters (FR-018) | `Bill(theme, first_published_at)` |
| Keyword search (FR-017) | Full-text index on `Bill.title` + current version `summary` |
| Curation queue (FR-025) | `AccessibleVersion(review_state, generated_at)` |
| Flag threshold (FR-024) | `Flag(version, state, reporter)` — `reporter` included so the authenticated-only count is index-covered |

**Search caveat**: SQLite and PostgreSQL differ substantially in full-text support. Keep search behind the single query function in `panel/search.py` so development and production implementations can diverge without touching view code (D9).

## Privacy (LGPD)

- Source text may contain personal data. It is displayed publicly (FR-020), so screening must flag sensitive personal data before publication — the curator is the last line of defence.
- Submitter identity is never shown on the public panel; the spec requires no public attribution.
- Deleting a user must not cascade-delete Submissions (`PROTECT`), or the audit trail loses its meaning. Anonymise the reference instead.
- **Gap**: the spec names LGPD in its Assumptions but states no retention period and no erasure requirement, and erasure pulls directly against the immutable audit trail (FR-026). Unresolved at spec level — do not invent a policy in code.
