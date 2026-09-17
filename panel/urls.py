from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_list, name='panel_list'),
    path('projeto/<slug:slug>/', views.panel_detail, name='panel_detail'),
]
urlpatterns.extend([
    path('projeto/<slug:slug>/original/', views.panel_original, name='panel_original'),
    path('projeto/<slug:slug>/sinalizar/', views.panel_sinalizar, name='panel_sinalizar'),
])
