from django.contrib import admin
from .models import Castracao, Obito, Internacao, ComplementoResgate


@admin.register(Castracao)
class CastracaoAdmin(admin.ModelAdmin):
    list_display = ('pet', 'data_castracao', 'origem', 'local_tipo', 'nome_local')
    search_fields = ('pet__nome', 'nome_tutor', 'nome_local')


@admin.register(Obito)
class ObitoAdmin(admin.ModelAdmin):
    list_display = ('pet', 'data_obito')
    search_fields = ('pet__nome', 'motivo')


@admin.register(Internacao)
class InternacaoAdmin(admin.ModelAdmin):
    list_display = ('pet', 'data_internacao', 'clinica', 'data_alta')
    search_fields = ('pet__nome', 'clinica', 'motivo')


@admin.register(ComplementoResgate)
class ComplementoResgateAdmin(admin.ModelAdmin):
    list_display = ('resgate', 'quantidade_gatos', 'destino')
    search_fields = ('resgate__pet__nome', 'resgate__local')
