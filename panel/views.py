from django.shortcuts import render, get_object_or_404
from bills.models import Bill, Theme
from .search import search_bills
from django.core.paginator import Paginator

def panel_list(request):
    qs = Bill.objects.filter(current_version__isnull=False, current_version__published_at__isnull=False).order_by('-first_published_at')
    
    q = request.GET.get('q')
    qs = search_bills(qs, q)
    
    theme_slug = request.GET.get('theme')
    if theme_slug:
        qs = qs.filter(theme__slug=theme_slug)
        
    origin = request.GET.get('origin')
    if origin:
        qs = qs.filter(origin_body__icontains=origin)
        
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
        current_version__isnull=False, 
        current_version__published_at__isnull=False
    )
    return render(request, 'panel/detail.html', {'bill': bill})

def panel_original(request, slug):
    bill = get_object_or_404(
        Bill, 
        slug=slug, 
        current_version__isnull=False, 
        current_version__published_at__isnull=False
    )
    return render(request, 'panel/original.html', {'bill': bill})

def panel_sinalizar(request, slug):
    bill = get_object_or_404(
        Bill, 
        slug=slug, 
        current_version__isnull=False, 
        current_version__published_at__isnull=False
    )
    if request.method == 'POST':
        description = request.POST.get('description')
        excerpt = request.POST.get('excerpt', '')
        if description:
            from bills.models import Flag
            Flag.objects.create(
                version=bill.current_version,
                reporter=request.user if request.user.is_authenticated else None,
                description=description,
                excerpt=excerpt
            )
            return render(request, 'panel/sinalizar_sucesso.html', {'bill': bill})
    return render(request, 'panel/sinalizar.html', {'bill': bill})
