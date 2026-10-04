import json
import inspect
from unittest.mock import patch, Mock
from django.test import TestCase

from bills.adapters.gemini_adapter import (
    generate_accessible_version,
    TransientGenerationError,
    PermanentGenerationError,
    GenerationResult
)

class GeminiAdapterContractTests(TestCase):
    def setUp(self):
        self.themes = ["Health", "Education"]
        self.valid_text = "Projeto de Lei n. 123..."

    @patch('bills.adapters.gemini_adapter.client.models.generate_content')
    def test_valid_generation(self, mock_generate):
        mock_response = Mock()
        mock_response.text = '{"official_title": "Plano de Governo Teste", "summary": "A summary", "who_is_affected": "People", "practical_changes": "Changes", "points_of_attention": "Points", "is_valid_document": true, "suggested_theme": "Health"}'
        mock_generate.return_value = mock_response

        result = generate_accessible_version(self.valid_text, self.themes)
        self.assertTrue(result.is_valid_document)
        self.assertEqual(result.summary, "A summary")
        self.assertEqual(result.official_title, "Plano de Governo Teste")

    @patch('bills.adapters.gemini_adapter.client.models.generate_content')
    def test_is_valid_document_false(self, mock_generate):
        mock_response = Mock()
        mock_response.text = '{"official_title": "", "summary": "", "who_is_affected": "", "practical_changes": "", "points_of_attention": "", "is_valid_document": false, "suggested_theme": null}'
        mock_generate.return_value = mock_response

        # Em vez de jogar PermanentGenerationError, o adapter deve retornar o resultado normalmente
        result = generate_accessible_version("Receita de bolo", self.themes)
        self.assertFalse(result.is_valid_document)
        self.assertEqual(result.official_title, "")

    @patch('bills.adapters.gemini_adapter.client.models.generate_content')
    def test_transient_error(self, mock_generate):
        from google.genai.errors import APIError
        # Mocking an APIError requires passing a message or similar, we can mock the exception string
        class MockAPIError(APIError):
            def __init__(self, message):
                self.message = message
            def __str__(self):
                return self.message

        mock_generate.side_effect = MockAPIError("429 Too Many Requests")

        with self.assertRaisesMessage(TransientGenerationError, "429"):
            generate_accessible_version(self.valid_text, self.themes)


class BulletPointFormattingTests(TestCase):
    """
    Testes para validar que o adapter exige hierarquia visual e espaçamento
    entre seções.

    T059: os testes da antiga regra de "no mínimo 15 bullet points" (T056)
    foram removidos — a regra foi substituída pelas exigências de
    escaneabilidade e cobertura completa (ver `test_scannability.py`).
    """

    def test_prompt_requires_hierarchy_with_indented_sub_bullets(self):
        """
        O prompt deve instruir o uso de hierarquia visual com sub-bullets
        indentados (ex: '  -') para subtópicos e categorias.
        """
        source = inspect.getsource(generate_accessible_version)
        has_hierarchy_instruction = any(term in source.lower() for term in [
            "sub-bullet", "indentação", "hierarquia", "sub-item", "indented"
        ])
        self.assertTrue(has_hierarchy_instruction, "O prompt deve instruir o uso de hierarquia visual.")

    def test_prompt_requires_blank_lines_between_sections(self):
        """
        O prompt deve exigir linha em branco entre cada tópico/seção
        para melhorar a legibilidade.
        """
        source = inspect.getsource(generate_accessible_version)
        has_blank_line_instruction = any(term in source.lower() for term in [
            "linha em branco", "blank line", "linha vazia"
        ])
        self.assertTrue(has_blank_line_instruction, "O prompt deve exigir linhas em branco entre tópicos/seções.")
