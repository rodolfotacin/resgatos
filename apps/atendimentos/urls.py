
from django.urls import path

from . import views

app_name = 'atendimentos'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
]
