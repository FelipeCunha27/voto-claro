# 🏛️ Playbook de Desenvolvimento — Voto Claro (Antigravity Edition)

> Guia passo a passo para construir o projeto **do zero ao deploy**, aplicando a metodologia **DAPIA** (Desenvolvimento Assistido por IA) da Pythonando, adaptada para o ecossistema **Google Antigravity (Gemini)**.

---

## O Projeto

**Voto Claro** é um sistema web que recebe projetos políticos (leis, propostas, emendas), traduz os termos complexos para linguagem acessível usando IA, e apresenta as propostas de forma clara para o público leigo.

### Visão do Produto

| Campo | Valor |
|---|---|
| **Stack** | Python + Django + SQLite → PostgreSQL |
| **IA** | Gemini API (gemini-1.5-flash) para tradução/simplificação |
| **Frontend** | Django Templates + HTMX (interatividade sem SPA) |
| **Público** | Cidadãos que querem entender propostas políticas |
| **Ferramenta IA**| **Antigravity 2.0 / Antigravity IDE** |
| **Metodologia** | SDD + TDD + Context Engineering + Quality Gate + Segurança |

---

## Fase 1 — Setup do Ferramental (Antigravity)

Nesta fase, substituímos o Claude Code pelo Antigravity, ganhando recursos mais avançados como Hooks e execução paralela.

### 1.1 Criar o projeto Django

```bash
mkdir voto_claro && cd voto_claro
uv init
uv venv
source .venv/bin/activate
uv add django google-genai python-dotenv
django-admin startproject core .
```

### 1.2 Setup do Antigravity Workspace

1. Abra o **Antigravity 2.0**
2. Vá na barra lateral em **Projects** e adicione a pasta `voto_claro`.
3. Crie o arquivo `GEMINI.md` na raiz (Substitui o antigo `CLAUDE.md`).

**Conteúdo do `GEMINI.md`:**
```markdown
# Voto Claro

## Stack
- Python 3.12+, Django 5.x, HTMX
- IA: OpenAI API para simplificação de textos

## Regras
- Views: usar Class-Based Views (CBV)
- Templates: herdar de `base.html`, usar parciais com prefixo `_`
- TDD: Teste (Red) -> Implementação (Green) -> Refatoração (Blue) obrigatório.
```

### 1.3 Configurar Skills e Hooks

O Antigravity usa a pasta `.agents/` para customizações.

```text
.agents/
├── hooks.json                     # Automações de ciclo de vida
└── skills/
    ├── django-expert/SKILL.md     # Padrões Django
    ├── django-tdd/SKILL.md        # Padrões de teste
    └── speckit-.../SKILL.md       # Ferramentas SDD
```

**O superpoder do Antigravity: `hooks.json`**
Crie um hook para rodar o linter automaticamente toda vez que o agente editar um arquivo:

```json
{
  "auto-lint": {
    "PostToolUse": [
      {
        "matcher": "replace_file_content|write_to_file",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check --fix . 2>/dev/null || true",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

### 1.4 Conectar MCP Servers (Context7)

No Antigravity, você gerencia os MCPs globalmente em `~/.gemini/config/mcp_config.json`. Adicione o Context7 para trazer a documentação atualizada do Django/OpenAI:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

---

## Fase 2 — Spec Driven Development (SDD)

> Regra de ouro: escrever código é a **última etapa**.

No Antigravity, as skills do SpecKit guiam o desenvolvimento a partir de um PRD (Product Requirements Document).

### 2.1 O PRD do Voto Claro (spec.md)

Escreva a especificação em linguagem não-técnica. Exemplo para a tradução de leis:

```markdown
# Funcionalidade: Tradução para Linguagem Acessível

O sistema deve receber um projeto de lei submetido pelo admin e traduzir
automaticamente para linguagem acessível. A tradução deve:
- Substituir termos jurídicos por equivalentes simples.
- Gerar um resumo de 3 parágrafos.
- Listar pontos positivos e negativos em tópicos.
- Permitir edição manual antes da publicação no painel.
```

### 2.2 Fluxo SpecKit no Antigravity

Peça diretamente no chat do Antigravity:

1. **Especifique:** `"Use o speckit-specify para criar a spec.md detalhada"`
2. **Planeje:** `"Use o speckit-plan para gerar o plano técnico (models, rotas)"`
3. **Quebre em tarefas:** `"Use o speckit-tasks para gerar as tasks de implementação"`
4. **Implemente:** `"Use o speckit-implement para executar a task-001"`

*(Cada funcionalidade deve ter sua própria pasta em `specs/` e sua própria branch).*

---

## Fase 3 — TDD com IA

Com a skill `django-tdd` ativada, o agente sabe que deve seguir o Red-Green-Refactor.

### O Fluxo Perfeito no Antigravity

1. O agente lê a task (ex: "Criar view de submissão de projeto").
2. Ele escreve os testes primeiro (ex: `test_retorna_200`, `test_cria_projeto_no_banco`).
3. O agente roda o teste (`uv run manage.py test`) -> **FALHA (Red)**.
4. O agente implementa a view e os models mínimos necessários.
5. O agente roda o teste novamente -> **PASSA (Green)**.
6. O agente usa o hook de `PostToolUse` para formatar e rodar linters automaticamente.

---

## Fase 4 — CI/CD (Code Review com Gemini via ChatOps)

Para replicar a experiência ensinada no curso (onde você chama a IA diretamente pelos comentários do GitHub), configuraremos o Gemini como um *Tech Lead sob demanda*. Em vez de rodar automaticamente em todo PR, ele só fará o review quando você chamar o comando `/gemini review` em um comentário.

### 4.1 O Papel do Gemini no Code Review
Sempre que acionado, o Gemini lerá as diferenças de código do PR e o seu comentário. Ele focará em:
1. **Regra de Idioma:** Verificar se alguém usou inglês no domínio.
2. **Conformidade TDD:** Identificar testes faltantes na pasta `tests/`.
3. **Segurança de IA (Prompt Injection):** Garantir sanitização de inputs.
4. **Padrões Django:** Garantir boas práticas (ex: uso de CBVs).

### 4.2 O Caminho do Arquivo e o Workflow
Crie o arquivo exatamente neste caminho dentro do seu projeto:
👉 `.github/workflows/gemini_chat_review.yml`

E cole o seguinte conteúdo:

```yaml
name: Gemini ChatOps Review

on:
  issue_comment:
    types: [created] # Dispara apenas quando um comentário for postado

jobs:
  gemini-review:
    # Só executa se for um Pull Request E o comentário contiver o comando mágico
    if: ${{ github.event.issue.pull_request && contains(github.event.comment.body, '/gemini review') }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout das Regras do Projeto
        uses: actions/checkout@v4

      - name: Extrair Diff do Pull Request
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Usa o CLI do GitHub para baixar o diff do PR atual com segurança
          gh pr diff ${{ github.event.issue.number }} --repo ${{ github.repository }} > pr_diff.txt

      - name: Instalar Antigravity CLI (agy)
        run: curl -fsSL https://antigravity.google/install.sh | bash

      - name: Tech Lead Gemini Review
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          USER_PROMPT: ${{ github.event.comment.body }}
        run: |
          agy run "
            Aja como o Tech Lead do projeto 'Voto Claro'.
            O desenvolvedor pediu o review usando este comando: '$USER_PROMPT'
            
            Leia o arquivo 'pr_diff.txt'. Com base nas regras do arquivo 'GEMINI.md', analise este Pull Request e gere um relatório Markdown.
            Foque principalmente no que o desenvolvedor pediu no comando. Se não pedir nada específico, foque em: Idioma, TDD e Segurança.
          " > review_report.md
          
      - name: Postar Resposta no PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('review_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: "🤖 **Gemini Code Review**\n\n" + report
            });
```

### 4.3 Como funciona na prática
1. O desenvolvedor abre um Pull Request no GitHub.
2. Na aba de conversas (Conversation) do PR, o desenvolvedor digita um comentário: 
   > ` /gemini review Pode checar se os testes que fiz para a extração de PDF estão cobrindo os casos de erro? `
3. O GitHub Actions reconhece o comando.
4. O Gemini baixa o diff do PR, cruza com seu comentário e com o `GEMINI.md`.
5. O Gemini posta um novo comentário no PR com a análise focada no que você pediu.

---

## Fase 5 — Context Engineering

Mantenha o contexto técnico para que a IA não se perca conforme o projeto cresce. Use a skill `doc-cycle-onboard`.

### Documentos Obrigatórios (`docs/`):
- `architecture.md`: Stack, mapa de dependências (Mermaid), estrutura de pastas.
- `database.md`: Descrição dos Models, campos e relações.
- `admin.md`: Configurações de .env e deploy.

**Como atualizar:**
Ao terminar uma funcionalidade, peça no chat:
> *"Execute a skill doc-cycle-onboard para atualizar os documentos com base nas novas views e models de Projetos Políticos"*

O agente percorrerá o código em modo leitura e atualizará a pasta `docs/` sem quebrar seu código.

---

## Fase 6 — Quality Gate

Os pilares da qualidade que você deve cobrar do agente:

1. **Performance:** Use a skill `load-test-runner` para configurar o Locust (`locustfile.py`) e testar a rota de tradução (que chama a API externa).
2. **Complexidade:** Peça ao agente para rodar o `radon cc .` e garantir complexidade A ou B.
3. **Cobertura:** Mantenha testes acima de 80%. O hook do Antigravity garante que eles rodem a cada arquivo salvo.

---

## Fase 7 — Segurança

Segurança é vital em projetos políticos e com uso de IA.

1. **Pentest Automatizado:** Peça no chat:
   > *"Use a skill security-scanner para auditar a view de tradução."*
2. **Mitigações de IA:**
   - **Prompt Injection:** Garanta que o texto da lei é escapado e sanitizado antes de ir para o prompt do sistema.
   - **Rate Limiting:** Evite chamadas massivas à API do Gemini.
   - **Data Leakage:** Nunca passe dados do usuário logado ao prompt, apenas o texto da lei pública.

---

## Resumo da Estrutura Final (Antigravity Padrão)

```
voto_claro/
├── GEMINI.md                          # Regras Globais (Substitui CLAUDE.md)
├── AGENTS.md                          # Regras complementares
├── .agents/                           # Customizações do Antigravity
│   ├── hooks.json                     # Lifecycle (Auto-lint)
│   └── skills/                        # Skills (Progressive Disclosure)
│       ├── django-expert/SKILL.md
│       ├── django-tdd/SKILL.md
│       ├── doc-cycle-onboard/SKILL.md
│       ├── load-test-runner/SKILL.md
│       ├── security-scanner/SKILL.md
│       └── speckit-*/SKILL.md
├── docs/                              # Context Engineering
├── specs/                             # Spec Driven Development
├── core/                              # Projeto Django
├── accounts/                          # Autenticação
├── projects/                          # Leis Originais
├── translator/                        # Motor IA (OpenAI)
└── dashboard/                         # Painel Público (HTMX)
```
