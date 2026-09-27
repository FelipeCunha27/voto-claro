# Database

## Entidades da User Story 3 (Sinalizações)
- `Flag`: Representa um alerta ou denúncia de imprecisão reportado por um usuário sobre o resumo da IA.
  - Campos: `version` (FK para AccessibleVersion), `reporter` (FK para User, anulável), `description` (Texto), `state` (Aberto, Resolvido), `excerpt` (Texto destacado).
