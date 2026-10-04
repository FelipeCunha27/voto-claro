from unittest.mock import patch
from django.test import TestCase
from bills.models import Submission
from bills.tasks import generate_accessible_version_task
from django.contrib.auth import get_user_model
from bills.adapters.gemini_adapter import GenerationResult

User = get_user_model()

class GenerateAccessibleVersionTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.submission = Submission.objects.create(
            submitter=self.user,
            title="Receita de bolo",
            source_text="Bata 2 ovos com açúcar...",
            input_kind=Submission.InputKind.PASTED,
            content_hash="dummyhash",
            status=Submission.Status.RECEIVED
        )

    @patch('bills.tasks.generate_accessible_version')
    def test_rejection_for_invalid_document(self, mock_generate):
        # T045: Mockamos um resultado de "is_valid_document=False"
        mock_result = GenerationResult(
            summary="",
            who_is_affected="",
            practical_changes="",
            points_of_attention="",
            is_valid_document=False,
            suggested_theme=None
        )
        mock_generate.return_value = mock_result

        # Quando chamamos a task, o resultado deve ser REJECTED em vez de um erro FAILED
        # Dependendo do uso do django_tasks, talvez precisemos invocar apenas a função interna
        # se generate_accessible_version_task for um objeto.
        if hasattr(generate_accessible_version_task, 'call'):
            generate_accessible_version_task.call(self.submission.id)
        else:
            generate_accessible_version_task.func(self.submission.id)
        
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, Submission.Status.REJECTED)
        self.assertEqual(self.submission.rejection_reason, "O texto enviado não parece ser um documento político válido para análise.")

    @patch('bills.tasks.generate_accessible_version')
    def test_official_title_updates_submission_and_bill(self, mock_generate):
        # T058: A IA extrai o título inteligente e a task atualiza a model
        mock_result = GenerationResult(
            official_title="Plano de Governo Oficial - Candidato X",
            summary="Resumo",
            who_is_affected="Povo",
            practical_changes="Mudanças",
            points_of_attention="Atenção",
            is_valid_document=True,
            suggested_theme="Desenvolvimento"
        )
        mock_generate.return_value = mock_result

        # A submissão começa com um título inicial burro
        self.submission.title = "Apenas 50 caracteres"
        self.submission.save()

        if hasattr(generate_accessible_version_task, 'call'):
            generate_accessible_version_task.call(self.submission.id)
        else:
            generate_accessible_version_task.func(self.submission.id)
        
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, Submission.Status.GENERATED)
        self.assertEqual(self.submission.title, "Plano de Governo Oficial - Candidato X")
        
        # Garante que o Bill criado também herdou esse novo título
        self.assertIsNotNone(self.submission.bill)
        self.assertEqual(self.submission.bill.title, "Plano de Governo Oficial - Candidato X")
