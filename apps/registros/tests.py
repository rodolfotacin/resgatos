from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.pessoas.models import Pessoa, Usuario
from apps.pets.models import Pet
from apps.resgates.models import Resgate
from .forms import InternacaoForm, ComplementoResgateForm
from .models import Castracao, Obito, Internacao, ComplementoResgate


class RegistrosEspeciaisTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pessoa = Pessoa.objects.create(
            nome='Administrador de Teste', cpf='111.222.333-44',
            email='supervisor-teste@example.invalid', telefone='11988887777',
            cep='00000-000', endereco='Rua Teste', numero='1',
            bairro='Centro', cidade='Cidade', estado='SP'
        )
        cls.usuario = Usuario.objects.create_superuser(
            pessoa=cls.pessoa, username='admin-teste', password='TesteForte!123'
        )
        cls.pet = Pet.objects.create(nome='Safado', especie='gato', sexo='M')
        cls.outro = Pet.objects.create(nome='Mingau', especie='gato', sexo='F')
        cls.resgate = Resgate.objects.create(
            pet=cls.pet, data_resgate=timezone.now(), local='Bairro Centro'
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_abas_carregam(self):
        for tipo in ('castracoes', 'obitos', 'internacoes', 'resgates'):
            resp = self.client.get(reverse('registros:lista', kwargs={'tipo': tipo}))
            self.assertEqual(resp.status_code, 200, tipo)

    def test_castracao_e_cadastro_original_preservado(self):
        resposta = self.client.post(reverse('registros:criar', kwargs={'tipo': 'castracoes'}), {
            'pet': self.pet.pk, 'data_castracao': '2026-10-13', 'sexo': 'M',
            'origem': 'ONG', 'local_tipo': 'PUBLICO', 'nome_local': 'Zoonoses'
        })
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(Castracao.objects.filter(pet=self.pet).exists())
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.nome, 'Safado')
        self.assertEqual(self.pet.sexo, 'M')

    def test_castracao_tutor_exige_identificacao(self):
        resposta = self.client.post(reverse('registros:criar', kwargs={'tipo': 'castracoes'}), {
            'pet': self.pet.pk, 'data_castracao': '2026-10-13', 'sexo': 'M',
            'origem': 'TUTOR', 'local_tipo': 'PUBLICO', 'nome_local': 'Zoonoses'
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Castracao.objects.count(), 0)

    def test_obito_nao_inativa_pet_e_nao_permite_duplicar(self):
        url = reverse('registros:criar', kwargs={'tipo': 'obitos'})
        payload = {'pet': self.pet.pk, 'data_obito': '2026-10-20', 'motivo': 'Causa documentada'}
        self.assertEqual(self.client.post(url, payload).status_code, 302)
        self.assertEqual(self.client.post(url, payload).status_code, 200)
        self.assertEqual(Obito.objects.count(), 1)
        self.pet.refresh_from_db()
        self.assertTrue(self.pet.is_active)

    def test_internacao_alta_nao_pode_preceder_entrada(self):
        form = InternacaoForm(data={
            'pet': self.pet.pk, 'data_internacao': '2026-10-15', 'motivo': 'Exames',
            'clinica': 'Clínica exemplo', 'data_alta': '2026-10-14',
            'situacao_pos_alta': 'Recuperação'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('data_alta', form.errors)

    def test_internacao_aberta_e_alta_posterior(self):
        url = reverse('registros:criar', kwargs={'tipo': 'internacoes'})
        resposta = self.client.post(url, {
            'pet': self.pet.pk, 'data_internacao': '2026-10-15',
            'motivo': 'Observação', 'clinica': 'Clínica exemplo',
            'data_alta': '', 'situacao_pos_alta': ''
        })
        self.assertEqual(resposta.status_code, 302)
        internacao = Internacao.objects.get(pet=self.pet)
        self.assertIsNone(internacao.data_alta)

    def test_resgate_complemento_vincula_outros_gatos(self):
        url = reverse('registros:criar', kwargs={'tipo': 'resgates'})
        resposta = self.client.post(url, {
            'resgate': self.resgate.pk, 'quantidade_gatos': '3',
            'outros_pets': [self.outro.pk],
            'situacao_encontrada': 'Em caixa', 'estado_saude': 'Estável',
            'destino': 'ONG', 'destino_outro': '', 'local_encaminhamento': ''
        })
        self.assertEqual(resposta.status_code, 302)
        complemento = ComplementoResgate.objects.get(resgate=self.resgate)
        self.assertEqual(complemento.quantidade_gatos, 3)
        self.assertEqual(list(complemento.outros_pets.all()), [self.outro])
        self.resgate.refresh_from_db()
        self.assertEqual(self.resgate.local, 'Bairro Centro')

    def test_complemento_rejeita_contagem_menor_que_animais_vinculados(self):
        form = ComplementoResgateForm(data={
            'resgate': self.resgate.pk, 'quantidade_gatos': '1',
            'outros_pets': [self.outro.pk],
            'situacao_encontrada': 'Rua', 'estado_saude': 'Bom',
            'destino': 'ONG', 'destino_outro': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade_gatos', form.errors)

    def test_modulo_exige_login(self):
        self.client.logout()
        resposta = self.client.get(reverse('registros:lista', kwargs={'tipo': 'obitos'}))
        self.assertEqual(resposta.status_code, 302)
