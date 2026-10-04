import re

# Compila as regexes em nível de módulo (executado apenas uma vez no startup)
_TITLE_PATTERNS = [
    re.compile(r"^projeto\s+de\s+lei\b", re.IGNORECASE),
    re.compile(r"^plano\s+de\s+governo\b", re.IGNORECASE),
    re.compile(r"^proposta\s+de\s+emenda\b", re.IGNORECASE),
    re.compile(r"^medida\s+provisória\b", re.IGNORECASE),
    re.compile(r"^pec\b", re.IGNORECASE)
]

_USELESS_HEADER_PATTERNS = [
    re.compile(r"câmara\s+dos\s+deputados", re.IGNORECASE),
    re.compile(r"senado\s+federal", re.IGNORECASE),
    re.compile(r"^protocolo:", re.IGNORECASE),
    re.compile(r"gabinete\s+do", re.IGNORECASE),
    re.compile(r"eleições\s+20", re.IGNORECASE),
    re.compile(r"coligação", re.IGNORECASE),
    re.compile(r"^\d{2}/\d{2}/\d{4}$", re.IGNORECASE), # Apenas datas isoladas
]

def extract_intelligent_title(source_text: str) -> str:
    """
    Extrai o título do documento pulando cabeçalhos genéricos e sujeira comum.
    
    Tenta primeiro casar com as _TITLE_PATTERNS conhecidas. Se não encontrar,
    filtra cabeçalhos ignorados usando _USELESS_HEADER_PATTERNS e retorna
    a primeira linha que tenha um mínimo de conteúdo relevante (> 15 chars).
    """
    if not source_text or not source_text.strip():
        return "Sem título"

    lines = [line.strip() for line in source_text.split('\n') if line.strip()]

    # 1. Procura indicadores explícitos de título (PL, Plano de Governo, PEC, etc)
    for line in lines:
        if any(pattern.search(line) for pattern in _TITLE_PATTERNS):
            return line[:150]

    # 2. Fallback: ignora cabeçalhos inúteis e pega a primeira linha com sustância
    for line in lines:
        if any(pattern.search(line) for pattern in _USELESS_HEADER_PATTERNS):
            continue
        
        # Se for uma linha com tamanho razoável, assumimos que é o início do texto/título
        if len(line) > 15:
            return line[:150]

    # 3. Fallback absoluto
    return lines[0][:50] if lines else "Sem título"
