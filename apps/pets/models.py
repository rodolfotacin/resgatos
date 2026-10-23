
from django.db import models
from core.utils.upload import foto_pet

from apps.pessoas.models import Pessoa


class Pet(models.Model):
    id = models.AutoField(primary_key=True)

    microchip = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    nome = models.CharField(max_length=45)
    especie = models.CharField(max_length=100)

    raca = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    sexo = models.CharField(
        max_length=1,
        blank=True,
        null=True,
    )

    cor = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )

    data_nascimento = models.DateField(
        blank=True,
        null=True,
    )

    porte = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )

    pelagem = models.CharField(
        max_length=45,
        blank=True,
        null=True,
    )

    foto = models.ImageField(
        upload_to=foto_pet,
        blank=True,
        null=True,
    )

    observacoes = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'pet'
        verbose_name = 'Pet'
        verbose_name_plural = 'Pets'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class PessoaPet(models.Model):
    tipo_relacao = models.CharField(max_length=45)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name='vinculos_pets',
        db_column='pessoa_id',
    )

    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT,
        related_name='vinculos_pessoas',
        db_column='pet_id',
    )

    class Meta:
        db_table = 'pessoa_pet'
        verbose_name = 'Vínculo entre pessoa e pet'
        verbose_name_plural = 'Vínculos entre pessoas e pets'

    def __str__(self):
        return f'{self.pessoa.nome} - {self.pet.nome}'


class PetSituacao(models.Model):
    id = models.AutoField(primary_key=True)

    situacao = models.CharField(max_length=50)
    data_inicio = models.DateField()
    data_fim = models.DateField(
        blank=True,
        null=True,
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
    )

    pet = models.ForeignKey(
        Pet,
        on_delete=models.PROTECT,
        related_name='situacoes',
        db_column='pet_id',
    )

    class Meta:
        db_table = 'pet_situacao'
        verbose_name = 'Situação do pet'
        verbose_name_plural = 'Situações do pet'
        ordering = ['-data_inicio', '-id']

    def __str__(self):
        return f'{self.pet.nome} - {self.situacao}'