from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.pessoas.models import Pessoa
from apps.fornecedores.models import Fornecedor
from apps.medicamentos.models import Medicamento

from .models import EntradaEstoque


@login_required
def lista(request):
    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 20))
    except (TypeError, ValueError):
        por_pagina = 20

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 20

    entradas = EntradaEstoque.objects.annotate(
        total_lotes=Count('lotes')
    )

    if busca:
        entradas = entradas.filter(
            Q(tipo_origem__icontains=busca)
            | Q(numero_nota_fiscal__icontains=busca)
            | Q(observacoes__icontains=busca)
            | Q(pessoa__nome__icontains=busca)
            | Q(fornecedor__razao_social__icontains=busca)
            | Q(fornecedor__nome_fantasia__icontains=busca)
        )

    entradas = entradas.order_by('-data', '-pk')

    paginator = Paginator(entradas, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(
        request,
        'estoque/lista.html',
        {
            'entradas': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'busca': busca,
            'por_pagina': por_pagina,
        },
    )


@login_required
def adicionar(request):
    if request.method != 'POST':
        return render(
            request,
            'estoque/formulario.html',
            {
                'dados': {
                    'tipo_origem': 'DOACAO',
                    'tipo_pessoa_origem': '',
                    'data': date.today().isoformat(),
                    'numero_nota_fiscal': '',
                    'observacoes': '',
                    'pessoa_id': '',
                    'fornecedor_id': '',
                },
                'pessoas': Pessoa.objects.filter(is_active=True),
                'fornecedores': Fornecedor.objects.filter(is_active=True),
            },
        )

    dados = {
        'tipo_origem': request.POST.get('tipo_origem', '').strip(),
        'tipo_pessoa_origem': request.POST.get(
            'tipo_pessoa_origem',
            '',
        ).strip(),
        'data': request.POST.get('data', '').strip(),
        'numero_nota_fiscal': (
            request.POST.get('numero_nota_fiscal', '').strip() or None
        ),
        'observacoes': request.POST.get('observacoes', '').strip() or None,
    }

    pessoa_id = request.POST.get('pessoa_id', '').strip()
    fornecedor_id = request.POST.get('fornecedor_id', '').strip()

    contexto = {
        'dados': {
            **dados,
            'pessoa_id': pessoa_id,
            'fornecedor_id': fornecedor_id,
        },
        'pessoas': Pessoa.objects.filter(is_active=True),
        'fornecedores': Fornecedor.objects.filter(is_active=True),
    }

    tipos_validos = dict(EntradaEstoque.TIPO_ORIGEM_CHOICES)

    if dados['tipo_origem'] not in tipos_validos:
        messages.error(request, 'Selecione um tipo de origem válido.')
        return render(request, 'estoque/formulario.html', contexto)

    try:
        data_entrada = date.fromisoformat(dados['data'])
    except (TypeError, ValueError):
        messages.error(request, 'Informe uma data válida para a entrada.')
        return render(request, 'estoque/formulario.html', contexto)

    # Nesta etapa, exigimos uma pessoa ou um fornecedor.
    # A escolha não é determinada automaticamente pelo tipo de origem.
    tipo_pessoa_origem = dados['tipo_pessoa_origem']

    if tipo_pessoa_origem not in ('PESSOA', 'FORNECEDOR'):
        messages.error(
            request,
            'Selecione Pessoa Física ou Pessoa Jurídica (Fornecedor).',
        )
        return render(request, 'estoque/formulario.html', contexto)

    if tipo_pessoa_origem == 'PESSOA':
        if not pessoa_id:
            messages.error(request, 'Selecione uma pessoa.')
            return render(request, 'estoque/formulario.html', contexto)

        fornecedor_id = ''

    elif tipo_pessoa_origem == 'FORNECEDOR':
        if not fornecedor_id:
            messages.error(request, 'Selecione um fornecedor.')
            return render(request, 'estoque/formulario.html', contexto)

        pessoa_id = ''

    contexto['dados']['pessoa_id'] = pessoa_id
    contexto['dados']['fornecedor_id'] = fornecedor_id

    pessoa = None
    fornecedor = None

    try:
        if pessoa_id:
            pessoa = Pessoa.objects.get(
                pk=int(pessoa_id),
                is_active=True,
            )

        if fornecedor_id:
            fornecedor = Fornecedor.objects.get(
                pk=int(fornecedor_id),
                is_active=True,
            )

    except (Pessoa.DoesNotExist, Fornecedor.DoesNotExist, ValueError, TypeError):
        messages.error(
            request,
            'A pessoa ou o fornecedor selecionado não é válido ou está inativo.',
        )
        return render(request, 'estoque/formulario.html', contexto)

    try:
        with transaction.atomic():
            entrada = EntradaEstoque.objects.create(
                tipo_origem=dados['tipo_origem'],
                data=data_entrada,
                numero_nota_fiscal=dados['numero_nota_fiscal'],
                observacoes=dados['observacoes'],
                pessoa=pessoa,
                fornecedor=fornecedor,
            )

        messages.success(request, 'Entrada de estoque cadastrada com sucesso.')

        return redirect(
            'estoque:editar',
            entrada_id=entrada.pk,
        )

    except IntegrityError:
        messages.error(
            request,
            'Não foi possível cadastrar a entrada de estoque.',
        )
        return render(request, 'estoque/formulario.html', contexto)


@login_required
def editar(request, entrada_id):
    entrada = get_object_or_404(
        EntradaEstoque,
        pk=entrada_id,
    )

    if request.method == 'POST':
        dados = {
            'tipo_origem': request.POST.get('tipo_origem', '').strip(),
            'data': request.POST.get('data', '').strip(),
            'numero_nota_fiscal': (
                request.POST.get('numero_nota_fiscal', '').strip() or None
            ),
            'observacoes': request.POST.get('observacoes', '').strip() or None,
        }

        pessoa_id = request.POST.get('pessoa_id', '').strip()
        fornecedor_id = request.POST.get('fornecedor_id', '').strip()

        contexto = {
            'entrada': entrada,
            'dados': {
                **dados,
                'pessoa_id': pessoa_id,
                'fornecedor_id': fornecedor_id,
            },
            'pessoas': Pessoa.objects.filter(is_active=True),
            'fornecedores': Fornecedor.objects.filter(is_active=True),
        }

        tipos_validos = dict(EntradaEstoque.TIPO_ORIGEM_CHOICES)

        if dados['tipo_origem'] not in tipos_validos:
            messages.error(request, 'Selecione um tipo de origem válido.')
            return render(request, 'estoque/formulario.html', contexto)

        try:
            data_entrada = date.fromisoformat(dados['data'])
        except (TypeError, ValueError):
            messages.error(request, 'Informe uma data válida para a entrada.')
            return render(request, 'estoque/formulario.html', contexto)

        if bool(pessoa_id) == bool(fornecedor_id):
            messages.error(
                request,
                'Selecione uma pessoa ou um fornecedor para a entrada.',
            )
            return render(request, 'estoque/formulario.html', contexto)

        pessoa = None
        fornecedor = None

        try:
            if pessoa_id:
                pessoa = Pessoa.objects.get(
                    pk=int(pessoa_id),
                    is_active=True,
                )

            if fornecedor_id:
                fornecedor = Fornecedor.objects.get(
                    pk=int(fornecedor_id),
                    is_active=True,
                )

        except (
            Pessoa.DoesNotExist,
            Fornecedor.DoesNotExist,
            ValueError,
            TypeError,
        ):
            messages.error(
                request,
                'A pessoa ou o fornecedor selecionado não é válido ou está inativo.',
            )
            return render(request, 'estoque/formulario.html', contexto)

        try:
            with transaction.atomic():
                entrada.tipo_origem = dados['tipo_origem']
                entrada.data = data_entrada
                entrada.numero_nota_fiscal = dados['numero_nota_fiscal']
                entrada.observacoes = dados['observacoes']
                entrada.pessoa = pessoa
                entrada.fornecedor = fornecedor

                entrada.save()

            messages.success(
                request,
                'Entrada de estoque atualizada com sucesso.',
            )

            return redirect(
                'estoque:editar',
                entrada_id=entrada.pk,
            )

        except IntegrityError:
            messages.error(
                request,
                'Não foi possível atualizar a entrada de estoque.',
            )

    else:
        dados = {
            'tipo_origem': entrada.tipo_origem,
            'data': entrada.data.isoformat(),
            'numero_nota_fiscal': entrada.numero_nota_fiscal or '',
            'observacoes': entrada.observacoes or '',
            'pessoa_id': entrada.pessoa_id or '',
            'fornecedor_id': entrada.fornecedor_id or '',
        }

        contexto = {
            'entrada': entrada,
            'dados': dados,
            'pessoas': Pessoa.objects.filter(is_active=True),
            'fornecedores': Fornecedor.objects.filter(is_active=True),
        }

    return render(
        request,
        'estoque/formulario.html',
        contexto,
    )


@login_required
@require_POST
def excluir(request, entrada_id):
    entrada = get_object_or_404(
        EntradaEstoque,
        pk=entrada_id,
    )

    if entrada.lotes.exists():
        messages.error(
            request,
            'Não é possível excluir esta entrada porque existem '
            'lotes associados a ela.',
        )
        return redirect('estoque:lista')

    try:
        with transaction.atomic():
            entrada.delete()

        messages.success(
            request,
            'Entrada de estoque excluída com sucesso.',
        )

    except IntegrityError:
        messages.error(
            request,
            'Não foi possível excluir esta entrada porque existem '
            'registros associados a ela.',
        )

    return redirect('estoque:lista')
