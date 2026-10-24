
from django.urls import path

from . import views

app_name = 'medicamentos'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('editar/<int:pk>/', views.editar, name='editar'),
    path('inativar/<int:pk>/', views.inativar, name='inativar'),
]
