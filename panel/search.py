from bills.models import Bill

def search_bills(queryset, query: str):
    if not query:
        return queryset
    # SQLite full text search simulation or simple icontains
    return queryset.filter(
        title__icontains=query
    ) | queryset.filter(
        current_version__summary__icontains=query
    )
