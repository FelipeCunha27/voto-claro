# Voto Claro 🇧🇷

**Voto Claro** é uma plataforma que traduz projetos de lei, PECs e planos de governo do "juridiquês" e "politiquês" para uma linguagem simples e acessível usando Inteligência Artificial.

Imagine um funil: qualquer cidadão pode enviar um arquivo PDF ou texto de uma lei complexa no sistema. Nos bastidores, a IA "lê" esse documento e gera um resumo explicando exatamente o que muda na prática, quem é afetado e quais os pontos de atenção. Depois, nossa equipe de curadoria aprova essa tradução, e ela é publicada em um painel público para todos lerem.

👉 **Se você é novo no time, comece lendo a nossa documentação central:** [📚 Documentação do Projeto (docs/index.md)](docs/index.md)

---

## 🚀 Como testar localmente (One-Click Demo)

Este projeto utiliza o [uv](https://github.com/astral-sh/uv) como gerenciador de dependências. Preparamos um script para você testar a interface **sem precisar configurar chaves de API da OpenAI/Google**.

### 1. Pré-requisitos
- Python 3.14+
- `uv` instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 2. Instalação e Banco de Dados
Clone o repositório e aplique as migrações (o `.venv` é automático):

```bash
uv sync
cp .env.example .env
uv run manage.py migrate
```

### 3. Popular Dados Fictícios (Mock Data)
Para facilitar testes de portfólio, crie o ambiente de demonstração. Isso injetará projetos de lei fictícios já "traduzidos" no banco e criará o usuário administrador.

```bash
uv run manage.py setup_demo
```
> **Credenciais de Acesso à Curadoria:**
> Usuário: `admin` | Senha: `admin123`

### 4. Rodando o servidor
```bash
uv run manage.py runserver
```
- **Painel Público (Visualização):** `http://localhost:8000/`
- **Painel de Curadoria (Aprovação):** `http://localhost:8000/curadoria/`

---

## ✨ Destaques de Engenharia

O desenvolvimento deste MVP priorizou resiliência, escalabilidade e testes estruturados. Principais desafios resolvidos:

- **1. Resiliência de LLMs (Circuit Breaker):** Durante o desenvolvimento, a API do Gemini sofreu com Erros 503 (Overload). Desenvolvemos um *Fallback Array* acoplado a um *Exponential Backoff*. O sistema tenta conectar ao modelo principal (3.5-flash); em caso de indisponibilidade, escala para os modelos 3.6 e 3.8 com aguardo progressivo, garantindo que a geração não quebre.
- **2. Arquitetura Assíncrona via SQLite:** O processamento de linguagem natural é muito lento para o ciclo de request/response padrão. Integramos o `django-tasks` rodando diretamente no banco SQLite para enfileirar as traduções no background, evitando o over-engineering de subir um Redis logo no MVP.
- **3. Prevenção de Duplicidade Oculta:** Múltiplos usuários enviando o mesmo PDF gerariam gasto desnecessário de tokens. O sistema implementa uma camada de extração via `pypdf/python-docx` e salva um Hash Criptográfico do texto; textos repetidos são apenas linkados à versão já traduzida.
- **4. Strict Quality Gate (TDD):** A aplicação foi guiada por Spec Driven Development e TDD rigoroso. Atualmente, a cobertura de testes da suíte automatizada está em **84%**, mantendo o código na Complexidade Ciclomática "A" (via `radon`).
- **5. Documentação Viva (Context Engineering):** Uso avançado de *AI Agentic Coding*, com um subagent especializado em ler diffs e atualizar a documentação `docs/` mantendo diagramas estruturais via `mermaid.js` atualizados com o código sem desperdiçar tokens.

---

## 📸 Demonstração da Interface
*Adicione os screenshots do sistema rodando aqui*

![Painel Público](docs/images/placeholder_public.png)
*(Sugestão: Adicione aqui uma foto da tela pública)*

![Painel de Curadoria](docs/images/placeholder_curation.png)
*(Sugestão: Adicione aqui uma foto da tela de curadoria)*

## 🏗️ Arquitetura Geral (Resumo)
- **Framework:** Django 6.1
- **Banco de Dados:** SQLite (padrão local)
- **Filas Assíncronas:** `django_tasks_db` (banco de dados como fila)
- **Inteligência Artificial:** Integração via API do Google Gemini (`gemini-2.5-flash`)
- **Separação de Módulos:**
  - `accounts`: Autenticação e gestão de usuários/curadores.
  - `bills`: O "motor" do sistema (recebimento de documentos, extração de texto, fila assíncrona, integração com a IA, e interface de curadoria).
  - `panel`: O "vitrine" pública (busca, leitura de resumos gerados e submissão de sinalizações/denúncias).
  - `core`: Configurações centrais do Django.

**Vá para [docs/index.md](docs/index.md) para o aprofundamento técnico e ordem de leitura sugerida.**
