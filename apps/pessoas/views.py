
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

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

    pessoas = Pessoa.objects.all()

    if busca:
        pessoas = pessoas.filter(
            Q(nome__icontains=busca)
            | Q(cpf__icontains=busca)
            | Q(telefone__icontains=busca)
        )

    return render(
        request,
        'pessoas/lista.html',
        {
            'pessoas': pessoas,
            'busca': busca,
        },
    )
