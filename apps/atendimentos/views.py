from datetime import datetime
from django.utils import timezone
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Exists, OuterRef
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.estoque.models import Lote
from apps.pets.models import Pet
from apps.pessoas.models import Pessoa
from apps.medicamentos.models import Medicamento
from apps.estoque.services import (
    registrar_medicamento as registrar_medicamento_estoque,
    editar_medicamento_ministrado,
    excluir_medicamento_ministrado,
)
from apps.estoque.services import calcular_saldo_lote

from .models import Atendimento, AtendimentoMedicamento


@login_required
def lista(request):
    busca = request.GET.get('busca', '').strip()

    try:
        por_pagina = int(request.GET.get('por_pagina', 20))
    except (TypeError, ValueError):
        por_pagina = 20

    if por_pagina not in (10, 20, 50, 100):
        por_pagina = 20

    atendimentos = Atendimento.objects.select_related(
        'pet',
        'responsavel',
    ).annotate(
        possui_medicamentos=Exists(
            AtendimentoMedicamento.objects.filter(
                atendimento_id=OuterRef('pk')
            )
        )
    ).order_by(
        '-data_hora',
        '-id',
    )

    if busca:
        atendimentos = atendimentos.filter(
            Q(pet__nome__icontains=busca)
            | Q(tipo__icontains=busca)
            | Q(motivo__icontains=busca)
            | Q(observacoes__icontains=busca)
        )

    paginator = Paginator(atendimentos, por_pagina)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(
        request,
        'atendimentos/lista.html',
        {
            'atendimentos': page_obj.object_list,
            'page_obj': page_obj,
            'paginator': paginator,
            'busca': busca,
            'por_pagina': por_pagina,
        },
    )


def dados_atendimento(atendimento=None):
    if not atendimento:
        agora = timezone.localtime()

        return {
            'pet_id': '',
            'responsavel_id': '',
            'data_hora': agora.strftime('%Y-%m-%dT%H:%M'),
            'tipo': '',
            'peso': '',
            'motivo': '',
            'avaliacao': '',
            'observacoes': '',
        }

    return {
        'pet_id': str(atendimento.pet_id),
        'responsavel_id': str(atendimento.responsavel_id),
        'data_hora': timezone.localtime(
            atendimento.data_hora
        ).strftime('%Y-%m-%dT%H:%M'),
        'tipo': atendimento.tipo,
        'peso': (
            str(atendimento.peso)
            if atendimento.peso is not None
            else ''
        ),
        'motivo': atendimento.motivo or '',
        'avaliacao': atendimento.avaliacao or '',
        'observacoes': atendimento.observacoes or '',
    }


@login_required
def adicionar(request):
    dados = dados_atendimento()

    if request.method == 'POST':
        dados = {
            'pet_id': request.POST.get('pet_id', '').strip(),
            'responsavel_id': request.POST.get(
                'responsavel_id', ''
            ).strip(),
            'data_hora': request.POST.get(
                'data_hora', ''
            ).strip(),
            'tipo': request.POST.get('tipo', '').strip(),
            'peso': request.POST.get('peso', '').strip(),
            'motivo': request.POST.get('motivo', '').strip(),
            'avaliacao': request.POST.get(
                'avaliacao', ''
            ).strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
        }

        obrigatorios = [
            'pet_id',
            'responsavel_id',
            'data_hora',
            'tipo',
        ]

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )
        elif dados['tipo'] not in Atendimento.Tipo.values:
            messages.error(
                request,
                'Selecione um tipo de atendimento válido.'
            )
        else:
            try:
                pet = Pet.objects.get(
                    pk=dados['pet_id'],
                    is_active=True,
                )

                responsavel = Pessoa.objects.get(
                    pk=dados['responsavel_id'],
                    is_active=True,
                    is_attendance_responsible=True,
                )

                data_hora = datetime.strptime(
                    dados['data_hora'],
                    '%Y-%m-%dT%H:%M',
                )

                data_hora = timezone.make_aware(
                    data_hora,
                    timezone.get_current_timezone(),
                )

                peso = None

                if dados['peso']:
                    peso = Decimal(
                        dados['peso'].replace(',', '.')
                    )

                    if peso <= 0:
                        raise ValueError(
                            'O peso deve ser maior que zero.'
                        )

                atendimento = Atendimento(
                    pet=pet,
                    responsavel=responsavel,
                    data_hora=data_hora,
                    tipo=dados['tipo'],
                    peso=peso,
                    motivo=dados['motivo'] or None,
                    avaliacao=dados['avaliacao'] or None,
                    observacoes=dados['observacoes'] or None,
                )

                atendimento.save()

                messages.success(
                    request,
                    'Atendimento registrado com sucesso.'
                )

                return redirect(
                    'atendimentos:editar',
                    atendimento_id=atendimento.pk,
                )

            except (Pet.DoesNotExist, Pessoa.DoesNotExist):
                messages.error(
                    request,
                    'Selecione um Pet ativo e um responsável habilitado '
                    'para realizar atendimentos.'
                )

            except (ValueError, InvalidOperation):
                messages.error(
                    request,
                    'Verifique a data, a hora e o peso informados.'
                )

    return render(
        request,
        'atendimentos/formulario.html',
        {
            'dados': dados,
            'pets': Pet.objects.filter(
                is_active=True
            ).order_by('nome'),
            'responsaveis': Pessoa.objects.filter(
                is_active=True,
                is_attendance_responsible=True
            ).order_by('nome'),
            'tipos_atendimento': Atendimento.Tipo.choices,
        },
    )


@login_required
def editar(request, atendimento_id):
    atendimento = get_object_or_404(
        Atendimento.objects.select_related(
            'pet',
            'responsavel',
        ),
        pk=atendimento_id,
    )

    dados = dados_atendimento(atendimento)

    if request.method == 'POST':
        dados = {
            'pet_id': request.POST.get('pet_id', '').strip(),
            'responsavel_id': request.POST.get(
                'responsavel_id', ''
            ).strip(),
            'data_hora': request.POST.get(
                'data_hora', ''
            ).strip(),
            'tipo': request.POST.get('tipo', '').strip(),
            'peso': request.POST.get('peso', '').strip(),
            'motivo': request.POST.get('motivo', '').strip(),
            'avaliacao': request.POST.get(
                'avaliacao', ''
            ).strip(),
            'observacoes': request.POST.get(
                'observacoes', ''
            ).strip(),
        }

        obrigatorios = [
            'pet_id',
            'responsavel_id',
            'data_hora',
            'tipo',
        ]

        if any(not dados[campo] for campo in obrigatorios):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )

        elif dados['tipo'] not in Atendimento.Tipo.values:
            messages.error(
                request,
                'Selecione um tipo de atendimento válido.'
            )

        else:
            try:
                pet = Pet.objects.get(
                    pk=dados['pet_id'],
                    is_active=True,
                )

                responsavel = Pessoa.objects.get(
                    pk=dados['responsavel_id'],
                    is_active=True,
                    is_attendance_responsible=True,
                )

                data_hora = datetime.strptime(
                    dados['data_hora'],
                    '%Y-%m-%dT%H:%M',
                )

                data_hora = timezone.make_aware(
                    data_hora,
                    timezone.get_current_timezone(),
                )

                peso = None

                if dados['peso']:
                    peso = Decimal(
                        dados['peso'].replace(',', '.')
                    )

                    if peso <= 0:
                        raise ValueError(
                            'O peso deve ser maior que zero.'
                        )

                atendimento.pet = pet
                atendimento.responsavel = responsavel
                atendimento.data_hora = data_hora
                atendimento.tipo = dados['tipo']
                atendimento.peso = peso
                atendimento.motivo = dados['motivo'] or None
                atendimento.avaliacao = dados['avaliacao'] or None
                atendimento.observacoes = (
                    dados['observacoes'] or None
                )

                atendimento.save()

                messages.success(
                    request,
                    'Atendimento atualizado com sucesso.'
                )

                return redirect('atendimentos:lista')

            except (Pet.DoesNotExist, Pessoa.DoesNotExist):
                messages.error(
                    request,
                    'Selecione um Pet ativo e um responsável '
                    'habilitado para realizar atendimentos.'
                )

            except (ValueError, InvalidOperation):
                messages.error(
                    request,
                    'Verifique a data, a hora e o peso informados.'
                )

    medicamentos_ministrados = (
        atendimento.medicamentos_utilizados
        .select_related('lote__medicamento')
        .order_by('pk')
    )

    return render(
        request,
        'atendimentos/formulario.html',
        {
            'atendimento': atendimento,
            'dados': dados,
            'pets': Pet.objects.filter(
                is_active=True,
            ).order_by('nome'),
            'responsaveis': Pessoa.objects.filter(
                is_active=True,
                is_attendance_responsible=True,
            ).order_by('nome'),
            'tipos_atendimento': Atendimento.Tipo.choices,
            'medicamentos_ministrados': medicamentos_ministrados,
            'modo_edicao': True,
        },
    )


@login_required
@require_http_methods(['POST'])
def excluir(request, atendimento_id):
    atendimento = get_object_or_404(
        Atendimento,
        pk=atendimento_id,
    )

    # Impede excluir o atendimento enquanto houver
    # medicamentos ministrados vinculados a ele.
    if atendimento.medicamentos_utilizados.exists():
        messages.error(
            request,
            (
                'Não é possível excluir este atendimento, pois existem '
                'medicamentos ministrados vinculados a ele. '
                'Exclua primeiro os medicamentos registrados.'
            ),
        )
        return redirect('atendimentos:lista')

    atendimento.delete()

    messages.success(
        request,
        'Atendimento excluído com sucesso.',
    )

    return redirect('atendimentos:lista')




@login_required
def medicamentos_ministrados(request, atendimento_id):
    atendimento = get_object_or_404(
        Atendimento,
        pk=atendimento_id,
    )

    medicamentos = (
        atendimento.medicamentos_utilizados
        .select_related('lote__medicamento')
        .order_by('pk')
    )

    return render(
        request,
        'atendimentos/partials/medicamentos_ministrados.html',
        {
            'atendimento': atendimento,
            'medicamentos_ministrados': medicamentos,
        },
    )


@login_required
def lotes_disponiveis(request):
    medicamento_id = request.GET.get('medicamento_id')
    utilizacao_id = request.GET.get('utilizacao_id')

    if not medicamento_id or not medicamento_id.isdigit():
        return JsonResponse(
            {'erro': 'Medicamento inválido.'},
            status=400,
        )

    utilizacao_atual = None

    if utilizacao_id:
        if not utilizacao_id.isdigit():
            return JsonResponse(
                {'erro': 'Utilização inválida.'},
                status=400,
            )

        utilizacao_atual = get_object_or_404(
            AtendimentoMedicamento.objects.select_related('lote'),
            pk=utilizacao_id,
        )

        # A utilização precisa pertencer ao medicamento solicitado.
        if str(utilizacao_atual.lote.medicamento_id) != str(medicamento_id):
            return JsonResponse(
                {'erro': 'A utilização não pertence a este medicamento.'},
                status=400,
            )

    lotes = Lote.objects.filter(
        medicamento_id=medicamento_id,
        data_validade__gte=timezone.localdate(),
    ).order_by('data_validade', 'pk')

    dados = []

    for lote in lotes:
        saldo = calcular_saldo_lote(lote)

        # Na edição, devolve logicamente a quantidade deste registro
        # ao saldo disponível, sem alterar o estoque no banco.
        if utilizacao_atual and lote.pk == utilizacao_atual.lote_id:
            saldo += utilizacao_atual.quantidade

        if saldo > 0 or (
            utilizacao_atual
            and lote.pk == utilizacao_atual.lote_id
        ):
            dados.append({
                'id': lote.pk,
                'numero_lote': lote.numero_lote,
                'data_validade': lote.data_validade.strftime('%d/%m/%Y'),
                'saldo': str(saldo),
            })

    return JsonResponse({'lotes': dados})


@login_required
@require_http_methods(['GET', 'POST'])
def registrar_medicamento(request, atendimento_id):
    atendimento = get_object_or_404(
        Atendimento,
        pk=atendimento_id,
    )

    if request.method == 'GET':
        medicamentos = Medicamento.objects.filter(
            is_active=True,
        ).order_by('nome')

        return render(
            request,
            'atendimentos/formulario_medicamento.html',
            {
                'atendimento': atendimento,
                'medicamentos': medicamentos,
            },
        )

    medicamento_id = request.POST.get('medicamento_id')
    lote_id = request.POST.get('lote_id')
    quantidade = request.POST.get('quantidade')
    via_administracao = request.POST.get('via_administracao', '')
    observacoes = request.POST.get('observacoes', '')

    if not medicamento_id or not lote_id:
        return JsonResponse(
            {'erro': 'Selecione o medicamento e o lote.'},
            status=400,
        )

    if not via_administracao.strip():
        return JsonResponse(
            {'erro': 'Informe a via de administração.'},
            status=400,
        )

    lote = get_object_or_404(
        Lote.objects.select_related('medicamento'),
        pk=lote_id,
    )

    if str(lote.medicamento_id) != str(medicamento_id):
        return JsonResponse(
            {'erro': 'O lote selecionado não pertence ao medicamento.'},
            status=400,
        )

    try:
        utilizacao = registrar_medicamento_estoque(
            atendimento=atendimento,
            lote_id=lote.pk,
            quantidade=quantidade,
            via_administracao=via_administracao,
            observacoes=observacoes,
        )

    except ValidationError as erro:
        return JsonResponse(
            {'erro': ' '.join(erro.messages)},
            status=400,
        )

    return JsonResponse({
        'sucesso': True,
        'mensagem': 'Medicamento registrado com sucesso.',
        'medicamento': {
            'id': utilizacao.pk,
            'nome': utilizacao.lote.medicamento.nome,
            'lote': utilizacao.lote.numero_lote,
            'quantidade': str(utilizacao.quantidade),
            'via_administracao': utilizacao.via_administracao,
            'observacoes': utilizacao.observacoes or '',
        },
    })



@login_required
@require_http_methods(['GET', 'POST'])
def editar_medicamento(request, utilizacao_id):
    utilizacao = get_object_or_404(
        AtendimentoMedicamento.objects.select_related(
            'atendimento',
            'lote__medicamento',
        ),
        pk=utilizacao_id,
    )

    if request.method == 'GET':
        if utilizacao.lote.data_validade < timezone.localdate():
            return JsonResponse(
                {
                    'erro': (
                        'Não é possível editar um registro '
                        'vinculado a um lote vencido.'
                    )
                },
                status=400,
            )

        medicamentos = Medicamento.objects.filter(
            is_active=True,
        ).order_by('nome')

        return render(
            request,
            'atendimentos/formulario_medicamento.html',
            {
                'atendimento': utilizacao.atendimento,
                'medicamentos': medicamentos,
                'utilizacao': utilizacao,
                'modo_edicao': True,
            },
        )

    medicamento_id = request.POST.get('medicamento_id')
    lote_id = request.POST.get('lote_id')
    quantidade = request.POST.get('quantidade')
    via_administracao = request.POST.get('via_administracao', '')
    observacoes = request.POST.get('observacoes', '')

    if not medicamento_id or not lote_id:
        return JsonResponse(
            {'erro': 'Selecione o medicamento e o lote.'},
            status=400,
        )

    if not via_administracao.strip():
        return JsonResponse(
            {'erro': 'Informe a via de administração.'},
            status=400,
        )

    lote = get_object_or_404(
        Lote.objects.select_related('medicamento'),
        pk=lote_id,
    )

    if str(lote.medicamento_id) != str(medicamento_id):
        return JsonResponse(
            {'erro': 'O lote selecionado não pertence ao medicamento.'},
            status=400,
        )

    try:
        utilizacao = editar_medicamento_ministrado(
            utilizacao_id=utilizacao.pk,
            lote_id=lote.pk,
            quantidade=quantidade,
            via_administracao=via_administracao,
            observacoes=observacoes,
        )
    except ValidationError as erro:
        return JsonResponse(
            {'erro': ' '.join(erro.messages)},
            status=400,
        )

    return JsonResponse({
        'sucesso': True,
        'mensagem': 'Medicamento atualizado com sucesso.',
        'medicamento': {
            'id': utilizacao.pk,
            'nome': utilizacao.lote.medicamento.nome,
            'lote': utilizacao.lote.numero_lote,
            'quantidade': str(utilizacao.quantidade),
            'via_administracao': utilizacao.via_administracao,
            'observacoes': utilizacao.observacoes or '',
        },
    })


@login_required
@require_http_methods(['POST'])
def excluir_medicamento(request, utilizacao_id):
    utilizacao = get_object_or_404(
        AtendimentoMedicamento.objects.select_related(
            'atendimento',
        ),
        pk=utilizacao_id,
    )

    atendimento_id = utilizacao.atendimento_id

    try:
        excluir_medicamento_ministrado(
            utilizacao_id=utilizacao.pk,
        )
    except ValidationError as erro:
        return JsonResponse(
            {'erro': ' '.join(erro.messages)},
            status=400,
        )

    return JsonResponse({
        'sucesso': True,
        'mensagem': 'Medicamento excluído com sucesso.',
        'atendimento_id': atendimento_id,
    })
