from unittest.mock import patch, Mock
from django.test import TestCase
import openai

from bills.adapters.openai_adapter import (
    generate_accessible_version,
    TransientGenerationError,
    PermanentGenerationError,
    GenerationResult
)

class OpenAIAdapterContractTests(TestCase):
    """
    Testes de contrato para o adaptador da OpenAI (T009).
    Verificam os cenários de sucesso, falhas transientes, 
    violação de schema/refusal e texto não legislativo.
    """

    def setUp(self):
        self.themes = ["Health", "Education"]
        self.valid_text = "Projeto de Lei n. 123..."

    @patch('bills.adapters.openai_adapter.client.beta.chat.completions.parse')
    def test_valid_generation(self, mock_parse):
        """Deve retornar um GenerationResult com os dados parseados corretamente."""
        mock_message = Mock()
        mock_message.refusal = None
        mock_message.parsed = GenerationResult(
            summary="A summary",
            who_is_affected="People",
            practical_changes="Changes",
            points_of_attention="Points",
            is_legislative_text=True,
            suggested_theme="Health"
        )
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_parse.return_value = mock_response

        result = generate_accessible_version(self.valid_text, self.themes)

        self.assertTrue(result.is_legislative_text)
        self.assertEqual(result.summary, "A summary")
        mock_parse.assert_called_once()

    @patch('bills.adapters.openai_adapter.client.beta.chat.completions.parse')
    def test_transient_errors(self, mock_parse):
        """Deve lançar TransientGenerationError em caso de erro de conexão ou rate limit."""
        mock_parse.side_effect = openai.APIConnectionError(request=Mock())

        with self.assertRaises(TransientGenerationError):
            generate_accessible_version(self.valid_text, self.themes)

    @patch('bills.adapters.openai_adapter.client.beta.chat.completions.parse')
    def test_schema_violation_or_refusal(self, mock_parse):
        """Deve lançar PermanentGenerationError se o modelo se recusar a responder (refusal)."""
        mock_message = Mock()
        mock_message.parsed = None
        mock_message.refusal = "I cannot fulfill this request."
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_parse.return_value = mock_response

        with self.assertRaisesMessage(PermanentGenerationError, "Schema violation or refusal"):
            generate_accessible_version(self.valid_text, self.themes)

    @patch('bills.adapters.openai_adapter.client.beta.chat.completions.parse')
    def test_is_legislative_text_false(self, mock_parse):
        """Deve lançar PermanentGenerationError se não for um texto legislativo."""
        mock_message = Mock()
        mock_message.refusal = None
        mock_message.parsed = GenerationResult(
            summary="",
            who_is_affected="",
            practical_changes="",
            points_of_attention="",
            is_legislative_text=False,
            suggested_theme=None
        )
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_parse.return_value = mock_response

        with self.assertRaisesMessage(PermanentGenerationError, "Not a legislative text"):
            generate_accessible_version("Receita de bolo", self.themes)
