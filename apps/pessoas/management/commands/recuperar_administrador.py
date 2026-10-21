
import getpass

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.pessoas.models import Pessoa, Usuario


class Command(BaseCommand):
    help = 'Cria ou recupera a conta administrativa do Resgatos.'

    def handle(self, *args, **options):
        username = 'supervisor'

        self.stdout.write(
            'Recuperação da conta administrativa do Resgatos'
        )

        senha = getpass.getpass(
            'Senha inicial do supervisor: '
        )

        if not senha:
            raise CommandError('A senha não pode ficar vazia.')

        with transaction.atomic():
            pessoa, pessoa_criada = Pessoa.objects.get_or_create(
                cpf='999.999.999-99',
                defaults={
                    'nome': 'Supervisor do Sistema',
                    'email': 'supervisor@univesp',
                    'telefone': '(99) 99999-9999',
                    'cep': '00000-000',
                    'endereco': 'Endereco ficticio',
                    'numero': '0',
                    'bairro': 'Nao aplicavel',
                    'cidade': 'Nao aplicavel',
                    'estado': 'NA',
                    'is_active': True,
                },
            )

            if not pessoa.is_active:
                pessoa.is_active = True
                pessoa.save(update_fields=['is_active'])

            usuario = Usuario.objects.filter(
                username__iexact=username
            ).first()

            if usuario is None:
                usuario = Usuario.objects.filter(
                    pessoa=pessoa
                ).first()

            if usuario is not None:
                usuario.is_active = True
                usuario.is_staff = True
                usuario.is_superuser = True
                usuario.set_password(senha)
                usuario.save()
                acao = 'recuperada'
            else:
                usuario = Usuario.objects.create_superuser(
                    pessoa=pessoa,
                    password=senha,
                    username=username,
                )
                acao = 'criada'

        self.stdout.write(
            self.style.SUCCESS(
                f'Conta administrativa {acao} com sucesso.'
            )
        )
