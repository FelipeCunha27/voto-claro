"""
Rotas principais (Root URLconf) do projeto Voto Claro.

Inclui as rotas do painel público, submissão de projetos (bills) e contas (accounts).
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Rotas de autenticação e contas
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    
    # Rotas de domínio principal (painel e submissões)
    path("", include("panel.urls")),
    path("", include("bills.urls")),
]
