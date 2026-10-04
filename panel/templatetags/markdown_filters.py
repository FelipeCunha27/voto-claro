import re

from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


def _normalize_list_indentation(text: str) -> str:
    """Normaliza indentação de listas de 2 espaços para 4 espaços por nível.

    A biblioteca Python `markdown` exige 4 espaços por nível de aninhamento.
    A IA (e a escrita humana comum) tipicamente usa 2 espaços. Esta função
    detecta linhas que começam com bullet points indentados e dobra sua
    indentação para compatibilidade.
    """
    lines = text.split('\n')
    result = []
    for line in lines:
        match = re.match(r'^( +)([-*]|\d+\.)', line)
        if match:
            spaces = match.group(1)
            # Dobra a indentação (2 espaços → 4, 4 → 8, etc.)
            new_indent = ' ' * (len(spaces) * 2)
            result.append(new_indent + line[len(spaces):])
        else:
            result.append(line)
    return '\n'.join(result)


def _ensure_blank_lines_before_lists(text: str) -> str:
    """Garante que listas (numeradas ou não) sejam precedidas por uma linha em branco.
    
    A biblioteca python `markdown` não renderiza corretamente listas que aparecem
    imediatamente após um parágrafo de texto se não houver uma linha em branco.
    """
    lines = text.split('\n')
    out = []
    
    list_marker_re = re.compile(r'^\s*([-*]|\d+\.)\s+')
    
    for i, line in enumerate(lines):
        if i > 0:
            prev = lines[i-1].strip()
            if list_marker_re.match(line):
                # Se a linha anterior não for vazia, título ou lista, adiciona linha em branco
                if prev != '' and not prev.startswith('#') and not list_marker_re.match(lines[i-1]):
                    out.append('')
        out.append(line)
        
    return '\n'.join(out)


@register.filter(name='markdownify')
def markdownify(text):
    """Renderiza Markdown seguro dividindo o texto em blocos.
    
    A divisão por linhas em branco garante que cada seção gere seu
    próprio elemento <ul> de forma independente, permitindo separação visual
    entre os tópicos.
    """
    if not text:
        return ""
        
    text = _normalize_list_indentation(text)
    text = _ensure_blank_lines_before_lists(text)
    
    blocks = [block.strip() for block in text.split('\n\n') if block.strip()]
    rendered_blocks = [markdown.markdown(block) for block in blocks]
    
    return mark_safe('\n'.join(rendered_blocks))
