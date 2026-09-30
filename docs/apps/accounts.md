# 👤 Módulo `accounts`

## 1. Visão Geral
Módulo extremamente enxuto responsável pela criação e autenticação de pessoas. Se um cidadão quer subir um PDF de um Projeto de Lei para a IA ler, ele precisa ter se cadastrado aqui antes.

## 2. Estrutura de Arquivos

| Arquivo | Papel no Voto Claro |
|---------|---------------------|
| `models.py` | Extensão da tabela padrão (`AbstractUser`). |
| `views.py` | Controller responsável apenas pelo `/registrar/`. Todo o resto (login/logout) usa as views nativas do Django `auth`. |
| `urls.py` | Mapeia o registro. |

## 3. Modelos (Entidades)
Temos apenas o modelo `User` (herda de `AbstractUser`).
- A única diferença pro Django padrão é o booleano `is_curator`. 
- É o responsável por liberar ou bloquear o acesso às views do módulo `bills/views.py` (Curadoria).

## 4. Rotas

| Rota (Endpoint) | Handler (View) | Nome | O que faz |
|-----------------|----------------|------|-----------|
| `/accounts/registrar/` | `accounts.views.registrar` | `registrar` | Exibe o formulário e salva um usuário novo, logando-o imediatamente via `login()`. |
| `/accounts/login/` | `django.contrib.auth.views` | `login` | (Nativa) Entra no sistema. |

## 5. Pegadinhas (Tech Debts)
- **Hardcode de Redirecionamento:** O `/registrar/` da `accounts/views.py` tem o comando `return redirect("/")` fixo em código. Se a página principal do portal mudar, esse trecho de código quebra silenciosamente.
