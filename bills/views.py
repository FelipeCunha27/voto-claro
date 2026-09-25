from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bills.forms import SubmissionForm
from bills.models import Bill, Submission
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
            
            # Extraction
            if submission.uploaded_file:
                input_kind = 'pdf' if submission.uploaded_file.name.endswith('.pdf') else 'docx'
                submission.input_kind = input_kind
                # read file
                submission.source_text = extract_text(request.FILES['uploaded_file'], input_kind)
            else:
                submission.input_kind = Submission.InputKind.PASTED
                
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

def is_curator(user):
    return user.is_authenticated and user.is_curator

@user_passes_test(is_curator)
def curadoria_lista(request):
    return render(request, 'bills/curadoria_lista.html')

@user_passes_test(is_curator)
def curadoria_detalhe(request, pk):
    return render(request, 'bills/curadoria_detalhe.html')

@user_passes_test(is_curator)
def curadoria_aprovar(request, pk):
    return redirect('curadoria_lista')

@user_passes_test(is_curator)
def curadoria_editar(request, pk):
    return redirect('curadoria_lista')

@user_passes_test(is_curator)
def curadoria_regerar(request, pk):
    return redirect('curadoria_lista')

@user_passes_test(is_curator)
def curadoria_despublicar(request, pk):
    return redirect('curadoria_lista')

@user_passes_test(is_curator)
def curadoria_rejeitar(request, pk):
    return redirect('curadoria_lista')

@user_passes_test(is_curator)
def curadoria_resolver_sinalizacao(request, pk):
    return redirect('curadoria_lista')

@user_passes_test(is_curator)
def curadoria_projeto_aviso(request, slug):
    return redirect('curadoria_lista')
