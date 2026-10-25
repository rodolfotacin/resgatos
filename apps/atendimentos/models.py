
from django.db import models


class Atendimento(models.Model):
    data_hora = models.DateTimeField()

    class Tipo(models.TextChoices):
        AVALIACAO = 'AVALIACAO', 'Avaliação'
        CONSULTA = 'CONSULTA', 'Consulta'
        RETORNO = 'RETORNO', 'Retorno'
        TRATAMENTO = 'TRATAMENTO', 'Tratamento'
        VACINACAO = 'VACINACAO', 'Vacinação'
        PROCEDIMENTO = 'PROCEDIMENTO', 'Procedimento'
        EMERGENCIA = 'EMERGENCIA', 'Emergência'
        OUTRO = 'OUTRO', 'Outro'

    # Demais campos do modelo...

    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
    )

    motivo = models.TextField(blank=True, null=True)
    peso = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    avaliacao = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    pet = models.ForeignKey(
        'pets.Pet',
        on_delete=models.PROTECT,
        related_name='atendimentos',
    )

    responsavel = models.ForeignKey(
        'pessoas.Pessoa',
        on_delete=models.PROTECT,
        related_name='atendimentos_realizados',
    )

    class Meta:
        db_table = 'atendimento'
        ordering = ['-data_hora']

    def __str__(self):
        return f'Atendimento #{self.pk} - {self.pet}'


class AtendimentoMedicamento(models.Model):
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    via_administracao = models.CharField(max_length=45)

    observacoes = models.TextField(blank=True, null=True)

    atendimento = models.ForeignKey(
        Atendimento,
        on_delete=models.CASCADE,
        related_name='medicamentos_utilizados',
    )

    lote = models.ForeignKey(
        'estoque.Lote',
        on_delete=models.PROTECT,
        related_name='utilizacoes',
    )

    class Meta:
        db_table = 'atendimento_medicamento'

    def __str__(self):
        return (
            f'{self.lote.medicamento.nome} - '
            f'{self.quantidade}'
        )
