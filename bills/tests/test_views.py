from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from bills.models import Submission

User = get_user_model()

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="password")
        self.client.login(username="user", password="password")
        
    def test_enviar_view_get(self):
        # Depending on url routing, we might need to mock reverse
        # but let's test directly later when urls are registered.
        pass
