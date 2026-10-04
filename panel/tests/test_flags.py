from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from bills.models import Bill, Submission, AccessibleVersion, Flag

User = get_user_model()

class FlagModelAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.bill = Bill.objects.create(
            slug='pl-123-2023',
            title='Projeto Teste',
        )
        self.submission = Submission.objects.create(
            submitter=self.user,
            title='Projeto Teste',
            source_text='Texto fonte',
            input_kind=Submission.InputKind.PASTED,
            content_hash='dummyhash',
            status=Submission.Status.GENERATED
        )
        self.version = AccessibleVersion.objects.create(
            bill=self.bill,
            submission=self.submission,
            version_number=1,
            summary='Resumo',
            who_is_affected='Todos',
            practical_changes='Nenhuma',
            points_of_attention='Nenhum',
            generator_reference='ref',
            is_ai_generated=True,
            review_state=AccessibleVersion.ReviewState.APPROVED,
            published_at='2023-01-01T00:00:00Z'
        )
        self.bill.current_version = self.version
        self.bill.save()

    def test_flag_creation_auth_user(self):
        """T027: Deve ser possível criar uma flag com um usuário autenticado."""
        flag = Flag.objects.create(
            version=self.version,
            reporter=self.user,
            description="Isso está incorreto."
        )
        self.assertEqual(flag.reporter, self.user)
        self.assertEqual(flag.state, Flag.State.OPEN)

    def test_flag_creation_anon_user(self):
        """T027: Deve ser possível criar uma flag com usuário anônimo (nullity)."""
        flag = Flag.objects.create(
            version=self.version,
            reporter=None,
            description="Isso está incorreto, mas sou anônimo."
        )
        self.assertIsNone(flag.reporter)
        self.assertEqual(flag.state, Flag.State.OPEN)

    def test_flag_description_required(self):
        """T027: Description deve ser obrigatória (teste de validação do model)."""
        flag = Flag(version=self.version, description="")
        with self.assertRaises(ValidationError):
            flag.full_clean()

    def test_flag_str_representation(self):
        """T027: Teste do __str__ do model Flag."""
        flag = Flag.objects.create(
            version=self.version,
            description="Test flag"
        )
        # O __str__ deve conter pelo menos 'Flag on' ou o slug do projeto
        self.assertIn("Flag", str(flag))
        self.assertIn(self.bill.slug, str(flag))

    def test_original_view_get(self):
        """T029: GET /projeto/<slug>/original/ deve renderizar o template de comparação."""
        url = reverse('panel_original', kwargs={'slug': self.bill.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panel/original.html')
        self.assertIn('bill', response.context)
        self.assertEqual(response.context['bill'], self.bill)

    def test_original_renders_markdown(self):
        """T049: GET /projeto/<slug>/original/ deve renderizar Markdown na versão acessível e no texto original."""
        self.version.practical_changes = "Intro\n\n- Bullet 1\n- Bullet 2"
        self.version.save()
        
        # Test also source_text for linebreaks
        self.submission.source_text = "Orig 1\nOrig 2"
        self.submission.save()

        url = reverse('panel_original', kwargs={'slug': self.bill.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<li>Bullet 1</li>", html=False)
        self.assertContains(response, "Orig 1<br>Orig 2", html=False)  # source_text can use linebreaks or markdown

    def test_sinalizar_view_get(self):
        """T030: GET /projeto/<slug>/sinalizar/ deve renderizar o formulário de sinalização."""
        url = reverse('panel_sinalizar', kwargs={'slug': self.bill.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panel/sinalizar.html')
        self.assertIn('bill', response.context)
        
    def test_sinalizar_view_post_auth(self):
        """T030: POST /projeto/<slug>/sinalizar/ autenticado deve criar Flag com reporter."""
        self.client.login(username='testuser', password='password123')
        url = reverse('panel_sinalizar', kwargs={'slug': self.bill.slug})
        response = self.client.post(url, {
            'description': 'Texto confuso',
            'excerpt': 'Artigo 5'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panel/sinalizar_sucesso.html')
        
        flag = Flag.objects.get(version=self.version)
        self.assertEqual(flag.reporter, self.user)
        self.assertEqual(flag.description, 'Texto confuso')
        self.assertEqual(flag.excerpt, 'Artigo 5')

    def test_sinalizar_view_post_anon(self):
        """T030: POST /projeto/<slug>/sinalizar/ anônimo deve criar Flag sem reporter."""
        url = reverse('panel_sinalizar', kwargs={'slug': self.bill.slug})
        response = self.client.post(url, {
            'description': 'Acho que está errado'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panel/sinalizar_sucesso.html')
        
        flag = Flag.objects.get(version=self.version)
        self.assertIsNone(flag.reporter)
        self.assertEqual(flag.description, 'Acho que está errado')
        self.assertEqual(flag.excerpt, '')
        
    def test_sinalizar_view_post_invalid(self):
        """T030: POST /projeto/<slug>/sinalizar/ sem descrição deve falhar e não criar Flag."""
        url = reverse('panel_sinalizar', kwargs={'slug': self.bill.slug})
        response = self.client.post(url, {
            'description': ''
        })
        self.assertEqual(Flag.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'panel/sinalizar.html')
        self.assertContains(response, "Este campo é obrigatório", status_code=200)
