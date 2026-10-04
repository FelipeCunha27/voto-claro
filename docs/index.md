# 📚 Documentação do Voto Claro

Bem-vindo(a) ao **Voto Claro**! Esta documentação foi feita para que você, desenvolvedor(a) que acabou de chegar, consiga entender a arquitetura, os fluxos e até as "pegadinhas" (dívidas técnicas) do projeto sem precisar perguntar a ninguém.

## 🧭 Ordem de Leitura Sugerida

Siga a ordem abaixo para um entendimento progressivo:

1. **[Arquitetura do Sistema](architecture.md)**: Entenda o ecossistema, os apps existentes e como os dados fluem do envio até a publicação.
2. **[Banco de Dados](database.md)**: Conheça as entidades, o Diagrama ER e as peculiaridades de modelagem (como tabelas append-only).
3. **[Módulo `bills` (O Motor Central)](apps/bills.md)**: Entenda a ingestão de PDFs, extração de texto, fila assíncrona, curadoria e integração com a IA (Google Gemini).
4. **[Módulo `panel` (A Vitrine)](apps/panel.md)**: Entenda como as versões aprovadas são exibidas para a população e como funciona o fluxo de sinalização (denúncias).
5. **[Módulo `accounts` (Autenticação)](apps/accounts.md)**: Autenticação simples e a distinção entre usuários comuns e curadores.
6. **[Módulo `core` (Configurações)](apps/core.md)**: O coração do Django, middlewares e configurações globais.
7. **[Curadoria & Admin](admin.md)**: O guia operacional e técnico do painel restrito de curadoria.

---

## 🗂️ Índice de Documentos

### Documentos Gerais
| Documento | Descrição |
|-----------|-----------|
| [`architecture.md`](architecture.md) | Diagramas de fluxo, comunicação entre módulos e fluxos assíncronos. |
| [`database.md`](database.md) | Entidades, relacionamentos (Diagrama ER) e dicionário de dados. |
| [`admin.md`](admin.md) | Como funciona a interface de revisão e aprovação (Curadoria) e o painel Admin. |
| [`ci_cd.md`](ci_cd.md) | Como funcionam os fluxos de AI-Powered DevOps (Tech Lead e Scrum Master via GitHub Actions). |

### Documentação por Módulo (Apps)
| App | Responsabilidade | Link |
|-----|------------------|------|
| **bills** | Receber documentos, processar via IA, gerenciar submissões e auditoria. | [`apps/bills.md`](apps/bills.md) |
| **panel** | Exibir os resultados de forma acessível ao público e colher feedbacks. | [`apps/panel.md`](apps/panel.md) |
| **accounts** | Gestão de usuários base e controle de acesso para curadores. | [`apps/accounts.md`](apps/accounts.md) |
| **core** | Configurações centrais do Django, URLs de raiz, tarefas e cache. | [`apps/core.md`](apps/core.md) |

---

## 📝 Convenções da Documentação
- Todos os documentos listam as dívidas técnicas (tech debts) e "pegadinhas" encontradas no código-fonte real. 
- Diagramas Mermaid são usados em fluxos dinâmicos e relacionamentos.
- Nomes de classes e métodos referenciam o código exato existente na raiz.
