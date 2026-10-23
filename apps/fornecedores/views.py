from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Value
from django.db.models.functions import Replace
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.urls import reverse

from .models import Fornecedor


@login_required
def lista(request):
    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 10))
    except (ValueError, TypeError):
        por_pagina = 10

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 10

    fornecedores = Fornecedor.objects.filter(is_active=True)

    if busca:
        cnpj_numeros = ''.join(
            caractere for caractere in busca
            if caractere.isdigit()
        )

        filtros = (
                Q(razao_social__icontains=busca)
                | Q(nome_fantasia__icontains=busca)
                | Q(email__icontains=busca)
                | Q(telefone__icontains=busca)
        )

        # Pesquisa o CNPJ sem pontos, barra e hífen.
        cnpj_sem_formatacao = Replace(
            Replace(
                Replace(
                    Replace('cnpj', Value('.')),
                    Value('/'),
                    Value('')
                ),
                Value('-'),
                Value('')
            ),
            Value(' '),
            Value('')
        )

        if cnpj_numeros:
            filtros |= Q(**{
                'cnpj__icontains': busca
            })
            filtros |= Q(
                **{'id__in': Fornecedor.objects.annotate(
                    cnpj_limpo=cnpj_sem_formatacao
                ).filter(
                    cnpj_limpo__icontains=cnpj_numeros
                ).values('id')}
            )

        fornecedores = fornecedores.filter(filtros)

    fornecedores = fornecedores.order_by('razao_social')

    paginator = Paginator(fornecedores, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'fornecedores/lista.html',
        {
            'fornecedores': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'busca': busca,
            'por_pagina': por_pagina,
        },
    )


def normalizar_cnpj(valor):
    return ''.join(caractere for caractere in valor if caractere.isdigit())


def formatar_cnpj(cnpj):
    numeros = normalizar_cnpj(cnpj)

    if len(numeros) != 14:
        return cnpj

    return (
        f'{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/'
        f'{numeros[8:12]}-{numeros[12:]}'
    )


@login_required
def consultar_cnpj(request):
    cnpj_recebido = request.GET.get('cnpj', '')
    cnpj = normalizar_cnpj(cnpj_recebido)

    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return JsonResponse({
            'encontrado': False,
            'erro': 'Informe um CNPJ com 14 dígitos.',
            'quantidade_digitos': len(cnpj),
        })

    # Localiza o fornecedor pelo CNPJ, considerando apenas os números.
    fornecedor = next(
        (
            item
            for item in Fornecedor.objects.all().only(
                'id',
                'razao_social',
                'nome_fantasia',
                'cnpj',
                'is_active',
            )
            if normalizar_cnpj(item.cnpj) == cnpj
        ),
        None,
    )

    if not fornecedor:
        return JsonResponse({
            'encontrado': False,
        })

    return JsonResponse({
        'encontrado': True,
        'fornecedor_id': fornecedor.id,
        'nome': fornecedor.nome_fantasia or fornecedor.razao_social,
        'razao_social': fornecedor.razao_social,
        'is_active': fornecedor.is_active,
        'url_editar': reverse(
            'fornecedores:editar',
            args=[fornecedor.id],
        ),
    })


@login_required
def adicionar(request):
    dados = {}

    if request.method == 'POST':
        dados = {
            'razao_social': request.POST.get('razao_social', '').strip(),
            'nome_fantasia': request.POST.get('nome_fantasia', '').strip(),
            'cnpj': request.POST.get('cnpj', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'telefone': request.POST.get('telefone', '').strip(),
            'observacoes': request.POST.get('observacoes', '').strip(),
        }

        erros = []

        cnpj_numeros = normalizar_cnpj(dados['cnpj'])

        if not dados['razao_social']:
            erros.append('Informe a razão social.')

        if not dados['nome_fantasia']:
            erros.append('Informe o nome fantasia.')

        if len(cnpj_numeros) != 14:
            erros.append('Informe um CNPJ válido com 14 dígitos.')
        elif cnpj_numeros == cnpj_numeros[0] * 14:
            erros.append('Informe um CNPJ válido.')

        if dados['email']:
            try:
                validate_email(dados['email'])
            except ValidationError:
                erros.append('Informe um endereço de e-mail válido.')

        if len(dados['razao_social']) > 150:
            erros.append('A razão social deve ter no máximo 150 caracteres.')

        if len(dados['nome_fantasia']) > 100:
            erros.append('O nome fantasia deve ter no máximo 100 caracteres.')

        if len(dados['telefone']) > 20:
            erros.append('O telefone deve ter no máximo 20 caracteres.')

        if len(dados['email']) > 100:
            erros.append('O e-mail deve ter no máximo 100 caracteres.')

        if not erros:
            # Procura o CNPJ independentemente da máscara utilizada.
            fornecedor_existente = next(
                (
                    fornecedor
                    for fornecedor in Fornecedor.objects.all().only(
                        'id', 'cnpj', 'is_active'
                    )
                    if normalizar_cnpj(fornecedor.cnpj) == cnpj_numeros
                ),
                None,
            )

            if fornecedor_existente and fornecedor_existente.is_active:
                messages.error(
                    request,
                    'Já existe um fornecedor ativo cadastrado com esse CNPJ.'
                )
            else:
                try:
                    with transaction.atomic():
                        if fornecedor_existente:
                            fornecedor = Fornecedor.objects.get(
                                pk=fornecedor_existente.pk
                            )
                            mensagem = 'Fornecedor existente atualizado e reativado.'
                        else:
                            fornecedor = Fornecedor()
                            mensagem = 'Fornecedor cadastrado com sucesso.'

                        fornecedor.razao_social = dados['razao_social']
                        fornecedor.nome_fantasia = dados['nome_fantasia']
                        fornecedor.cnpj = formatar_cnpj(cnpj_numeros)
                        fornecedor.email = dados['email'] or None
                        fornecedor.telefone = dados['telefone'] or None
                        fornecedor.observacoes = dados['observacoes'] or None
                        fornecedor.is_active = True
                        fornecedor.save()

                    messages.success(request, mensagem)
                    return redirect('fornecedores:lista')

                except Exception:
                    messages.error(
                        request,
                        'Não foi possível salvar o fornecedor. '
                        'Verifique os dados e tente novamente.'
                    )

        for erro in erros:
            messages.error(request, erro)

    return render(
        request,
        'fornecedores/formulario.html',
        {
            'dados': dados,
            'fornecedor': None,
        },
    )



@login_required
def editar(request, fornecedor_id):
    fornecedor = get_object_or_404(
        Fornecedor,
        pk=fornecedor_id,
    )

    reativar = (
        request.GET.get('reativar') == '1'
        or request.POST.get('reativar') == '1'
    )

    dados = {
        'razao_social': fornecedor.razao_social,
        'nome_fantasia': fornecedor.nome_fantasia,
        'cnpj': fornecedor.cnpj,
        'email': fornecedor.email or '',
        'telefone': fornecedor.telefone or '',
        'observacoes': fornecedor.observacoes or '',
    }

    erros = []

    if request.method == 'POST':
        dados = {
            'razao_social': request.POST.get('razao_social', '').strip(),
            'nome_fantasia': request.POST.get('nome_fantasia', '').strip(),
            'cnpj': request.POST.get('cnpj', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'telefone': request.POST.get('telefone', '').strip(),
            'observacoes': request.POST.get('observacoes', '').strip(),
        }

        cnpj_numeros = normalizar_cnpj(dados['cnpj'])

        if not dados['razao_social']:
            erros.append('Informe a razão social.')

        if len(dados['razao_social']) > 150:
            erros.append('A razão social deve ter no máximo 150 caracteres.')

        if not dados['nome_fantasia']:
            erros.append('Informe o nome fantasia.')

        if len(dados['nome_fantasia']) > 100:
            erros.append('O nome fantasia deve ter no máximo 100 caracteres.')

        if len(cnpj_numeros) != 14:
            erros.append('Informe um CNPJ válido com 14 dígitos.')
        elif cnpj_numeros == cnpj_numeros[0] * 14:
            erros.append('Informe um CNPJ válido.')

        if dados['email']:
            try:
                validate_email(dados['email'])
            except ValidationError:
                erros.append('Informe um endereço de e-mail válido.')

        if len(dados['email']) > 100:
            erros.append('O e-mail deve ter no máximo 100 caracteres.')

        if len(dados['telefone']) > 20:
            erros.append('O telefone deve ter no máximo 20 caracteres.')

        # Impede que o CNPJ seja alterado para o de outro fornecedor.
        if len(cnpj_numeros) == 14:
            for outro in Fornecedor.objects.exclude(pk=fornecedor.pk).only(
                'id', 'cnpj'
            ):
                if normalizar_cnpj(outro.cnpj) == cnpj_numeros:
                    erros.append(
                        'Este CNPJ já está cadastrado em outro fornecedor.'
                    )
                    break

        if not erros:
            try:
                with transaction.atomic():
                    fornecedor.razao_social = dados['razao_social']
                    fornecedor.nome_fantasia = dados['nome_fantasia']
                    fornecedor.cnpj = formatar_cnpj(cnpj_numeros)
                    fornecedor.email = dados['email'] or None
                    fornecedor.telefone = dados['telefone'] or None
                    fornecedor.observacoes = dados['observacoes'] or None

                    # Reativa somente quando a intenção foi confirmada
                    # e o formulário foi salvo.
                    if reativar:
                        fornecedor.is_active = True

                    fornecedor.save()

                messages.success(
                    request,
                    'Fornecedor atualizado com sucesso.'
                    if not reativar
                    else 'Fornecedor reativado e atualizado com sucesso.'
                )
                return redirect('fornecedores:lista')

            except Exception:
                messages.error(
                    request,
                    'Não foi possível salvar as alterações. '
                    'Verifique os dados e tente novamente.'
                )

        for erro in erros:
            messages.error(request, erro)

    return render(
        request,
        'fornecedores/formulario.html',
        {
            'dados': dados,
            'fornecedor': fornecedor,
            'reativar': reativar,
        },
    )


@login_required
def inativar(request, fornecedor_id):
    if request.method != 'POST':
        return redirect('fornecedores:lista')

    fornecedor = get_object_or_404(
        Fornecedor,
        pk=fornecedor_id,
        is_active=True,
    )

    fornecedor.is_active = False
    fornecedor.save(update_fields=['is_active', 'updated_at'])

    messages.success(
        request,
        'Fornecedor inativado com sucesso.',
    )

    return redirect('fornecedores:lista')
