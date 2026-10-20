from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.urls import reverse

from .models import Pessoa, Usuario


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

    pessoas = Pessoa.objects.filter(
        is_active=True
    ).prefetch_related('vinculos_pets__pet')

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
        'is_active': request.POST.get('is_active') == 'true',
        'is_attendance_responsible': (
            request.POST.get('is_attendance_responsible') == 'on'
        ),
    }

    possui_acesso = request.POST.get('possui_acesso') == '1'
    senha = request.POST.get('senha', '')
    confirmar_senha = request.POST.get('confirmar_senha', '')
    usuario_is_active = (
        request.POST.get('usuario_is_active') == 'true'
    )

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

    if possui_acesso:
        if not senha:
            messages.error(
                request,
                'Informe a senha para criar o acesso ao sistema.'
            )
            return render(
                request,
                'pessoas/formulario.html',
                {'dados': dados}
            )

        if senha != confirmar_senha:
            messages.error(
                request,
                'A senha e a confirmação não coincidem.'
            )
            return render(
                request,
                'pessoas/formulario.html',
                {'dados': dados}
            )

        if len(senha) < 8:
            messages.error(
                request,
                'A senha deve possuir pelo menos 8 caracteres.'
            )
            return render(
                request,
                'pessoas/formulario.html',
                {'dados': dados}
            )

    try:
        with transaction.atomic():
            pessoa = Pessoa.objects.create(**dados)

            if possui_acesso:
                usuario = Usuario(
                    pessoa=pessoa,
                    is_active=usuario_is_active,
                )
                usuario.set_password(senha)
                usuario.save()

        messages.success(
            request,
            'Cadastro efetuado com sucesso.'
        )
        return redirect(
            'pessoas:editar',
            pessoa_id=pessoa.id,
        )

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


@login_required
def editar(request, pessoa_id):
    pessoa = get_object_or_404(Pessoa, pk=pessoa_id)

    usuario = Usuario.objects.filter(pessoa=pessoa).first()

    if request.method == 'POST':
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
            'is_active': request.POST.get('is_active') == 'true',
            'is_attendance_responsible': (
                request.POST.get('is_attendance_responsible') == 'on'
            ),
        }

        possui_acesso = request.POST.get('possui_acesso') == '1'
        senha = request.POST.get('senha', '')
        confirmar_senha = request.POST.get('confirmar_senha', '')
        usuario_is_active = (
            request.POST.get('usuario_is_active') == 'true'
        )

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
                {
                    'pessoa': pessoa,
                    'dados': dados,
                    'usuario': usuario,
                    'possui_acesso': possui_acesso,
                    'usuario_is_active': usuario_is_active,
                }
            )

        if possui_acesso and usuario is None:
            if not senha:
                messages.error(
                    request,
                    'Informe uma senha para criar o acesso.'
                )
                return render(
                    request,
                    'pessoas/formulario.html',
                    {
                        'pessoa': pessoa,
                        'dados': dados,
                        'usuario': usuario,
                        'possui_acesso': possui_acesso,
                        'usuario_is_active': usuario_is_active,
                    }
                )

            if senha != confirmar_senha:
                messages.error(
                    request,
                    'A senha e a confirmação não coincidem.'
                )
                return render(
                    request,
                    'pessoas/formulario.html',
                    {
                        'pessoa': pessoa,
                        'dados': dados,
                        'usuario': usuario,
                        'possui_acesso': possui_acesso,
                        'usuario_is_active': usuario_is_active,
                    }
                )

            if len(senha) < 8:
                messages.error(
                    request,
                    'A senha deve possuir pelo menos 8 caracteres.'
                )
                return render(
                    request,
                    'pessoas/formulario.html',
                    {
                        'pessoa': pessoa,
                        'dados': dados,
                        'usuario': usuario,
                        'possui_acesso': possui_acesso,
                        'usuario_is_active': usuario_is_active,
                    }
                )

        elif possui_acesso and senha:
            if senha != confirmar_senha:
                messages.error(
                    request,
                    'A senha e a confirmação não coincidem.'
                )
                return render(
                    request,
                    'pessoas/formulario.html',
                    {
                        'pessoa': pessoa,
                        'dados': dados,
                        'usuario': usuario,
                        'possui_acesso': possui_acesso,
                        'usuario_is_active': usuario_is_active,
                    }
                )

            if len(senha) < 8:
                messages.error(
                    request,
                    'A senha deve possuir pelo menos 8 caracteres.'
                )
                return render(
                    request,
                    'pessoas/formulario.html',
                    {
                        'pessoa': pessoa,
                        'dados': dados,
                        'usuario': usuario,
                        'possui_acesso': possui_acesso,
                        'usuario_is_active': usuario_is_active,
                    }
                )

        try:
            with transaction.atomic():
                for campo, valor in dados.items():
                    setattr(pessoa, campo, valor)

                pessoa.save()

                if usuario:
                    # Não exclui o usuário existente.
                    # Desmarcar "Possui acesso" suspende o login.
                    usuario.is_active = (
                        possui_acesso
                        and usuario_is_active
                        and pessoa.is_active
                    )

                    if possui_acesso and senha:
                        usuario.set_password(senha)

                    usuario.save()

                elif possui_acesso:
                    usuario = Usuario(
                        pessoa=pessoa,
                        is_active=(
                            usuario_is_active and pessoa.is_active
                        ),
                    )
                    usuario.set_password(senha)
                    usuario.save()

            messages.success(
                request,
                'Cadastro atualizado com sucesso.'
            )
            return redirect(
                'pessoas:editar',
                pessoa_id=pessoa.id,
            )

        except IntegrityError:
            messages.error(
                request,
                'Não foi possível atualizar. Verifique se o CPF, '
                'e-mail ou telefone já pertence a outra pessoa.'
            )

            return render(
                request,
                'pessoas/formulario.html',
                {
                    'pessoa': pessoa,
                    'dados': dados,
                    'usuario': usuario,
                    'possui_acesso': possui_acesso,
                    'usuario_is_active': usuario_is_active,
                }
            )

    dados = {
        campo: getattr(pessoa, campo)
        for campo in [
            'nome', 'cpf', 'email', 'telefone', 'cep',
            'endereco', 'numero', 'complemento', 'bairro',
            'cidade', 'estado', 'is_active',
            'is_attendance_responsible',
        ]
    }

    reativar_pessoa = request.GET.get('reativar') == '1'
    if reativar_pessoa:
        dados['is_active'] = True

    return render(
        request,
        'pessoas/formulario.html',
        {
            'pessoa': pessoa,
            'dados': dados,
            'usuario': usuario,
            'possui_acesso': (
                    usuario is not None and usuario.is_active
            ),
            'usuario_is_active': (
                usuario.is_active if usuario else False
            ),
        }
    )


@login_required
def inativar(request, pessoa_id):
    if request.method != 'POST':
        return redirect('pessoas:lista')

    pessoa = get_object_or_404(
        Pessoa,
        pk=pessoa_id,
        is_active=True,
    )

    with transaction.atomic():
        pessoa.is_active = False
        pessoa.save(update_fields=['is_active', 'updated_at'])

        Usuario.objects.filter(
            pessoa=pessoa
        ).update(is_active=False)

    messages.success(
        request,
        'Cadastro excluído com sucesso.'
    )

    return redirect('pessoas:lista')


@login_required
@require_GET
def consultar_cpf(request):
    cpf = request.GET.get('cpf', '')
    numeros = ''.join(c for c in cpf if c.isdigit())

    if len(numeros) != 11:
        return JsonResponse({
            'encontrado': False,
            'erro': 'CPF inválido.',
        }, status=400)

    cpf_formatado = (
        f'{numeros[:3]}.{numeros[3:6]}.'
        f'{numeros[6:9]}-{numeros[9:]}'
    )

    pessoa = Pessoa.objects.filter(cpf=cpf_formatado).first()

    if not pessoa:
        return JsonResponse({
            'encontrado': False,
        })

    return JsonResponse({
        'encontrado': True,
        'pessoa_id': pessoa.pk,
        'nome': pessoa.nome,
        'is_active': pessoa.is_active,
        'url_editar': reverse(
            'pessoas:editar',
            kwargs={'pessoa_id': pessoa.pk},
        ),
    })