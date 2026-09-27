from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from bills.forms import SubmissionForm
from bills.models import Bill, Submission, AccessibleVersion, AuditEntry, Flag
from bills.services.extraction import extract_text
from bills.services.screening import compute_content_hash
from bills.tasks import generate_accessible_version_task

@login_required
def enviar(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            
            submission = form.save(commit=False)
            submission.submitter = request.user
            
            # --- INJEÇÃO AUTOMÁTICA ---
            # Preenchendo os campos obrigatórios do banco para a interface ficar limpa
            submission.title = "Aguardando processamento da Inteligência Artificial"
            submission.origin_body = "Desconhecido"
            # --------------------------

            
            # Extraction
            if submission.uploaded_file:
                input_kind = 'pdf' if submission.uploaded_file.name.endswith('.pdf') else 'docx'
                submission.input_kind = input_kind
                # read file
                submission.source_text = extract_text(request.FILES['uploaded_file'], input_kind)
            
            else:
                submission.input_kind = Submission.InputKind.PASTED
                if submission.official_source_url and not submission.source_text:
                    submission.source_text = ("A IA vai processar o link a seguir: " + submission.official_source_url + " . ") * 20

                
            # Duplicate check
            content_hash = compute_content_hash(submission.source_text)
            submission.content_hash = content_hash
            
            existing = Submission.objects.filter(content_hash=content_hash).first()
            if existing and existing.bill:
                submission.bill = existing.bill
                submission.status = Submission.Status.PUBLISHED # just link it
                submission.save()
                return redirect('minhas_submissoes_detail', pk=submission.pk)
                
            try:
                submission.full_clean() # model validation
                submission.save()
                generate_accessible_version_task.enqueue(str(submission.pk))
                return redirect('minhas_submissoes_detail', pk=submission.pk)
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = SubmissionForm()
    return render(request, 'bills/enviar.html', {'form': form})

@login_required
def minhas_submissoes(request):
    submissions = Submission.objects.filter(submitter=request.user).order_by('-created_at')
    return render(request, 'bills/minhas_submissoes.html', {'submissions': submissions})

@login_required
def minhas_submissoes_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk, submitter=request.user)
    return render(request, 'bills/minhas_submissoes_detail.html', {'submission': submission})

from functools import wraps

def curator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not getattr(request.user, 'is_curator', False):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@curator_required
def curation_list(request):
    versions = AccessibleVersion.objects.filter(review_state=AccessibleVersion.ReviewState.PENDING).select_related('bill').order_by('-generated_at')
    return render(request, 'bills/curation_list.html', {'versions': versions})

@curator_required
def curation_detail(request, pk):
    version = get_object_or_404(AccessibleVersion, pk=pk)
    return render(request, 'bills/curation_detail.html', {'version': version})

@require_POST
@curator_required
def curation_approve(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    version = AccessibleVersion.objects.filter(submission=submission).first()
    if version:
        version.review_state = AccessibleVersion.ReviewState.APPROVED
        version.published_at = timezone.now()
        version.save()
    
    submission.status = Submission.Status.PUBLISHED
    submission.save()
    
    AuditEntry.objects.create(
        action=AuditEntry.Action.APPROVED,
        actor=request.user,
        version=version,
        bill=submission.bill,
        submission=submission
    )
    return redirect('curation_list')

@require_POST
@curator_required
def curation_edit(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    version = AccessibleVersion.objects.filter(submission=submission).first()
    if version:
        version.summary = request.POST.get('summary', version.summary)
        version.who_is_affected = request.POST.get('who_is_affected', version.who_is_affected)
        version.practical_changes = request.POST.get('practical_changes', version.practical_changes)
        version.points_of_attention = request.POST.get('points_of_attention', version.points_of_attention)
        version.edited_by_curator = True
        version.save()
    return redirect('curation_detail', pk=pk)

@require_POST
@curator_required
def curation_regenerate(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    version = AccessibleVersion.objects.filter(submission=submission).first()
    AuditEntry.objects.create(
        action=AuditEntry.Action.REGENERATED,
        actor=request.user,
        version=version,
        bill=submission.bill,
        submission=submission,
        reason=request.POST.get('reason', '')
    )
    generate_accessible_version_task.enqueue(str(submission.pk))
    return redirect('curation_list')

@require_POST
@curator_required
def curation_unpublish(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    version = AccessibleVersion.objects.filter(submission=submission).first()
    if version:
        version.unpublished_at = timezone.now()
        version.review_state = AccessibleVersion.ReviewState.PENDING
        version.save()
    
    submission.status = Submission.Status.UNPUBLISHED
    submission.save()
    
    AuditEntry.objects.create(
        action=AuditEntry.Action.UNPUBLISHED,
        actor=request.user,
        version=version,
        bill=submission.bill,
        submission=submission,
        reason=request.POST.get('reason', '')
    )
    return redirect('curation_list')

@require_POST
@curator_required
def curation_reject(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    version = AccessibleVersion.objects.filter(submission=submission).first()
    if version:
        version.review_state = AccessibleVersion.ReviewState.REJECTED
        version.save()
    
    submission.status = Submission.Status.REJECTED
    reason = request.POST.get('reason', '')
    submission.rejection_reason = reason
    submission.save()
    
    AuditEntry.objects.create(
        action=AuditEntry.Action.REJECTED,
        actor=request.user,
        version=version,
        bill=submission.bill,
        submission=submission,
        reason=reason
    )
    return redirect('curation_list')

@require_POST
@curator_required
def curation_resolve_flag(request, pk):
    flag = get_object_or_404(Flag, pk=pk)
    flag.state = Flag.State.RESOLVED
    flag.resolved_at = timezone.now()
    flag.resolved_by = request.user
    flag.resolution_note = request.POST.get('resolution_note', '')
    flag.save()
    
    AuditEntry.objects.create(
        action=AuditEntry.Action.FLAG_RESOLVED,
        actor=request.user,
        version=flag.version,
        bill=flag.version.bill,
        reason=f"Flag {flag.id} resolved: {flag.resolution_note}"
    )
    return redirect('curation_detail', pk=flag.version.pk)

@require_POST
@curator_required
def curation_bill_notice_override(request, slug):
    bill = get_object_or_404(Bill, slug=slug)
    bill.review_notice_override = request.POST.get('override_type', Bill.ReviewNoticeOverride.AUTO)
    bill.save()
    
    AuditEntry.objects.create(
        action=AuditEntry.Action.NOTICE_OVERRIDDEN,
        actor=request.user,
        bill=bill,
        reason=f"Override set to {bill.review_notice_override}"
    )
    return redirect('curation_list')
