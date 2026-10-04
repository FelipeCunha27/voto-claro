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
            
            
            "source_text": valid_source_text,
        })
        
        submission = Submission.objects.order_by('-created_at').first()
        self.assertIsNotNone(submission)
        self.assertEqual(submission.input_kind, Submission.InputKind.PASTED)
        self.assertEqual(response.status_code, 302)

    @patch("bills.views.extract_text")
    def test_enviar_view_post_title_from_text(self, mock_extract):
        """T043: O título da submissão deve ser baseado no texto, e não um valor fixo."""
        valid_source_text = "Projeto de lei válido com texto em português que supera os quinhentos caracteres. " * 10
        
        response = self.client.post(reverse("enviar"), {
            "source_text": valid_source_text,
        })
        
        submission = Submission.objects.order_by('-created_at').first()
        self.assertIsNotNone(submission)
        self.assertNotEqual(submission.title, "Aguardando processamento da Inteligência Artificial")
        self.assertTrue(submission.title.strip().startswith("Projeto de lei"), "O título deve ser derivado do texto inicial")

    @patch("bills.views.extract_text")
    def test_enviar_view_post_link_without_hack(self, mock_extract):
        """T046: O envio de links não deve precisar da gambiarra do multiplicador de string."""
        url = "https://legis.senado.leg.br/sdleg-getter/documento?download=ns"
        response = self.client.post(reverse("enviar"), {
            "official_source_url": url,
            "source_text": "",
        })
        
        submission = Submission.objects.order_by('-created_at').first()
        self.assertIsNotNone(submission)
        # We expect the source_text to be just a simple phrase, NOT repeated 20 times.
        expected_text = f"A IA vai processar o link a seguir: {url} ."
        self.assertEqual(submission.source_text.strip(), expected_text.strip())

    def test_minhas_submissoes_list(self):
        """O método GET na rota /minhas-submissoes/ deve listar as submissões do usuário atual."""
        Submission.objects.create(
            submitter=self.user,
            title="Listed Bill",
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
            source_text="Este texto é válido em português com mais de quinhentos caracteres. " * 10,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash"
        )
        response = self.client.get(reverse("minhas_submissoes_detail", kwargs={"pk": sub.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["submission"].pk, sub.pk)

    def test_minhas_submissoes_detail_auto_reloads_on_pending(self):
        """T061: A página de detalhe deve conter auto-reload se o status for RECEIVED ou PROCESSING."""
        for status in [Submission.Status.RECEIVED, Submission.Status.PROCESSING]:
            with self.subTest(status=status):
                sub = Submission.objects.create(
                    submitter=self.user,
                    title=f"Submissão {status}",
                    source_text="Texto válido. " * 10,
                    input_kind=Submission.InputKind.PASTED,
                    content_hash=f"hash_{status}",
                    status=status
                )
                response = self.client.get(reverse("minhas_submissoes_detail", kwargs={"pk": sub.pk}))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'http-equiv="refresh"', msg_prefix=f"Falta meta refresh para o status {status}")
                self.assertContains(response, 'gerando o relat', msg_prefix=f"Falta mensagem de loading para status {status}")

    def test_minhas_submissoes_detail_no_reload_on_completed(self):
        """T061: A página NÃO deve dar auto-reload se o status for finalizado."""
        for status in [Submission.Status.GENERATED, Submission.Status.PUBLISHED, Submission.Status.FAILED, Submission.Status.REJECTED]:
            with self.subTest(status=status):
                sub = Submission.objects.create(
                    submitter=self.user,
                    title=f"Submissão {status}",
                    source_text="Texto válido. " * 10,
                    input_kind=Submission.InputKind.PASTED,
                    content_hash=f"hash_{status}",
                    status=status
                )
                response = self.client.get(reverse("minhas_submissoes_detail", kwargs={"pk": sub.pk}))
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'http-equiv="refresh"', msg_prefix=f"Não deve ter meta refresh no status {status}")
                self.assertNotContains(response, 'gerando o relat', msg_prefix=f"Não deve ter mensagem de loading no status {status}")
