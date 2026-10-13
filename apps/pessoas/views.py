
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

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

