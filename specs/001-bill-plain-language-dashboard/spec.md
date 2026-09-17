# Feature Specification: Tradução de Projetos Políticos para Linguagem Acessível com Painel Público

**Feature Branch**: `001-bill-plain-language-dashboard`

**Created**: 2026-09-09

**Status**: Draft

**Input**: User description: "O usuário submete projetos políticos, o sistema traduz para linguagem acessível com IA e mostra num painel público"

## Clarifications

### Session 2026-09-13

- Q: Quando duas pessoas submetem o mesmo projeto de lei, o que o sistema deve usar para reconhecer que se trata de uma duplicata? (FR-007) → A: Identidade do texto — comparação do conteúdo normalizado; só é duplicata se o texto for essencialmente idêntico.
- Q: Quem define o tema de um projeto, que o painel público usa como filtro? (FR-018) → A: A geração por IA sugere um tema a partir de um vocabulário controlado; o Administrador confirma ou corrige no momento da aprovação.
- Q: Sinalizações de imprecisão feitas por leitores anônimos devem contar para acionar o aviso público de "revisão pendente"? (FR-022, FR-024) → A: Não — sinalizações anônimas vão para a fila do administrador, mas só as de contas autenticadas acionam o aviso público.
- Q: Como o remetente fica sabendo que a versão acessível do projeto dele ficou pronta? (FR-012, FR-014) → A: Apenas por consulta no site, em uma página com as próprias submissões; nenhuma notificação por e-mail nesta versão.
- Q: Quais limites concretos o sistema deve aplicar a cada submissão — quantos envios por remetente e qual tamanho de texto aceito? (FR-004, FR-006) → A: 5 submissões por remetente a cada 24 horas; texto entre 500 e 50.000 caracteres.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submeter um projeto e receber a versão acessível (Priority: P1)

Uma pessoa interessada em política encontra um projeto de lei escrito em linguagem jurídica densa e não consegue entender o que ele realmente propõe. Ela submete o texto do projeto ao sistema, informa alguns dados mínimos de identificação (título, origem/casa legislativa, número/ano quando conhecido) e, em poucos minutos, recebe uma versão em linguagem simples que explica: o que o projeto quer fazer, quem é afetado, o que muda na prática e qual o estágio da tramitação informado.

**Why this priority**: É o núcleo da proposta de valor. Mesmo sem painel público, sem busca e sem moderação, uma única pessoa conseguindo entender um projeto que antes era incompreensível já entrega o valor central do produto. Todas as outras histórias dependem da existência dessa capacidade.

**Independent Test**: Pode ser testada de ponta a ponta submetendo um projeto de lei real conhecido e verificando que a versão gerada é compreensível por um leitor sem formação jurídica, preserva o sentido do original e não inventa conteúdo ausente do texto-fonte.

**Acceptance Scenarios**:

1. **Given** um usuário autorizado a submeter com um texto de projeto válido em português, **When** ele envia a submissão, **Then** o sistema confirma o recebimento, informa que o processamento está em andamento e apresenta a versão em linguagem acessível quando concluída.
2. **Given** uma submissão em processamento, **When** o usuário consulta o estado dela, **Then** o sistema exibe um estado inequívoco entre "recebido", "em processamento", "concluído", "falhou" ou "rejeitado", com uma explicação legível em caso de falha ou rejeição.
3. **Given** uma versão acessível gerada, **When** o usuário a visualiza, **Then** a página exibe um rótulo explícito de conteúdo gerado por inteligência artificial, a data de geração e acesso ao texto original submetido.
4. **Given** um texto submetido que não corresponde a um projeto político (texto aleatório, propaganda, conteúdo ofensivo), **When** o sistema o processa, **Then** a submissão é rejeitada com motivo informado e nenhuma versão acessível é publicada.
5. **Given** o serviço de tradução automática indisponível, **When** o usuário submete um projeto, **Then** a submissão é preservada, marcada como pendente e processada quando o serviço voltar, sem perda de dados nem necessidade de reenvio.

---

### User Story 2 - Consultar o painel público de projetos traduzidos (Priority: P2)

Um cidadão sem cadastro acessa o painel público, navega pelos projetos já traduzidos, filtra por tema, casa legislativa ou período, busca por palavra-chave e abre a versão acessível de um projeto que lhe interessa — tudo sem precisar entender jargão legislativo nem criar conta.

**Why this priority**: Transforma traduções individuais em um bem público consultável. É o que dá escala e alcance ao produto, mas depende de já existirem traduções (P1).

**Independent Test**: Pode ser testada carregando um conjunto de projetos já traduzidos e verificando que um visitante anônimo consegue localizar um projeto específico por busca ou filtro e ler sua versão acessível sem autenticação.

**Acceptance Scenarios**:

1. **Given** um visitante não autenticado, **When** ele acessa o painel público, **Then** vê a lista de projetos com versão acessível publicada, ordenada por data de publicação mais recente por padrão.
2. **Given** um visitante no painel, **When** ele busca por uma palavra-chave presente no título ou no resumo acessível, **Then** os projetos correspondentes são listados e os não correspondentes são omitidos.
3. **Given** um visitante no painel, **When** ele aplica filtros por tema, casa legislativa ou período, **Then** apenas os projetos que satisfazem todos os filtros aplicados são exibidos.
4. **Given** uma busca ou combinação de filtros sem resultados, **When** o painel é exibido, **Then** uma mensagem clara informa a ausência de resultados e oferece caminho para limpar os filtros.
5. **Given** um projeto que ainda não teve sua tradução publicada, **When** o painel público é consultado, **Then** esse projeto não aparece na listagem pública.

---

### User Story 3 - Conferir a fidelidade da tradução e sinalizar problemas (Priority: P3)

Um leitor mais atento — jornalista, estudante, ativista — quer confiar no que está lendo. Ele compara a versão acessível com o texto original lado a lado, verifica de onde veio o conteúdo e, ao identificar uma simplificação enganosa, uma omissão relevante ou um viés, sinaliza o problema para revisão.

**Why this priority**: Traduzir conteúdo político com IA cria risco real de distorção e desinformação. O mecanismo de conferência e sinalização é o que sustenta a credibilidade do painel a médio prazo, mas o produto já entrega valor sem ele.

**Independent Test**: Pode ser testada abrindo um projeto publicado, alternando entre versão original e versão acessível, enviando uma sinalização de imprecisão e verificando que ela é registrada e fica visível para quem administra o conteúdo.

**Acceptance Scenarios**:

1. **Given** um projeto publicado no painel, **When** o leitor solicita ver o texto original, **Then** o texto-fonte integral submetido é exibido junto da versão acessível.
2. **Given** um leitor visualizando uma versão acessível, **When** ele sinaliza um trecho como impreciso e descreve o problema, **Then** a sinalização é registrada com referência ao projeto e ao trecho, e o leitor recebe confirmação.
3. **Given** um projeto que acumulou sinalizações de contas autenticadas acima de um limite definido, **When** o painel público o exibe, **Then** um aviso de revisão pendente acompanha a versão acessível.
4. **Given** uma sinalização registrada, **When** quem administra o conteúdo a analisa, **Then** é possível resolvê-la corrigindo, regerando ou despublicando a versão acessível, com o desfecho registrado.

---

### User Story 4 - Curar e publicar o conteúdo do painel (Priority: P4)

Quem administra o Voto Claro acompanha as submissões recebidas, revisa as versões geradas, corrige ou solicita nova geração quando necessário, e controla o que entra e o que sai do painel público — incluindo despublicar conteúdo problemático.

**Why this priority**: Necessária para operar o painel com responsabilidade em escala, mas não é pré-requisito para demonstrar o valor das três primeiras histórias.

**Independent Test**: Pode ser testada acessando a área administrativa com uma submissão pendente, aprovando-a e confirmando que ela passa a aparecer no painel público — e depois despublicando-a e confirmando que sai.

**Acceptance Scenarios**:

1. **Given** submissões com versões acessíveis geradas, **When** o administrador acessa a fila de curadoria, **Then** vê as submissões pendentes com texto original, versão gerada e sinalizações associadas.
2. **Given** uma versão acessível na fila, **When** o administrador a aprova, **Then** ela passa a constar no painel público com data de publicação registrada.
3. **Given** uma versão acessível publicada e problemática, **When** o administrador a despublica, **Then** ela deixa de aparecer no painel público e o motivo é registrado.
4. **Given** uma versão acessível considerada insatisfatória, **When** o administrador solicita nova geração, **Then** uma nova versão é produzida e a versão anterior permanece registrada no histórico.

---

### Edge Cases

- **Documento muito extenso**: projeto com centenas de páginas ou anexos volumosos — o sistema recusa acima de 50.000 caracteres aproveitáveis, informa o limite ao usuário no momento da recusa e não trunca conteúdo silenciosamente.
- **Texto inutilizável**: conteúdo vazio, ilegível, com poucos caracteres aproveitáveis ou fora do português — rejeição com motivo explícito, sem consumir processamento de IA repetidamente.
- **Conteúdo indevido**: spam, texto ofensivo, material com dados pessoais sensíveis ou conteúdo que não é projeto político — bloqueado antes da publicação pública.
- **Duplicidade**: o mesmo texto submetido mais de uma vez — o sistema identifica a duplicata pela comparação do texto normalizado, evita entradas repetidas no painel público e associa a nova submissão ao registro existente, preservando a procedência de cada remetente. Dois envios do mesmo projeto com textos materialmente diferentes (por exemplo, redações de fontes distintas) não são reconhecidos como duplicata e geram registros públicos separados até que a curadoria intervenha.
- **Projeto alterado depois de traduzido**: uma nova versão do texto original é submetida — a versão acessível anterior não é sobrescrita silenciosamente; a versão exibida indica a qual texto-fonte corresponde.
- **Falha ou lentidão do serviço de IA**: indisponibilidade, tempo limite excedido ou resposta malformada — a submissão não é perdida, é reprocessada segundo uma política de novas tentativas, e após esgotá-las é marcada como falha com motivo legível.
- **Tradução com erro grave**: a versão acessível contradiz, omite ou inverte um ponto central do original — precisa ser corrigível e despublicável sem apagar o histórico do que foi exibido publicamente.
- **Submissões em volume abusivo**: um mesmo remetente envia grande quantidade de submissões em curto intervalo — a partir da sexta submissão em 24 horas o envio é recusado, com indicação de quando será possível tentar de novo (FR-006).
- **Sinalização em massa para desacreditar um projeto**: alguém dispara muitas sinalizações anônimas contra o mesmo projeto — o aviso público de revisão pendente não é acionado por elas (FR-024) e o projeto não é marcado como suspeito sem decisão humana; as sinalizações seguem registradas para análise.
- **Ausência total de conteúdo publicado**: painel público sem nenhum projeto aprovado — exibe estado vazio explicativo em vez de página em branco ou erro.

## Requirements *(mandatory)*

### Functional Requirements

#### Submissão

- **FR-001**: O sistema MUST permitir que um usuário submeta um projeto político informando o texto do projeto e metadados de identificação (título, casa/órgão de origem, número e ano quando disponíveis, link para a fonte oficial quando houver).
- **FR-002**: O sistema MUST exigir conta autenticada para submeter um projeto. O cadastro é aberto a qualquer pessoa; a leitura do painel público permanece sem autenticação.
- **FR-003**: O sistema MUST aceitar o conteúdo do projeto de duas formas: texto colado diretamente e upload de arquivo PDF ou DOCX, do qual o texto é extraído para processamento. Arquivos sem camada de texto aproveitável (por exemplo, PDF escaneado) são rejeitados com orientação de colar o texto manualmente.
- **FR-004**: O sistema MUST validar cada submissão quanto a tamanho, idioma e presença de conteúdo aproveitável antes de acionar a geração da versão acessível. O texto aproveitável MUST ter entre 500 e 50.000 caracteres; fora dessa faixa a submissão é recusada com o limite informado ao remetente. Os valores são configuráveis, mas esses são os vigentes.
- **FR-005**: O sistema MUST rejeitar submissões que não correspondam a um projeto político, informando ao remetente o motivo da rejeição em linguagem clara.
- **FR-006**: O sistema MUST limitar cada remetente a 5 submissões a cada 24 horas, para conter abuso e custo de processamento. Ao atingir o limite, a submissão é recusada com mensagem informando quando o remetente poderá enviar novamente. O valor é configurável, mas esse é o vigente.
- **FR-007**: O sistema MUST detectar submissões duplicadas comparando o texto do projeto após normalização (espaços, quebras de linha, capitalização e pontuação irrelevante). Uma submissão cujo texto normalizado coincide com o de uma submissão já registrada MUST ser associada ao mesmo Projeto Político, sem gerar nova versão acessível nem nova entrada no painel público. Divergência de metadados não impede o reconhecimento da duplicata; coincidência de metadados, isoladamente, não caracteriza duplicata.

#### Geração da versão acessível

- **FR-008**: O sistema MUST gerar, para cada submissão válida, uma versão em linguagem acessível em português contendo, no mínimo: resumo do objetivo do projeto, quem é afetado, o que muda na prática e principais pontos de atenção.
- **FR-008a**: A geração MUST também propor um tema para o projeto, escolhido obrigatoriamente de um vocabulário controlado mantido pelos administradores. Um tema proposto fora do vocabulário é descartado e o projeto segue sem tema até que um administrador o defina.
- **FR-009**: A versão acessível MUST ser fiel ao texto submetido: não pode acrescentar fatos ausentes do original, emitir juízo de valor sobre o mérito político do projeto, nem recomendar posicionamento a favor ou contra.
- **FR-010**: O sistema MUST preservar o texto original submetido integralmente e de forma imutável, vinculado à versão acessível correspondente.
- **FR-011**: O sistema MUST registrar, para cada versão acessível, a data e hora de geração e o histórico de versões anteriores quando houver regeração.
- **FR-012**: O sistema MUST expor o estado de cada submissão ao remetente entre "recebido", "em processamento", "concluído", "falhou" e "rejeitado", em uma página autenticada que lista as submissões do próprio remetente. O acompanhamento é por consulta: o sistema não envia notificação por e-mail nesta versão, e o motivo de rejeição ou falha MUST estar legível nessa mesma página.
- **FR-013**: O sistema MUST reprocessar automaticamente submissões cuja geração falhou por indisponibilidade temporária, e marcar como falha definitiva com motivo legível após esgotar as tentativas.
- **FR-014**: O sistema MUST processar submissões de forma assíncrona, sem exigir que o remetente permaneça aguardando na tela.

#### Publicação e painel público

- **FR-015**: Uma versão acessível MUST ser publicada no painel público apenas após aprovação humana explícita por um administrador. Nenhuma versão gerada automaticamente fica visível ao público sem essa aprovação.
- **FR-016**: O painel público MUST ser consultável por qualquer visitante sem cadastro ou autenticação.
- **FR-017**: O painel público MUST permitir busca por palavra-chave sobre título e conteúdo da versão acessível.
- **FR-018**: O painel público MUST permitir filtrar projetos por tema, casa/órgão de origem e período, e ordenar os resultados por data. O tema de cada projeto MUST ser confirmado ou corrigido por um administrador no momento da aprovação, a partir do vocabulário controlado (FR-008a); um projeto sem tema definido permanece publicável, mas não aparece sob nenhum filtro de tema.
- **FR-019**: Toda versão acessível exibida publicamente MUST apresentar rótulo explícito indicando que o conteúdo foi gerado por inteligência artificial e não substitui o texto oficial.
- **FR-020**: O painel público MUST oferecer acesso ao texto original submetido e ao link da fonte oficial, quando informado, a partir da página de cada projeto.
- **FR-021**: O painel público MUST exibir estado vazio explicativo quando não houver projetos publicados ou quando busca e filtros não retornarem resultados.

#### Confiança, sinalização e curadoria

- **FR-022**: O sistema MUST permitir que qualquer leitor sinalize uma versão acessível como imprecisa, informando descrição do problema e, opcionalmente, o trecho afetado.
- **FR-023**: O sistema MUST registrar cada sinalização vinculada ao projeto e à versão acessível vigente no momento da sinalização.
- **FR-024**: O sistema MUST exibir aviso de revisão pendente no painel público quando um projeto ultrapassar um limite configurável de sinalizações não resolvidas. Apenas sinalizações feitas por contas autenticadas contam para esse limite; sinalizações anônimas são registradas e encaminhadas à fila do administrador, mas nunca acionam o aviso público por si só. Um administrador MUST poder marcar ou retirar o aviso de revisão pendente manualmente, independentemente do limite.
- **FR-025**: O sistema MUST permitir que administradores aprovem, corrijam, regerem ou despubliquem versões acessíveis e confirmem ou corrijam o tema do projeto, registrando autor, data e motivo de cada ação.
- **FR-026**: O sistema MUST manter registro auditável das publicações e despublicações, de modo que seja possível reconstituir o que esteve visível publicamente e em que período.

#### Acessibilidade e conteúdo

- **FR-027**: A versão acessível MUST ser escrita em português brasileiro, em nível de leitura compatível com ensino fundamental completo, evitando jargão jurídico não explicado.
- **FR-028**: As páginas públicas MUST ser navegáveis por teclado e compatíveis com leitores de tela, com contraste e estrutura de títulos adequados.
- **FR-029**: As páginas públicas MUST ser utilizáveis em telas de celular sem perda de conteúdo ou funcionalidade.

### Key Entities *(include if feature involves data)*

- **Submissão**: um envio de projeto político ao sistema. Reúne texto original, metadados informados (título, origem, número, ano, link da fonte), quem submeteu, data de envio e estado de processamento.
- **Projeto Político**: a entidade pública consultável que consolida um projeto legislativo. Agrega uma ou mais submissões duplicadas, os metadados canônicos e a versão acessível vigente.
- **Versão Acessível**: o texto em linguagem simples derivado de uma submissão. Guarda conteúdo gerado, data de geração, indicação de origem automática, estado de publicação e vínculo com a submissão que a originou.
- **Tema**: categoria de assunto usada para navegar o painel (ex.: saúde, educação, tributação). Vocabulário controlado mantido pelos administradores; sugerido pela geração e confirmado na aprovação.
- **Remetente**: quem envia uma submissão. Identificação e permissões dependem do modelo de acesso definido (ver FR-002).
- **Administrador**: quem cura o conteúdo — aprova, corrige, regenera, despublica e resolve sinalizações.
- **Sinalização**: relato de imprecisão feito por um leitor sobre uma versão acessível. Contém descrição, trecho opcional, data, estado (aberta/resolvida), desfecho e a indicação de o autor estar ou não autenticado — o que determina se ela conta para o aviso público de revisão pendente.
- **Registro de Auditoria**: histórico das transições relevantes de estado — geração, publicação, regeração, despublicação — com autor, data e motivo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 90% das submissões válidas resultam em versão acessível disponível ao remetente em até 3 minutos a partir do envio.
- **SC-002**: Em teste de compreensão com leitores sem formação jurídica, 85% identificam corretamente o objetivo principal e quem é afetado por um projeto, lendo apenas a versão acessível.
- **SC-003**: Um leitor com ensino fundamental completo consegue ler a versão acessível de um projeto e explicá-la com as próprias palavras em menos de 5 minutos.
- **SC-004**: Um visitante que chega ao painel público sem conhecimento prévio localiza um projeto de interesse por busca ou filtro em menos de 30 segundos.
- **SC-005**: Menos de 5% das versões acessíveis publicadas acumulam sinalizações de imprecisão confirmadas em revisão.
- **SC-006**: 100% das versões acessíveis exibidas publicamente apresentam rótulo de conteúdo gerado por IA e acesso ao texto original.
- **SC-007**: Nenhuma submissão válida é perdida em caso de indisponibilidade do serviço de tradução: 100% são reprocessadas ou marcadas com falha explícita.
- **SC-008**: Sinalizações de imprecisão são analisadas e resolvidas em até 7 dias em 90% dos casos.
- **SC-009**: As páginas públicas atendem aos critérios de acessibilidade WCAG 2.1 nível AA nas telas de listagem e de leitura de projeto.
- **SC-010**: O painel suporta pelo menos 200 submissões por dia e 5.000 leituras diárias sem degradação perceptível para o visitante.

## Assumptions

- O público-alvo é brasileiro e o conteúdo — original e traduzido — está em português brasileiro; suporte a outros idiomas está fora do escopo desta versão.
- "Projetos políticos" abrange projetos de lei, propostas de emenda, medidas provisórias e documentos legislativos equivalentes, em qualquer esfera (federal, estadual, municipal).
- A leitura do painel público é aberta e não exige cadastro; apenas submissão e curadoria envolvem identificação de usuário (decisão confirmada em 2026-09-10, FR-002).
- Toda publicação passa por aprovação humana (decisão confirmada em 2026-09-10, FR-015). Isso limita deliberadamente a taxa de crescimento do painel à capacidade da equipe de curadoria e torna a fila de revisão parte do MVP, não um recurso posterior.
- A entrada aceita texto colado e arquivos PDF/DOCX (decisão confirmada em 2026-09-10, FR-003). Reconhecimento óptico de caracteres para documentos escaneados está fora do escopo desta versão.
- O Voto Claro não é fonte oficial e não tem vínculo com órgãos legislativos; a versão acessível é material de apoio à compreensão e o texto oficial sempre prevalece.
- A geração da versão acessível depende de um provedor externo de inteligência artificial, sujeito a indisponibilidade, latência variável e custo por processamento — daí os requisitos de limite de taxa, processamento assíncrono e novas tentativas.
- O tratamento de dados de remetentes e de sinalizações segue a LGPD; dados pessoais eventualmente presentes no texto submetido não devem ser expostos no painel público.
- A entrega é uma aplicação web responsiva; aplicativos móveis nativos estão fora do escopo.
- Notificações por e-mail sobre o desfecho de uma submissão estão fora do escopo desta versão (decisão confirmada em 2026-09-13, FR-012). O acompanhamento é por consulta na página de submissões do remetente; o risco assumido é o de uma rejeição passar despercebida por quem não retorna ao site.
- Não há integração automática com sistemas legislativos oficiais nesta versão; a origem do conteúdo é a submissão feita por pessoas.
- A curadoria é feita por uma equipe pequena, o que torna relevante o custo operacional de qualquer etapa de revisão manual.
- A constituição do projeto (`.specify/memory/constitution.md`) ainda está no estado de template não preenchido, portanto nenhum princípio de governança específico foi aplicado a esta especificação.
