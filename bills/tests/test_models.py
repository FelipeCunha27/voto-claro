from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from bills.models import Submission

User = get_user_model()

class SubmissionModelTest(TestCase):
    """
    Testes de unidade para as validações do modelo Submission (T010).
    Verifica limites de texto, restrição de idioma, extensões de arquivos
    e os limites de tentativas por tempo (rate limit).
    """
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        
        submission = Submission(
            submitter=self.user,
            title="Test Bill 6",
            origin_body="Camara",
            source_text="Este texto é um projeto de lei válido em português com mais de quinhentos caracteres. " * 10,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash"
        )
        with self.assertRaisesMessage(ValidationError, "Limite de submissões excedido"):
            submission.clean()

