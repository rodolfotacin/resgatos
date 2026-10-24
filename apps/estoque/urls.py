
from django.urls import path

from . import views

app_name = 'estoque'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('<int:entrada_id>/editar/', views.editar, name='editar'),
    path('<int:entrada_id>/excluir/', views.excluir, name='excluir'),
]
