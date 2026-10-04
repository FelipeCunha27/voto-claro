# 🏭 Módulo `bills`

## 1. Visão Geral (Linguagem Simples)
O `bills` é o "chão de fábrica" do Voto Claro. Ele abriga toda a engrenagem pesada do sistema. Se um cidadão quer enviar uma lei (em PDF ou link), é este módulo que segura o arquivo, espreme o texto usando bibliotecas python, envia assincronamente para a Inteligência Artificial e tenta transformar tudo num "resumo simples".
Além disso, toda a interface secreta dos "Curadores" (a galera que aprova ou rejeita o que a IA escreveu) vive neste módulo.

## 2. Estrutura de Arquivos

| Arquivo / Pasta | Papel no Voto Claro |
|-----------------|---------------------|
| `models.py` | Gigante. Contém `Bill`, `Submission`, `AccessibleVersion`, `Flag`, `Theme`, `Category` e `AuditEntry`. |
| `views.py` | Lida com as telas do usuário ("Minhas Submissões", "Enviar") e as dezenas de rotas exclusivas do painel `/curadoria/`. |
| `tasks.py` | Contém o "worker" assíncrono `generate_accessible_version_task`. |
| `adapters/gemini_adapter.py` | "Conversa" com a API do Google, enviando o prompt do sistema. |
| `services/extraction.py` | Usa `pypdf` e `python-docx` para garimpar texto bruto. |
| `services/screening.py` | Checa duplicidade via Hash e validações rudimentares de texto. |

## 3. Entidades (Models)
A anatomia do banco se baseia na passagem de bastão:
`Submission` (tentativa bruta) ➡️ `AccessibleVersion` (texto da IA) ➡️ `Bill` (O projeto final perene).
*(Para tabelas, campos e diagramas ER, visite a documentação de [Banco de Dados](../database.md))*

## 4. Rotas e Endpoints

### Para Usuários Comuns (Logados)
| Rota | Handler | Nome | O que faz |
|------|---------|------|-----------|
| `/enviar/` | `views.enviar` | `enviar` | Formulário de upload de PDFs, DOCs ou links. |
| `/minhas-submissoes/` | `views.minhas_submissoes` | `minhas_submissoes` | Lista os acompanhamentos do que o cara mandou (se tá na fila da IA, deu erro, etc). |
| `/minhas-submissoes/<id>/` | `views.minhas_submissoes_detail` | `minhas_submissoes_detail` | View de status específica. |

### Para Curadores (`@curator_required`)
*(Para as rotas que começam com `/curadoria/`, veja a doc em [Curadoria & Admin](../admin.md))*

## 5. Fluxo de Geração (O "Motor")

```mermaid
graph TD
    A(Usuário manda PDF) --> B[extraction.py extrai o texto]
    B --> C[screening.py checa duplicata (Hash)]
    C -->|Novo| D[Salva Submission no DB]
    C -->|Já existe| E[Avisa Usuário que já tá lá]
    D --> F[Task Assíncrona no background]
    
    F --> G(gemini_adapter.py envia o Prompt)
    G --> H{É um documento político válido?}
    H -->|Sim| I[Cria Bill e AccessibleVersion]
    H -->|Não| J[Rejeita: REJECTED]
```

## 6. ⚠️ Dívidas Técnicas / Bugs Latentes Enormes
Existem falhas latentes críticas em produção nos arquivos de base:

1. **Engolir Erros de PDF Silenciosamente:** Em `extraction.py`, o loop que lê o PDF está num bloco `try... except Exception: pass`. Se o arquivo PDF for corrompido ou encriptado, ele retorna string vazia sem dar erro.
2. **Título Derivado Incompleto:** Na `views.enviar`, o código parou de forçar um título estático ("Aguardando processamento..."), mas agora utiliza os primeiros 50 caracteres do `source_text`. Isso pode gerar títulos confusos no painel temporário, especialmente se o texto extraído do arquivo iniciar com metadados, cabeçalhos irrelevantes ou sujeira de formatação.
