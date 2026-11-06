from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction

from apps.pets.models import Pet
from apps.resgates.models import Resgate
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CastracaoForm, ObitoForm, InternacaoForm, ComplementoResgateForm
from .forms_resgate_integrado import ResgateCompletoForm
from .models import Castracao, Obito, Internacao, ComplementoResgate


TIPOS = {
    'castracoes': (Castracao, CastracaoForm, 'Castrações'),
    'obitos': (Obito, ObitoForm, 'Óbitos'),
    'internacoes': (Internacao, InternacaoForm, 'Internações'),
    'resgates': (ComplementoResgate, ComplementoResgateForm, 'Complementos de resgate'),
}


def dados_tipo(tipo):
    try:
        return TIPOS[tipo]
    except KeyError:
        raise Http404('Tipo de registro desconhecido.')


@login_required
def inicio(request):
    return redirect('registros:lista', tipo='castracoes')


@login_required
def lista(request, tipo):
    modelo, _, titulo = dados_tipo(tipo)
    busca = request.GET.get('busca', '').strip()
    if tipo == 'resgates':
        registros = modelo.objects.select_related('resgate__pet')
        if busca:
            registros = registros.filter(Q(resgate__pet__nome__icontains=busca) | Q(resgate__local__icontains=busca))
    else:
        registros = modelo.objects.select_related('pet')
        if busca:
            registros = registros.filter(pet__nome__icontains=busca)
    return render(request, 'registros/lista.html', {
        'tipo': tipo, 'titulo': titulo, 'registros': registros[:100], 'busca': busca,
        'total': registros.count(),
    })


@login_required
def criar(request, tipo):
    _, formulario, titulo = dados_tipo(tipo)

    # Fluxo integrado: cria o resgate original e o complemento juntos.
    # O formulário antigo continua disponível com ?existente=1.
    modo_existente = (
        request.GET.get('existente') == '1'
        or bool(request.GET.get('resgate_id'))
        or request.POST.get('modo') == 'existente'
        or bool(request.POST.get('resgate'))
    )
    if tipo == 'resgates' and not modo_existente:
        form = ResgateCompletoForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            dados = form.cleaned_data
            with transaction.atomic():
                resgate = Resgate.objects.create(
                    pet=dados['pet_principal'],
                    data_resgate=dados['data_resgate'],
                    local=dados['local_resgate'],
                    descricao=dados.get('descricao_resgate') or None,
                    observacoes=dados.get('observacoes_resgate') or None,
                    is_active=True,
                )
                complemento = form.save(commit=False)
                complemento.resgate = resgate
                complemento.save()
                form.save_m2m()
            messages.success(request, 'Resgate e seus detalhes cadastrados com sucesso.')
            return redirect('registros:lista', tipo='resgates')
        return render(request, 'registros/formulario.html', {
            'tipo': tipo, 'titulo': 'Resgate completo', 'form': form,
            'edicao': False, 'novo_resgate': True,
        })
    initial = {}
    if tipo == 'resgates' and request.GET.get('resgate_id'):
        initial['resgate'] = request.GET.get('resgate_id')
    elif tipo != 'resgates' and request.GET.get('pet_id'):
        initial['pet'] = request.GET.get('pet_id')
    form = formulario(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Registro criado com sucesso.')
        return redirect('registros:lista', tipo=tipo)
    return render(request, 'registros/formulario.html', {
        'tipo': tipo, 'titulo': titulo, 'form': form, 'edicao': False,
        'modo_existente': modo_existente,
        'pet_sexos': dict(Pet.objects.values_list('id', 'sexo')) if tipo == 'castracoes' else {},
    })


@login_required
def editar(request, tipo, pk):
    modelo, formulario, titulo = dados_tipo(tipo)
    obj = get_object_or_404(modelo, pk=pk)
    form = formulario(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Registro atualizado com sucesso.')
        return redirect('registros:lista', tipo=tipo)
    return render(request, 'registros/formulario.html', {
        'tipo': tipo, 'titulo': titulo, 'form': form, 'edicao': True,
        'pet_sexos': dict(Pet.objects.values_list('id', 'sexo')) if tipo == 'castracoes' else {},
    })
