---
name: project-structure
description: Mapeamento de documentos e convenções do projeto Voto Claro
metadata:
  type: project
---

- O projeto possui a regra de usar código em Inglês e docs em Português (PT-BR).
- Documentos principais vivem em `docs/` (`database.md`, `architecture.md`, `admin.md`, `index.md`).
- Documentação de apps individuais vivem em `docs/apps/<app_name>.md`.
- As tabelas de Dicionário de Dados e os ER Diagrams em Mermaid estão no arquivo `docs/database.md`. Se adicionar um Model, lembre-se de atualizar ambos.
- O painel de Admin nativo (Django) serve apenas para gestão de configurações básicas (Temas, Categorias, Usuários). Todo o fluxo de aprovação fica na "Área de Curadoria" (`/curadoria/`), detalhada em `docs/admin.md`.
