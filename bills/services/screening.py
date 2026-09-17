import hashlib
import re

def normalize_text(text: str) -> str:
    # Remove extra spaces, newlines, and lowercase it
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def compute_content_hash(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def is_valid_size(text: str) -> bool:
    usable_chars = len(text.strip())
    return 500 <= usable_chars <= 50000

# Language checking could be done with a library, but the prompt says 
# "screening decision" includes size, etc. LLM decides if it's legislative text.
