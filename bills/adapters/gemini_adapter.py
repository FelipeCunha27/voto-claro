import os
import json
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import APIError

class GenerationResult(BaseModel):
    summary: str
    who_is_affected: str
    practical_changes: str
    points_of_attention: str
    is_legislative_text: bool
    suggested_theme: str | None

class TransientGenerationError(Exception):
    pass

class PermanentGenerationError(Exception):
    pass

# Inicializa o client apenas se a chave existir e não for a de exemplo
api_key = os.environ.get("GEMINI_API_KEY")
if api_key and api_key != "sua-chave-api-do-google-aqui":
    client = genai.Client(api_key=api_key)
else:
    client = None

def generate_accessible_version(source_text: str, themes: list[str]) -> GenerationResult:
    if not client:
        raise PermanentGenerationError("Chave GEMINI_API_KEY ausente ou inválida no arquivo .env")
        
    prompt = f'''
    Você é um analista político especializado em avaliação de programas eleitorais e leis. Sua tarefa é analisar um projeto político de forma sistemática e imparcial, extraindo e explicando seus tópicos principais em linguagem acessível ao público geral, sem conhecimento prévio de política.

    ## Seu Objetivo
    Produzir um **relatório extremamente abrangente, exaustivo, mas com um tom altamente informal e acessível**. Você NÃO DEVE resumir demais, mas DEVE explicar tudo como se estivesse conversando com um amigo que não entende nada de política. Fuja do tom professoral ou formal. É mandatório que o seu relatório cubra TODOS os tópicos, propostas, áreas e medidas citadas no documento original, sem omitir absolutamente nada.

    ## Como Proceder
    1. **Identifique ABSOLUTAMENTE TODOS os tópicos principais e secundários** mencionados no projeto — inclua políticas econômicas, sociais, educacionais, de saúde, segurança, meio ambiente, infraestrutura, e qualquer outra área abordada no texto. NÃO faça cortes ou seleções; se está no texto original, deve estar na sua análise.
    2. **Para cada tópico, apresente:**
       - O que o projeto propõe especificamente (usando analogias do dia a dia e linguagem muito simples)
       - Os objetivos declarados
       - Os mecanismos ou ações sugeridas para alcançá-los
       - Possíveis impactos ou consequências descritos no texto
    3. **Mantenha neutralidade absoluta:** não expresse concordância ou discordância, mas use um tom acolhedor, informal e livre de qualquer jargão político, jurídico ou econômico (se o texto original usar jargão, traduza o significado na hora). Seu papel é descrever o que está no projeto, não avaliar se é bom ou ruim.
    4. **Cite passagens diretas do documento** quando apropriado, para ancorar suas observações no texto original e permitir verificação pelo leitor.
    5. **Destaque lacunas ou ambiguidades** — se o projeto mencionar um objetivo mas não detalhar como será implementado, sinalize isso claramente.
    6. **Organize de forma clara:** use estrutura lógica e evite jargão político. Quando precisar usar um termo técnico, explique-o em termos simples.


    [REGRAS DE FORMATAÇÃO E IDIOMA]
    1. É MANDATÓRIO escrever em Português do Brasil gramaticalmente perfeito.
    2. VOCÊ DEVE OBRIGATORIAMENTE USAR ACENTUAÇÃO (á, é, í, ó, ú, ã, õ, ç, ê, etc). NUNCA escreva palavras sem seus devidos acentos (Ex: escreva "Missão" e nunca "Missao"; escreva "eleições" e nunca "eleicoes").
    3. NÃO RESUMA DEMAIS. Seja exaustivo e cubra cada detalhe.

    [REGRAS DE INTEGRAÇÃO DO SISTEMA VOTO CLARO]
    Se o texto for um documento político (projeto de lei, PEC, plano de governo), marque 'is_legislative_text' como true. Se for uma receita de bolo ou texto aleatório, marque como false.
    
    Por favor, estruture sua análise preenchendo os seguintes campos solicitados:
    - summary: Visão geral e os objetivos declarados do projeto.
    - who_is_affected: Grupos da sociedade afetados pelas medidas e impactos esperados.
    - practical_changes: O que o projeto propõe e os mecanismos de ação detalhados PARA TODOS OS TÓPICOS IDENTIFICADOS SEM EXCEÇÃO. Cite passagens diretas do documento para ancorar as explicações.
    - points_of_attention: Destaque lacunas, pontos não explicados, falta de plano de financiamento ou ambiguidades (usando tom sempre neutro).
    - suggested_theme: Um tema central do projeto (ex: Segurança, Infraestrutura, Saúde).

    Texto Original:
    {source_text}
    '''
    
    
    
    import time
    modelos_fallback = ['gemini-3.5-flash', 'gemini-3.6-flash', 'gemini-3.8-flash']
    ultimo_erro = None
    
    # Vamos tentar o loop inteiro 3 vezes antes de desistir
    for tentativa in range(3):
        for modelo in modelos_fallback:
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=GenerationResult,
                        temperature=0.2,
                    ),
                )
                
                if not response.text:
                    raise PermanentGenerationError("A IA retornou uma resposta vazia.")
                    
                parsed_data = json.loads(response.text)
                result = GenerationResult(**parsed_data)
                
                if not result.is_legislative_text:
                    raise PermanentGenerationError("O documento enviado não é um texto legislativo válido.")
                    
                return result
                
            except APIError as e:
                ultimo_erro = e
                if "429" in str(e) or "503" in str(e):
                    print(f"Modelo {modelo} lotado (503). Tentando o próximo...")
                    time.sleep(1) # Espera 1s para não bater de frente com o limitador
                    continue
                raise PermanentGenerationError(str(e))
            except Exception as e:
                ultimo_erro = e
                break
                
        print(f"Rodada {tentativa+1} falhou. Aguardando 5 segundos para a IA respirar...")
        time.sleep(5)

    # Se saiu do loop, todos falharam várias vezes
    if ultimo_erro:
        if "429" in str(ultimo_erro) or "503" in str(ultimo_erro):
            raise TransientGenerationError(str(ultimo_erro))
        raise PermanentGenerationError(str(ultimo_erro))

