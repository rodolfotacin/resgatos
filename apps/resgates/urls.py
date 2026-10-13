
from django.urls import path

from . import views

app_name = 'resgates'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
]
