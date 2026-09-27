# Architecture

## Painel Público (User Story 2)
Foi implementado o app `panel` que atua como a vitrine do sistema. 
Ele garante que a população acesse exclusivamente projetos (`Bill`) que já tenham passado pelo motor de IA e possuam o status de submissão associado como `GENERATED`.
A arquitetura conta com paginação, busca (`search_bills`) e visualização desacoplada do modelo de submissão bruta.

## Fluxo de Sinalização (User Story 3)
A aplicação permite que usuários comparem a versão original (rota `panel_original`) e enviem sinalizações de erros na tradução via formulário (rota `panel_sinalizar`).
O model `Bill` agora possui a propriedade dinâmica `has_pending_review` que informa à interface se o projeto atual deve renderizar um aviso visual vermelho alertando o leitor de que a tradução foi contestada.
