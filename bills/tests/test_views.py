from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from bills.models import Submission

User = get_user_model()


class ViewsIntegrationTests(TestCase):
    """
    Testes de integração para as views de submissão (T011).
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

    def test_enviar_view_get(self):
        """O método GET na rota /enviar/ deve retornar 200 e fornecer o formulário."""
        response = self.client.get(reverse("enviar"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    @patch("bills.views.extract_text")
    def test_enviar_view_post_valid_pasted(self, mock_extract):
        """Um POST na rota /enviar/ com texto válido deve criar a submissão e enfileirar a task."""
        valid_source_text = "Projeto de lei válido com texto em português que supera os quinhentos caracteres. " * 10
        
        response = self.client.post(reverse("enviar"), {
            "title": "Test Bill",
            "origin_body": "Camara",
            "source_text": valid_source_text,
        })
        
        submission = Submission.objects.filter(title="Test Bill").first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.input_kind, Submission.InputKind.PASTED)
        self.assertEqual(response.status_code, 302)

    def test_minhas_submissoes_list(self):
        """O método GET na rota /minhas-submissoes/ deve listar as submissões do usuário atual."""
        Submission.objects.create(
            submitter=self.user,
            title="Listed Bill",
            origin_body="Camara",
            source_text="Este texto é válido em português com mais de quinhentos caracteres. " * 10,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash"
        )
        response = self.client.get(reverse("minhas_submissoes"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["submissions"]), 1)
        self.assertEqual(response.context["submissions"][0].title, "Listed Bill")

    def test_minhas_submissoes_detail(self):
        """O método GET na rota /minhas-submissoes/<pk>/ deve retornar os detalhes da submissão."""
        sub = Submission.objects.create(
            submitter=self.user,
            title="Listed Bill",
            origin_body="Camara",
            source_text="Este texto é válido em português com mais de quinhentos caracteres. " * 10,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash"
        )
        response = self.client.get(reverse("minhas_submissoes_detail", kwargs={"pk": sub.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["submission"].pk, sub.pk)
