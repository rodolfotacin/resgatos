from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction

from .models import Medicamento


@login_required
def lista(request):
    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 20))
    except (TypeError, ValueError):
        por_pagina = 20

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 20

    medicamentos = Medicamento.objects.filter(
        is_active=True
    )

    if busca:
        medicamentos = medicamentos.filter(
            Q(nome__icontains=busca)
            | Q(principio_ativo__icontains=busca)
            | Q(fabricante__icontains=busca)
        )

    medicamentos = medicamentos.order_by('nome')

    paginator = Paginator(medicamentos, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'medicamentos/lista.html',
        {
            'medicamentos': page_obj.object_list,
            'busca': busca,
            'por_pagina': por_pagina,
            'page_obj': page_obj,
            'paginator': paginator,
        }
    )


@login_required
def adicionar(request):
    dados = {
        'nome': '',
        'principio_ativo': '',
        'concentracao': '',
        'forma_farmaceutica': '',
        'fabricante': '',
        'unidade_medida': '',
        'estoque_minimo': '0.00',
        'observacoes': '',
    }

    if request.method == 'POST':
        dados = {
            'nome': request.POST.get('nome', '').strip(),
            'principio_ativo': request.POST.get(
                'principio_ativo', ''
            ).strip(),
            'concentracao': request.POST.get(
                'concentracao', ''
            ).strip(),
            'forma_farmaceutica': request.POST.get(
                'forma_farmaceutica', ''
            ).strip(),
            'fabricante': request.POST.get(
                'fabricante', ''
            ).strip(),
            'unidade_medida': request.POST.get(
                'unidade_medida', ''
            ).strip(),
            'estoque_minimo': request.POST.get(
                'estoque_minimo', '0'
            ).strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
        }

        obrigatorios = [
            'nome',
            'principio_ativo',
            'concentracao',
            'forma_farmaceutica',
            'unidade_medida',
        ]

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )
            return render(
                request,
                'medicamentos/formulario.html',
                {'dados': dados},
            )

        try:
            estoque_minimo = Decimal(dados['estoque_minimo'])

            if (
                not estoque_minimo.is_finite()
                or estoque_minimo < 0
                or estoque_minimo.as_tuple().exponent < -2
                or estoque_minimo >= Decimal('100000000')
            ):
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            messages.error(
                request,
                'Informe quantidades de estoque válidas, '
                'não negativas e com no máximo duas casas decimais.'
            )
            return render(
                request,
                'medicamentos/formulario.html',
                {'dados': dados},
            )

        try:
            with transaction.atomic():
                Medicamento.objects.create(
                    nome=dados['nome'],
                    principio_ativo=dados['principio_ativo'],
                    concentracao=dados['concentracao'],
                    forma_farmaceutica=dados['forma_farmaceutica'],
                    fabricante=dados['fabricante'],
                    unidade_medida=dados['unidade_medida'],
                    estoque_atual=Decimal('0.00'),
                    estoque_minimo=estoque_minimo,
                    observacoes=dados['observacoes'] or None,
                    is_active=True,
                )

            messages.success(
                request,
                'Medicamento cadastrado com sucesso.'
            )
            return redirect('medicamentos:lista')

        except Exception:
            messages.error(
                request,
                'Não foi possível cadastrar o medicamento. '
                'Verifique os dados informados.'
            )
            return render(
                request,
                'medicamentos/formulario.html',
                {'dados': dados},
            )

    return render(
        request,
        'medicamentos/formulario.html',
        {'dados': dados},
    )



@login_required
def editar(request, pk):
    medicamento = get_object_or_404(
        Medicamento,
        pk=pk,
        is_active=True
    )

    dados = {
        'nome': medicamento.nome,
        'principio_ativo': medicamento.principio_ativo,
        'concentracao': medicamento.concentracao,
        'forma_farmaceutica': medicamento.forma_farmaceutica,
        'fabricante': medicamento.fabricante,
        'unidade_medida': medicamento.unidade_medida,
        'estoque_minimo': str(medicamento.estoque_minimo),
        'observacoes': medicamento.observacoes or '',
    }

    if request.method == 'POST':
        dados = {
            'nome': request.POST.get('nome', '').strip(),
            'principio_ativo': request.POST.get('principio_ativo', '').strip(),
            'concentracao': request.POST.get('concentracao', '').strip(),
            'forma_farmaceutica': request.POST.get('forma_farmaceutica', '').strip(),
            'fabricante': request.POST.get('fabricante', '').strip(),
            'unidade_medida': request.POST.get('unidade_medida', '').strip(),
            'estoque_minimo': request.POST.get('estoque_minimo', '0').strip(),
            'observacoes': request.POST.get('observacoes', '').strip(),
        }

        obrigatorios = [
            'nome',
            'principio_ativo',
            'concentracao',
            'forma_farmaceutica',
            'unidade_medida',
        ]

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )
            return render(
                request,
                'medicamentos/formulario.html',
                {'medicamento': medicamento, 'dados': dados}
            )

        try:
            estoque_minimo = Decimal(dados['estoque_minimo'])

            if (
                not estoque_minimo.is_finite()
                or estoque_minimo < 0
                or estoque_minimo.as_tuple().exponent < -2
                or estoque_minimo >= Decimal('100000000')
            ):
                raise InvalidOperation

        except (InvalidOperation, ValueError):
            messages.error(
                request,
                'Informe quantidades de estoque válidas, não negativas '
                'e com no máximo duas casas decimais.'
            )
            return render(
                request,
                'medicamentos/formulario.html',
                {'medicamento': medicamento, 'dados': dados}
            )

        medicamento.nome = dados['nome']
        medicamento.principio_ativo = dados['principio_ativo']
        medicamento.concentracao = dados['concentracao']
        medicamento.forma_farmaceutica = dados['forma_farmaceutica']
        medicamento.fabricante = dados['fabricante']
        medicamento.unidade_medida = dados['unidade_medida']
        medicamento.estoque_minimo = estoque_minimo
        medicamento.observacoes = dados['observacoes'] or None

        medicamento.save()

        messages.success(
            request,
            'Medicamento atualizado com sucesso.'
        )
        return redirect('medicamentos:lista')

    return render(
        request,
        'medicamentos/formulario.html',
        {'medicamento': medicamento, 'dados': dados}
    )



@login_required
@require_POST
def inativar(request, pk):
    medicamento = get_object_or_404(
        Medicamento,
        pk=pk,
        is_active=True
    )

    if medicamento.estoque_atual != 0:
        messages.error(
            request,
            (
                f'Não é possível inativar o medicamento '
                f'"{medicamento.nome}", pois ele possui '
                f'estoque de {medicamento.estoque_atual} '
                f'{medicamento.unidade_medida}. '
                'Zere o estoque antes de inativá-lo.'
            )
        )
        return redirect('medicamentos:lista')

    medicamento.is_active = False
    medicamento.save(update_fields=['is_active'])

    messages.success(
        request,
        'Medicamento inativado com sucesso.'
    )

    return redirect('medicamentos:lista')
