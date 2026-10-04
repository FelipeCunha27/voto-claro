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
- [x] T008 [P] Setup base URL routing for `accounts`, `bills`, and `panel` in `core/urls.py`.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Submeter um projeto e receber a versão acessível (Priority: P1) 🎯 MVP

**Goal**: Permitir que usuário autorizado submeta texto/PDF/DOCX de projeto político e receba versão traduzida via IA.

**Independent Test**: Submeter projeto conhecido e verificar se versão acessível é gerada e legível na área do remetente, testável ponta a ponta sem dor.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Contract tests for `openai_adapter` (valid, transient errors, schema violation, `is_legislative_text=false`) in `src/voto_claro/bills/tests/test_adapters.py`.
- [x] T010 [P] [US1] Unit tests for `Submission` validation (500-50k chars, Portuguese, PDF/DOCX) and rate limit (5/24h) in `src/voto_claro/bills/tests/test_models.py`.
- [x] T011 [P] [US1] Integration tests for `enviar` and `minhas-submissoes` views in `src/voto_claro/bills/tests/test_views.py`.

### Implementation for User Story 1

- [x] T012 [US1] Create `Theme` (id, name, slug) and `Bill` (id: uuid, slug: unique, title, origin_body, bill_number, bill_year, theme: FK nullable, official_source_url, current_version: FK nullable, review_notice_override: enum 'auto|forced_on|forced_off', first_published_at, updated_at) in `src/voto_claro/bills/models.py`.
- [x] T013 [US1] Create `Submission` model in `src/voto_claro/bills/models.py`. Constraints: `submitter` FK PROTECT, `title` string(300), `origin_body` string(200), `bill_number` string(50) optional, `bill_year` integer optional, `source_text` text write-once (500-50k chars), `input_kind` enum pasted/pdf/docx, `content_hash` string(64), `status` enum (received/processing/generated/published/unpublished/failed/rejected), `attempt_count` int.
- [x] T014 [US1] Create `AccessibleVersion` model in `src/voto_claro/bills/models.py`. Constraints: append-only, `bill` FK CASCADE, `submission` FK PROTECT, `version_number` int unique with bill, `summary` text required, `who_is_affected` text required, `practical_changes` text required, `points_of_attention` text required, `is_ai_generated` bool default true, `review_state` enum (pending/approved/rejected/superseded).
- [x] T015 [US1] Implement text extraction (`pypdf`, `python-docx`) in `src/voto_claro/bills/services/extraction.py`.
- [x] T016 [US1] Implement duplicate detection (via `content_hash`) and submission screening in `src/voto_claro/bills/services/screening.py`.
- [x] T017 [US1] Implement `generate_accessible_version` port using `client.responses.parse` in `src/voto_claro/bills/adapters/openai_adapter.py`.
- [x] T018 [US1] Implement async task `generate_accessible_version` coordinating adapter and state machine in `src/voto_claro/bills/tasks.py`.
- [x] T019 [US1] Create submission form and POST `/enviar/` view with rate limiting (max 5 in 24h) in `src/voto_claro/bills/views.py`.
- [x] T020 [US1] Create GET `/minhas-submissoes/` list and `/minhas-submissoes/<uuid>/` detail views/templates in `src/voto_claro/bills/views.py`.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Consultar o painel público de projetos traduzidos (Priority: P2)

**Goal**: Visitante anônimo lista, busca e lê projetos traduzidos publicados no painel público.

**Independent Test**: Visitante acessa painel, filtra por tema e abre projeto.

### Tests for User Story 2 ⚠️

- [x] T021 [P] [US2] Write failing tests for public `/` list view filtering and search logic in `src/voto_claro/panel/tests/test_views.py`.
- [x] T022 [P] [US2] Write failing tests for `/projeto/<slug>/` detail view (404 for unpublished, AI label rendering) in `src/voto_claro/panel/tests/test_views.py`.

### Implementation for User Story 2

- [x] T023 [P] [US2] Implement keyword search against title and summary in `src/voto_claro/panel/search.py`.
- [x] T024 [US2] Implement GET `/` public panel view with filters (theme, origin, date) and pagination in `src/voto_claro/panel/views.py`.
- [x] T025 [US2] Implement GET `/projeto/<slug>/` view displaying the 4 accessible fields and AI label in `src/voto_claro/panel/views.py`.
- [x] T026 [US2] Create accessible templates (WCAG 2.1 AA) for the panel listing and detail views, including empty states.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Conferir a fidelidade da tradução e sinalizar problemas (Priority: P3)

**Goal**: Leitor compara versão acessível com original e reporta imprecisões.

**Independent Test**: Leitor abre versão original e cadastra sinalização de imprecisão com trecho destacado.

### Tests for User Story 3 ⚠️

- [x] T027 [P] [US3] Write failing tests for flag creation (auth vs anon nullity) in `src/voto_claro/panel/tests/test_flags.py`.

### Implementation for User Story 3

- [x] T028 [US3] Create `Flag` model in `src/voto_claro/bills/models.py`. Constraints: `version` FK AccessibleVersion, `reporter` FK nullable, `description` text required, `state` enum (open/resolved/dismissed), `excerpt` text optional.
- [x] T029 [US3] Implement GET `/projeto/<slug>/original/` view and side-by-side comparison template in `src/voto_claro/panel/views.py`.
- [x] T030 [US3] Implement GET/POST `/projeto/<slug>/sinalizar/` flag submission view in `src/voto_claro/panel/views.py`.
- [x] T031 [US3] Add pending review notice logic to `/projeto/<slug>/` template, checking authenticated flags vs `review_notice_override`.

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Curar e publicar o conteúdo do painel (Priority: P4)

**Goal**: Administrador revisa traduções e gerencia publicação.

**Independent Test**: Curador aprova submissão pendente e ela aparece no painel público, depois despublica.

### Tests for User Story 4 ⚠️

- [x] T032 [P] [US4] Write failing tests for curator access control (`is_curator`) on all actions in `src/voto_claro/bills/tests/test_curation.py`.
- [x] T033 [P] [US4] Write failing tests for append-only `AuditEntry` logging in `src/voto_claro/bills/tests/test_audit.py`.

### Implementation for User Story 4

- [x] T034 [P] [US4] Create `AuditEntry` model in `src/voto_claro/bills/models.py`. Constraints: append-only, `action` enum, `actor` FK nullable, `reason` text required for unpublished/rejected.
- [x] T035 [US4] Implement GET `/curadoria/` and `/curadoria/<uuid>/` queue views for curators in `src/voto_claro/bills/views.py`.
- [x] T036 [US4] Implement POST actions (`aprovar`, `editar`, `regerar`, `despublicar`, `rejeitar`) appending to `AuditEntry` in `src/voto_claro/bills/views.py`.
- [x] T037 [US4] Implement flag resolution POST `/curadoria/sinalizacoes/<uuid>/resolver/` in `src/voto_claro/bills/views.py`.
- [x] T038 [US4] Implement review notice override POST `/curadoria/projeto/<slug>/aviso/` in `src/voto_claro/bills/views.py`.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T039 Update `docs/architecture.md`, `docs/database.md`, and `docs/admin.md` with new features and models.
- [x] T040 Security Review: Verify LGPD compliance (no public PII) and CSRF protection on all forms.
- [x] T041 Code cleanup, review indexes according to data-model.md.
- [x] T042 Demand punctuation in the submission Text.
- [x] T043 Changing the title submission for something related to the text.
- [x] T044 Remove "Oŕgão de Origem".
- [x] T045 Ajustar submissões para gerar resultado corretamente quando é enviado documento do plano de governo.
- [x] T046 Remover completamente a regra de limite de caracteres (500 a 50.000) na submissão de projetos.
- [x] T047 Formatar campos do relatório na IA com bullet points e garantir renderização de quebras de linha (`linebreaks`) nos templates.
- [x] T048 Remover o limite de taxa de submissões (5 submissões por 24h).
- [x] T049 Corrigir formatação Markdown da IA nos templates, substituindo o `linebreaks` por uma renderização de Markdown real que suporte negrito (`**`) e listas corretas.
- [x] T050 Reforçar formatação do texto gerado pela IA com bullet points detalhados e hierarquia visual.
- [x] T051 Atualizar o prompt em `bills/adapters/gemini_adapter.py` para exigir **no mínimo 15 bullet points** por campo, separando cada tópico/seção com uma linha em branco.
- [x] T052 Exigir uso de bullet points (`-` ou `*`) para cada item individual.
- [x] T053 Quando houver subtópicos ou categorias, exigir hierarquia visual usando indentação (sub-bullets com `  -`) ou diferentes estilos de marcadores.
- [x] T054 O conteúdo original deve ser mantido intacto — a mudança é puramente de formatação e organização.
- [x] T055 Garantir que o filtro `markdownify` em `panel/templatetags/markdown_filters.py` renderize corretamente listas aninhadas (nested lists) e espaçamento entre seções.
- [x] T056 Escrever testes unitários para o adapter validando que a resposta contém ≥ 15 linhas iniciando com `-` ou `*` nos campos `summary`, `practical_changes`, `who_is_affected` e `points_of_attention`.
- [x] T057 Escrever testes para o template filter verificando renderização correta de listas aninhadas com Markdown.
- [x] **T058: Extração Inteligente do Título da Submissão**
  - [x] **Contexto:** Atualmente, o `Submission.clean()` apenas recorta os primeiros 50 caracteres do `source_text` para definir o título.
  - [x] **Objetivo:** Alterar essa lógica para identificar e extrair o título real / texto principal da primeira página do projeto de lei, plano de governo ou PEC.
  - [x] Implementar heurística no `bills/models.py` (ou delegar ao adapter da IA durante a submissão) para capturar o título oficial em vez de lixo/protocolo do início do PDF.
  - [x] Atualizar os testes da submissão para validar esse novo comportamento.
- [x] **T059: Escaneabilidade e Legibilidade dos Campos Gerados pela IA**
  - [x] **Contexto:** Os campos gerados pelo Gemini (`summary`, `who_is_affected`, `practical_changes` e `points_of_attention`) hoje seguem a regra rígida de **no mínimo 15 bullet points** (T051/T056), o que deixa o texto denso, repetitivo e difícil de "bater o olho" para o cidadão comum.
  - [x] **Objetivo:** Reformatar **os 4 campos gerados pela IA** aplicando princípios de escaneabilidade, para que o leitor capte a informação principal sem precisar ler tudo de forma linear.
  - [x] **Escopo:** A reformatação vale para `summary`, `who_is_affected`, `practical_changes` e `points_of_attention`. Documentação e textos fixos da interface ficam fora desta task.
  - [x] **Remover a regra dos 15 tópicos:**
    - [x] Retirar a exigência de "no mínimo 15 bullet points" do prompt principal e do prompt de enrichment (`_build_enrichment_prompt`) em `bills/adapters/gemini_adapter.py`.
    - [x] Remover ou substituir `validate_bullet_point_formatting(min_bullets=15)` e `_has_sufficient_formatting` por uma checagem que não dependa de contagem de bullets.
    - [x] Atualizar ou remover os testes do T056 que validam ≥ 15 linhas com `-`/`*`.
  - [x] **Cobertura completa obrigatória:** Sem o mínimo de 15 tópicos, cada campo ainda precisa cobrir **todos os tópicos/eixos do documento** relevantes ao seu propósito (ex.: todos os eixos de um plano de governo, como saúde, educação, segurança, economia etc.), sem omitir nenhum. A quantidade de itens passa a ser definida pelo conteúdo, não por um número fixo.
  - [x] **Público-alvo e tom:** Público geral. Tom **conversacional e acessível**: evitar jargão desnecessário (ou explicá-lo quando inevitável), escrevendo como se estivesse explicando a um amigo. Em `points_of_attention`, manter o tom neutro e apartidário já exigido hoje.
  - [x] **Técnicas de escaneabilidade a exigir no prompt para os 4 campos:**
    - [x] **Títulos e subtítulos claros:** dividir cada campo em seções com cabeçalhos descritivos (`###`/`####`) que resumam cada parte (ex.: um subtítulo por eixo/tópico do documento).
    - [x] **Listas com marcadores ou numeração:** converter parágrafos densos em listas quando fizer sentido, agrupando ideias relacionadas.
    - [x] **Destaque visual:** usar **negrito** para termos-chave, conceitos centrais e conclusões importantes.
    - [x] **Parágrafos curtos:** no máximo 2–3 frases por parágrafo.
    - [x] **Espaçamento:** linha em branco entre seções para reduzir a densidade visual.
    - [x] **Frases diretas:** priorizar clareza; colocar a informação essencial no início de cada ponto.
  - [x] **O que preservar:** manter o significado e **toda** a informação relevante do documento original, incluindo as citações diretas exigidas em `practical_changes`. A mudança é de formatação e acessibilidade, não de conteúdo.
  - [x] Ajustar o mecanismo de "enrichment" (retry) do adapter para reforçar as regras de escaneabilidade e de cobertura completa quando qualquer um dos 4 campos vier fora do padrão (ex.: sem subtítulos, com parágrafos longos ou com tópicos faltando).
  - [x] Garantir que o filtro `markdownify` (`panel/templatetags/markdown_filters.py`) e o CSS (`static/css/style.css`) renderizem bem cabeçalhos, negritos, listas numeradas e espaçamento nos blocos dos 4 campos em `panel/templates/panel/detail.html`.
  - [x] **TDD (Red → Green → Refactor):** escrever antes os testes:
    - [x] Adapter: o prompt contém as instruções de escaneabilidade, tom e cobertura completa para os 4 campos; o prompt **não** contém mais a exigência de 15 bullets; campos com subtítulos, negrito e parágrafos ≤ 3 frases são aceitos; qualquer campo fora do padrão dispara o enrichment. *(Red: `bills/tests/test_scannability.py`)*
    - [x] Template filter: renderização correta de `###`/`####`, `**negrito**`, listas numeradas e aninhadas. *(Red: `panel/tests/test_markdown_filters.py`)*
    - [x] Templates/Integração: a página de detalhe exibe no HTML final os cabeçalhos e listas dos 4 campos. *(Red: `panel/tests/test_views.py` e `bills/tests/test_scannability_integration.py`)*
  - [x] Ao concluir, executar a skill `doc-sync-onboarding` para atualizar `docs/` e o `GEMINI.md`.

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
- [x] **T060: Nova Formatação em Prosa Espaçada (Remover Bullets)**
  - [x] **Contexto:** O cliente solicitou uma nova estrutura visual onde listas com marcadores (`-`, `*`) são totalmente abandonadas em favor de parágrafos diretos introduzidos por rótulos (ex: "**Nome do Grupo:** descrição").
  - [x] **Objetivo:** Atualizar os prompts e validações para gerar texto no novo formato especificado.
  - [x] **Regras atualizadas:**
    - Proibir o uso de listas/bullet points (`-`, `*`).
    - Exigir que os itens sejam formatados como parágrafos independentes começando com um termo em **negrito**, seguido de dois pontos.
    - Exigir o uso de subtítulos (como "O Grande Objetivo", "Os Grupos Mais Afetados", etc) usando Markdown (`###` ou `####`).
    - Manter o espaçamento duplo obrigatório entre todos os parágrafos.
  - [x] **TDD (Red → Green → Refactor):**
    - [x] Atualizar `test_scannability.py` para exigir ausência de bullet points e presença de rótulos em negrito.
    - [x] Modificar o prompt do Gemini para aplicar a nova estrutura.
- [x] **T061: Tela de Carregamento/Auto-reload na Geração da IA**
  - [x] **Contexto:** Após enviar um documento, o usuário é redirecionado para a página de detalhes da submissão. Como a geração pela IA ocorre em background via task assíncrona, o usuário precisa ficar recarregando a página manualmente para ver o resultado.
  - [x] **Objetivo:** Implementar um mecanismo de auto-reload (polling) na página de detalhes da submissão quando ela estiver em status de processamento (`RECEIVED` ou `PROCESSING`).
  - [x] **O que fazer:**
    - Atualizar o template `bills/minhas_submissoes_detail.html` para incluir um `<meta http-equiv="refresh" content="5">` ou um script JS leve de polling condicionado ao status da submissão.
    - Otimizar a UI desse estado de carregamento: adicionar um "spinner" de loading animado e uma mensagem amigável (ex: *"A inteligência artificial está lendo o seu documento e gerando o relatório... Por favor, aguarde."*).
    - Garantir que a página pare de recarregar automaticamente assim que a submissão transicionar para um status final (ex: `GENERATED`, `PUBLISHED`, `FAILED`, `REJECTED`).
  - [x] **TDD (Red → Green → Refactor):**
    - [x] Criar teste de visualização (view test) garantindo que o cabeçalho de reload ou o script JS está presente na resposta quando o status é `PROCESSING`.
    - [x] Garantir que o script/reload não está presente quando o status é `GENERATED`.
