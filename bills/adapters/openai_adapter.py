import os

import openai
from pydantic import BaseModel


class GenerationResult(BaseModel):
    summary: str
    who_is_affected: str
    practical_changes: str
    points_of_attention: str
    is_legislative_text: bool
    suggested_theme: str | None


class TransientGenerationError(Exception):
    """Erro transiente na comunicação com a OpenAI (ex: timeout, limit rate)."""
    pass


class PermanentGenerationError(Exception):
    """Erro permanente ou violação de contrato com a OpenAI."""
    pass


try:
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy"))
except Exception:
    client = None


def generate_accessible_version(source_text: str, themes: list[str]) -> GenerationResult:
    """
    Gera uma versão acessível do texto legislativo utilizando a API da OpenAI.
    """
    if not client:
        raise PermanentGenerationError("API key missing or invalid")
        
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant. Use themes: {themes}"},
                {"role": "user", "content": source_text}
            ],
            response_format=GenerationResult,
            timeout=30,
        )
        
        message = response.choices[0].message
        
        if getattr(message, "refusal", None) or getattr(message, "parsed", None) is None:
            raise PermanentGenerationError("Schema violation or refusal")
            
        if not message.parsed.is_legislative_text:
            raise PermanentGenerationError("Not a legislative text")
            
        return message.parsed
        
    except (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError) as e:
        raise TransientGenerationError(str(e))
    except PermanentGenerationError:
        raise
    except Exception as e:
        raise PermanentGenerationError(str(e))
