# Database

## Entidades da User Story 3 (Sinalizações)
- `Flag`: Representa um alerta ou denúncia de imprecisão reportado por um usuário sobre o resumo da IA.
  - Campos: `version` (FK para AccessibleVersion), `reporter` (FK para User, anulável), `description` (Texto), `state` (Aberto, Resolvido), `excerpt` (Texto destacado).

## Entidades da User Story 4 (Curadoria)
- `AuditEntry`: Log inalterável (append-only) de todas as ações sensíveis realizadas no sistema.
  - Campos: `bill`, `version`, `submission` (FKs anuláveis), `action` (Enum com a ação), `actor` (FK para o User curador), `reason` (Texto de justificativa), `occurred_at` (Data da ocorrência).
  - Triggers/Regras: Possui sobrescritas em `.save()` e `.delete()` para barrar qualquer operação de Update ou Delete, forçando a preservação do histórico de auditoria.
