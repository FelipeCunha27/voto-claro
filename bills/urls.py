from django.urls import path
from . import views

urlpatterns = [
    path('enviar/', views.enviar, name='enviar'),
    path('minhas-submissoes/', views.minhas_submissoes, name='minhas_submissoes'),
    path('minhas-submissoes/<uuid:pk>/', views.minhas_submissoes_detail, name='minhas_submissoes_detail'),
]
urlpatterns.extend([
    path('curadoria/', views.curadoria_lista, name='curadoria_lista'),
    path('curadoria/<uuid:pk>/', views.curadoria_detalhe, name='curadoria_detalhe'),
    path('curadoria/<uuid:pk>/aprovar/', views.curadoria_aprovar, name='curadoria_aprovar'),
    path('curadoria/<uuid:pk>/editar/', views.curadoria_editar, name='curadoria_editar'),
    path('curadoria/<uuid:pk>/regerar/', views.curadoria_regerar, name='curadoria_regerar'),
    path('curadoria/<uuid:pk>/despublicar/', views.curadoria_despublicar, name='curadoria_despublicar'),
    path('curadoria/<uuid:pk>/rejeitar/', views.curadoria_rejeitar, name='curadoria_rejeitar'),
    path('curadoria/sinalizacoes/<uuid:pk>/resolver/', views.curadoria_resolver_sinalizacao, name='curadoria_resolver_sinalizacao'),
    path('curadoria/projeto/<slug:slug>/aviso/', views.curadoria_projeto_aviso, name='curadoria_projeto_aviso'),
])
