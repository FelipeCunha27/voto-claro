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
        
    prompt = f"""
    Você é um tradutor especializado em 'Linguagem Simples' (Plain Language) focado em cidadania.
    Sua missão é pegar textos políticos complexos e traduzi-los para a população em geral.
    
    REGRAS DE TOM E ESTILO OBRIGATÓRIAS:
    1. Escreva como se estivesse explicando para um jovem de 14 anos de forma muito didática.
    2. NUNCA use palavras difíceis, jargões jurídicos ou econômicos (como 'desindexar', 'pacto federativo', 'direito penal do inimigo') sem explicar o que isso significa na prática.
    3. Use frases curtas e diretas. Seja objetivo.
    4. O tom deve ser neutro e acessível, fugindo completamente da linguagem formal de advogados ou políticos.
    
    Analise o texto a seguir. 
    Se o texto for um documento legislativo (projeto de lei, PEC) OU um plano de governo/projeto político de um candidato, marque 'is_legislative_text' como true.
    Se não tiver nada a ver com o mundo político/legislativo, marque 'is_legislative_text' como false e retorne o resto vazio.
    
    Para planos de governo de candidatos:
    - No campo 'practical_changes', foque nas promessas que afetam a rotina das pessoas, explicando de forma muito simples.
    - No campo 'who_is_affected', cite grupos reais de pessoas.
    
    Texto Original:
    {source_text}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
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
        if "429" in str(e) or "503" in str(e):
            raise TransientGenerationError(str(e))
        raise PermanentGenerationError(str(e))
    except PermanentGenerationError:
        raise
    except Exception as e:
        raise PermanentGenerationError(str(e))
