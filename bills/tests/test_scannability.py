"""
T059 — Escaneabilidade e legibilidade dos campos gerados pela IA.

Fase RED do TDD: estes testes descrevem o comportamento esperado do
`gemini_adapter` após a T059:

- A regra antiga de "no mínimo 15 bullet points" deixa de existir.
- Os 4 campos (`summary`, `who_is_affected`, `practical_changes` e
  `points_of_attention`) devem ser escaneáveis: subtítulos, negrito,
  parágrafos curtos (≤ 3 frases), listas e frases diretas.
- O conteúdo continua cobrindo TODOS os tópicos do documento.
- O enrichment (retry) passa a ser disparado por falta de escaneabilidade,
  e não mais por contagem de bullets.
"""
import json
import re
from unittest.mock import Mock, patch

from django.test import TestCase

from bills.adapters.gemini_adapter import generate_accessible_version


ACCESSIBLE_FIELDS = ('summary', 'who_is_affected', 'practical_changes', 'points_of_attention')


def _get_validator():
    """Importa o novo validador de forma tardia.

    Assim, enquanto a função não existir (fase Red), apenas os testes que a
    usam falham — o restante do módulo continua sendo executado.
    """
    from bills.adapters.gemini_adapter import validate_scannable_formatting
    return validate_scannable_formatting


def _scannable_field(label: str) -> str:
    """Campo escaneável: subtítulos, negrito, parágrafos curtos e PROSA (sem bullets)."""
    return (
        f"### {label}: visão geral\n"
        "\n"
        f"Aqui vai o essencial sobre **{label.lower()}**. A ideia é explicar de um jeito simples.\n"
        "\n"
        f"### {label}: principais pontos\n"
        "\n"
        "**Saúde:** Mais postos de atendimento nos bairros.\n"
        "\n"
        "**Educação:** Escolas funcionando em tempo integral.\n"
        "\n"
        "**Segurança:** Policiamento mais próximo da comunidade.\n"
    )


def _wall_of_text_field() -> str:
    """Campo NÃO escaneável: um bloco único, sem subtítulos nem negrito."""
    return (
        "O plano trata de saúde. Também fala de educação. Fala ainda de segurança. "
        "Cita a infraestrutura das cidades. Comenta sobre meio ambiente. "
        "E por fim menciona a economia."
    )


def _response_payload(**overrides) -> dict:
    payload = {
        "official_title": "Plano de Governo - Candidato Teste",
        "summary": _scannable_field("Resumo"),
        "who_is_affected": _scannable_field("Quem é afetado"),
        "practical_changes": _scannable_field("O que muda"),
        "points_of_attention": _scannable_field("Pontos de atenção"),
        "is_valid_document": True,
        "suggested_theme": "Saúde",
    }
    payload.update(overrides)
    return payload


def _mock_response(payload: dict) -> Mock:
    response = Mock()
    response.text = json.dumps(payload)
    return response


class ScannableFormattingValidatorTests(TestCase):
    """Valida a nova função `validate_scannable_formatting(text) -> bool`."""

    def test_accepts_spaced_prose(self):
        """Aceita formatação em parágrafos espaçados com rótulos em negrito, sem bullets."""
        validate = _get_validator()
        self.assertTrue(validate(_scannable_field("Resumo")))

    def test_rejects_traditional_lists(self):
        """Listas tradicionais com marcadores (-, *) não são mais permitidas."""
        validate = _get_validator()
        text = (
            "### Como vai funcionar\n"
            "\n"
            "O programa terá **três etapas**. Cada uma dura um ano.\n"
            "\n"
            "- Cadastro das famílias\n"
            "- Liberação do benefício\n"
            "- Acompanhamento dos resultados\n"
        )
        self.assertFalse(validate(text), "Não deve aceitar marcadores de lista.")

    def test_rejects_text_without_headings(self):
        """Sem nenhum subtítulo (### ou ####), o texto não é escaneável."""
        validate = _get_validator()
        text = (
            "O plano fala de **saúde**. A ideia é ampliar o atendimento.\n"
            "\n"
            "- Mais postos de saúde\n"
            "- Mais médicos\n"
        )
        self.assertFalse(validate(text))

    def test_rejects_text_without_bold(self):
        """Sem negrito para destacar termos-chave, o texto não é escaneável."""
        validate = _get_validator()
        text = (
            "### Saúde\n"
            "\n"
            "O plano fala de saúde. A ideia é ampliar o atendimento.\n"
            "\n"
            "- Mais postos de saúde\n"
            "- Mais médicos\n"
        )
        self.assertFalse(validate(text))

    def test_rejects_paragraph_longer_than_three_sentences(self):
        """Parágrafos de prosa com mais de 3 frases quebram a escaneabilidade."""
        validate = _get_validator()
        text = (
            "### Saúde\n"
            "\n"
            "O plano fala de **saúde**. Quer mais postos. Quer mais médicos. "
            "Quer mais remédios. Quer filas menores.\n"
        )
        self.assertFalse(validate(text))

    def test_accepts_paragraph_with_exactly_three_sentences(self):
        """O limite é inclusivo: 3 frases por parágrafo ainda é aceito."""
        validate = _get_validator()
        text = (
            "### Saúde\n"
            "\n"
            "O plano fala de **saúde**. Quer mais postos. Quer mais médicos.\n"
        )
        self.assertTrue(validate(text))

    def test_rejects_wall_of_text(self):
        validate = _get_validator()
        self.assertFalse(validate(_wall_of_text_field()))

    def test_rejects_empty_or_none(self):
        validate = _get_validator()
        self.assertFalse(validate(""))
        self.assertFalse(validate(None))


@patch('bills.adapters.gemini_adapter.client')
class ScannabilityPromptTests(TestCase):
    """O prompt efetivamente enviado ao Gemini deve conter as regras da T059."""

    def _sent_prompt(self, mock_client) -> str:
        mock_client.models.generate_content.return_value = _mock_response(_response_payload())
        generate_accessible_version("Plano de governo com vários eixos.", [])
        first_call = mock_client.models.generate_content.call_args_list[0]
        return first_call.kwargs['contents']

    def test_prompt_no_longer_requires_minimum_of_15_bullets(self, mock_client):
        prompt = self._sent_prompt(mock_client)
        self.assertNotRegex(prompt, r"(?i)m[íi]nimo\s+(de\s+)?15")
        self.assertNotRegex(prompt, r"(?i)15\s+bullet")

    def test_prompt_requires_scannability_for_all_fields(self, mock_client):
        prompt = self._sent_prompt(mock_client).lower()
        self.assertIn("escaneab", prompt, "O prompt deve citar explicitamente a escaneabilidade.")
        self.assertIn("todos os campos", prompt,
            "As regras de escaneabilidade devem valer para todos os campos.")
        for field in ACCESSIBLE_FIELDS:
            self.assertIn(field, prompt)

    def test_prompt_requires_headings(self, mock_client):
        prompt = self._sent_prompt(mock_client)
        self.assertIn("###", prompt, "O prompt deve exigir subtítulos em Markdown (###/####).")
        self.assertIn("subtítulo", prompt.lower())

    def test_prompt_requires_bold_for_key_terms(self, mock_client):
        prompt = self._sent_prompt(mock_client).lower()
        self.assertIn("negrito", prompt)

    def test_prompt_requires_short_paragraphs(self, mock_client):
        prompt = self._sent_prompt(mock_client)
        self.assertRegex(prompt, r"2\s*(a|-|–)\s*3\s+frases",
            "O prompt deve limitar os parágrafos a 2–3 frases.")

    def test_prompt_forbids_bullet_points(self, mock_client):
        prompt = self._sent_prompt(mock_client).lower()
        self.assertRegex(prompt, r"n[ãa]o use (listas|bullet points|marcadores)", "O prompt deve proibir explicitamente o uso de bullet points.")

    def test_prompt_requires_direct_sentences_with_essential_info_first(self, mock_client):
        prompt = self._sent_prompt(mock_client).lower()
        self.assertRegex(prompt, r"informaç(ão|ões) essencia(l|is)")

    def test_prompt_keeps_conversational_tone(self, mock_client):
        """Regressão: tom conversacional, como se explicasse a um amigo."""
        prompt = self._sent_prompt(mock_client).lower()
        self.assertIn("amigo", prompt)

    def test_prompt_requires_full_topic_coverage(self, mock_client):
        """Sem o mínimo de 15, a cobertura de TODOS os tópicos continua obrigatória."""
        prompt = self._sent_prompt(mock_client).lower()
        self.assertIn("todos os tópicos", prompt)

    def test_prompt_keeps_neutral_tone_for_points_of_attention(self, mock_client):
        """Regressão: points_of_attention continua com tom neutro."""
        prompt = self._sent_prompt(mock_client).lower()
        self.assertIn("neutro", prompt)


@patch('bills.adapters.gemini_adapter.client')
class ScannabilityEnrichmentTests(TestCase):
    """O enrichment (retry) passa a ser guiado pela escaneabilidade."""

    def test_scannable_result_with_few_bullets_does_not_trigger_enrichment(self, mock_client):
        """Um resultado escaneável com só 3 bullets por campo NÃO deve gerar retry."""
        mock_client.models.generate_content.return_value = _mock_response(_response_payload())

        result = generate_accessible_version("Plano de governo.", [])

        self.assertEqual(mock_client.models.generate_content.call_count, 1,
            "Resultado escaneável não deve disparar o enrichment.")
        self.assertEqual(result.summary, _scannable_field("Resumo"))

    def test_non_scannable_result_triggers_enrichment(self, mock_client):
        """Campos em 'parede de texto' devem disparar o enrichment."""
        wall = _wall_of_text_field()
        poor = _response_payload(
            summary=wall, who_is_affected=wall,
            practical_changes=wall, points_of_attention=wall,
        )
        enriched = _response_payload()
        mock_client.models.generate_content.side_effect = [
            _mock_response(poor), _mock_response(enriched),
        ]

        result = generate_accessible_version("Plano de governo.", [])

        self.assertEqual(mock_client.models.generate_content.call_count, 2)
        self.assertEqual(result.summary, enriched["summary"])

    def test_single_non_scannable_field_triggers_enrichment(self, mock_client):
        """Basta UM dos 4 campos fora do padrão para disparar o enrichment."""
        for field in ACCESSIBLE_FIELDS:
            with self.subTest(field=field):
                mock_client.reset_mock()
                poor = _response_payload(**{field: _wall_of_text_field()})
                mock_client.models.generate_content.side_effect = [
                    _mock_response(poor), _mock_response(_response_payload()),
                ]

                generate_accessible_version("Plano de governo.", [])

                self.assertEqual(mock_client.models.generate_content.call_count, 2,
                    f"O campo '{field}' fora do padrão deveria disparar o enrichment.")

    def test_enrichment_prompt_requires_scannability_without_15_bullets(self, mock_client):
        wall = _wall_of_text_field()
        poor = _response_payload(summary=wall)
        mock_client.models.generate_content.side_effect = [
            _mock_response(poor), _mock_response(_response_payload()),
        ]

        generate_accessible_version("Plano de governo.", [])

        enrichment_prompt = mock_client.models.generate_content.call_args_list[1].kwargs['contents']
        self.assertNotRegex(enrichment_prompt, r"(?i)m[íi]nimo\s+(de\s+)?15")
        self.assertNotRegex(enrichment_prompt, r"(?i)15\s+bullet")
        self.assertIn("###", enrichment_prompt)
        self.assertIn("negrito", enrichment_prompt.lower())
        self.assertRegex(enrichment_prompt, r"2\s*(a|-|–)\s*3\s+frases")
        self.assertIn("todos os tópicos", enrichment_prompt.lower(),
            "O enrichment também deve exigir cobertura completa dos tópicos.")

    def test_invalid_document_does_not_trigger_enrichment(self, mock_client):
        """Regressão: documentos inválidos nunca disparam o enrichment."""
        invalid = _response_payload(
            summary="", who_is_affected="", practical_changes="",
            points_of_attention="", is_valid_document=False, suggested_theme=None,
        )
        mock_client.models.generate_content.return_value = _mock_response(invalid)

        result = generate_accessible_version("Receita de bolo.", [])

        self.assertFalse(result.is_valid_document)
        self.assertEqual(mock_client.models.generate_content.call_count, 1)
