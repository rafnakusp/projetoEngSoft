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

- python versão 3.6 ou superior

## Guia de uso:

### Para iniciar o ambiente:
- Criar um ambiente virtual chamado env usando: python -m venv env
- Ativar o ambiente virtual do python com o comando '.\env\scripts\Activate.ps1'
- Instalar o django utilizando o pip com 'pip install django'
- Inicializar o servidor com o comando 'python manage.py runserver'

### Para subir o banco de dados e testá-lo:
- Criar a migração do banco: 'python manage.py makemigrations'
- Criar o banco de dados SQLite: 'python manage.py migrate'
- Executar os testes: 'python manage.py test'
