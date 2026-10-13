
from django.urls import path

from . import views

app_name = 'pets'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
]
