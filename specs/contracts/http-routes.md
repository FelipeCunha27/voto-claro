# Contract: HTTP Routes

**Feature**: `001-bill-plain-language-dashboard` | **Date**: 2026-09-13

This is a server-rendered Django application, so the external interface is its URL surface, not a JSON API. Each route below fixes method, access level, inputs and observable outcomes. Access level is the contract's load-bearing column: FR-016 makes the entire panel anonymous, while FR-002 and FR-025 gate everything that writes.

**Access levels**: `anon` = no authentication; `auth` = any logged-in user; `curator` = `is_curator` required, enforced server-side on every request (never by hiding UI).

---

## Public panel (`voto_claro.panel`) — all `anon`

| Route | Method | Inputs | Outcome |
|-------|--------|--------|---------|
| `/` | GET | `q`, `theme`, `origin`, `date_from`, `date_to`, `order`, `page` | Lists bills whose `current_version` is published, newest first by default (FR-016, FR-018). Non-matching bills omitted (FR-017). Empty result renders an explanatory state with a link clearing filters (FR-021) |
| `/projeto/<slug>/` | GET | — | Bill detail: the four plain-language fields, the AI-generated label, `generated_at`, a link to the original text and to `official_source_url` when present (FR-019, FR-020). Shows the pending-review notice when FR-024's condition holds. 404 if not published |
| `/projeto/<slug>/original/` | GET | — | The full submitted source text alongside the accessible version (FR-020, US3 scenario 1) |
| `/projeto/<slug>/sinalizar/` | GET, POST | `description` (required), `excerpt` (optional) | Records a Flag against the bill's **current** version (FR-022, FR-023), then confirms to the reader. `reporter` is the user when authenticated, null otherwise — and that nullity decides whether it counts toward FR-024 |

**Contract invariants**

- No route in this app writes to any model except `Flag`. That is enforced structurally: `panel` has no other write path.
- A bill with no published `current_version` is a 404 here, never a stub page (US2 scenario 5).
- Filters combine with AND (US2 scenario 3). Unknown filter values yield the empty state, not a 500.
- Generated content is always escaped. Model output is untrusted input.

---

## Submission (`voto_claro.bills`) — `auth`

| Route | Method | Inputs | Outcome |
|-------|--------|--------|---------|
| `/enviar/` | GET, POST | `title` (required), `origin_body`, `bill_number`, `bill_year`, `official_source_url`, and exactly one of `source_text` or `uploaded_file` | Validates, screens, deduplicates, creates a Submission and enqueues generation. Redirects to the status page with `status=received` (FR-001, FR-003, FR-014) |
| `/minhas-submissoes/` | GET | `page` | Lists **only the requesting user's** submissions with current status and, for failures and rejections, a legible reason (FR-012) |
| `/minhas-submissoes/<uuid>/` | GET | — | One submission's status and, once generated, its accessible version. 404 for another user's submission — not 403, which would confirm the id exists |

**Rejection responses** — all re-render the form with a specific message, never a generic error:

| Condition | Message must state |
|---|---|
| Text outside 500–50,000 usable characters (FR-004) | The limit that was breached |
| Not Portuguese, or too few usable characters (FR-004) | Why it was unusable, and to paste text if a scan was uploaded (FR-003) |
| Not a bill / failed moderation (FR-005) | The reason, in plain language |
| 6th submission within 24h (FR-006) | When the submitter may try again |
| `content_hash` already known (FR-007) | Links to the existing bill; no new generation is enqueued |

**Contract invariant**: a submission that passes validation is durably stored *before* the response is sent. No accepted submission may exist only in memory (SC-007).

---

## Curation (`voto_claro.bills`) — `curator`

| Route | Method | Inputs | Outcome |
|-------|--------|--------|---------|
| `/curadoria/` | GET | `state`, `page` | Queue of versions in `review_state=pending`, oldest first, each showing source text, generated version, suggested theme and open flags (US4 scenario 1) |
| `/curadoria/<uuid>/` | GET | — | Side-by-side original and generated text. Required by risk 2 in `research.md`: without easy comparison, approval degrades into rubber-stamping |
| `/curadoria/<uuid>/aprovar/` | POST | `theme` (confirm or override the suggestion) | Publishes: sets `published_at`, points `Bill.current_version` here, supersedes the previous version, writes `Bill.theme`, appends an AuditEntry (FR-015, FR-018, FR-025) |
| `/curadoria/<uuid>/editar/` | POST | the four content fields | Saves curator corrections, sets `edited_by_curator`; the AI label still renders (FR-019, FR-025) |
| `/curadoria/<uuid>/regerar/` | POST | `reason` | Enqueues a new generation. The previous version is retained and marked `superseded` (FR-011, US4 scenario 4) |
| `/curadoria/<uuid>/despublicar/` | POST | `reason` (**required**) | Removes it from the panel, sets `unpublished_at`, appends an AuditEntry (FR-025, FR-026, US4 scenario 3) |
| `/curadoria/<uuid>/rejeitar/` | POST | `reason` (**required**) | Marks the submission rejected; nothing is published (FR-005) |
| `/curadoria/sinalizacoes/<uuid>/resolver/` | POST | `state` (`resolved`\|`dismissed`), `resolution_note` | Closes a flag with its outcome recorded (FR-025, US3 scenario 4) |
| `/curadoria/projeto/<slug>/aviso/` | POST | `override` (`auto`\|`forced_on`\|`forced_off`) | Forces the review notice on or off regardless of the flag count (FR-024) |

**Contract invariants**

- Every route here is POST-only for mutations, CSRF-protected, and appends exactly one AuditEntry per successful action (FR-026).
- `reason` is mandatory for `despublicar` and `rejeitar`. An empty reason is a validation error, not an empty string in the audit log.
- No route deletes an AccessibleVersion or an AuditEntry. Unpublishing hides; it never erases (FR-026).
- Approval is the **only** path to public visibility. No other route may set `published_at` (FR-015).

---

## Non-functional obligations across all routes

- Public pages meet WCAG 2.1 AA — keyboard navigable, screen-reader compatible, sufficient contrast, correct heading order (FR-028, SC-009).
- Public pages remain usable on mobile widths without loss of content or function (FR-029).
- All copy is Brazilian Portuguese (FR-027).
- No route sends email. Status is pull-only in this version (FR-012).
