from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user_is_curator_default_false(self):
        user = User.objects.create_user(username="testuser", password="password")
        self.assertFalse(user.is_curator)

    def test_create_curator(self):
        user = User.objects.create_user(username="curator", password="password", is_curator=True)
        self.assertTrue(user.is_curator)
