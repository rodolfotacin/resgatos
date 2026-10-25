
from django.urls import path

from . import views

app_name = 'estoque'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('<int:entrada_id>/editar/', views.editar, name='editar'),
    path('<int:entrada_id>/excluir/', views.excluir, name='excluir'),

    path('<int:entrada_id>/lotes/', views.lotes, name='lotes'),
    path('<int:entrada_id>/lotes/adicionar/', views.adicionar_lote, name='adicionar_lote'),
    path('<int:entrada_id>/lotes/<int:lote_id>/editar/', views.editar_lote, name='editar_lote'),
    path('<int:entrada_id>/lotes/<int:lote_id>/excluir/', views.excluir_lote, name='excluir_lote'),
]
