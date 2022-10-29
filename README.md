# projetoEngSoft
Projeto de Engenharia de Software do segundo quadrimestre acadêmico de 2022

## Nome do grupo 
Grupo 4

## Integrantes do grupo
- Gabriel Coutinho Ribeiro - 11803437
- Rafael Katsuo Nakata     - 11803819
- Vinicius de Castro Lopes - 10770134

## Informações Gerais 
Esse é o projeto da disciplina Laboratório de Engenharia de Software - PCS3643, que é um webapp em django para monitorar os voos de um aeroporto hipotético.

## Exigências de ambiente
- Windows
- Powershell
- python versão 3.6 ou superior
- git

## Guia de uso

### Para baixar o projeto
- Na pasta que preferir, executar o comando `git clone https://github.com/rafnakusp/projetoEngSoft.git`

### Para criar um ambiente virtual
- Entrar na pasta `.\projetoEngSoft\source do projeto`
- Criar um ambiente virtual chamado env usando: `python -m venv env`

### Para ativar o ambiente e rodar a aplicação
- Ativar o ambiente virtual do python com o comando `.\env\scripts\Activate.ps1` ou `.\env\bin\Activate.ps1`
- Se já não instalado, instalar as dependências com `pip install -r requirements.txt`
- Ir para a pasta `.\source\MyProj`
- Inicializar o servidor com o comando `python manage.py runserver`

### Para subir o banco de dados e testá-lo
- Criar a migração do banco: `python manage.py makemigrations`
- Criar o banco de dados SQLite: `python manage.py migrate`
- Executar os testes: `python manage.py test`
- Inicializar o servidor com o comando `python manage.py runserver`

### Para acessar os templates da aplicação a partir da pasta do projeto
- Entrar na pasta `.\template`

### Para acessar a aplicação no navegador
- Acessar a url: `localhost:8000/login/`

### Para gerar as tabelas básicas
- Acessar a url: `localhost:8000/criartabelasproducao/`
