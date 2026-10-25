"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static
from django.db.models import Q, Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.pessoas.models import Pessoa
from apps.pets.models import Pet, PessoaPet
from apps.resgates.models import Resgate
from apps.atendimentos.models import Atendimento
from apps.fornecedores.models import Fornecedor
from apps.estoque.models import EntradaEstoque, Lote
from apps.medicamentos.models import Medicamento

from apps.pessoas.views import login_view


def inicio_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    hoje = timezone.localdate()
    inicio_mes = hoje.replace(day=1)
    proximos_30_dias = hoje + timedelta(days=30)

    # Pessoas e animais
    total_pessoas = Pessoa.objects.filter(is_active=True).count()

    total_pets = Pet.objects.filter(is_active=True).count()

    total_vinculos = PessoaPet.objects.filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje),
        pessoa__is_active=True,
        pet__is_active=True,
    ).count()

    # Resgates e atendimentos
    total_resgates = Resgate.objects.filter(is_active=True).count()

    total_atendimentos = Atendimento.objects.count()

    atendimentos_mes = Atendimento.objects.filter(
        data_hora__date__gte=inicio_mes,
        data_hora__date__lte=hoje,
    ).count()

    # Últimos 10 atendimentos
    atendimentos_recentes = (
        Atendimento.objects
        .select_related('pet', 'responsavel')
        .order_by('-data_hora', '-id')[:10]
    )

    # Fornecedores, entradas e medicamentos
    total_fornecedores = Fornecedor.objects.filter(
        is_active=True
    ).count()

    total_entradas = EntradaEstoque.objects.count()

    medicamentos_ativos = Medicamento.objects.filter(
        is_active=True
    ).count()

    medicamentos_estoque_baixo = Medicamento.objects.filter(
        is_active=True,
        estoque_atual__lte=F('estoque_minimo'),
    ).count()

    # Todos os medicamentos ativos, ordenados pela diferença
    # entre o estoque atual e o estoque mínimo.
    medicamentos_reposicao = (
        Medicamento.objects
        .filter(is_active=True)
        .annotate(
            diferenca_estoque=F('estoque_atual') - F('estoque_minimo')
        )
        .order_by('diferenca_estoque', 'nome')
    )

    # Alertas de validade dos lotes com saldo disponível.
    lotes_com_saldo = Lote.objects.annotate(
        quantidade_ministrada=Coalesce(
            Sum('utilizacoes__quantidade'),
            Value(
                0,
                output_field=DecimalField(
                    max_digits=10,
                    decimal_places=2,
                ),
            ),
            output_field=DecimalField(
                max_digits=10,
                decimal_places=2,
            ),
        )
    )

    lotes_vencidos = 0
    lotes_proximos_vencimento = 0

    for lote in lotes_com_saldo.select_related('medicamento'):
        saldo = (
            lote.quantidade_recebida
            - lote.quantidade_descartada
            - lote.quantidade_ministrada
        )

        if saldo <= 0:
            continue

        if lote.data_validade < hoje:
            lotes_vencidos += 1
        elif lote.data_validade <= proximos_30_dias:
            lotes_proximos_vencimento += 1


    contexto = {
        'total_pessoas': total_pessoas,
        'total_pets': total_pets,
        'total_vinculos': total_vinculos,
        'total_resgates': total_resgates,
        'total_atendimentos': total_atendimentos,
        'atendimentos_mes': atendimentos_mes,
        'atendimentos_recentes': atendimentos_recentes,
        'total_fornecedores': total_fornecedores,
        'total_entradas': total_entradas,
        'medicamentos_ativos': medicamentos_ativos,
        'medicamentos_estoque_baixo': medicamentos_estoque_baixo,
        'medicamentos_reposicao': medicamentos_reposicao,
        'lotes_vencidos': lotes_vencidos,
        'lotes_proximos_vencimento': lotes_proximos_vencimento,
    }

    return render(request, 'inicio.html', contexto)



urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação
    path('', login_view, name='login'),
    path('sair/', LogoutView.as_view(next_page='login'), name='logout'),

    # Aplicação
    path('inicio/', inicio_view, name='inicio'),
    path('pessoas/', include('apps.pessoas.urls')),
    path('pets/', include('apps.pets.urls')),
    path('resgates/', include('apps.resgates.urls')),
    path('atendimentos/', include('apps.atendimentos.urls')),
    path('estoque/', include('apps.estoque.urls')),
    path('medicamentos/', include('apps.medicamentos.urls')),
    path('fornecedores/', include('apps.fornecedores.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )