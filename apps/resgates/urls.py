
from django.urls import path

from . import views

app_name = 'resgates'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('<int:resgate_id>/editar/', views.editar, name='editar'),
    path('<int:resgate_id>/inativar/', views.inativar, name='inativar',
),
]
