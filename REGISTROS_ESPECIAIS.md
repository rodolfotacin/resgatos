# Registros especiais do Resgatos

Este upgrade adiciona Castracoes, Obitos, Internacoes e um fluxo integrado
de Resgates com informacoes complementares, preservando o cadastro original.

## Instalar

1. Instale as dependencias atualizadas: python -m pip install -r requirements.txt.
2. Configure o MySQL e as variaveis de ambiente como ja e feito no projeto.
3. Execute python manage.py migrate para criar as novas tabelas.
4. Inicie o servidor e abra /registros/ apos o login.

Os campos de castracao, obito e internacao vinculam-se a um gato cadastrado.
Um novo resgate pode ser cadastrado diretamente em Registros Especiais,
ou um resgate ja existente pode receber um complemento.

## Testes

python manage.py test apps.registros --settings=config.settings_test_registros

Os testes usam SQLite temporario em memoria; nao enviam nem modificam dados
de operacao reais. Arquivos .env, bancos, backups e fotos nao devem ser
versionados.
