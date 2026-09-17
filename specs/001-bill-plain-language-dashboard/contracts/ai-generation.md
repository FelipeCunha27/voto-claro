# Contract: Plain-Language Generation

**Feature**: `001-bill-plain-language-dashboard` | **Date**: 2026-09-13

The second external interface is the LLM boundary. This contract fixes the shape of what crosses it, so that everything on the Django side — retries, validation, tests — depends on the shape rather than on the provider.

**Sole implementation**: `src/voto_claro/bills/adapters/openai_adapter.py`. It is the only module in the project permitted to `import openai`. Verified in openai 3.10.0: `client.responses.parse(...)` accepts `text_format`, `input`, `instructions`, `model`, `temperature`, `max_output_tokens`, `timeout`.

---

## The port

```text
generate_accessible_version(source_text: str, themes: list[str]) -> GenerationResult
    raises TransientGenerationError   # retryable: timeout, rate limit, connection, 5xx
    raises PermanentGenerationError   # not retryable: schema violation, refusal, invalid key
```

Callers depend on this signature and these two exception types only. Swapping providers must not require changes outside the adapter — that is the test of whether the boundary is real.

## Output schema

A Pydantic model passed as `text_format`, so a malformed response surfaces as a validation error instead of a broken page.

| Field | Type | Maps to | Rule |
|-------|------|---------|------|
| `summary` | str | `AccessibleVersion.summary` | Non-empty. What the bill sets out to do (FR-008) |
| `who_is_affected` | str | `who_is_affected` | Non-empty (FR-008) |
| `practical_changes` | str | `practical_changes` | Non-empty (FR-008) |
| `points_of_attention` | str | `points_of_attention` | Non-empty (FR-008) |
| `is_legislative_text` | bool | screening decision | False ⇒ reject the submission, store nothing (FR-005) |
| `suggested_theme` | str \| null | `AccessibleVersion.suggested_theme` | Must match a Theme name exactly; anything else is discarded (FR-008a) |

**Schema invariants**

- No field invites an opinion. There is deliberately no `assessment`, `recommendation` or `sentiment` — FR-009 forbids a value judgement on the bill's merits, and the cheapest way to not get one is to give it nowhere to go.
- `is_legislative_text` is returned by the same call that generates, so junk is identified without a second round trip — but only after the free deterministic checks and moderation have already run (D5).
- All fields are plain text. The renderer escapes them; nothing generated is ever trusted as HTML.

## Prompt obligations (FR-009, FR-027)

The instructions must require the model to:

1. Use **only** the supplied text. State that something is not addressed rather than inferring it.
2. Write Brazilian Portuguese at a reading level for completed *ensino fundamental*, explaining any legal term it cannot avoid.
3. Express no view on whether the bill is good, and recommend no position for or against.
4. Preserve scope — not soften, sharpen or invert what the text says.
5. Choose `suggested_theme` only from the supplied list, or return null.

These reduce harm; they do not guarantee it. **Human approval (FR-015) is the actual control**, and the side-by-side curation view is what makes that control real rather than nominal.

## Failure handling (FR-013, SC-007)

| Condition | Classification | Result |
|---|---|---|
| Timeout, rate limit, connection error, 5xx | Transient | Task-level retry; `attempt_count` incremented on the Submission |
| Schema validation failure | Transient **once**, then permanent | One retry absorbs a stray malformation; a second means the prompt or model is wrong, not the weather |
| `is_legislative_text = false` | Not a failure | Submission `rejected` with a reason (FR-005) |
| Missing or invalid API key | Permanent | Fail loudly at startup, not per request (D7) |
| Retry cap exhausted | Permanent | Submission `failed` with a legible `failure_reason` (FR-013) |

Two retry layers exist and must not be collapsed: the SDK's own `max_retries` (default 2) covers transport blips inside a single call; the task-level retry persists `attempt_count` on the Submission so it survives a worker restart. Only the second satisfies SC-007.

## Recorded with every generation

`generator_reference` stores the model identifier and prompt version. Without it, a batch of bad output cannot later be scoped — you would know something went wrong but not which versions to re-examine.

## Testing

Tests use a fake adapter implementing the port, never HTTP mocking. The fakes to provide: a valid result, each transient error, a schema violation, and `is_legislative_text = false`. No test may require network access or an API key.
