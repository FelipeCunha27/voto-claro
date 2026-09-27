# Architecture

## Painel Público (User Story 2)
Foi implementado o app `panel` que atua como a vitrine do sistema. 
Ele garante que a população acesse exclusivamente projetos (`Bill`) que já tenham passado pelo motor de IA e possuam o status de submissão associado como `GENERATED`.
A arquitetura conta com paginação, busca (`search_bills`) e visualização desacoplada do modelo de submissão bruta.
