# Voto Claro 🇧🇷

**Voto Claro** é uma plataforma que traduz projetos de lei, PECs e planos de governo do "juridiquês" e "politiquês" para uma linguagem simples e acessível usando Inteligência Artificial.

Imagine um funil: qualquer cidadão pode enviar um arquivo PDF ou texto de uma lei complexa no sistema. Nos bastidores, a IA "lê" esse documento e gera um resumo explicando exatamente o que muda na prática, quem é afetado e quais os pontos de atenção. Depois, nossa equipe de curadoria aprova essa tradução, e ela é publicada em um painel público para todos lerem.

👉 **Se você é novo no time, comece lendo a nossa documentação central:** [📚 Documentação do Projeto (docs/index.md)](docs/index.md)

---

## 🚀 Como rodar o projeto localmente

Este projeto utiliza o [uv](https://github.com/astral-sh/uv) como gerenciador de dependências e ambientes.

### 1. Pré-requisitos
- Python 3.14+
- `uv` instalado na máquina (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 2. Configuração do ambiente
Clone o repositório e sincronize as dependências. O `uv` vai criar o `.venv` automaticamente.

```bash
uv sync
```

Crie o arquivo de variáveis de ambiente:
```bash
cp .env.example .env
```
> **Nota:** Certifique-se de configurar a variável `GEMINI_API_KEY` com uma chave válida no `.env`.

### 3. Banco de dados e Migrações
O projeto usa SQLite por padrão no ambiente local.
```bash
uv run manage.py migrate
```

Crie um usuário superadmin (necessário para acessar a curadoria, lembre-se de marcar `is_curator=True` via shell ou Django Admin se necessário):
```bash
uv run manage.py createsuperuser
```
*(Dívida Técnica: Atualmente não há um comando customizado para criar curador direto; você pode promover um usuário acessando o painel de admin padrão `/admin/` e marcando a flag `is_curator`)*.

### 4. Rodando o servidor
```bash
uv run manage.py runserver
```

Acesse `http://localhost:8000`.

---

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
