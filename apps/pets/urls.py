
from django.urls import path

from . import views

app_name = 'pets'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('<int:pet_id>/editar/', views.editar, name='editar'),
]
