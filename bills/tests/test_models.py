import unittest
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
        
    
    def test_submission_rate_limit_removed(self):
        """T048: The submission rate limit has been removed."""
        for i in range(5):
            Submission.objects.create(
                submitter=self.user,
                title=f"Test Bill {i}",
                source_text="Este texto é um projeto de lei válido em português com mais de quinhentos caracteres. " * 10,
                input_kind=Submission.InputKind.PASTED,
                content_hash=f"hash{i}"
            )
        
        # 6th submission should NOT raise ValidationError
        submission = Submission(
            submitter=self.user,
            title="Test Bill 6",
            source_text="Este texto é um projeto de lei válido em português com mais de quinhentos caracteres. " * 10,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash6"
        )
        try:
            submission.clean()
        except ValidationError as e:
            self.fail(f"A 6ª submissão não deveria falhar: {e}")


    
    def test_source_text_size_limits_removed(self):
        """T046: A regra de limite de caracteres deve ser removida."""
        # Muito pequeno (menos de 500) mas com português e pontuação válidos
        small_text = "Projeto de lei válido com menos de quinhentos caracteres. " * 3
        self.assertTrue(len(small_text) < 500)
        
        submission1 = Submission(
            submitter=self.user,
            title="Test Bill",
            source_text=small_text,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash1"
        )
        try:
            submission1.clean()
        except ValidationError as e:
            self.fail(f"Texto pequeno não deveria falhar: {e}")

        # Muito grande (mais de 50000)
        large_text = "Projeto de lei válido em português muito longo. " * 2000
        self.assertTrue(len(large_text) > 50000)
        
        submission2 = Submission(
            submitter=self.user,
            title="Test Bill",
            source_text=large_text,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash2"
        )
        try:
            submission2.clean()
        except ValidationError as e:
            self.fail(f"Texto gigante não deveria falhar: {e}")

    
    def test_portuguese_language_validation(self):
        # English text
        english_text = "This is an english text that has more than five hundred characters. " * 10
        submission = Submission(
            submitter=self.user,
            title="Test Bill",
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
            source_text="Texto válido em português com mais de quinhentos caracteres. " * 10,
            input_kind=Submission.InputKind.DOCX,
            content_hash="hash"
        )
        submission_docx.uploaded_file.name = "document.pdf"
        with self.assertRaisesMessage(ValidationError, "O arquivo enviado deve corresponder ao tipo selecionado (PDF/DOCX)"):
            submission_docx.clean()

    def test_submission_requires_punctuation(self):
        """T042: O texto da submissão deve conter pontuação."""
        text_without_punctuation = "Este texto e valido em portugues com mais de quinhentos caracteres porem nao tem nenhuma pontuacao no meio " * 10
        submission = Submission(
            submitter=self.user,
            title="Test Bill",
            source_text=text_without_punctuation,
            input_kind=Submission.InputKind.PASTED,
            content_hash="hash"
        )
        with self.assertRaisesMessage(ValidationError, "O texto deve conter pontuação"):
            submission.clean()

    def test_models_do_not_have_origin_body(self):
        """T044: O campo origin_body deve ser removido de Bill e Submission."""
        from bills.models import Bill, Submission
        
        submission_fields = [f.name for f in Submission._meta.get_fields()]
        self.assertNotIn('origin_body', submission_fields)
        
        bill_fields = [f.name for f in Bill._meta.get_fields()]
        self.assertNotIn('origin_body', bill_fields)

from bills.models import Category
from django.db.utils import IntegrityError

class CategoryModelTest(TestCase):
    """
    Testes de unidade para o modelo Category.
    """
    def test_category_creation(self):
        category = Category.objects.create(
            name="Educação",
            description="Projetos relacionados à educação."
        )
        self.assertEqual(category.name, "Educação")
        self.assertEqual(category.description, "Projetos relacionados à educação.")
        self.assertEqual(str(category), "Educação")
    
    def test_category_name_unique(self):
        Category.objects.create(name="Saúde")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Saúde")
