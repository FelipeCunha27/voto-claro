# Playbook do Projeto: Voto Claro 🇧🇷
*Documento vivo de arquitetura e histórico de evolução do projeto.*

## Metodologia Geral
- **Regra de Idioma (Bilinguismo):** O código-fonte, models, variáveis e arquivos de configuração são escritos obrigatoriamente em **Inglês**. A documentação (`.md`), os templates visuais (HTML) e as interações com o usuário final são escritos em **Português (PT-BR)**. Essa regra está fixada no `GEMINI.md`.
- **Desenvolvimento Guiado a Testes (TDD):** Adoção rigorosa do ciclo Red-Green-Blue (Refactor). Todas as views e models têm cobertura de testes unitários.

---

## Histórico de Fases e Progresso

### Fase 1: Fundação e Setup do Projeto ✅
- **Gerenciamento de Pacotes:** Inicialização do projeto usando `uv` como gerenciador de pacotes e ambientes virtuais, garantindo altíssima velocidade.
- **Configurações Iniciais do Django:** Criação do projeto `voto_claro` e do app `core`.
- **Fila de Tarefas (Background):** Instalação e configuração do `django-tasks` (com `django-tasks-db`) em `core/settings.py` para processamento assíncrono de Inteligência Artificial sem travar o navegador do usuário.
- **Integração Contínua (ChatOps):** Criação de workflows automatizados na pasta `.github/workflows/`:
  - `gemini_pr_review.yml`: Tech Lead automatizado que valida TDD, Idioma e gera Changelogs em Pull Requests.
  - `gemini_issue_triage.yml`: Scrum Master virtual que estima Story Points nas issues.
  - `gemini_chat_review.yml`: Acionamento sob demanda do Gemini via comentários no PR.

### Fase 2: Autenticação de Usuários ✅
- **App `accounts`:** Criação do módulo de autenticação.
- **Testes (TDD):** Criação de `tests_views.py` cobrindo o registro de contas, login e logout com sucesso (Status 200/302).
- **Formulários e Views:** Criação do `CustomUserCreationForm` para simplificar o cadastro (sem necessidade de e-mail obrigatório no MVP).
- **Templates (UI):** Telas `login.html` e `register.html` minimalistas e traduzidas para PT-BR. Configuração de redirecionamento (`LOGIN_REDIRECT_URL`).

### Fase 3: MVP - Envio de Projetos Políticos (User Story 1) ✅
- **App `bills`:** Criação do módulo central do sistema de leis.
- **Modelagem de Dados:**
  - `Submission`: Guarda a fila de processamento (PDF anexado, Link ou Texto), com status (`received`, `processing`, `generated`, `failed`).
  - `Bill`: O projeto de lei ou plano de governo consolidado, com campo `slug` auto-gerado via UUID para evitar falhas de integridade (IntegrityError).
  - `AccessibleVersion`: A tradução estruturada em linguagem simples.
- **UI Minimalista:** Criação de `enviar.html` com apenas 3 opções: Link, Texto ou Arquivo. HTML5 form validation bloqueios (`required=True` e limite de 50.000 caracteres) foram removidos no backend para focar na experiência do usuário.
- **Gestão de Banco de Dados:** Remoção do teto de submissões (de 5 para 5.000 requisições/dia) para permitir testes massivos em desenvolvimento.

### Fase 4: O "Cérebro" de Inteligência Artificial ✅
- **Motor de IA:** Transição da biblioteca da OpenAI para o uso exclusivo do SDK Oficial do Google (`google-genai`).
- **Resolução de Instabilidade de Modelos:** 
  - Tratamento do erro `404 NOT FOUND` em modelos descontinuados (`gemini-2.5-flash`).
  - Tratamento de erro de infraestrutura `503 UNAVAILABLE` (Alta Demanda) no novo `gemini-3.8-flash`.
  - Fixação no modelo `gemini-3.6-flash`, que provou ser rápido e altamente estável para a arquitetura de Structured Outputs.
- **Engenharia de Prompt (Plain Language):** 
  - Regra de idade: O Gemini foi instruído a escrever para um "jovem de 14 anos", eliminando palavras como "desindexação" ou "pacto federativo" sem prévia explicação prática.
  - Expansão de Escopo: A IA, que inicialmente recusava textos que não fossem leis formais, foi re-treinada para aceitar e extrair dados de **Planos de Governo** e propostas políticas de campanhas eleitorais.
- **Fila em Ação:** Teste com sucesso do comando `uv run manage.py db_worker`, onde o operário pega a submissão, extrai o texto do PDF, conversa com o Google Gemini e salva a tradução de forma assíncrona no banco de dados.

---

## O Diferencial do Voto Claro (Nosso Moat)
Como o sistema se diferencia de pedir um resumo direto no ChatGPT?
1. **Acervo Público Permanente:** As leis são processadas uma vez e disponibilizadas para milhões de forma estruturada.
2. **Saída Estruturada Fixa:** Toda lei tem um cabeçalho de "Resumo", "Mudanças Práticas", "Quem é afetado" e "Pontos de Atenção", facilitando a comparação.
3. **Deduplicação de Custos:** Sistema de *hash* evita re-processamento caro de APIs se usuários submeterem o mesmo PDF.
4. **Camada de Auditoria (Próxima Fase):** Prevenção de alucinações através do Painel de Curadoria.

## Próximos Passos
- Avançar para a **User Story 2**: O Painel Público (Public Dashboard), para que qualquer cidadão não-autenticado possa buscar e ler as leis já traduzidas no banco de dados.
- Avançar para a **User Story 4**: O Painel de Curadoria para administradores revisarem textos antes de irem ao público.
