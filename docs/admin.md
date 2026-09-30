# 🛠️ Curadoria e Admin

## 1. Visão Geral (Linguagem Simples)
O Voto Claro precisa de uma equipe de "revisores editoriais" humanos. Por mais que a IA seja esperta, ela pode alucinar (inventar coisas) ou usar jargões. 
Por isso, construímos uma **Área de Curadoria** isolada. Não usamos o painel branco-e-azul tradicional do Django (o `/admin/`) para aprovar leis. O painel nativo do Django existe, mas serve apenas para criar Temas (Saúde, Educação), Categorias, ou promover um cidadão comum ao cargo de Curador.
Toda a operação de "aprovar resumo" e "rejeitar resumo" vive na URL `/curadoria/`.

## 2. Como usar no dia a dia (O Painel de Curadoria)
Acessível apenas se o usuário tiver `is_curator=True`.

### Rotas e Operações Administrativas
| Rota | Método HTTP | O que faz na prática |
|------|-------------|----------------------|
| `/curadoria/` | GET | Lista os resumos que acabaram de ser gerados pela IA e precisam de leitura. |
| `/curadoria/<id>/` | GET | Tela de leitura onde o curador lê o texto da IA lado a lado com o original. |
| `/curadoria/<id>/aprovar/` | POST | Publica! A lei vai instantaneamente aparecer no site público para todos. Muda o status da submissão para `PUBLISHED`. |
| `/curadoria/<id>/editar/` | POST | Salva mudanças no texto caso o curador queira alterar uma palavra que a IA escreveu mal. Marca a flag `edited_by_curator=True`. |
| `/curadoria/<id>/regerar/` | POST | Diz: "IA, esse texto ficou horrível, tente de novo". Joga a submissão atual pra `SUPERSEDED` e enfileira uma nova requisição pro Gemini. |
| `/curadoria/<id>/rejeitar/` | POST | Bane o projeto. Geralmente usado quando um usuário submete uma "Receita de Bolo" como se fosse lei. Exige justificativa. |
| `/curadoria/<id>/despublicar/` | POST | Remove um projeto do ar (se descobrirem um erro grave). Muda o status para `UNPUBLISHED`. |

## 3. Fluxo de Sinalizações (Flags)
Se algum leitor reclamar de uma tradução lá no site público (criando um model `Flag`), o alerta piscará nesta tela de Curadoria.
A rota `/curadoria/sinalizacoes/<id>/resolver/` (POST) permite que o curador feche a denúncia digitando "Verificamos e a IA estava certa" e a salve como `RESOLVED`. 

*Nota Operacional:* A lei ganha um selo visual vermelho automático se tiver flags pendentes de leitura. O curador pode desligar isso artificialmente via rota de Override (`/curadoria/projeto/<slug>/aviso/`).

## 4. ⚠️ Pegadinhas do Admin Nativo
- **Promover curadores:** Não existe view para gerenciar a equipe de curadores no próprio painel de curadoria. O desenvolvedor ou Dono do Produto deve abrir `localhost:8000/admin/`, ir nos "Users" do app *accounts*, e marcar a caixa `is_curator`.
- Se você acessar `localhost:8000/admin/` como curador, nada funcionará (o acesso ao Admin nativo do Django requer `is_staff=True` e `is_superuser=True`, o qual é diferente de ser apenas curador do Voto Claro).
