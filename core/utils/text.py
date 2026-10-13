
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
