
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Pessoa(models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=150, unique=True)
    telefone = models.CharField(max_length=45, unique=True)
    foto = models.ImageField(upload_to='pessoas/', blank=True, null=True)

    cep = models.CharField(max_length=15)
    endereco = models.CharField(max_length=150)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=150, blank=True, null=True)
    bairro = models.CharField(max_length=45)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=45)

    is_attendance_responsible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'pessoa'
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class UsuarioManager(BaseUserManager):
    def create_user(self, pessoa, password=None, **extra_fields):
        if not pessoa:
            raise ValueError('Uma pessoa deve ser informada.')

        usuario = self.model(pessoa=pessoa, **extra_fields)

        if password:
            usuario.set_password(password)
        else:
            raise ValueError('A senha deve ser informada.')

        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, pessoa, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        return self.create_user(pessoa, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.PROTECT,
        related_name='usuario',
        db_column='pessoa_id',
    )

    # A senha é armazenada como hash pelo mecanismo do Django.
    password = models.CharField(max_length=128, db_column='senha')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        db_column='last_access',
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'pessoa'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.pessoa.nome
