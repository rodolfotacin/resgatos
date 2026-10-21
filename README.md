# Resgatos --- Sistema de Gestão de Resgates de Animais

Aplicação web desenvolvida em **Python e Django** para apoiar a
organização das atividades da ONG Resgatos, centralizando informações
sobre pessoas, animais e resgates.

O projeto foi desenvolvido como parte da disciplina **Projeto Integrador II 
do Eixo de Computação da Universidade Virtual do Estado de São Paulo (Univesp)**.

**Repositório:** https://github.com/rodolfotacin/resgatos

## Problema que a aplicação busca resolver

Organizações de resgate precisam manter registros organizados sobre os
animais atendidos, as pessoas relacionadas a eles e os resgates
realizados. O Resgatos busca centralizar esses registros em uma
aplicação web, facilitando a consulta e a atualização das informações.

## Tecnologias

-   Python
-   Django
-   MySQL
-   HTML, CSS e JavaScript

## Requisitos

Antes de começar, instale:

1.  **Python 3**, em uma versão compatível com as dependências do
    projeto.
2.  **MySQL Server**, em execução.
3.  **Git**, para clonar o repositório.
4.  **pip**, normalmente incluído na instalação do Python.
5.  Opcionalmente, um cliente MySQL, como o MySQL Workbench.

Confira as instalações:

``` bash
python --version
python -m pip --version
mysql --version
git --version
```

No Windows, se `python` não for reconhecido, tente `py --version`.

## Instalação e execução local

### 1. Clonar o repositório

``` bash
git clone https://github.com/rodolfotacin/resgatos.git
cd resgatos
```

Execute os próximos comandos no diretório que contém o arquivo
`manage.py`.

### 2. Criar e ativar um ambiente virtual

O ambiente virtual mantém as dependências do projeto isoladas.

**Windows --- Git Bash:**

``` bash
python -m venv .venv
source .venv/Scripts/activate
```

**Windows --- Prompt de Comando (CMD):**

``` bat
python -m venv .venv
.venv\Scripts\activate
```

**Windows --- PowerShell:**

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux ou macOS:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

Atualize o `pip`:

``` bash
python -m pip install --upgrade pip
```

O repositório contém o arquivo `requirements.txt`. Instale as
dependências declaradas nele:

``` bash
python -m pip install -r requirements.txt
```

### 4. Criar o banco de dados MySQL

Inicie o MySQL e conecte-se com uma conta administrativa. Crie o banco:

``` sql
CREATE DATABASE resgatos
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

Recomenda-se criar um usuário exclusivo para a aplicação, com acesso
apenas ao banco `resgatos`. Exemplo --- substitua a senha por uma senha
forte:

``` sql
CREATE USER 'resgatos_app'@'localhost'
    IDENTIFIED BY 'SUBSTITUA_POR_UMA_SENHA_FORTE';

GRANT ALL PRIVILEGES ON resgatos.*
    TO 'resgatos_app'@'localhost';

FLUSH PRIVILEGES;
```

Não utilize a conta administrativa do MySQL como usuário de conexão da
aplicação.

### 5. Configurar a conexão com o banco

Abra as configurações do projeto, localizadas no diretório `config`, e
confira a configuração `DATABASES` no arquivo de settings utilizado pela
aplicação.

Os parâmetros devem apontar para o banco criado, por exemplo:

``` python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'resgatos',
        'USER': 'resgatos_app',
        'PASSWORD': 'SENHA_CONFIGURADA_NO_MYSQL',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

Esse é um exemplo de configuração: mantenha o formato efetivamente
utilizado pelo projeto. Se as configurações forem carregadas por
variáveis de ambiente, defina-as no ambiente local e não grave
credenciais reais no repositório.

O Django também precisa de um driver MySQL compatível. Confira se o
driver necessário está declarado em `requirements.txt`; não instale
versões aleatórias sem verificar a compatibilidade.

### 6. Criar as tabelas do banco

Com o MySQL em execução, a conexão configurada e o ambiente virtual
ativado, execute:

``` bash
python manage.py migrate
```

O comando aplica as migrações do Django e cria as tabelas necessárias.
Ele **não cria automaticamente o usuário inicial da aplicação**.

Para conferir o estado das migrações:

``` bash
python manage.py showmigrations
```

Se houver erro, confira o serviço do MySQL, nome do banco, usuário,
senha e driver.

### 7. Criar ou recuperar o usuário administrativo

O projeto está sendo preparado para disponibilizar o comando de
recuperação administrativa:

``` bash
python manage.py recuperar_administrador
```

Execute esse comando somente depois de confirmar que ele está presente
no código-fonte e que as alterações correspondentes foram aplicadas.
Siga as instruções exibidas no terminal.

As credenciais iniciais são fornecidas diretamente pela equipe criadora
da solução às pessoas autorizadas. **Elas não devem ser publicadas neste
README, em issues ou em commits do GitHub.** A senha também não deve ser
gravada no código-fonte.

O comando administrativo pode criar ou reativar uma conta privilegiada
e, conforme sua implementação, redefinir a senha. Utilize-o somente em
ambiente controlado e por integrantes autorizados da equipe.

### 8. Executar a aplicação

Inicie o servidor de desenvolvimento:

``` bash
python manage.py runserver
```

Abra no navegador:

http://127.0.0.1:8000/

Para interromper o servidor, pressione `Ctrl+C` no terminal.

O servidor `runserver` é destinado ao desenvolvimento local, não à
publicação em produção.

## Comandos úteis

  --------------------------------------------------------------------------------
  Comando                                      Finalidade
  -------------------------------------------- -----------------------------------
  `python manage.py runserver`                 Inicia o servidor de
                                               desenvolvimento

  `python manage.py migrate`                   Aplica as migrações

  `python manage.py makemigrations`            Gera migrações a partir de
                                               alterações nos modelos

  `python manage.py showmigrations`            Lista o estado das migrações

  `python manage.py check`                     Verifica problemas comuns na
                                               configuração do Django

  `python manage.py recuperar_administrador`   Cria ou recupera a conta
                                               administrativa, quando o comando
                                               estiver implementado
  --------------------------------------------------------------------------------

## Segurança

-   Não publique senhas, chaves secretas, arquivos `.env`, backups ou
    dados pessoais no GitHub.
-   Não versione dumps do banco de dados nem arquivos que contenham
    credenciais.
-   Use um usuário MySQL exclusivo para a aplicação e limite suas
    permissões ao banco do projeto.
-   Compartilhe as credenciais administrativas apenas com pessoas
    autorizadas da equipe.
-   Use o comando de recuperação administrativa somente quando
    necessário e com acesso autorizado.

## Contexto acadêmico

Projeto desenvolvido para a disciplina **Projeto Integrador da
Univesp**, aplicando conhecimentos de desenvolvimento de software na
construção de uma solução de apoio às atividades de resgate animal.

## Equipe

Alan dos Santos de Oliveira,
Antonio Fernandes Braga Neto, 
Emerson Carvalho, 
Erica Priscila de Carvalho Santos, 
Maillon Rangel Jacob Moreira, 
Rodolfo Vendrasco Tacin, 
Simone Aparecida Brasil Miller
