
from django.urls import path

from . import views

app_name = 'pets'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('<int:pet_id>/editar/', views.editar, name='editar'),
    path('<int:pet_id>/situacoes/adicionar/', views.situacao_adicionar, name='situacao_adicionar'),
    path('<int:pet_id>/situacoes/<int:situacao_id>/editar/', views.situacao_editar, name='situacao_editar'),
    path('<int:pet_id>/situacoes/<int:situacao_id>/excluir/', views.situacao_excluir, name='situacao_excluir'),
]
