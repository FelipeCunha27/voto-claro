from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from bills.models import Bill, Submission

User = get_user_model()

class PublicPanelViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        
        # Projeto Gerado
        self.bill_generated = Bill.objects.create(
            slug="projeto-gerado",
            title="Projeto Gerado",
            origin_body="Câmara",
            bill_number="123",
            bill_year=2023
        )
        self.sub_generated = Submission.objects.create(
            submitter=self.user,
            title="Projeto Gerado",
            origin_body="Câmara",
            source_text="Texto do projeto gerado",
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash1",
            status=Submission.Status.GENERATED,
            bill=self.bill_generated
        )

        # Projeto Processando
        self.bill_processing = Bill.objects.create(
            slug="projeto-processando",
            title="Projeto Processando",
            origin_body="Câmara",
            bill_number="124",
            bill_year=2023
        )
        self.sub_processing = Submission.objects.create(
            submitter=self.user,
            title="Projeto Processando",
            origin_body="Câmara",
            source_text="Texto do projeto processando",
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash2",
            status=Submission.Status.PROCESSING,
            bill=self.bill_processing
        )

        # Projeto Falho
        self.bill_failed = Bill.objects.create(
            slug="projeto-falho",
            title="Projeto Falho",
            origin_body="Câmara",
            bill_number="125",
            bill_year=2023
        )
        self.sub_failed = Submission.objects.create(
            submitter=self.user,
            title="Projeto Falho",
            origin_body="Câmara",
            source_text="Texto do projeto falho",
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash3",
            status=Submission.Status.FAILED,
            bill=self.bill_failed
        )

    def test_home_lists_only_generated_submissions(self):
        """
        A rota da Home (/) deve listar apenas submissões com status GENERATED.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        
        # Deve conter o projeto gerado
        self.assertContains(response, self.bill_generated.title)
        
        # Não deve conter os projetos em processamento ou com falha
        self.assertNotContains(response, self.bill_processing.title)
        self.assertNotContains(response, self.bill_failed.title)

    def test_detail_returns_200_for_generated_project(self):
        """
        A rota de Detalhes (/projeto/<slug>/) deve retornar Status 200 para projetos gerados.
        """
        response = self.client.get(f"/projeto/{self.bill_generated.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.bill_generated.title)

    def test_detail_returns_404_for_processing_project(self):
        """
        A rota de Detalhes (/projeto/<slug>/) deve retornar Erro 404 para projetos que estão em processamento.
        """
        response = self.client.get(f"/projeto/{self.bill_processing.slug}/")
        self.assertEqual(response.status_code, 404)

    def test_detail_returns_404_for_failed_project(self):
        """
        A rota de Detalhes (/projeto/<slug>/) deve retornar Erro 404 para projetos com falha.
        """
        response = self.client.get(f"/projeto/{self.bill_failed.slug}/")
        self.assertEqual(response.status_code, 404)

    def test_search_filters_by_title(self):
        """
        Garante que a busca pelo parâmetro 'q' filtra os projetos corretamente.
        """
        bill_search = Bill.objects.create(
            slug="projeto-busca-especifica",
            title="Projeto Busca Especifica",
            origin_body="Senado",
            bill_number="999",
            bill_year=2024
        )
        Submission.objects.create(
            submitter=self.user,
            title="Projeto Busca Especifica",
            origin_body="Senado",
            source_text="Texto",
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash999",
            status=Submission.Status.GENERATED,
            bill=bill_search
        )
        
        response = self.client.get("/?q=Especifica")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Busca Especifica")
        # O projeto gerado padrão não deve aparecer na busca
        self.assertNotContains(response, self.bill_generated.title)

    def test_pagination_is_applied(self):
        """
        Garante que a lista é paginada em 20 itens.
        """
        for i in range(25):
            b = Bill.objects.create(
                slug=f"projeto-paginado-{i}",
                title=f"Projeto Paginado {i}",
                origin_body="Camara",
                bill_number=str(i),
                bill_year=2024
            )
            Submission.objects.create(
                submitter=self.user,
                title=f"Projeto Paginado {i}",
                origin_body="Camara",
                source_text="Texto",
                input_kind=Submission.InputKind.PASTED,
                content_hash=f"hash-pag-{i}",
                status=Submission.Status.GENERATED,
                bill=b
            )
            
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        # O Paginator está configurado para 20
        self.assertTrue(response.context['page_obj'].has_next())
        self.assertEqual(len(response.context['page_obj']), 20)
