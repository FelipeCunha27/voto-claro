# Resumo de Contexto (Voto Claro)

## O que já foi concluído na sessão anterior:
- O projeto foi migrado completamente para o Antigravity e API do Gemini (v3.6-flash).
- Criamos o arquivo de regras mestras `GEMINI.md` na raiz do projeto.
- O Playbook estratégico foi consolidado e está salvo em `docs/playbook.md`.
- Geramos o checklist granular no arquivo `specs/001-bill-plain-language-dashboard/tasks.md`.
- Concluímos as tarefas **T001 até a T006**, estabelecendo a base do Django, o banco de dados e o modelo customizado `User` (com o campo `is_curator` implementado via TDD).
- Configuramos a automação de CI/CD via GitHub Actions (`gemini_chat_review.yml`) para realizar Code Review através do SDK `google-genai` sempre que o desenvolvedor comentar `/gemini review` em um Pull Request.

## Próximos Passos (Onde continuar):
- Abrir o arquivo `tasks.md` e iniciar a execução a partir das tarefas **T007** (Roteamento de URLs em `core/urls.py`) e **T008** (Templates base do HTMX).
- Seguir o padrão de TDD para implementar a User Story 1 (extração de PDFs e Docx para o Gemini simplificar o texto).

## Links de Referência para a IA:
- Checklist de Tarefas: `specs/001-bill-plain-language-dashboard/tasks.md`
- Playbook: `docs/playbook.md`
