from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404

from apps.atendimentos.models import (
    AtendimentoMedicamento,
)
from apps.estoque.models import Lote
from apps.medicamentos.models import Medicamento


def calcular_saldo_lote(lote):
    quantidade_ministrada = (
        AtendimentoMedicamento.objects
        .filter(lote=lote)
        .aggregate(total=Sum('quantidade'))['total']
        or Decimal('0')
    )

    return (
        lote.quantidade_recebida
        - lote.quantidade_descartada
        - quantidade_ministrada
    )


@transaction.atomic
def registrar_medicamento(
    atendimento,
    lote_id,
    quantidade,
    via_administracao,
    observacoes='',
):
    try:
        quantidade = Decimal(
            str(quantidade).replace(',', '.')
        )
    except (InvalidOperation, ValueError):
        raise ValidationError(
            'Informe uma quantidade válida.'
        )

    if not quantidade.is_finite() or quantidade <= 0:
        raise ValidationError(
            'A quantidade deve ser maior que zero.'
        )

    # Identifica o medicamento associado ao lote.
    lote_referencia = Lote.objects.get(pk=lote_id)

    # Serializa alterações de estoque deste medicamento.
    medicamento = Medicamento.objects.select_for_update().get(
        pk=lote_referencia.medicamento_id
    )

    # Bloqueia o lote para evitar duas utilizações simultâneas
    # que ultrapassem seu saldo.
    lote = Lote.objects.select_for_update().get(
        pk=lote_id,
        medicamento_id=medicamento.pk,
    )

    if lote.data_validade < timezone.localdate():
        raise ValidationError(
            'Não é possível utilizar um lote vencido.'
        )

    saldo_lote = calcular_saldo_lote(lote)

    if quantidade > saldo_lote:
        raise ValidationError(
            f'Quantidade indisponível. '
            f'Saldo do lote: {saldo_lote}.'
        )

    if quantidade > medicamento.estoque_atual:
        raise ValidationError(
            'A quantidade solicitada excede o estoque atual '
            'do medicamento.'
        )

    utilizacao = AtendimentoMedicamento.objects.create(
        atendimento=atendimento,
        lote=lote,
        quantidade=quantidade,
        via_administracao=via_administracao.strip(),
        observacoes=observacoes.strip() or None,
    )

    medicamento.estoque_atual -= quantidade
    medicamento.save(update_fields=['estoque_atual'])

    return utilizacao



@transaction.atomic
def editar_medicamento_ministrado(
    utilizacao_id,
    lote_id,
    quantidade,
    via_administracao,
    observacoes='',
):
    utilizacao = get_object_or_404(
        AtendimentoMedicamento.objects.select_related('lote'),
        pk=utilizacao_id,
    )

    lote_atual = utilizacao.lote

    # Nenhum campo pode ser alterado se o lote atual estiver vencido.
    if lote_atual.data_validade < timezone.localdate():
        raise ValidationError(
            'Não é possível editar um registro vinculado a '
            'um lote vencido.'
        )

    try:
        quantidade = Decimal(
            str(quantidade).replace(',', '.')
        )
    except (InvalidOperation, ValueError):
        raise ValidationError(
            'Informe uma quantidade válida.'
        )

    if not quantidade.is_finite() or quantidade <= 0:
        raise ValidationError(
            'A quantidade deve ser maior que zero.'
        )

    # Bloqueia o medicamento e o lote para evitar concorrência.
    medicamento = Medicamento.objects.select_for_update().get(
        pk=lote_atual.medicamento_id
    )

    lote = Lote.objects.select_for_update().get(
        pk=lote_id,
        medicamento_id=medicamento.pk,
    )

    if lote.data_validade < timezone.localdate():
        raise ValidationError(
            'Não é possível utilizar um lote vencido.'
        )

    # O saldo atual já desconta a utilização que está sendo editada.
    # Se for o mesmo lote, somamos a quantidade antiga para calcular
    # quanto realmente está disponível para esta edição.
    saldo_lote = calcular_saldo_lote(lote)

    if lote.pk == lote_atual.pk:
        saldo_lote += utilizacao.quantidade

    if quantidade > saldo_lote:
        raise ValidationError(
            f'Quantidade indisponível. Saldo do lote: {saldo_lote}.'
        )

    # O estoque atual já está descontado pela utilização antiga.
    # Devolvemos essa quantidade ao cálculo antes de validar a nova.
    estoque_disponivel = (
        medicamento.estoque_atual + utilizacao.quantidade
    )

    if quantidade > estoque_disponivel:
        raise ValidationError(
            'A quantidade solicitada excede o estoque atual '
            'do medicamento.'
        )



    print(
        'DIAGNÓSTICO EDIÇÃO MEDICAMENTO',
        {
            'utilizacao_id': utilizacao.pk,
            'quantidade_anterior': str(utilizacao.quantidade),
            'quantidade_nova': str(quantidade),
            'estoque_atual_antes': str(medicamento.estoque_atual),
            'estoque_disponivel': str(estoque_disponivel),
            'estoque_calculado': str(
                estoque_disponivel - quantidade
            ),
            'lote_anterior': lote_atual.pk,
            'lote_novo': lote.pk,
        }
    )

    medicamento.estoque_atual = (
        estoque_disponivel - quantidade
    )
    medicamento.save(update_fields=['estoque_atual'])

    utilizacao.lote = lote




    # Atualiza o estoque considerando a diferença entre as quantidades.
    medicamento.estoque_atual = (
        estoque_disponivel - quantidade
    )
    medicamento.save(update_fields=['estoque_atual'])

    utilizacao.lote = lote
    utilizacao.quantidade = quantidade
    utilizacao.via_administracao = via_administracao.strip()
    utilizacao.observacoes = observacoes.strip() or None
    utilizacao.save(
        update_fields=[
            'lote',
            'quantidade',
            'via_administracao',
            'observacoes',
        ]
    )

    return utilizacao


@transaction.atomic
def excluir_medicamento_ministrado(utilizacao_id):
    utilizacao = get_object_or_404(
        AtendimentoMedicamento.objects.select_related('lote'),
        pk=utilizacao_id,
    )

    medicamento = Medicamento.objects.select_for_update().get(
        pk=utilizacao.lote.medicamento_id
    )

    # A exclusão devolve ao estoque a quantidade utilizada,
    # mesmo se o lote estiver vencido.
    medicamento.estoque_atual += utilizacao.quantidade
    medicamento.save(update_fields=['estoque_atual'])

    utilizacao.delete()
