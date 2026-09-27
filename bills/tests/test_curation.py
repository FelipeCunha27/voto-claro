from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from bills.models import Submission

User = get_user_model()

class TestCuratorAccessControl(TestCase):
    
    def setUp(self):
        self.normal_user = User.objects.create_user(username="normal", password="password")
        self.curator_user = User.objects.create_user(username="curator", password="password")
        # Simula flag de curador (depende da implementação do Dev)
        setattr(self.curator_user, 'is_curator', True)
        self.curator_user.save()
        
        self.submission = Submission.objects.create(
            submitter=self.normal_user,
            title="Test Submission",
            source_text="Test content",
            input_kind="pasted",
            content_hash="testhash"
        )

    def test_approve_action_denied_for_normal_user(self):
        self.client.force_login(self.normal_user)
        # Assumindo que a view de aprovar requer POST e uuid
        url = reverse('curation_approve', kwargs={'pk': self.submission.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_approve_action_allowed_for_curator(self):
        self.client.force_login(self.curator_user)
        url = reverse('curation_approve', kwargs={'pk': self.submission.id})
        response = self.client.post(url)
        self.assertIn(response.status_code, [200, 302])
