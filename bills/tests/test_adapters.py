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
        mock_response.text = '{"summary": "A summary", "who_is_affected": "People", "practical_changes": "Changes", "points_of_attention": "Points", "is_legislative_text": true, "suggested_theme": "Health"}'
        mock_generate.return_value = mock_response

        result = generate_accessible_version(self.valid_text, self.themes)
        self.assertTrue(result.is_legislative_text)
        self.assertEqual(result.summary, "A summary")
        mock_generate.assert_called_once()

    @patch('bills.adapters.gemini_adapter.client.models.generate_content')
    def test_is_legislative_text_false(self, mock_generate):
        mock_response = Mock()
        mock_response.text = '{"summary": "", "who_is_affected": "", "practical_changes": "", "points_of_attention": "", "is_legislative_text": false, "suggested_theme": null}'
        mock_generate.return_value = mock_response

        with self.assertRaisesMessage(PermanentGenerationError, "O documento enviado não é um texto legislativo válido."):
            generate_accessible_version("Receita de bolo", self.themes)
