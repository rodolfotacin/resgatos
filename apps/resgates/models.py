
from django.db import models

from apps.pets.models import Pet


class Resgate(models.Model):
    id = models.AutoField(primary_key=True)
    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT,
        related_name='resgates',
        db_column='pet_id',
    )
    data_resgate = models.DateTimeField()
    local = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'resgate'
        verbose_name = 'Resgate'
        verbose_name_plural = 'Resgates'
        ordering = ['-data_resgate', '-id']

    def __str__(self):
        return f'{self.pet.nome} - {self.data_resgate:%d/%m/%Y}'
