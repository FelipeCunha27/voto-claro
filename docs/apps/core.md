# ⚙️ Módulo `core`

## 1. Visão Geral
O app `core` não é um módulo de regras de negócio. Ele é a pasta raiz de configurações do framework Django. Se você precisa instalar um novo pacote, alterar a linguagem padrão do site ou adicionar um middleware de segurança, é aqui que você mexe.

## 2. Estrutura de Arquivos

| Arquivo | Papel no Voto Claro |
|---------|---------------------|
| `settings.py` | Configurações principais. Instalação de apps, dicionários do banco de dados (`DATABASES`), definições estáticas. Lê de um `.env` usando a biblioteca `python-dotenv`. |
| `urls.py` | O "guardinha" principal de rotas. Recebe a requisição inicial e delega para os apps `accounts`, `bills` ou `panel`. |
| `wsgi.py` / `asgi.py` | Servidores e entrypoints em produção (Gunicorn / Uvicorn). |

## 3. Pegadinhas (Tech Debts)
1. **`ALLOWED_HOSTS = ['*']`**: Está escancarado no `settings.py`. Isso é uma grande falha de segurança que deve ser arrumada antes do deploy em produção.
2. Não possui um padrão sólido de logs (o `LOGGING` nativo do Django está ausente).
