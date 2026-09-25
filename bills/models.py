from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.conf import settings
import uuid

class Theme(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Bill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=300)
    origin_body = models.CharField(max_length=200)
    bill_number = models.CharField(max_length=50, blank=True, null=True)
    bill_year = models.IntegerField(blank=True, null=True)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True)
    official_source_url = models.URLField(blank=True, null=True)
    current_version = models.ForeignKey('AccessibleVersion', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    
    class ReviewNoticeOverride(models.TextChoices):
        AUTO = 'auto', 'Auto'
        FORCED_ON = 'forced_on', 'Forced On'
        FORCED_OFF = 'forced_off', 'Forced Off'

    review_notice_override = models.CharField(max_length=20, choices=ReviewNoticeOverride.choices, default=ReviewNoticeOverride.AUTO)
    first_published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Submission(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'received', 'Received'
        PROCESSING = 'processing', 'Processing'
        GENERATED = 'generated', 'Generated'
        PUBLISHED = 'published', 'Published'
        UNPUBLISHED = 'unpublished', 'Unpublished'
        FAILED = 'failed', 'Failed'
        REJECTED = 'rejected', 'Rejected'

    class InputKind(models.TextChoices):
        PASTED = 'pasted', 'Pasted'
        PDF = 'pdf', 'PDF'
        DOCX = 'docx', 'DOCX'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=300)
    origin_body = models.CharField(max_length=200)
    bill_number = models.CharField(max_length=50, blank=True, null=True)
    bill_year = models.IntegerField(blank=True, null=True)
    official_source_url = models.URLField(blank=True, null=True)
    source_text = models.TextField() # Write-once, 500-50k chars
    uploaded_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    input_kind = models.CharField(max_length=10, choices=InputKind.choices)
    content_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    rejection_reason = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    attempt_count = models.IntegerField(default=0)
    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.source_text:
            usable_chars = len(self.source_text.strip())
            if usable_chars < 500 or usable_chars > 50000:
                raise ValidationError("O texto deve ter entre 500 e 50.000 caracteres.")
                
            common_pt_words = {"de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "não", "uma", "os", "no"}
            words = set(self.source_text.lower().split())
            if not common_pt_words.intersection(words):
                raise ValidationError("O texto deve estar em português.")

        if self.input_kind in [self.InputKind.PDF, self.InputKind.DOCX]:
            if not self.uploaded_file:
                raise ValidationError("O arquivo enviado deve corresponder ao tipo selecionado (PDF/DOCX).")
            
            ext = self.uploaded_file.name.split('.')[-1].lower() if self.uploaded_file.name else ""
            if self.input_kind == self.InputKind.PDF and ext != 'pdf':
                raise ValidationError("O arquivo enviado deve corresponder ao tipo selecionado (PDF/DOCX).")
            if self.input_kind == self.InputKind.DOCX and ext != 'docx':
                raise ValidationError("O arquivo enviado deve corresponder ao tipo selecionado (PDF/DOCX).")

        if self._state.adding and getattr(self, "submitter_id", None):
            yesterday = timezone.now() - timedelta(days=1)
            recent_count = Submission.objects.filter(submitter=self.submitter, created_at__gte=yesterday).count()
            if recent_count >= 5:
                raise ValidationError("Limite de submissões excedido. Você pode enviar até 5 projetos a cada 24 horas.")

class AccessibleVersion(models.Model):
    class ReviewState(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        SUPERSEDED = 'superseded', 'Superseded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, on_delete=models.PROTECT)
    version_number = models.IntegerField()
    summary = models.TextField()
    who_is_affected = models.TextField()
    practical_changes = models.TextField()
    points_of_attention = models.TextField()
    suggested_theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    generator_reference = models.CharField(max_length=200)
    is_ai_generated = models.BooleanField(default=True)
    edited_by_curator = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    unpublished_at = models.DateTimeField(null=True, blank=True)
    review_state = models.CharField(max_length=20, choices=ReviewState.choices, default=ReviewState.PENDING)

    class Meta:
        unique_together = ('bill', 'version_number')


class Flag(models.Model):
    class State(models.TextChoices):
        OPEN = 'open', 'Open'
        RESOLVED = 'resolved', 'Resolved'
        DISMISSED = 'dismissed', 'Dismissed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.ForeignKey(AccessibleVersion, on_delete=models.CASCADE)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    excerpt = models.TextField(blank=True)
    description = models.TextField()
    state = models.CharField(max_length=20, choices=State.choices, default=State.OPEN)
    resolution_note = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

class AuditEntry(models.Model):
    class Action(models.TextChoices):
        GENERATED = 'generated', 'Generated'
        REGENERATED = 'regenerated', 'Regenerated'
        APPROVED = 'approved', 'Approved'
        PUBLISHED = 'published', 'Published'
        UNPUBLISHED = 'unpublished', 'Unpublished'
        REJECTED = 'rejected', 'Rejected'
        FLAG_RESOLVED = 'flag_resolved', 'Flag Resolved'
        THEME_CHANGED = 'theme_changed', 'Theme Changed'
        NOTICE_OVERRIDDEN = 'notice_overridden', 'Notice Overridden'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bill = models.ForeignKey(Bill, on_delete=models.SET_NULL, null=True, blank=True)
    version = models.ForeignKey(AccessibleVersion, on_delete=models.SET_NULL, null=True, blank=True)
    submission = models.ForeignKey(Submission, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise Exception("AuditEntry is append-only and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise Exception("AuditEntry cannot be deleted.")
