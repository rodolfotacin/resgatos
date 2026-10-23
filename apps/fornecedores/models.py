
from django.db import models


class Fornecedor(models.Model):
    razao_social = models.CharField(max_length=150)
    nome_fantasia = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'fornecedor'
        ordering = ['razao_social']
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return self.nome_fantasia or self.razao_social
