# Spec: User Story 2 - Painel Público

## Visão Geral
Cidadãos (não logados) precisam de um portal para buscar, navegar e ler os projetos políticos que já foram traduzidos para a Linguagem Simples pela Inteligência Artificial.

## Regras de Negócio
1. **Filtro de Segurança:** Apenas objetos `Submission` cujo `status` seja `GENERATED` podem ser exibidos ao público.
2. **Listagem (Home):** Exibir os projetos em formato de cards ordenados do mais recente para o mais antigo.
3. **Detalhes:** Ao clicar em um card, a URL deve usar o `slug` (ex: `/projeto/projeto-uuid/`) e exibir os dados armazenados na tabela `AccessibleVersion`.
4. **Busca (HTMX):** Permitir a filtragem em tempo real pelo título do projeto.
