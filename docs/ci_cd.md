# 🤖 CI/CD e AI-Powered DevOps

Além do uso de IA na aplicação final, a esteira de desenvolvimento do **Voto Claro** utiliza automações baseadas em Inteligência Artificial através de GitHub Actions integradas com a API do Google Gemini.

Essa arquitetura demonstra a aplicação prática de **AI-Agentic Workflows**, onde a IA atua não apenas como feature de produto, mas como membro da equipe de desenvolvimento.

## Workflows Disponíveis

### 1. Automated PR Review (O "Tech Lead" AI)
**Arquivo:** `.github/workflows/gemini_pr_review.yml`

Toda vez que um novo *Pull Request* é aberto ou atualizado, esta action é disparada:
- Extrai o *diff* do PR (o que foi adicionado, alterado ou deletado).
- Envia as alterações para o modelo do Gemini analisá-las.
- O Gemini atua como um Tech Lead: verifica a qualidade do código, avalia se as mudanças fazem sentido para o contexto do PR, aponta potenciais problemas e sugere um *Changelog* formatado.
- Por fim, publica automaticamente um comentário no Pull Request com o relatório de revisão.

### 2. Issue Triage (O "Scrum Master" AI)
**Arquivo:** `.github/workflows/gemini_issue_triage.yml`

Quando uma nova *Issue* é criada no repositório:
- A action captura o Título e o Corpo da *Issue*.
- O Gemini avalia a solicitação atuando como um Scrum Master.
- Analisa a complexidade, sugere uma pontuação (Story Points) para a tarefa e identifica quais partes do código provavelmente precisarão ser tocadas.
- Publica a análise diretamente como comentário na *Issue*.

### 3. Chat Review
**Arquivo:** `.github/workflows/gemini_chat_review.yml`

Este workflow adicional suporta a interação contínua nas PRs e Issues através de comandos, permitindo que a equipe tire dúvidas diretas sobre o contexto das mudanças ou peça revisões complementares.

## Dependências e Autenticação
Esses workflows utilizam o SDK oficial `google-genai` e dependem da injeção da variável `GEMINI_API_KEY` através dos *GitHub Secrets* configurados no repositório. O acesso de escrita aos *Pull Requests* e *Issues* é garantido automaticamente via `GITHUB_TOKEN`.
