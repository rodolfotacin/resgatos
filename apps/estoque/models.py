
from django.db import models


class EntradaEstoque(models.Model):

    TIPO_ORIGEM_CHOICES = [
        ('DOACAO', 'Doação'),
        ('COMPRA', 'Compra'),
    ]

    tipo_origem = models.CharField(
        max_length=45,
        choices=TIPO_ORIGEM_CHOICES,
    )

    data = models.DateField()

    numero_nota_fiscal = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )

    observacoes = models.TextField(
        blank=True,
        null=True,
    )

    pessoa = models.ForeignKey(
        'pessoas.Pessoa',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='entradas_estoque',
    )

    fornecedor = models.ForeignKey(
        'fornecedores.Fornecedor',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='entradas_estoque',
    )

    recebedor = models.ForeignKey(
        'pessoas.Pessoa',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='entradas_estoque_recebidas',
    )

    class Meta:
        db_table = 'entrada_estoque'
        ordering = ['-data', '-id']
        verbose_name = 'Entrada de estoque'
        verbose_name_plural = 'Entradas de estoque'

    def __str__(self):
        return f'{self.get_tipo_origem_display()} - {self.data:%d/%m/%Y}'



class Lote(models.Model):

    entrada_estoque = models.ForeignKey(
        'estoque.EntradaEstoque',
        on_delete=models.PROTECT,
        related_name='lotes',
    )

    medicamento = models.ForeignKey(
        'medicamentos.Medicamento',
        on_delete=models.PROTECT,
        related_name='lotes',
    )

    numero_lote = models.CharField(
        max_length=100,
    )

    data_validade = models.DateField()

    quantidade_recebida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    quantidade_descartada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    observacoes = models.TextField(
        blank=True,
        null=True,
    )

    class Meta:
        db_table = 'lote'
        ordering = ['data_validade', 'numero_lote']
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'

    def __str__(self):
        return f'{self.medicamento.nome} - {self.numero_lote}'
