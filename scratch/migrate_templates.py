import os
import glob
import re

html_files = [
    './accounts/templates/registration/login.html',
    './accounts/templates/accounts/registrar.html',
    './bills/templates/bills/enviar.html',
    './bills/templates/bills/minhas_submissoes.html',
    './bills/templates/bills/minhas_submissoes_detail.html',
    './bills/templates/bills/curation_detail.html',
    './bills/templates/bills/curation_list.html',
    './panel/templates/panel/detail.html',
    './panel/templates/panel/original.html',
    './panel/templates/panel/sinalizar.html',
    './panel/templates/panel/sinalizar_sucesso.html'
]

pattern = re.compile(r'<!DOCTYPE html>.*?(?:</nav>|<h1>|<\?)\s*(.*)</body>.*?</html>', re.DOTALL | re.IGNORECASE)
nav_pattern = re.compile(r'<nav style="background-color: #f8f9fa.*?</nav>', re.DOTALL | re.IGNORECASE)

for filepath in html_files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r') as f:
        content = f.read()
    
    if '{% extends' in content:
        continue
        
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else 'Voto Claro'
    
    # remove doctype, head, body, nav
    content = re.sub(r'<!DOCTYPE html>.*?</head>\s*<body.*?>\s*', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(nav_pattern, '', content)
    content = re.sub(r'</body>\s*</html>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Trim whitespace
    content = content.strip()
    
    # Convert some specific tags to new CSS classes
    content = content.replace('<button type="submit">', '<button type="submit" class="btn btn-primary">')
    content = content.replace('<a href="', '<a href="') # Just ensuring a exists
    
    new_content = f"""{{% extends 'base.html' %}}

{{% block title %}}{title}{{% endblock %}}

{{% block content %}}
{content}
{{% endblock %}}
"""
    with open(filepath, 'w') as f:
        f.write(new_content)
        
print("Refactored all templates to extend base.html")
