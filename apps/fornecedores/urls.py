
from django.urls import path

from . import views

app_name = 'fornecedores'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('consultar-cnpj/', views.consultar_cnpj, name='consultar_cnpj'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('editar/<int:fornecedor_id>/', views.editar, name='editar'),
    path('inativar/<int:fornecedor_id>/', views.inativar, name='inativar'),
]