from django.urls import path
from . import views

app_name = 'registros'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('<str:tipo>/', views.lista, name='lista'),
    path('<str:tipo>/novo/', views.criar, name='criar'),
    path('<str:tipo>/<int:pk>/editar/', views.editar, name='editar'),
]
