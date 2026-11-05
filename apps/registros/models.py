from django.core.validators import MinValueValidator
from django.db import models

from apps.pessoas.models import Pessoa
from apps.pets.models import Pet
from apps.resgates.models import Resgate


class Castracao(models.Model):
    class Origem(models.TextChoices):
        ONG = 'ONG', 'Gato da ONG ResGatos'
        TUTOR = 'TUTOR', 'Gato de tutor (doação/intermediação)'

    class LocalTipo(models.TextChoices):
        PUBLICO = 'PUBLICO', 'Zoonoses / serviço público'
        PARTICULAR = 'PARTICULAR', 'Clínica particular'

    pet = models.ForeignKey(Pet, on_delete=models.PROTECT, related_name='castracoes')
    data_castracao = models.DateField('Data da castração')
    sexo = models.CharField('Sexo no procedimento', max_length=1, choices=[('M', 'Macho'), ('F', 'Fêmea')])
    origem = models.CharField('Origem do gato', max_length=10, choices=Origem.choices)
    tutor = models.ForeignKey(Pessoa, on_delete=models.PROTECT, null=True, blank=True, related_name='castracoes_acompanhadas', verbose_name='Tutor já cadastrado (opcional)')
    nome_tutor = models.CharField('Nome do tutor (se não cadastrado)', max_length=150, blank=True)
    local_tipo = models.CharField('Onde foi realizada', max_length=12, choices=LocalTipo.choices)
    nome_local = models.CharField('Nome da clínica / local', max_length=180)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registro_castracao'
        ordering = ['-data_castracao', '-pk']
        verbose_name = 'Castração'
        verbose_name_plural = 'Castrações'

    def __str__(self):
        return f'{self.pet.nome} - {self.data_castracao:%d/%m/%Y}'


class Obito(models.Model):
    pet = models.OneToOneField(Pet, on_delete=models.PROTECT, related_name='registro_obito')
    data_obito = models.DateField('Data do óbito')
    motivo = models.TextField('Motivo do óbito')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registro_obito'
        ordering = ['-data_obito', '-pk']
        verbose_name = 'Óbito'
        verbose_name_plural = 'Óbitos'

    def __str__(self):
        return f'{self.pet.nome} - {self.data_obito:%d/%m/%Y}'


class Internacao(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.PROTECT, related_name='internacoes')
    data_internacao = models.DateField('Data da internação')
    motivo = models.TextField('Motivo')
    clinica = models.CharField('Clínica veterinária', max_length=180)
    data_alta = models.DateField('Data da alta / retorno à ONG', blank=True, null=True)
    situacao_pos_alta = models.TextField('Situação após a alta', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registro_internacao'
        ordering = ['-data_internacao', '-pk']
        verbose_name = 'Internação'
        verbose_name_plural = 'Internações'

    def __str__(self):
        return f'{self.pet.nome} - {self.data_internacao:%d/%m/%Y}'


class ComplementoResgate(models.Model):
    class Destino(models.TextChoices):
        ONG = 'ONG', 'ONG'
        CLINICA = 'CLINICA', 'Clínica veterinária'
        LAR = 'LAR', 'Lar temporário'
        OUTRO = 'OUTRO', 'Outro'

    resgate = models.OneToOneField(Resgate, on_delete=models.PROTECT, related_name='complemento', verbose_name='Resgate principal')
    quantidade_gatos = models.PositiveSmallIntegerField('Quantidade de gatos resgatados', default=1, validators=[MinValueValidator(1)])
    outros_pets = models.ManyToManyField(Pet, blank=True, related_name='resgates_em_grupo', verbose_name='Outros gatos já cadastrados no mesmo resgate')
    situacao_encontrada = models.TextField('Situação em que foi encontrado')
    estado_saude = models.TextField('Estado de saúde')
    destino = models.CharField('Destino após o resgate', max_length=10, choices=Destino.choices)
    destino_outro = models.CharField('Outro destino (especifique)', max_length=180, blank=True)
    local_encaminhamento = models.CharField('Clínica / local para onde foi encaminhado', max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registro_complemento_resgate'
        ordering = ['-pk']
        verbose_name = 'Detalhe complementar de resgate'
        verbose_name_plural = 'Detalhes complementares de resgates'

    def __str__(self):
        return f'Resgate #{self.resgate_id} - {self.resgate.pet.nome}'
