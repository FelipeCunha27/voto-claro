# Tasks: Tradução de Projetos Políticos para Linguagem Acessível com Painel Público

**Input**: Design documents from `/specs/001-bill-plain-language-dashboard/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD is mandatory per project rules. Tests are placed before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create Django project structure in `core/` and apps `accounts`, `bills`, `panel` in `src/voto_claro/` per plan.md.
- [x] T002 Add dependencies via `uv`: Django 6.1, openai 3.10.0, python-dotenv, django-tasks-db, pypdf, python-docx.
- [x] T003 Configure `core/settings.py` (env vars, INSTALLED_APPS for voto_claro apps, SQLite, MAILERS).
- [x] T004 [P] Configure `django-tasks-db` worker process in settings.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Write failing tests for custom User model in `src/voto_claro/accounts/tests/test_models.py`.
- [x] T006 Create `User` model extending Django's `AbstractUser` with `is_curator` (boolean) in `src/voto_claro/accounts/models.py`.
- [x] T007 Configure initial migrations and authentication backend (login, logout, registration) for `accounts` app.
- [ ] T008 [P] Setup base URL routing for `accounts`, `bills`, and `panel` in `core/urls.py`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Submeter um projeto e receber a versão acessível (Priority: P1) 🎯 MVP

**Goal**: Permitir que usuário autorizado submeta texto/PDF/DOCX de projeto político e receba versão traduzida via IA.

**Independent Test**: Submeter projeto conhecido e verificar se versão acessível é gerada e legível na área do remetente, testável ponta a ponta sem dor.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Contract tests for `openai_adapter` (valid, transient errors, schema violation, `is_legislative_text=false`) in `src/voto_claro/bills/tests/test_adapters.py`.
- [ ] T010 [P] [US1] Unit tests for `Submission` validation (500-50k chars, Portuguese, PDF/DOCX) and rate limit (5/24h) in `src/voto_claro/bills/tests/test_models.py`.
- [ ] T011 [P] [US1] Integration tests for `enviar` and `minhas-submissoes` views in `src/voto_claro/bills/tests/test_views.py`.

### Implementation for User Story 1

- [ ] T012 [US1] Create `Theme` (id, name, slug) and `Bill` (id: uuid, slug: unique, title, origin_body, bill_number, bill_year, theme: FK nullable, official_source_url, current_version: FK nullable, review_notice_override: enum 'auto|forced_on|forced_off', first_published_at, updated_at) in `src/voto_claro/bills/models.py`.
- [ ] T013 [US1] Create `Submission` model in `src/voto_claro/bills/models.py`. Constraints: `submitter` FK PROTECT, `title` string(300), `origin_body` string(200), `bill_number` string(50) optional, `bill_year` integer optional, `source_text` text write-once (500-50k chars), `input_kind` enum pasted/pdf/docx, `content_hash` string(64), `status` enum (received/processing/generated/published/unpublished/failed/rejected), `attempt_count` int.
- [ ] T014 [US1] Create `AccessibleVersion` model in `src/voto_claro/bills/models.py`. Constraints: append-only, `bill` FK CASCADE, `submission` FK PROTECT, `version_number` int unique with bill, `summary` text required, `who_is_affected` text required, `practical_changes` text required, `points_of_attention` text required, `is_ai_generated` bool default true, `review_state` enum (pending/approved/rejected/superseded).
- [ ] T015 [US1] Implement text extraction (`pypdf`, `python-docx`) in `src/voto_claro/bills/services/extraction.py`.
- [ ] T016 [US1] Implement duplicate detection (via `content_hash`) and submission screening in `src/voto_claro/bills/services/screening.py`.
- [ ] T017 [US1] Implement `generate_accessible_version` port using `client.responses.parse` in `src/voto_claro/bills/adapters/openai_adapter.py`.
- [ ] T018 [US1] Implement async task `generate_accessible_version` coordinating adapter and state machine in `src/voto_claro/bills/tasks.py`.
- [ ] T019 [US1] Create submission form and POST `/enviar/` view with rate limiting (max 5 in 24h) in `src/voto_claro/bills/views.py`.
- [ ] T020 [US1] Create GET `/minhas-submissoes/` list and `/minhas-submissoes/<uuid>/` detail views/templates in `src/voto_claro/bills/views.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Consultar o painel público de projetos traduzidos (Priority: P2)

**Goal**: Visitante anônimo lista, busca e lê projetos traduzidos publicados no painel público.

**Independent Test**: Visitante acessa painel, filtra por tema e abre projeto.

### Tests for User Story 2 ⚠️

- [ ] T021 [P] [US2] Write failing tests for public `/` list view filtering and search logic in `src/voto_claro/panel/tests/test_views.py`.
- [ ] T022 [P] [US2] Write failing tests for `/projeto/<slug>/` detail view (404 for unpublished, AI label rendering) in `src/voto_claro/panel/tests/test_views.py`.

### Implementation for User Story 2

- [ ] T023 [P] [US2] Implement keyword search against title and summary in `src/voto_claro/panel/search.py`.
- [ ] T024 [US2] Implement GET `/` public panel view with filters (theme, origin, date) and pagination in `src/voto_claro/panel/views.py`.
- [ ] T025 [US2] Implement GET `/projeto/<slug>/` view displaying the 4 accessible fields and AI label in `src/voto_claro/panel/views.py`.
- [ ] T026 [US2] Create accessible templates (WCAG 2.1 AA) for the panel listing and detail views, including empty states.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Conferir a fidelidade da tradução e sinalizar problemas (Priority: P3)

**Goal**: Leitor compara versão acessível com original e reporta imprecisões.

**Independent Test**: Leitor abre versão original e cadastra sinalização de imprecisão com trecho destacado.

### Tests for User Story 3 ⚠️

- [ ] T027 [P] [US3] Write failing tests for flag creation (auth vs anon nullity) in `src/voto_claro/panel/tests/test_flags.py`.

### Implementation for User Story 3

- [ ] T028 [US3] Create `Flag` model in `src/voto_claro/bills/models.py`. Constraints: `version` FK AccessibleVersion, `reporter` FK nullable, `description` text required, `state` enum (open/resolved/dismissed), `excerpt` text optional.
- [ ] T029 [US3] Implement GET `/projeto/<slug>/original/` view and side-by-side comparison template in `src/voto_claro/panel/views.py`.
- [ ] T030 [US3] Implement GET/POST `/projeto/<slug>/sinalizar/` flag submission view in `src/voto_claro/panel/views.py`.
- [ ] T031 [US3] Add pending review notice logic to `/projeto/<slug>/` template, checking authenticated flags vs `review_notice_override`.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Curar e publicar o conteúdo do painel (Priority: P4)

**Goal**: Administrador revisa traduções e gerencia publicação.

**Independent Test**: Curador aprova submissão pendente e ela aparece no painel público, depois despublica.

### Tests for User Story 4 ⚠️

- [ ] T032 [P] [US4] Write failing tests for curator access control (`is_curator`) on all actions in `src/voto_claro/bills/tests/test_curation.py`.
- [ ] T033 [P] [US4] Write failing tests for append-only `AuditEntry` logging in `src/voto_claro/bills/tests/test_audit.py`.

### Implementation for User Story 4

- [ ] T034 [P] [US4] Create `AuditEntry` model in `src/voto_claro/bills/models.py`. Constraints: append-only, `action` enum, `actor` FK nullable, `reason` text required for unpublished/rejected.
- [ ] T035 [US4] Implement GET `/curadoria/` and `/curadoria/<uuid>/` queue views for curators in `src/voto_claro/bills/views.py`.
- [ ] T036 [US4] Implement POST actions (`aprovar`, `editar`, `regerar`, `despublicar`, `rejeitar`) appending to `AuditEntry` in `src/voto_claro/bills/views.py`.
- [ ] T037 [US4] Implement flag resolution POST `/curadoria/sinalizacoes/<uuid>/resolver/` in `src/voto_claro/bills/views.py`.
- [ ] T038 [US4] Implement review notice override POST `/curadoria/projeto/<slug>/aviso/` in `src/voto_claro/bills/views.py`.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T039 Update `docs/architecture.md`, `docs/database.md`, and `docs/admin.md` with new features and models.
- [ ] T040 Security Review: Verify LGPD compliance (no public PII) and CSRF protection on all forms.
- [ ] T041 Code cleanup, review indexes according to data-model.md.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed sequentially (US1 → US2 → US3 → US4) or in parallel if developers are available.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### Parallel Example: User Story 1

```bash
# Launch tests for User Story 1 together:
Task: "Contract tests for openai_adapter"
Task: "Unit tests for Submission validation"
Task: "Integration tests for enviar views"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 & 2.
2. Complete Phase 3: User Story 1.
3. Validate: User can submit a bill and see the AI-generated translation in their own panel.

### Incremental Delivery

1. Complete Setup + Foundational.
2. Add User Story 1 (Submission & Generation).
3. Add User Story 2 (Public Panel).
4. Add User Story 3 (Flags & Original).
5. Add User Story 4 (Curation).

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Write tests first per TDD rules.
- Verify each phase completes independently.
- Avoid vague tasks.
