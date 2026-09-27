from django.urls import path
from . import views

urlpatterns = [
    path('enviar/', views.enviar, name='enviar'),
    path('minhas-submissoes/', views.minhas_submissoes, name='minhas_submissoes'),
    path('minhas-submissoes/<uuid:pk>/', views.minhas_submissoes_detail, name='minhas_submissoes_detail'),
]
urlpatterns.extend([
    path('curadoria/', views.curation_list, name='curation_list'),
    path('curadoria/<uuid:pk>/', views.curation_detail, name='curation_detail'),
    path('curadoria/<uuid:pk>/aprovar/', views.curation_approve, name='curation_approve'),
    path('curadoria/<uuid:pk>/editar/', views.curation_edit, name='curation_edit'),
    path('curadoria/<uuid:pk>/regerar/', views.curation_regenerate, name='curation_regenerate'),
    path('curadoria/<uuid:pk>/despublicar/', views.curation_unpublish, name='curation_unpublish'),
    path('curadoria/<uuid:pk>/rejeitar/', views.curation_reject, name='curation_reject'),
    path('curadoria/sinalizacoes/<uuid:pk>/resolver/', views.curation_resolve_flag, name='curation_resolve_flag'),
    path('curadoria/projeto/<slug:slug>/aviso/', views.curation_bill_notice_override, name='curation_bill_notice_override'),
])
