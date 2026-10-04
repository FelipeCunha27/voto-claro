from django.test import TestCase
from bills.services.title_extraction import extract_intelligent_title

class TitleExtractionTests(TestCase):
    """
    Testes para a extração inteligente do título (T058).
    Garante que a heurística ignore cabeçalhos genéricos e extraia o título principal.
    """

    def test_extracts_pl_title_skipping_protocol_and_headers(self):
        """
        Deve ignorar cabeçalhos como 'CÂMARA DOS DEPUTADOS' e 'Protocolo'
        e capturar o real título do projeto.
        """
        source_text = (
            "CÂMARA DOS DEPUTADOS\n"
            "GABINETE DO DEPUTADO JOÃO\n"
            "PROTOCOLO: 2024-001\n"
            "\n"
            "PROJETO DE LEI Nº 123, DE 2024\n"
            "\n"
            "Dispõe sobre a mobilidade urbana e dá outras providências.\n"
        )
        title = extract_intelligent_title(source_text)
        self.assertEqual(title, "PROJETO DE LEI Nº 123, DE 2024")

    def test_extracts_government_plan_skipping_cover(self):
        """
        Deve identificar o plano de governo pulando lixo do PDF.
        """
        source_text = (
            "Eleições 2024\n"
            "Coligação Unidos por São Paulo\n"
            "\n"
            "PLANO DE GOVERNO - SÃO PAULO DO FUTURO\n"
            "\n"
            "Introdução:\n"
            "Este plano visa modernizar a cidade..."
        )
        title = extract_intelligent_title(source_text)
        self.assertEqual(title, "PLANO DE GOVERNO - SÃO PAULO DO FUTURO")

    def test_fallback_to_first_meaningful_sentence(self):
        """
        Se não houver padrão claro de PL ou Plano, pega a primeira
        frase/linha útil, sem quebrar palavras no meio,
        limitando o tamanho mas de forma inteligente.
        """
        source_text = (
            "Neste documento apresentamos as bases para a nova "
            "regulamentação das inteligências artificiais no Brasil, "
            "com foco em transparência e auditoria de algoritmos.\n"
            "Art. 1..."
        )
        title = extract_intelligent_title(source_text)
        # Espera pegar o começo do parágrafo, ou a primeira frase com sentido
        self.assertTrue(title.startswith("Neste documento apresentamos as bases"))
        self.assertTrue(len(title) <= 150) # O título deve ser contido

    def test_handles_empty_or_too_short_text(self):
        """
        Deve lidar graciosamente com textos muito curtos ou nulos.
        """
        self.assertEqual(extract_intelligent_title("Oi"), "Oi")
        self.assertEqual(extract_intelligent_title("   \n   \n"), "Sem título")
        self.assertEqual(extract_intelligent_title(""), "Sem título")
        self.assertEqual(extract_intelligent_title(None), "Sem título")
