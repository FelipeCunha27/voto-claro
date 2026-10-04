from django.shortcuts import render, get_object_or_404, redirect
from bills.models import Bill, Submission, Theme, Flag
from .search import search_bills
from django.core.paginator import Paginator
from .forms import FlagForm

def panel_list(request):
    qs = Bill.objects.filter(submission__status=Submission.Status.GENERATED).distinct().order_by('-updated_at')
    
    q = request.GET.get('q')
    qs = search_bills(qs, q)
    
    theme_slug = request.GET.get('theme')
    if theme_slug:
        qs = qs.filter(theme__slug=theme_slug)
        
    date_from = request.GET.get('date_from')
    if date_from:
        qs = qs.filter(first_published_at__gte=date_from)
        
    date_to = request.GET.get('date_to')
    if date_to:
        qs = qs.filter(first_published_at__lte=date_to)
        
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'panel/list.html', {'page_obj': page_obj})

def panel_detail(request, slug):
    bill = get_object_or_404(
        Bill, 
        slug=slug, 
        submission__status=Submission.Status.GENERATED
    )
    return render(request, 'panel/detail.html', {'bill': bill})

def get_published_bill_or_404(slug):
    return get_object_or_404(
        Bill, 
        slug=slug, 
        current_version__isnull=False, 
        current_version__published_at__isnull=False
    )

def panel_original(request, slug):
    bill = get_published_bill_or_404(slug)
    return render(request, 'panel/original.html', {'bill': bill})

def panel_sinalizar(request, slug):
    bill = get_published_bill_or_404(slug)
    
    if request.method == 'POST':
        form = FlagForm(request.POST)
        if form.is_valid():
            flag = form.save(commit=False)
            flag.version = bill.current_version
            if request.user.is_authenticated:
                flag.reporter = request.user
            flag.save()
            return render(request, 'panel/sinalizar_sucesso.html', {'bill': bill})
    else:
        form = FlagForm()
        
    return render(request, 'panel/sinalizar.html', {'bill': bill, 'form': form})
