"""
T059 — Teste de integração (fase RED).

Jornada completa: o cidadão envia um plano de governo, a task de geração
chama o Gemini (mockado), a versão acessível é salva e a página pública de
detalhe exibe os 4 campos de forma escaneável.

Um resultado escaneável (agora em prosa espaçada, sem bullets tradicionais) deve
ser aceito de primeira, sem disparar o enrichment.
"""
import json
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from bills.models import Submission
from bills.tasks import generate_accessible_version_task

User = get_user_model()


def _scannable(label: str) -> str:
    return (
        f"### {label}: o essencial\n"
        "\n"
        f"Este é o ponto central de **{label.lower()}**. Dá para entender rapidinho.\n"
        "\n"
        f"#### {label}: por eixo\n"
        "\n"
        "**Saúde:** Mais postos nos bairros.\n"
        "\n"
        "**Educação:** Escolas em tempo integral.\n"
    )


LABELS = {
    "summary": "Resumo",
    "who_is_affected": "Afetados",
    "practical_changes": "Mudanças",
    "points_of_attention": "Atenção",
}


def _run_task(submission_id):
    if hasattr(generate_accessible_version_task, 'call'):
        generate_accessible_version_task.call(submission_id)
    else:
        generate_accessible_version_task(submission_id)


class ScannableGenerationIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cidadao", password="password")
        self.submission = Submission.objects.create(
            submitter=self.user,
            title="Plano de Governo",
            source_text="Plano de governo com eixos de saúde e educação.",
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash-t059",
            status=Submission.Status.RECEIVED,
        )

    @patch('bills.adapters.gemini_adapter.client')
    def test_scannable_generation_is_published_without_enrichment(self, mock_client):
        payload = {
            "official_title": "Plano de Governo - Candidata Teste",
            **{field: _scannable(label) for field, label in LABELS.items()},
            "is_valid_document": True,
            "suggested_theme": "Saúde",
        }
        response_mock = Mock()
        response_mock.text = json.dumps(payload)
        mock_client.models.generate_content.return_value = response_mock

        _run_task(self.submission.id)

        # 1) Sem a regra dos 15 bullets, o resultado escaneável é aceito de primeira
        self.assertEqual(mock_client.models.generate_content.call_count, 1,
            "Um resultado escaneável não deve disparar o enrichment.")

        # 2) A submissão é publicada com os 4 campos intactos
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, Submission.Status.GENERATED)
        version = self.submission.bill.current_version
        for field, label in LABELS.items():
            self.assertEqual(getattr(version, field), _scannable(label))

        # 3) A página pública exibe subtítulos, negrito e listas nos 4 campos
        page = self.client.get(f"/projeto/{self.submission.bill.slug}/")
        self.assertEqual(page.status_code, 200)
        for label in LABELS.values():
            with self.subTest(section=label):
                self.assertContains(page, f"<h3>{label}: o essencial</h3>", html=False)
                self.assertContains(page, f"<h4>{label}: por eixo</h4>", html=False)
                self.assertContains(page, f"<strong>{label.lower()}</strong>", html=False)
        self.assertContains(page, "<strong>Saúde:</strong>", count=4, html=False)
