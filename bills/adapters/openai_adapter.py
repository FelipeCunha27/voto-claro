from pydantic import BaseModel
import openai
import os
from django.conf import settings

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

try:
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy"))
except Exception:
    client = None

def generate_accessible_version(source_text: str, themes: list[str]) -> GenerationResult:
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
        return response.parsed
    except openai.RateLimitError as e:
        raise TransientGenerationError(str(e))
    except openai.APIConnectionError as e:
        raise TransientGenerationError(str(e))
    except openai.InternalServerError as e:
        raise TransientGenerationError(str(e))
    except openai.LengthError as e:
        raise PermanentGenerationError(str(e))
    except openai.BadRequestError as e:
        raise PermanentGenerationError(str(e))
    except Exception as e:
        raise PermanentGenerationError(str(e))
