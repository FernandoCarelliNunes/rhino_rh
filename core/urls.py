from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('candidato/novo/', views.cadastrar_candidato, name='cadastrar_candidato'),
    path('vaga/<int:vaga_id>/', views.detalhes_vaga, name='detalhes_vaga'),
    path('candidato/<int:candidato_id>/status/<str:novo_status>/', views.mudar_status_candidato, name='mudar_status'),
    path('vaga/nova/', views.cadastrar_vaga, name='cadastrar_vaga'),
    path('vaga/<int:vaga_id>/status/<str:novo_status>/', views.mudar_status_vaga, name='mudar_status_vaga'),
    path('relatorios/geral/', views.relatorio_geral, name='relatorio_geral'),
    path('cliente/novo/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('vaga/<int:vaga_id>/inscrever/', views.inscrever_vaga, name='inscrever_vaga'),
    path('candidato/<int:candidato_id>/status/<str:novo_status>/',views.mudar_status_candidato, name='mudar_status_candidato'),
]
 


