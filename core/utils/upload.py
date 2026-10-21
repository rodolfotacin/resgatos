import os


def foto_pessoa(instance, filename):
    extensao = os.path.splitext(filename)[1].lower()
    return f'pessoas/{instance.id}{extensao}'


def foto_pet(instance, filename):
    extensao = os.path.splitext(filename)[1].lower()
    return f'pets/{instance.id}{extensao}'