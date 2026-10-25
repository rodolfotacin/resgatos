
from django.urls import path

from . import views

app_name = 'atendimentos'

urlpatterns = [
    path('lista/', views.lista, name='lista'),
    path('adicionar/', views.adicionar, name='adicionar'),
    path('<int:atendimento_id>/editar/', views.editar, name='editar'),
    path('<int:atendimento_id>/excluir/', views.excluir, name='excluir'),

    path('<int:atendimento_id>/medicamentos/registrar/', views.registrar_medicamento, name='registrar_medicamento'),
    path('<int:atendimento_id>/medicamentos/ministrados/', views.medicamentos_ministrados, name='medicamentos_ministrados'),
    path('medicamentos/lotes-disponiveis/', views.lotes_disponiveis, name='lotes_disponiveis'),

    path('medicamentos/<int:utilizacao_id>/editar/', views.editar_medicamento, name='editar_medicamento'),
    path('medicamentos/<int:utilizacao_id>/excluir/', views.excluir_medicamento, name='excluir_medicamento'),
]
