
from django.contrib.auth.backends import ModelBackend

from .models import Usuario


class PessoaBackend(ModelBackend):

    def authenticate(
        self,
        request,
        username=None,
        password=None,
        **kwargs,
    ):
        if not username or not password:
            return None

        identificador = username.strip()

        usuarios = Usuario.objects.select_related('pessoa').filter(
            pessoa__is_active=True,
            is_active=True,
        )

        # Login administrativo por nome de usuário.
        usuario = usuarios.filter(
            username__iexact=identificador
        ).first()

        # Mantém os meios de login existentes.
        if usuario is None:
            usuario = usuarios.filter(
                pessoa__cpf=identificador
            ).first()

        if usuario is None:
            usuario = usuarios.filter(
                pessoa__email__iexact=identificador
            ).first()

        if usuario is None:
            usuario = usuarios.filter(
                pessoa__telefone=identificador
            ).first()

        if (
            usuario is not None
            and usuario.check_password(password)
            and self.user_can_authenticate(usuario)
        ):
            return usuario

        return None
