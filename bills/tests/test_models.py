from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from bills.models import Submission
from django.utils import timezone
import datetime

User = get_user_model()

class SubmissionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        
    def test_submission_rate_limit(self):
        for _ in range(5):
            Submission.objects.create(
                submitter=self.user,
                title="Test Bill",
                origin_body="Camara",
                source_text="A" * 600,
                input_kind=Submission.InputKind.PASTED,
                content_hash="hash"
            )
        
        # 6th submission should raise ValidationError on clean
        submission = Submission(
            submitter=self.user,
            title="Test Bill 6",
            origin_body="Camara",
            source_text="A" * 600,
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
