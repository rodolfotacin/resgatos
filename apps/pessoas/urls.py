
from django.urls import path

from . import views

app_name = 'pessoas'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
]
