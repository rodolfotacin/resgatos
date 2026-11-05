from django import forms
from django.core.exceptions import ValidationError
from .models import Castracao, Obito, Internacao, ComplementoResgate
from apps.pets.models import Pet
from apps.resgates.models import Resgate


class FormEstilizado(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, (forms.Select, forms.SelectMultiple)) else 'form-control'
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('rows', 3)
            # Exibe os seletores em português sem modificar as opções reais.
            if isinstance(field.widget, forms.Select) and not isinstance(field.widget, forms.SelectMultiple):
                if isinstance(field, forms.ModelChoiceField):
                    field.empty_label = 'Selecione a opção'
                else:
                    opcoes = list(field.choices)
                    if opcoes and opcoes[0][0] in ('', None):
                        opcoes[0] = (opcoes[0][0], 'Selecione a opção')
                        field.choices = opcoes


def campos_data(*nomes):
    return {nome: forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}) for nome in nomes}


class CastracaoForm(FormEstilizado):
    class Meta:
        model = Castracao
        fields = ['pet', 'data_castracao', 'sexo', 'origem', 'tutor', 'nome_tutor', 'local_tipo', 'nome_local']
        widgets = campos_data('data_castracao')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pet'].queryset = Pet.objects.order_by('nome')
        self.fields['tutor'].required = False

    def clean(self):
        dados = super().clean()
        pet = dados.get('pet')
        sexo = dados.get('sexo')
        if pet and pet.sexo in ('M', 'F') and sexo and sexo != pet.sexo:
            self.add_error('sexo', 'O sexo informado é diferente do cadastro do gato. Confira o cadastro do pet.')
        if dados.get('origem') == Castracao.Origem.TUTOR and not (dados.get('tutor') or dados.get('nome_tutor', '').strip()):
            self.add_error('nome_tutor', 'Informe o nome do tutor ou selecione um tutor cadastrado.')
        return dados


class ObitoForm(FormEstilizado):
    class Meta:
        model = Obito
        fields = ['pet', 'data_obito', 'motivo']
        widgets = campos_data('data_obito')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pet'].queryset = Pet.objects.order_by('nome')

    def clean_pet(self):
        pet = self.cleaned_data['pet']
        ja_existe = Obito.objects.filter(pet=pet)
        if self.instance.pk:
            ja_existe = ja_existe.exclude(pk=self.instance.pk)
        if ja_existe.exists():
            raise ValidationError('Já existe um registro de óbito para esse gato.')
        return pet


class InternacaoForm(FormEstilizado):
    class Meta:
        model = Internacao
        fields = ['pet', 'data_internacao', 'motivo', 'clinica', 'data_alta', 'situacao_pos_alta']
        widgets = campos_data('data_internacao', 'data_alta')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pet'].queryset = Pet.objects.order_by('nome')

    def clean(self):
        dados = super().clean()
        entrada, alta = dados.get('data_internacao'), dados.get('data_alta')
        if entrada and alta and alta < entrada:
            self.add_error('data_alta', 'A alta não pode ser anterior à internação.')
        if alta and not dados.get('situacao_pos_alta', '').strip():
            self.add_error('situacao_pos_alta', 'Descreva a situação após a alta.')
        if not alta and dados.get('situacao_pos_alta', '').strip():
            self.add_error('data_alta', 'Informe a data da alta para registrar a situação posterior.')
        return dados


class ComplementoResgateForm(FormEstilizado):
    class Meta:
        model = ComplementoResgate
        fields = ['resgate', 'quantidade_gatos', 'outros_pets', 'situacao_encontrada', 'estado_saude', 'destino', 'destino_outro', 'local_encaminhamento']
        widgets = {'outros_pets': forms.SelectMultiple(attrs={'size': 6})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Resgate.objects.filter(is_active=True, complemento__isnull=True)
        if self.instance.pk:
            qs = Resgate.objects.filter(pk=self.instance.resgate_id) | qs
        self.fields['resgate'].queryset = qs.select_related('pet').order_by('-data_resgate')
        self.fields['outros_pets'].queryset = Pet.objects.order_by('nome')
        self.fields['outros_pets'].help_text = 'Use Ctrl para selecionar mais de um. Não selecione o gato principal novamente.'

    def clean(self):
        dados = super().clean()
        resgate = dados.get('resgate')
        outros = dados.get('outros_pets')
        quantidade = dados.get('quantidade_gatos')
        if resgate and outros is not None:
            if any(p.pk == resgate.pet_id for p in outros):
                self.add_error('outros_pets', 'O gato principal já está incluído no resgate.')
            if quantidade is not None and quantidade < 1 + len(outros):
                self.add_error('quantidade_gatos', 'A quantidade não pode ser menor que o número de gatos vinculados.')
        if dados.get('destino') == ComplementoResgate.Destino.OUTRO and not dados.get('destino_outro', '').strip():
            self.add_error('destino_outro', 'Especifique o outro destino.')
        return dados
