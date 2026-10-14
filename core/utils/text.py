
import unicodedata


def get_initials(name: str) -> str:
    """Retorna os dois primeiros caracteres do nome, sem acentos."""

    name = name.strip()

    if not name:
        return ''

    # Decompõe os caracteres acentuados e remove os diacríticos.
    name = unicodedata.normalize('NFD', name)
    name = ''.join(
        char for char in name
        if unicodedata.category(char) != 'Mn'
    )

    # Obtém os dois primeiros caracteres.
    initials = name[:2]

    # Primeira letra maiúscula e segunda minúscula.
    if len(initials) == 1:
        return initials.upper()

    return initials[0].upper() + initials[1].lower()


def get_telefone(value: str) -> str:
    if not value:
        return ''

    numeros = ''.join(
        char for char in str(value)
        if char.isdigit()
    )

    # Remove o código do Brasil, quando presente
    if numeros.startswith('55') and len(numeros) in (12, 13):
        numeros = numeros[2:]

    if len(numeros) == 11:
        return f'({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}'

    if len(numeros) == 10:
        return f'({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}'

    return value


def get_cpf(value: str) -> str:
    if not value:
        return ''

    numeros = ''.join(
        char for char in str(value)
        if char.isdigit()
    )

    if len(numeros) == 11:
        return f'{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}'

    return value