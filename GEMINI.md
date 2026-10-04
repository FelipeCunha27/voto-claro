# Regras do Projeto — Voto Claro (Antigravity)

## 🌐 Idioma (REGRA ATUALIZADA)

**O projeto utiliza um modelo bilíngue (Documentação em pt-BR e Código em Inglês).**

- **Português (pt-BR):** Documentação (arquivos `.md`), comentários explicativos no código, textos da interface do usuário (templates HTML) e textos voltados ao usuário final.
- **Inglês:** Todo o código fonte. Isso inclui nomes de variáveis, classes, modelos (models), métodos, funções, arquivos, rotas e mensagens de commit.
*Exemplo Certo:* `class Bill(models.Model):`
*Exemplo Errado:* `class ProjetoDeLei(models.Model):`

## 🏗️ Estado do Projeto

O *Voto Claro* é um projeto Django 6.1. Já possui as apps de domínio (como bills, accounts e panel) configuradas com models, views, tarefas assíncronas e testes. Sempre busque entender o código existente antes de criar algo novo.

## 💻 Comandos

Tudo é executado através do gerenciador de pacotes `uv`. Não há necessidade de ativar ambiente virtual separadamente e nenhuma ferramenta de lint/format/test foi configurada ainda.

```bash
uv sync                                   # instala/atualiza o .venv a partir do uv.lock
uv add <pacote>                           # adiciona uma dependência
uv run manage.py runserver                # roda o servidor de desenvolvimento
uv run manage.py migrate                  # aplica as migrações no banco
uv run manage.py startapp <nome_do_app>   # cria um novo app Django
uv run manage.py test                     # roda os testes nativos do Django
```



## 📂 Estrutura (Layout)

Duas raízes Python coexistem com propósitos diferentes:

- `core/` — o pacote central do projeto Django na raiz do repositório (`settings.py`, `urls.py`).
- `src/voto_claro/` — o pacote de distribuição criado pelo `uv_build` (usado para o script de console).

**Importante:** Novos apps Django devem ser criados na raiz do repositório (usando `uv run manage.py startapp nome_do_app`) para manter as entradas do `INSTALLED_APPS` simples (ex: `'nome_do_app'`) e alinhadas com onde a pasta `core/` vive.

## ⚙️ Especificidades do Ambiente

- **Requisitos:** Python **3.14** e Django **6.1**. Ambos são muito recentes, então **sempre busque na documentação** via Context7 (MCP) em vez de tentar lembrar a API (especialmente para settings, e-mail ou async).
- O envio de e-mail é configurado pelo dicionário `MAILERS` no `core/settings.py` (padrão do Django 6.x), **não** use as antigas configurações `EMAIL_BACKEND`.
- `google-genai` (API do Gemini) e `python-dotenv` são dependências declaradas. `SECRET_KEY` e `DEBUG` devem ser lidos de variáveis de ambiente no `.env`.
- O arquivo `db.sqlite3` não deve ser versionado (adicione ao `.gitignore`).



## 🔒 Segurança

- Nunca expor API keys no código (use `.env`).
- Sanitizar todos os inputs antes de enviá-los ao Gemini (prevenção contra Prompt Injection).
- Manter proteção CSRF ativa em todos os formulários.
- Verificar permissões estritas em todas as views administrativas.



## 🧪 TDD — Obrigatório

Para cada nova funcionalidade, siga obrigatoriamente a skill `[`.agents/skills/django-tdd``](.claude/skills/django-tdd) — escreva os testes **antes** da implementação (Red → Green → Refactor).

1. **Red:** PRIMEIRO escreva os testes (que vão falhar).
2. **Green:** DEPOIS implemente o código mínimo para os testes passarem.
3. **Blue:** Refatore o código mantendo os testes passando.

*Nunca implemente uma funcionalidade sem antes ter testes escritos.*

Cobertura mínima exigida por funcionalidade: 

- **Models** — campos, validações, métodos, `__str__`, constraints. 
- **Forms** — validação de campos, `clean_`*, mensagens de erro. 
- **Views** — status codes, contexto, permissões, redirecionamentos. 
- **Templates** — renderização, blocos, presença de elementos esperados. 
- **Integração** — fluxo end-to-end cobrindo a jornada do usuário.

Só marque a funcionalidade como concluída depois que todos esses níveis de testes estiverem verdes.

## 📝 Context Engineering (Documentação)

- Toda a documentação técnica fica na pasta `docs/`.
- Após finalizar cada feature, atualize os arquivos `docs/architecture.md`, `docs/database.md` e `docs/admin.md` para refletir as mudanças no sistema.
- Use diagramas Mermaid em português para mapear relações.
- Toda a documentação técnica (em linguagem de negócio e técnica) fica na pasta `docs/`.
- **GATILHO OBRIGATÓRIO (Sync-Doc):** Sempre que você finalizar a criação de uma funcionalidade, correção de bug ou qualquer alteração de código neste repositório, **sua etapa final e obrigatória** é invocar a skill/subagent `doc-sync-onboarding`.
- O subagent usará *diffs* para atualizar os arquivos `docs/architecture.md`, `docs/database.md` e `docs/admin.md` e os diagramas Mermaid, mantendo o contexto da IA 100% fiel ao software atual sem desperdiçar tokens reescrevendo tudo do zero.
- Toda a documentação técnica fica na pasta `docs/`.
- Após finalizar cada feature, atualize os arquivos `docs/architecture.md`, `docs/database.md` e `docs/admin.md` para refletir as mudanças no sistema.
- Use diagramas Mermaid em português para mapear relações.
- **REGRA DE SINCRONIZAÇÃO OBRIGATÓRIA:** Ao finalizar o desenvolvimento de qualquer funcionalidade, correção ou alteração de código, a sua ÚLTIMA etapa obrigatória antes de encerrar o trabalho é executar a skill `doc-sync-onboarding` para atualizar a documentação em `docs/` refletindo as mudanças recentes.



## 🔄 Mudanças Recentes
- **bills:** Criação do model `Category` (com testes). Registrado no `admin.py` nativo, ainda sem relacionamentos diretos com outros models.
- **frontend:** Refatoração completa da interface usando a skill `frontend-design`. Implementado um arquivo CSS central (`static/css/style.css`), unificação de todos os templates via `base.html`, e aplicação de um design system institucional, focado em alta legibilidade e estrutura limpa sem dependência de classes utilitárias excessivas.
- **bills & panel:** Remoção completa do campo `origin_body` dos models `Bill` e `Submission`. Adicionada validação de pontuação obrigatória no `Submission.clean` e auto-preenchimento do título da submissão com os primeiros 50 caracteres do texto, em vez de uma string estática (T042, T043, T044).
- **bills:** Resolução do bug de "dead code" na integração do Gemini. A checagem mudou para `is_valid_document`, permitindo planos de governo e outros textos políticos, e rejeitando corretamente (status REJECTED) documentos inválidos com uma mensagem explicativa ao invés de lançar erro fatal (FAILED) (T045).
- **bills:** Remoção completa da regra de limite de caracteres (500 a 50.000) na submissão de projetos (T046). Foram limpas as validações no `Submission.clean()`, apagada a função órfã `is_valid_size` e extirpada a gambiarra que multiplicava links 20 vezes para burlar a regra antiga.
- **frontend/bills:** Melhoria na formatação e legibilidade dos resumos. O prompt da IA agora exige uso explícito de listas/bullets points com quebra de linha. Os templates `detail.html` e `original.html` foram ajustados com o filtro `linebreaks` para renderizar parágrafos reais no HTML em vez de esmagar tópicos na mesma linha (T047). Substituída a abordagem de linebreaks por uma renderização de Markdown real para exibir negritos e listas nativas (`<ul>`) (T049).
- **bills:** Remoção do limite de taxa (rate limit) de 5 submissões a cada 24 horas por usuário no model `Submission` (T048).
- **bills/panel:** Reforço na formatação estruturada da IA. O `gemini_adapter.py` agora exige no mínimo 15 bullet points por campo gerado e implementa um mecanismo de "enrichment" automático (retry) que reforça a formatação caso a IA devolva um resultado pobre. O filtro `markdownify` foi corrigido para garantir o espaçamento em blocos e a correta indentação (conversão de 2 para 4 espaços) de listas aninhadas (T050).
- **bills:** Implementação de extração heurística inteligente de título na view de submissões. Cabeçalhos genéricos e protocolos sujos no topo dos arquivos/textos colados agora são ignorados para que o título oficial (`PROJETO DE LEI...`, `PLANO DE GOVERNO...`) seja capturado automaticamente e associado à nova submissão (T058).
- **bills/panel:** Aplicação de princípios de escaneabilidade na formatação gerada pela IA (T059). A regra rígida de "no mínimo 15 bullet points" foi removida em favor de um texto acessível ao público geral que exige o uso de cabeçalhos (`###`), negrito, parágrafos curtos (máximo 2 a 3 frases) e listas. O filtro `markdownify` foi aprimorado para renderizar listas de forma robusta e o mecanismo de "enrichment" agora reavalia a geração com base nessas novas regras de escaneabilidade.
- **bills/panel:** Nova reestruturação de formato (T060). Listas tradicionais com marcadores (bullet points como `-` ou `*`) foram abolidas para os campos gerados pela IA. O layout agora adota prosa espaçada, utilizando termos em **negrito** como rótulos de tópicos, mantendo os subtítulos (`###`) e o espaçamento duplo rigoroso, visando um design mais limpo e conversacional.
- **bills/panel:** Implementada tela de carregamento com *auto-reload* (T061) na página de detalhes da submissão para quando o documento estiver aguardando o processamento assíncrono da Inteligência Artificial (`RECEIVED` ou `PROCESSING`), melhorando a experiência do usuário.
