from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from bills.models import Bill, Submission, AccessibleVersion, Flag

User = get_user_model()

class ReviewNoticeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='authuser', password='password123')
        
        self.bill = Bill.objects.create(
            slug='pl-notice',
            title='Projeto Notice Test',
            review_notice_override=Bill.ReviewNoticeOverride.AUTO
        )
        self.submission = Submission.objects.create(
            submitter=self.user,
            title='Projeto Notice Test',
            source_text='Texto fonte',
            input_kind=Submission.InputKind.PASTED,
            content_hash='dummyhash',
            status=Submission.Status.GENERATED,
            bill=self.bill
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
        self.url = reverse('panel_detail', kwargs={'slug': self.bill.slug})

    def test_notice_hidden_when_auto_and_no_flags(self):
        """T031: AUTO sem flags de auth_user -> aviso escondido."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Este resumo está pendente de revisão')

    def test_notice_hidden_when_auto_and_only_anon_flags(self):
        """T031: AUTO com flags anônimas -> aviso escondido."""
        Flag.objects.create(version=self.version, reporter=None, description="Erro")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Este resumo está pendente de revisão')

    def test_notice_shown_when_auto_and_auth_flags(self):
        """T031: AUTO com flags de auth_user -> aviso exibido."""
        Flag.objects.create(version=self.version, reporter=self.user, description="Erro grave")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este resumo está pendente de revisão')

    def test_notice_shown_when_forced_on(self):
        """T031: FORCED_ON -> aviso exibido independente de flags."""
        self.bill.review_notice_override = Bill.ReviewNoticeOverride.FORCED_ON
        self.bill.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este resumo está pendente de revisão')

    def test_notice_hidden_when_forced_off(self):
        """T031: FORCED_OFF -> aviso escondido mesmo com flags de auth_user."""
        self.bill.review_notice_override = Bill.ReviewNoticeOverride.FORCED_OFF
        self.bill.save()
        Flag.objects.create(version=self.version, reporter=self.user, description="Erro grave")
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Este resumo está pendente de revisão')
