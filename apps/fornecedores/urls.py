
from django.urls import path

from . import views

app_name = 'fornecedores'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
]
