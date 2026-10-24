from django.db import models


class Medicamento(models.Model):
    nome = models.CharField(max_length=100)
    principio_ativo = models.CharField(max_length=150)
    concentracao = models.CharField(max_length=100)
    forma_farmaceutica = models.CharField(max_length=100)
    fabricante = models.CharField(max_length=45)
    unidade_medida = models.CharField(max_length=45)

    estoque_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    observacoes = models.TextField(
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'medicamento'
        ordering = ['nome']
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'

    def __str__(self):
        return self.nome