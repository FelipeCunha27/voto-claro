---
name: gemini-adapter-enrichment
description: Estratégia de enrichment no adapter do Gemini
metadata:
  type: project
---

O projeto utiliza um adapter `gemini_adapter.py` para consultar a IA e gerar resumos. O adapter foi aprimorado com uma política de `content enrichment`. Como a IA é "preguiçosa" e costuma desobedecer as regras de prompt (como tamanho mínimo de bullet points), há uma validação implementada (15 bullets no mínimo). Se a IA falhar na validação, o adapter efetua automaticamente uma segunda chamada (enrichment) apenas focado na formatação estrutural, utilizando as próprias saídas da primeira geração para corrigir o formato e gerar mais itens. O `markdownify` exige conversão de indentação de 2 para 4 espaços para gerar corretamente os `<ul>` em blocos separados. 
