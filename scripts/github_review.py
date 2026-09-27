import os
from google import genai

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

try:
    with open('pr_diff.txt', 'r') as f:
        diff_content = f.read()
    with open('GEMINI.md', 'r') as f:
        rules_content = f.read()
except Exception as e:
    diff_content = f'Erro: {e}'
    rules_content = ''

prompt = f'''Aja como o Tech Lead do Voto Claro.
Analise o Pull Request atual.

REGRAS DO PROJETO:
{rules_content}

CÓDIGO MODIFICADO (DIFF):
{diff_content}

SUAS TAREFAS:
1. Code Review: Avalie o código contra as regras (TDD, Idioma, Segurança). Reprove se não houver testes para novas funcionalidades.
2. Geração de Changelog: Crie uma seção chamada "# 📝 Changelog Gerado" detalhando tecnicamente as alterações prontas para ir para a branch main.
'''

models_to_try = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash"]
response = None

for model_name in models_to_try:
    print(f"Tentando usar o modelo: {model_name}...")
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        print(f"Sucesso com o modelo: {model_name}!")
        break
    except Exception as e:
        print(f"Falha ao usar {model_name}: {e}")
        continue

if response:
    report_text = response.text
else:
    report_text = "❌ **Tech Lead Offline:** Todos os modelos da API do Gemini (3.5, 3.6 e 3.8) estão congestionados (Erro 503). O merge deste PR precisará ser revisado manualmente ou retentado mais tarde."

with open('review_report.md', 'w') as f:
    f.write(report_text)
