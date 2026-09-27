# Admin

## Curadoria de Sinalizações (Flags)
A gestão de `Flags` (denúncias) permite visualizar rapidamente o trecho destacado (`excerpt`) e a justificativa (`description`) do usuário. Em versões futuras (User Story 4), o Admin será usado para aceitar ou rejeitar essas sinalizações através do painel de Curadoria.

## Painel de Curadoria (Rotas Dedicadas)
O processo de revisão principal não ocorre mais apenas no Django Admin padrão, mas sim em rotas dedicadas (`/curadoria/`) exclusivas para usuários com `is_curator=True`.
As principais ações são feitas via POST e registradas no `AuditEntry`:
- **Aprovar**: Publica o `AccessibleVersion`.
- **Regerar**: Coloca o `Submission` novamente na fila da IA.
- **Editar**: Modifica os textos da versão, marcando a flag `edited_by_curator`.
- **Rejeitar/Despublicar**: Oculta do painel e exige preenchimento obrigatório de justificativa (`reason`).
- **Resolver Sinalização**: Fecha a denúncia (Flag) e insere as notas de resolução do curador.
- **Forçar Avisos**: Permite ao curador substituir a regra automática de contagem de Flags e ligar/desligar manualmente o selo de revisão (`review_notice_override`) de um Projeto.
