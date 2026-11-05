"""Testes adicionais da melhoria de cadastros e seletores."""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.pessoas.models import Pessoa, Usuario
from apps.pets.models import Pet
from apps.resgates.models import Resgate
from .models import ComplementoResgate


class MelhoriasRegistrosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pessoa = Pessoa.objects.create(
            nome='Usuário de Testes', cpf='222.333.444-55',
            email='registros-teste@example.invalid', telefone='11977776666',
            cep='00000-000', endereco='Rua Teste', numero='10',
            bairro='Centro', cidade='Cidade', estado='SP',
        )
        cls.usuario = Usuario.objects.create_superuser(
            pessoa=pessoa, username='registros-teste', password='SenhaDeTeste!123'
        )
        cls.pet = Pet.objects.create(nome='Safado', especie='gato', sexo='M')
        cls.outro = Pet.objects.create(nome='Mingau', especie='gato', sexo='F')

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_seletores_em_portugues_nos_tres_cadastros(self):
        for tipo in ('castracoes', 'obitos', 'internacoes'):
            with self.subTest(tipo=tipo):
                pagina = self.client.get(reverse('registros:criar', kwargs={'tipo': tipo}))
                self.assertEqual(pagina.status_code, 200)
                self.assertContains(pagina, 'Selecione a opção')
                self.assertNotContains(pagina, 'Select an option')

    def test_autopreenchimento_usa_sexo_do_pet(self):
        pagina = self.client.get(reverse('registros:criar', kwargs={'tipo': 'castracoes'}))
        self.assertContains(pagina, 'registros-pet-sexos')
        self.assertContains(pagina, 'preencherSexo')
        self.assertContains(pagina, 'M')
        self.assertContains(pagina, 'F')

    def test_resgate_completo_cria_original_e_complemento(self):
        url = reverse('registros:criar', kwargs={'tipo': 'resgates'})
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(Resgate.objects.count(), 0)
        resposta = self.client.post(url, {
            'pet_principal': self.pet.pk,
            'data_resgate': '2026-10-13T10:20',
            'local_resgate': 'Bairro Central',
            'quantidade_gatos': 3,
            'outros_pets': [self.outro.pk],
            'situacao_encontrada': 'Em uma caixa',
            'estado_saude': 'Exame necessário',
            'destino': 'ONG',
            'destino_outro': '',
            'local_encaminhamento': 'Sede da ONG',
            'descricao_resgate': 'Resgatados juntos',
        })
        self.assertEqual(resposta.status_code, 302, resposta.context['form'].errors if resposta.context else '')
        resgate = Resgate.objects.get()
        complemento = ComplementoResgate.objects.get(resgate=resgate)
        self.assertEqual(resgate.pet, self.pet)
        self.assertEqual(resgate.local, 'Bairro Central')
        self.assertEqual(complemento.quantidade_gatos, 3)
        self.assertEqual(list(complemento.outros_pets.all()), [self.outro])
        self.assertEqual(complemento.situacao_encontrada, 'Em uma caixa')

    def test_dados_invalidos_nao_criam_resgate_parcial(self):
        url = reverse('registros:criar', kwargs={'tipo': 'resgates'})
        resposta = self.client.post(url, {
            'pet_principal': self.pet.pk,
            'data_resgate': '2026-10-13T10:20',
            'local_resgate': 'Centro',
            'quantidade_gatos': 1,
            'outros_pets': [self.outro.pk],
            'situacao_encontrada': 'Rua',
            'estado_saude': 'Bom',
            'destino': 'ONG',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Resgate.objects.count(), 0)
        self.assertEqual(ComplementoResgate.objects.count(), 0)
        self.assertIn('quantidade_gatos', resposta.context['form'].errors)

    def test_fluxo_antigo_continua_disponivel(self):
        resgate = Resgate.objects.create(pet=self.pet, data_resgate=timezone.now(), local='Rua antiga')
        url = reverse('registros:criar', kwargs={'tipo': 'resgates'}) + '?existente=1'
        pagina = self.client.get(url)
        self.assertEqual(pagina.status_code, 200)
        self.assertContains(pagina, 'Selecione a opção')
        resposta = self.client.post(url, {
            'modo': 'existente',
            'resgate': resgate.pk, 'quantidade_gatos': 1,
            'situacao_encontrada': 'Em abrigo', 'estado_saude': 'Bom',
            'destino': 'ONG',
        })
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(Resgate.objects.count(), 1)
        self.assertTrue(ComplementoResgate.objects.filter(resgate=resgate).exists())

    def test_acesso_nao_autenticado_bloqueado(self):
        self.client.logout()
        url = reverse('registros:criar', kwargs={'tipo': 'resgates'})
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(url, {'local_resgate': 'Teste'}).status_code, 302)
        self.assertEqual(Resgate.objects.count(), 0)
