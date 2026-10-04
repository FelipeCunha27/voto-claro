from django.test import TestCase
from panel.templatetags.markdown_filters import markdownify


class MarkdownifyNestedListTests(TestCase):
    """
    Testes para o filtro markdownify renderizar corretamente
    listas aninhadas (nested lists) e espaçamento entre seções.
    """

    def test_renders_simple_bullet_list(self):
        """
        Uma lista simples com '-' deve ser renderizada como <ul><li>.
        """
        text = "- Item 1\n- Item 2\n- Item 3"
        html = markdownify(text)
        self.assertIn("<ul>", html)
        self.assertIn("<li>Item 1</li>", html)
        self.assertIn("<li>Item 2</li>", html)
        self.assertIn("<li>Item 3</li>", html)

    def test_renders_nested_bullet_list(self):
        """
        Sub-bullets indentados devem gerar <ul> aninhados dentro de <li>.
        """
        text = "- Tópico principal\n  - Subtópico 1\n  - Subtópico 2\n- Outro tópico"
        html = markdownify(text)
        # Deve haver pelo menos 2 <ul> (o principal e o aninhado)
        self.assertGreaterEqual(html.count("<ul>"), 2,
            "Listas aninhadas devem gerar múltiplos <ul>.")
        self.assertIn("Subtópico 1", html)
        self.assertIn("Subtópico 2", html)

    def test_renders_deeply_nested_list(self):
        """
        Listas com 3 níveis de profundidade devem renderizar corretamente.
        """
        text = (
            "- Nível 1\n"
            "  - Nível 2\n"
            "    - Nível 3"
        )
        html = markdownify(text)
        self.assertGreaterEqual(html.count("<ul>"), 3,
            "Listas com 3 níveis devem gerar 3 <ul> aninhados.")
        self.assertIn("Nível 3", html)

    def test_renders_asterisk_bullets(self):
        """
        Listas com '*' devem ser renderizadas da mesma forma que '-'.
        """
        text = "* Item A\n* Item B\n* Item C"
        html = markdownify(text)
        self.assertIn("<ul>", html)
        self.assertIn("<li>Item A</li>", html)

    def test_renders_bold_inside_bullet_list(self):
        """
        Negrito (**texto**) dentro de bullet points deve virar <strong>.
        """
        text = "- **Educação:** Investimento em escolas\n- **Saúde:** Mais hospitais"
        html = markdownify(text)
        self.assertIn("<strong>Educação:</strong>", html)
        self.assertIn("<strong>Saúde:</strong>", html)
        self.assertIn("<li>", html)

    def test_preserves_blank_lines_as_paragraph_separation(self):
        """
        Linhas em branco entre seções de bullet points devem criar
        separação visual (listas separadas ou parágrafos).
        """
        text = (
            "- Seção 1 item 1\n"
            "- Seção 1 item 2\n"
            "\n"
            "- Seção 2 item 1\n"
            "- Seção 2 item 2"
        )
        html = markdownify(text)
        # Com linhas em branco, devem ser gerados 2 blocos <ul> separados
        self.assertGreaterEqual(html.count("<ul>"), 2,
            "Linhas em branco entre listas devem gerar blocos <ul> separados.")

    def test_renders_15_plus_bullet_points(self):
        """
        Uma lista longa com 15+ bullets deve renderizar todos os itens.
        """
        items = [f"- Item {i}" for i in range(1, 18)]
        text = "\n".join(items)
        html = markdownify(text)
        self.assertEqual(html.count("<li>"), 17,
            "Todos os 17 bullet points devem ser renderizados como <li>.")

    def test_mixed_nested_with_bold_and_blank_lines(self):
        """
        Cenário completo: hierarquia, negrito e separação por linhas em branco.
        Representa o formato esperado da saída da IA após T050.
        """
        text = (
            "- **Educação**\n"
            "  - Construção de 500 novas escolas\n"
            "  - Aumento do salário dos professores\n"
            "\n"
            "- **Saúde**\n"
            "  - Mais 200 UBS em regiões carentes\n"
            "  - Programa de vacinação ampliado\n"
            "\n"
            "- **Segurança**\n"
            "  - Policiamento comunitário\n"
            "  - Câmeras de vigilância"
        )
        html = markdownify(text)
        # Deve ter <strong> para os títulos de seção
        self.assertIn("<strong>Educação</strong>", html)
        self.assertIn("<strong>Saúde</strong>", html)
        self.assertIn("<strong>Segurança</strong>", html)
        # Deve ter sub-items renderizados
        self.assertIn("Construção de 500 novas escolas", html)
        self.assertIn("Policiamento comunitário", html)
        # Deve ter listas aninhadas
        self.assertGreaterEqual(html.count("<ul>"), 2,
            "O cenário misto deve gerar listas aninhadas.")

    def test_empty_text_returns_empty_string(self):
        """
        Texto vazio ou None deve retornar string vazia (regressão).
        """
        self.assertEqual(markdownify(""), "")
        self.assertEqual(markdownify(None), "")


class MarkdownifyScannabilityTests(TestCase):
    """
    T059: o filtro deve renderizar bem os elementos de escaneabilidade que a
    IA passa a gerar — subtítulos, negrito, listas numeradas e parágrafos
    curtos — inclusive nos padrões comuns em que a IA não deixa linha em
    branco entre um texto e a lista seguinte.
    """

    def test_renders_h3_and_h4_headings(self):
        text = "### Saúde\n\n#### Atenção básica\n\nMais postos nos bairros."
        html = markdownify(text)
        self.assertIn("<h3>Saúde</h3>", html)
        self.assertIn("<h4>Atenção básica</h4>", html)

    def test_renders_heading_immediately_followed_by_list(self):
        """Subtítulo seguido de lista sem linha em branco deve gerar <h3> + <ul>."""
        html = markdownify("### Saúde\n- Mais postos\n- Mais médicos")
        self.assertIn("<h3>Saúde</h3>", html)
        self.assertIn("<li>Mais postos</li>", html)

    def test_renders_numbered_list(self):
        html = markdownify("1. Cadastro\n2. Benefício\n3. Acompanhamento")
        self.assertIn("<ol>", html)
        self.assertEqual(html.count("<li>"), 3)

    def test_renders_list_immediately_after_paragraph(self):
        """
        Padrão comum da IA: uma frase introdutória seguida direto da lista,
        sem linha em branco. A lista deve virar <ul>, não texto corrido.
        """
        html = markdownify("O plano propõe três medidas:\n- Mais postos\n- Mais médicos\n- Menos filas")
        self.assertIn("<ul>", html)
        self.assertIn("<li>Mais postos</li>", html)
        self.assertIn("<li>Menos filas</li>", html)

    def test_renders_numbered_list_immediately_after_bold_label(self):
        """Rótulo em negrito seguido direto de lista numerada deve gerar <strong> + <ol>."""
        html = markdownify("**Etapas do programa:**\n1. Cadastro\n2. Benefício")
        self.assertIn("<strong>Etapas do programa:</strong>", html)
        self.assertIn("<ol>", html)
        self.assertIn("<li>Cadastro</li>", html)

    def test_renders_numbered_list_nested_under_bullet(self):
        """Lista numerada com 2 espaços sob um bullet deve gerar <ol> aninhado em <li>."""
        text = "- **Saúde**\n  1. Mais postos\n  2. Mais médicos\n- **Educação**"
        html = markdownify(text)
        self.assertIn("<ol>", html, "A lista numerada aninhada deve gerar <ol>.")
        self.assertIn("<li>Mais postos</li>", html)
        self.assertRegex(html, r"<li>\s*<strong>Saúde</strong>\s*<ol>",
            "O <ol> deve estar aninhado dentro do <li> de 'Saúde'.")

    def test_short_paragraphs_separated_by_blank_lines_render_as_separate_p(self):
        text = "Primeiro parágrafo curto.\n\nSegundo parágrafo curto."
        html = markdownify(text)
        self.assertEqual(html.count("<p>"), 2)

    def test_full_scannable_section(self):
        """Cenário completo esperado da IA após a T059."""
        text = (
            "### Saúde\n"
            "\n"
            "O plano quer **ampliar o atendimento**. A meta é reduzir filas.\n"
            "\n"
            "- **Postos:** 200 novas unidades\n"
            "- **Médicos:** contratação via concurso\n"
            "\n"
            "### Educação\n"
            "\n"
            "1. Escolas em tempo integral\n"
            "2. Reforma de prédios antigos\n"
        )
        html = markdownify(text)
        self.assertIn("<h3>Saúde</h3>", html)
        self.assertIn("<h3>Educação</h3>", html)
        self.assertIn("<strong>ampliar o atendimento</strong>", html)
        self.assertIn("<ul>", html)
        self.assertIn("<ol>", html)
        self.assertIn("<li>Escolas em tempo integral</li>", html)
