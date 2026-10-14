
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction

from .models import Pessoa


def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    erro = None

    if request.method == 'POST':
        identificador = request.POST.get('username', '').strip()
        senha = request.POST.get('password', '')

        usuario = authenticate(
            request,
            username=identificador,
            password=senha,
        )

        if usuario is not None:
            login(request, usuario)

            if request.POST.get('lembrar_me') == 'on':
                # Mantém a sessão por 14 dias.
                request.session.set_expiry(60 * 60 * 24 * 14)
            else:
                # Expira a sessão ao fechar o navegador.
                request.session.set_expiry(0)

            return redirect('inicio')

        erro = 'Usuário ou senha inválidos.'

    return render(
        request,
        'registration/login.html',
        {'erro': erro},
    )



@login_required
def lista(request):
    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 20))
    except (TypeError, ValueError):
        por_pagina = 20

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 20

    pessoas = Pessoa.objects.prefetch_related(
        'vinculos_pets__pet'
    ).all()

    if busca:
        pessoas = pessoas.filter(
            Q(nome__icontains=busca)
            | Q(cpf__icontains=busca)
            | Q(telefone__icontains=busca)
            | Q(vinculos_pets__pet__nome__icontains=busca)
        ).distinct()

    paginator = Paginator(pessoas, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(
        request,
        'pessoas/lista.html',
        {
            'pessoas': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'busca': busca,
            'por_pagina': por_pagina,
        },
    )


@login_required
def adicionar(request):
    if request.method != 'POST':
        return render(request, 'pessoas/formulario.html')

    dados = {
        'nome': request.POST.get('nome', '').strip(),
        'cpf': request.POST.get('cpf', '').strip(),
        'email': request.POST.get('email', '').strip(),
        'telefone': request.POST.get('telefone', '').strip(),
        'cep': request.POST.get('cep', '').strip(),
        'endereco': request.POST.get('endereco', '').strip(),
        'numero': request.POST.get('numero', '').strip(),
        'complemento': request.POST.get('complemento', '').strip() or None,
        'bairro': request.POST.get('bairro', '').strip(),
        'cidade': request.POST.get('cidade', '').strip(),
        'estado': request.POST.get('estado', '').strip(),
        'is_attendance_responsible': (
            request.POST.get('is_attendance_responsible') == 'on'
        ),
    }

    obrigatorios = [
        'nome', 'cpf', 'email', 'telefone', 'cep',
        'endereco', 'numero', 'bairro', 'cidade', 'estado',
    ]

    if any(not dados[campo] for campo in obrigatorios):
        messages.error(
            request,
            'Preencha todos os campos obrigatórios.'
        )
        return render(
            request,
            'pessoas/formulario.html',
            {'dados': dados}
        )

    try:
        with transaction.atomic():
            Pessoa.objects.create(
                **dados,
                is_active=True
            )

        messages.success(request, 'Pessoa cadastrada com sucesso!')
        return redirect('pessoas:lista')

    except IntegrityError:
        messages.error(
            request,
            'Não foi possível cadastrar. Verifique se o CPF, '
            'e-mail ou telefone já está cadastrado.'
        )

        return render(
            request,
            'pessoas/formulario.html',
            {'dados': dados}
        )
