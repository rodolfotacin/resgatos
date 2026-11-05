"""Formulário novo: cadastra um resgate e seus detalhes na mesma operação.

Não modifica o modelo Resgate nem seu formulário original.
"""
from django import forms

from apps.pets.models import Pet
from .forms import FormEstilizado
from .models import ComplementoResgate


class ResgateCompletoForm(FormEstilizado):
    pet_principal = forms.ModelChoiceField(
        label='Gato principal',
        queryset=Pet.objects.none(),
        empty_label='Selecione a opção',
        help_text='Escolha um gato já cadastrado. Se ainda não existir, cadastre-o em Pets primeiro.',
    )
    data_resgate = forms.DateTimeField(
        label='Data e hora do resgate',
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
    )
    local_resgate = forms.CharField(
        label='Local do resgate',
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Endereço, bairro ou referência'}),
    )
    descricao_resgate = forms.CharField(
        label='Relato do resgate (opcional)', required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )
    observacoes_resgate = forms.CharField(
        label='Observações complementares (opcional)', required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    class Meta:
        model = ComplementoResgate
        fields = [
            'quantidade_gatos', 'outros_pets', 'situacao_encontrada',
            'estado_saude', 'destino', 'destino_outro',
            'local_encaminhamento',
        ]
        widgets = {'outros_pets': forms.SelectMultiple(attrs={'size': 6})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pet_principal'].queryset = Pet.objects.filter(is_active=True).order_by('nome')
        self.fields['outros_pets'].queryset = Pet.objects.filter(is_active=True).order_by('nome')
        self.fields['outros_pets'].help_text = (
            'Opcional. Segure Ctrl para selecionar vários. '
            'Não selecione novamente o gato principal.'
        )
        self.order_fields([
            'pet_principal', 'data_resgate', 'local_resgate',
            'quantidade_gatos', 'outros_pets', 'situacao_encontrada',
            'estado_saude', 'destino', 'destino_outro',
            'local_encaminhamento', 'descricao_resgate', 'observacoes_resgate',
        ])

    def clean(self):
        dados = super().clean()
        principal = dados.get('pet_principal')
        outros = dados.get('outros_pets')
        quantidade = dados.get('quantidade_gatos')
        if principal and outros is not None:
            if any(p.pk == principal.pk for p in outros):
                self.add_error('outros_pets', 'O gato principal já está incluído no resgate.')
            if quantidade is not None and quantidade < 1 + len(outros):
                self.add_error('quantidade_gatos', 'A quantidade não pode ser menor que o número de gatos vinculados.')
        if dados.get('destino') == ComplementoResgate.Destino.OUTRO and not dados.get('destino_outro', '').strip():
            self.add_error('destino_outro', 'Especifique o outro destino.')
        return dados
