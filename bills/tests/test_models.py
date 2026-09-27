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
        
    def test_submission_rate_limit(self):
        for _ in range(5):
            Submission.objects.create(
                submitter=self.user,
                title="Test Bill",
                origin_body="Camara",
                source_text="Este texto é um projeto de lei válido em português com mais de quinhentos caracteres. " * 10,
                input_kind=Submission.InputKind.PASTED,
                content_hash="hash"
            )
        
        # 6th submission should raise ValidationError on clean
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

    def test_source_text_size_limits(self):
        # Too small
        submission1 = Submission(
            submitter=self.user,
            title="Test Bill",
            origin_body="Camara",
            source_text="A" * 400,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash"
        )
        with self.assertRaisesMessage(ValidationError, "O texto deve ter entre"):
            submission1.clean()

        # Too large
        submission2 = Submission(
            submitter=self.user,
            title="Test Bill",
            origin_body="Camara",
            source_text="A" * 50001,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash"
        )
        with self.assertRaisesMessage(ValidationError, "O texto deve ter entre"):
            submission2.clean()

    def test_portuguese_language_validation(self):
        # English text
        english_text = "This is an english text that has more than five hundred characters. " * 10
        submission = Submission(
            submitter=self.user,
            title="Test Bill",
            origin_body="Camara",
            source_text=english_text,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash"
        )
        with self.assertRaisesMessage(ValidationError, "O texto deve estar em português"):
            submission.clean()

    def test_file_extension_for_pdf_and_docx(self):
        # PDF kind with wrong file
        submission_pdf = Submission(
            submitter=self.user,
            title="Test Bill",
            origin_body="Camara",
            source_text="Texto válido em português com mais de quinhentos caracteres. " * 10,
            input_kind=Submission.InputKind.PDF,
            content_hash="hash"
        )
        submission_pdf.uploaded_file.name = "document.txt"
        with self.assertRaisesMessage(ValidationError, "O arquivo enviado deve corresponder ao tipo selecionado (PDF/DOCX)"):
            submission_pdf.clean()

        # DOCX kind with wrong file
        submission_docx = Submission(
            submitter=self.user,
            title="Test Bill",
            origin_body="Camara",
            source_text="Texto válido em português com mais de quinhentos caracteres. " * 10,
            input_kind=Submission.InputKind.DOCX,
            content_hash="hash"
        )
        submission_docx.uploaded_file.name = "document.pdf"
        with self.assertRaisesMessage(ValidationError, "O arquivo enviado deve corresponder ao tipo selecionado (PDF/DOCX)"):
            submission_docx.clean()
