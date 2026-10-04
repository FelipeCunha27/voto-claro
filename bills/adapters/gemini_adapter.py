import os
import json
import time
import re

from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import APIError


class GenerationResult(BaseModel):
    official_title: str | None = None
    summary: str
    who_is_affected: str
    practical_changes: str
    points_of_attention: str
    is_valid_document: bool
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

# Campos textuais da versão acessível que devem ser escaneáveis
_ACCESSIBLE_FIELDS = ('summary', 'who_is_affected', 'practical_changes', 'points_of_attention')

# Modelos em ordem de prioridade para fallback
_MODELS = ('gemini-3.5-flash', 'gemini-3.6-flash', 'gemini-3.8-flash')

# Configuração compartilhada entre geração e enrichment
_GENERATION_CONFIG = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=GenerationResult,
    temperature=0.2,
)

# T059: regras de escaneabilidade
_MAX_SENTENCES_PER_PARAGRAPH = 3
_HEADING_RE = re.compile(r'^\s*#{3,4}\s+\S', re.MULTILINE)
_BULLET_RE = re.compile(r'^\s*[-*]\s', re.MULTILINE)
_BOLD_RE = re.compile(r'\*\*[^*\n]+\*\*')
_LIST_ITEM_RE = re.compile(r'^\s*([-*+]|\d+[.)])\s+')
_SENTENCE_END_RE = re.compile(r'[.!?…]+(?=\s|$)')


def _prose_paragraphs(text: str):
    """Extrai os parágrafos de prosa (ignora subtítulos, itens de lista e linhas vazias)."""
    paragraph = []
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or _LIST_ITEM_RE.match(line):
            if paragraph:
                yield ' '.join(paragraph)
                paragraph = []
            continue
        paragraph.append(stripped)
    if paragraph:
        yield ' '.join(paragraph)


def validate_scannable_formatting(text: str | None) -> bool:
    """Valida se o texto é escaneável (T059).

    Critérios: ao menos um subtítulo (### ou ####), ao menos um termo em
    negrito e nenhum parágrafo de prosa com mais de 3 frases. Não há
    quantidade mínima de bullet points.
    """
    if not text or not text.strip():
        return False
    if not _HEADING_RE.search(text) or not _BOLD_RE.search(text):
        return False
    if _BULLET_RE.search(text):
        return False
    return all(
        len(_SENTENCE_END_RE.findall(paragraph)) <= _MAX_SENTENCES_PER_PARAGRAPH
        for paragraph in _prose_paragraphs(text)
    )


def _build_enrichment_prompt(source_text: str, result: GenerationResult) -> str:
    """Constrói prompt para reformatar o relatório seguindo as regras de escaneabilidade."""
    return f'''
    O relatório abaixo foi gerado a partir de um documento político, mas a formatação
    não está escaneável o suficiente para o público geral.

    Reescreva TODOS os campos mantendo o conteúdo original intacto, mas reformatando para:
    - Dividir cada campo em seções com subtítulos descritivos em Markdown (### ou ####)
    - Usar **negrito** para termos-chave, conceitos centrais e conclusões importantes
    - Escrever parágrafos curtos, com no máximo 2 a 3 frases cada
    - NÃO USE listas ou bullet points ("-", "*"). Em vez disso, agrupe informações em parágrafos iniciados por um termo em **negrito** (ex: "**Tema:** explicação").
    - Criar hierarquia visual usando subtítulos Markdown (### ou ####) e parágrafos curtos.
    - Deixar uma linha em branco entre TODOS os parágrafos e antes de qualquer título
    - Colocar a informação essencial no início de cada ponto, com frases diretas
    - Cobrir TODOS os tópicos do documento original, sem omitir nenhum
    - NÃO repita o nome da seção/campo (ex: "Mudanças Práticas") no início do texto. Vá direto aos subtópicos.

    Relatório original:
    - official_title: {result.official_title}
    - summary: {result.summary}
    - who_is_affected: {result.who_is_affected}
    - practical_changes: {result.practical_changes}
    - points_of_attention: {result.points_of_attention}

    Texto original do documento:
    {source_text}

    Retorne o resultado com os mesmos campos, com is_valid_document=true, suggested_theme="{result.suggested_theme or ''}" e official_title="{result.official_title or ''}".
    '''


def _has_sufficient_formatting(result: GenerationResult) -> bool:
    """Verifica se todos os campos textuais atendem às regras de escaneabilidade."""
    return all(
        validate_scannable_formatting(getattr(result, field))
        for field in _ACCESSIBLE_FIELDS
    )


def _try_enrich(model_name: str, source_text: str, result: GenerationResult) -> GenerationResult | None:
    """Tenta enriquecer um resultado com formatação insuficiente.

    Faz uma chamada extra à API pedindo reformatação conforme as regras de escaneabilidade.
    Retorna o resultado enriquecido ou None se a tentativa falhar.
    """
    try:
        enrichment_prompt = _build_enrichment_prompt(source_text, result)
        response = client.models.generate_content(
            model=model_name,
            contents=enrichment_prompt,
            config=_GENERATION_CONFIG,
        )
        if response.text:
            return GenerationResult(**json.loads(response.text))
    except Exception:
        pass
    return None


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
    1. É MANDATÓRIO escrever em Português do Brasil gramaticalmente perfeito e usar acentuação corretamente.
    2. ESCREVA PARA O PÚBLICO GERAL: Mantenha um tom conversacional, acessível e direto. Evite jargão.
    3. NÃO RESUMA DEMAIS: Seja exaustivo e cubra CADA TÓPICO do documento original. Não omita conteúdo.
    4. ESCANEABILIDADE OBRIGATÓRIA - Use as seguintes técnicas em TODOS os campos (summary, who_is_affected, practical_changes, points_of_attention):
       - Títulos e subtítulos claros: Divida o texto com cabeçalhos descritivos em Markdown (### ou ####).
       - SEM BULLET POINTS: NÃO USE listas ou marcadores (-, *). Escreva os itens em forma de parágrafos curtos, introduzindo-os com um rótulo em **negrito** seguido de dois pontos (ex: "**Grupo A:** descrição...").
       - Destaque visual: Use **negrito** para termos-chave e conceitos centrais.
       - Parágrafos curtos: Limite os parágrafos a no máximo 2 a 3 frases.
       - Espaçamento: É OBRIGATÓRIO pular uma linha (deixar uma linha em branco) entre TODOS os parágrafos e antes de qualquer título. Não junte parágrafos.
       - Frases diretas: Coloque a informação essencial no início de cada ponto.
    5. HIERARQUIA VISUAL: Use apenas subtítulos (###) e parágrafos curtos. Não use indentação.
    6. SEM TÍTULOS REDUNDANTES: O sistema já exibe os nomes das seções na interface (Resumo, Mudanças Práticas, etc). NÃO inicie sua resposta repetindo o nome do campo, nem crie um título de introdução global. Vá direto ao conteúdo. Use cabeçalhos (### ou ####) APENAS para dividir os subtópicos e eixos do documento internamente.

    [REGRAS DE INTEGRAÇÃO DO SISTEMA VOTO CLARO]
    Se o texto for um documento político válido para análise (projeto de lei, PEC, plano de governo, etc), marque 'is_valid_document' como true. Se for uma receita de bolo, manual técnico não-político ou texto aleatório, marque como false.
    
    Por favor, estruture sua análise preenchendo os seguintes campos solicitados:
    - official_title: Vasculhe todo o texto e extraia o título oficial e completo do documento (incluindo o nome do candidato se for um plano de governo, ex: "Plano de Governo - Candidato Fulano" ou "Projeto de Lei 123/2024").
    - summary: Visão geral e os objetivos declarados do projeto.
    - who_is_affected: Grupos da sociedade afetados pelas medidas e impactos esperados.
    - practical_changes: O que o projeto propõe e os mecanismos de ação detalhados PARA TODOS OS TÓPICOS IDENTIFICADOS SEM EXCEÇÃO. Cite passagens diretas do documento para ancorar as explicações.
    - points_of_attention: Destaque lacunas, pontos não explicados, falta de plano de financiamento ou ambiguidades (usando tom sempre neutro).
    - suggested_theme: Um tema central do projeto (ex: Segurança, Infraestrutura, Saúde).

    Texto Original:
    {source_text}
    '''
    
    last_error = None
    for attempt in range(3):
        for model_name in _MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=_GENERATION_CONFIG,
                )
                
                if not response.text:
                    raise PermanentGenerationError("A IA retornou uma resposta vazia.")
                    
                result = GenerationResult(**json.loads(response.text))
                
                # T050: Valida formatação e tenta enriquecer se insuficiente
                if result.is_valid_document and not _has_sufficient_formatting(result):
                    enriched = _try_enrich(model_name, source_text, result)
                    if enriched:
                        return enriched
                
                return result
                
            except APIError as e:
                last_error = e
                error_str = str(e)
                if "404" in error_str:
                    # Modelo indisponível, pula para o próximo modelo do array
                    continue
                if "429" in error_str or "503" in error_str:
                    # Sobrecarga, tenta o próximo modelo
                    continue
                # Outros erros da API (ex: 400 Bad Request) são permanentes
                raise PermanentGenerationError(error_str)
            except PermanentGenerationError:
                raise
            except Exception as e:
                raise PermanentGenerationError(str(e))
                
        # Se esgotou os modelos na rodada, faz backoff de 5s antes de tentar novamente
        time.sleep(5)
        
    raise TransientGenerationError(f"Falha após múltiplas tentativas com os modelos de fallback: {str(last_error)}")