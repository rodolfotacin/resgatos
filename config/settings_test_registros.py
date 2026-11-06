# Copie este arquivo para: config/settings_test_registros.py
# Os testes usam SQLite em memória, não o MySQL real nem um banco para enviar ao GitHub.
from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
