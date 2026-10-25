from datetime import date
from django.db.models import Sum
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.atendimentos.models import AtendimentoMedicamento
from apps.pessoas.models import Pessoa
from apps.fornecedores.models import Fornecedor
from apps.medicamentos.models import Medicamento

from .models import EntradaEstoque, Lote


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
                    'tipo_origem': '',
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

    aba_ativa = request.GET.get('aba', 'cadastro')

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
            'aba_ativa': aba_ativa,
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
            'aba_ativa': aba_ativa,
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



@login_required
def lotes(request, entrada_id):
    entrada = get_object_or_404(
        EntradaEstoque,
        pk=entrada_id,
    )

    lotes = entrada.lotes.select_related(
        'medicamento'
    ).order_by('data_validade', 'pk')

    return render(
        request,
        'estoque/lotes.html',
        {
            'entrada': entrada,
            'lotes': lotes,
        },
    )


@login_required
def adicionar_lote(request, entrada_id):
    entrada = get_object_or_404(
        EntradaEstoque,
        pk=entrada_id
    )

    medicamentos = Medicamento.objects.filter(
        is_active=True
    ).order_by('nome')

    dados = {
        'medicamento_id': '',
        'numero_lote': '',
        'data_validade': '',
        'quantidade_recebida': '',
        'valor_unitario': '0.00',
        'quantidade_descartada': '0.00',
        'observacoes': '',
    }

    if request.method == 'POST':
        dados = {
            'medicamento_id': request.POST.get(
                'medicamento_id', ''
            ).strip(),
            'numero_lote': request.POST.get(
                'numero_lote', ''
            ).strip(),
            'data_validade': request.POST.get(
                'data_validade', ''
            ).strip(),
            'quantidade_recebida': request.POST.get(
                'quantidade_recebida', ''
            ).strip(),
            'valor_unitario': request.POST.get(
                'valor_unitario', '0'
            ).strip(),
            'quantidade_descartada': request.POST.get(
                'quantidade_descartada', '0'
            ).strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
        }

        obrigatorios = [
            'medicamento_id',
            'numero_lote',
            'data_validade',
            'quantidade_recebida',
        ]

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )
        else:
            try:
                medicamento = get_object_or_404(
                    Medicamento,
                    pk=int(dados['medicamento_id']),
                    is_active=True,
                )

                data_validade = date.fromisoformat(
                    dados['data_validade']
                )

                quantidade_recebida = Decimal(
                    dados['quantidade_recebida']
                )

                valor_unitario = Decimal(
                    dados['valor_unitario'] or '0'
                )

                quantidade_descartada = Decimal(
                    dados['quantidade_descartada'] or '0'
                )

                if quantidade_recebida <= 0:
                    raise ValueError(
                        'A quantidade recebida deve ser maior que zero.'
                    )

                if valor_unitario < 0:
                    raise ValueError(
                        'O valor unitário não pode ser negativo.'
                    )

                if quantidade_descartada < 0:
                    raise ValueError(
                        'A quantidade descartada não pode ser negativa.'
                    )

                if quantidade_descartada > quantidade_recebida:
                    raise ValueError(
                        'A quantidade descartada não pode ser maior '
                        'que a quantidade recebida.'
                    )

                with transaction.atomic():
                    medicamento = Medicamento.objects.select_for_update().get(
                        pk=medicamento.pk
                    )

                    lote = Lote.objects.create(
                        entrada_estoque=entrada,
                        medicamento=medicamento,
                        numero_lote=dados['numero_lote'],
                        data_validade=data_validade,
                        quantidade_recebida=quantidade_recebida,
                        valor_unitario=valor_unitario,
                        quantidade_descartada=quantidade_descartada,
                        observacoes=dados['observacoes'] or None,
                    )

                    total_recebido = Lote.objects.filter(
                        medicamento=medicamento
                    ).aggregate(
                        total=Sum('quantidade_recebida')
                    )['total'] or Decimal('0')

                    total_descartado = Lote.objects.filter(
                        medicamento=medicamento
                    ).aggregate(
                        total=Sum('quantidade_descartada')
                    )['total'] or Decimal('0')

                    total_utilizado = (
                        AtendimentoMedicamento.objects.filter(
                            lote__medicamento=medicamento
                        ).aggregate(
                            total=Sum('quantidade')
                        )['total'] or Decimal('0')
                    )

                    medicamento.estoque_atual = (
                        total_recebido
                        - total_descartado
                        - total_utilizado
                    )

                    medicamento.save(
                        update_fields=['estoque_atual']
                    )

                messages.success(
                    request,
                    'Lote cadastrado com sucesso.'
                )

                return redirect(
                    f"{reverse('estoque:editar', kwargs={'entrada_id': entrada.id})}?aba=lotes"
                )

            except (ValueError, InvalidOperation, OverflowError):
                messages.error(
                    request,
                    'Verifique os dados informados. '
                    'As quantidades e o valor devem ser válidos.'
                )

    return render(
        request,
        'estoque/lote_formulario.html',
        {
            'entrada': entrada,
            'medicamentos': medicamentos,
            'dados': dados,
        }
    )



@login_required
def editar_lote(request, entrada_id, lote_id):
    entrada = get_object_or_404(
        EntradaEstoque,
        pk=entrada_id,
    )

    lote = get_object_or_404(
        Lote,
        pk=lote_id,
        entrada_estoque=entrada,
    )

    medicamentos = Medicamento.objects.filter(
        Q(is_active=True) | Q(pk=lote.medicamento_id)
    ).order_by('nome')

    dados = {
        'medicamento_id': str(lote.medicamento_id),
        'numero_lote': lote.numero_lote,
        'data_validade': lote.data_validade.isoformat(),
        'quantidade_recebida': str(lote.quantidade_recebida),
        'quantidade_descartada': str(lote.quantidade_descartada),
        'valor_unitario': str(lote.valor_unitario),
        'observacoes': lote.observacoes or '',
    }

    contexto = {
        'entrada': entrada,
        'lote': lote,
        'medicamentos': medicamentos,
        'dados': dados,
    }

    if request.method == 'POST':
        dados = {
            'medicamento_id': request.POST.get(
                'medicamento_id', ''
            ).strip(),
            'numero_lote': request.POST.get(
                'numero_lote', ''
            ).strip(),
            'data_validade': request.POST.get(
                'data_validade', ''
            ).strip(),
            'quantidade_recebida': request.POST.get(
                'quantidade_recebida', ''
            ).strip(),
            'quantidade_descartada': request.POST.get(
                'quantidade_descartada', '0'
            ).strip(),
            'valor_unitario': request.POST.get(
                'valor_unitario', '0'
            ).strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
        }

        contexto['dados'] = dados

        obrigatorios = (
            'medicamento_id',
            'numero_lote',
            'data_validade',
            'quantidade_recebida',
        )

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios.',
            )
            return render(
                request,
                'estoque/lote_formulario.html',
                contexto,
            )

        try:
            medicamento = get_object_or_404(
                Medicamento,
                pk=int(dados['medicamento_id']),
            )

            if (
                not medicamento.is_active
                and medicamento.pk != lote.medicamento_id
            ):
                raise ValueError(
                    'Selecione um medicamento ativo.'
                )

            data_validade = date.fromisoformat(
                dados['data_validade']
            )

            quantidade_recebida = Decimal(
                dados['quantidade_recebida']
            )
            quantidade_descartada = Decimal(
                dados['quantidade_descartada'] or '0'
            )
            valor_unitario = Decimal(
                dados['valor_unitario'] or '0'
            )

            if quantidade_recebida <= 0:
                raise ValueError(
                    'A quantidade recebida deve ser maior que zero.'
                )

            if quantidade_descartada < 0:
                raise ValueError(
                    'A quantidade descartada não pode ser negativa.'
                )

            if valor_unitario < 0:
                raise ValueError(
                    'O valor unitário não pode ser negativo.'
                )

            with transaction.atomic():
                lote_bloqueado = Lote.objects.select_for_update().get(
                    pk=lote.pk,
                    entrada_estoque=entrada,
                )

                total_utilizado = (
                    AtendimentoMedicamento.objects
                    .filter(lote=lote_bloqueado)
                    .aggregate(total=Sum('quantidade'))['total']
                    or Decimal('0')
                )

                if quantidade_recebida < (
                    total_utilizado + quantidade_descartada
                ):
                    raise ValueError(
                        'A quantidade recebida não pode ser menor '
                        'que a soma das quantidades utilizadas e descartadas '
                        f'({total_utilizado + quantidade_descartada}).'
                    )

                if (
                    medicamento.pk != lote_bloqueado.medicamento_id
                    and total_utilizado > 0
                ):
                    raise ValueError(
                        'Não é possível trocar o medicamento de um lote '
                        'que já foi utilizado em atendimentos.'
                    )

                medicamento_anterior_id = (
                    lote_bloqueado.medicamento_id
                )

                lote_bloqueado.medicamento = medicamento
                lote_bloqueado.numero_lote = dados['numero_lote']
                lote_bloqueado.data_validade = data_validade
                lote_bloqueado.quantidade_recebida = (
                    quantidade_recebida
                )
                lote_bloqueado.quantidade_descartada = (
                    quantidade_descartada
                )
                lote_bloqueado.valor_unitario = valor_unitario
                lote_bloqueado.observacoes = (
                    dados['observacoes'] or None
                )

                lote_bloqueado.save()

                medicamentos_afetados = Medicamento.objects.filter(
                    pk__in={
                        medicamento_anterior_id,
                        medicamento.pk,
                    }
                ).order_by('pk')

                for medicamento_afetado in medicamentos_afetados:
                    total_recebido = (
                        Lote.objects
                        .filter(medicamento=medicamento_afetado)
                        .aggregate(
                            total=Sum('quantidade_recebida')
                        )['total']
                        or Decimal('0')
                    )

                    total_descartado = (
                        Lote.objects
                        .filter(medicamento=medicamento_afetado)
                        .aggregate(
                            total=Sum('quantidade_descartada')
                        )['total']
                        or Decimal('0')
                    )

                    total_utilizado_medicamento = (
                        AtendimentoMedicamento.objects
                        .filter(
                            lote__medicamento=medicamento_afetado
                        )
                        .aggregate(total=Sum('quantidade'))['total']
                        or Decimal('0')
                    )

                    medicamento_afetado.estoque_atual = (
                        total_recebido
                        - total_descartado
                        - total_utilizado_medicamento
                    )

                    medicamento_afetado.save(
                        update_fields=['estoque_atual']
                    )

            messages.success(
                request,
                'Lote atualizado com sucesso.',
            )

            return redirect(
                f"{reverse('estoque:editar', kwargs={'entrada_id': entrada.id})}?aba=lotes"
            )

        except (ValueError, InvalidOperation, OverflowError):
            messages.error(
                request,
                'Verifique os dados informados e as quantidades do lote.',
            )

        except IntegrityError:
            messages.error(
                request,
                'Não foi possível atualizar o lote.',
            )

    return render(
        request,
        'estoque/lote_formulario.html',
        contexto,
    )



@login_required
@require_POST
def excluir_lote(request, entrada_id, lote_id):
    entrada = get_object_or_404(
        EntradaEstoque,
        pk=entrada_id,
    )

    lote = get_object_or_404(
        Lote.objects.select_related('medicamento'),
        pk=lote_id,
        entrada_estoque=entrada,
    )

    medicamento_id = lote.medicamento_id

    try:
        with transaction.atomic():
            lote = Lote.objects.select_for_update().get(
                pk=lote_id,
                entrada_estoque=entrada,
            )

            # Não permite excluir lotes utilizados em atendimentos.
            if AtendimentoMedicamento.objects.filter(
                lote=lote
            ).exists():
                messages.error(
                    request,
                    'Não é possível excluir este lote, pois ele '
                    'está relacionado a um ou mais atendimentos.',
                )

                return redirect(
                    'estoque:editar',
                    entrada_id=entrada.id,
                ) + '?aba=lotes'

            lote.delete()

            # Recalcula o estoque do medicamento após a exclusão.
            medicamento = Medicamento.objects.select_for_update().get(
                pk=medicamento_id,
            )

            total_recebido = (
                Lote.objects
                .filter(medicamento_id=medicamento_id)
                .aggregate(total=Sum('quantidade_recebida'))['total']
                or Decimal('0')
            )

            total_descartado = (
                Lote.objects
                .filter(medicamento_id=medicamento_id)
                .aggregate(total=Sum('quantidade_descartada'))['total']
                or Decimal('0')
            )

            total_utilizado = (
                AtendimentoMedicamento.objects
                .filter(lote__medicamento_id=medicamento_id)
                .aggregate(total=Sum('quantidade'))['total']
                or Decimal('0')
            )

            medicamento.estoque_atual = (
                total_recebido
                - total_descartado
                - total_utilizado
            )

            medicamento.save(update_fields=['estoque_atual'])

        messages.success(
            request,
            'Lote excluído com sucesso.',
        )

    except IntegrityError:
        messages.error(
            request,
            'Não foi possível excluir o lote porque existem '
            'registros associados a ele.',
        )

    return redirect(
        f"{reverse('estoque:editar', kwargs={'entrada_id': entrada.id})}?aba=lotes"
    )
