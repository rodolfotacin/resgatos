
from django.urls import path

from . import views

app_name = 'pets'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('<int:pet_id>/editar/', views.editar, name='editar'),
    path('<int:pet_id>/inativar/', views.inativar, name='inativar'),

    path('<int:pet_id>/situacoes/adicionar/', views.situacao_adicionar, name='situacao_adicionar'),
    path('<int:pet_id>/situacoes/<int:situacao_id>/editar/', views.situacao_editar, name='situacao_editar'),
    path('<int:pet_id>/situacoes/<int:situacao_id>/excluir/', views.situacao_excluir, name='situacao_excluir'),

    path('associar/<int:pessoa_id>/', views.associar_pessoa, name='associar_pessoa'),
    path('vinculo/<int:vinculo_id>/editar/', views.editar_associacao, name='editar_associacao'),
    path('pessoa/<int:pessoa_id>/vinculo/<int:vinculo_id>/excluir/', views.excluir_vinculo_pet, name='excluir_vinculo_pet'),

    path('<int:pet_id>/associar-pessoa/', views.associar_pet_pessoa, name='associar_pet_pessoa'),
    path('vinculo/<int:vinculo_id>/excluir/', views.excluir_vinculo_pet, name='excluir_vinculo_pet_pet'),
]
