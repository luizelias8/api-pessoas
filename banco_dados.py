import os
from dotenv import load_dotenv
import psycopg2

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Função para obter a conexão PostgreSQL
def obter_conexao_postgresql():
    # Obtém as variáveis de ambiente para o banco de dados
    servidor = os.getenv('SERVIDOR_BANCO')
    porta = os.getenv('PORTA_BANCO', 5432) # Usa 5432 como valor padrão para a porta
    nome = os.getenv('NOME_BANCO')
    usuario = os.getenv('USUARIO_BANCO')
    senha = os.getenv('SENHA_BANCO')

    # Conectar ao banco usando psycopg2
    return psycopg2.connect(
        dbname=nome, # Nome do banco de dados
        user=usuario, # Usuário do banco
        password=senha, # Senha do banco
        host=servidor, # Servidor do banco
        port=porta # Porta do banco
    )

# Função para criar o banco de dados e a tabela
def criar_tabela():
    # Conecta ao banco de dados PostgreSQL
    conexao = obter_conexao_postgresql()

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()

    # Cria a tabela 'pessoas' caso ainda não exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id SERIAL PRIMARY KEY, -- ID único para cada pessoa (automaticamente gerado)
            nome TEXT NOT NULL, -- Nome da pessoa (obrigatório)
            idade INTEGER NOT NULL, -- Idade da pessoa (obrigatório)
            sexo TEXT NOT NULL, -- Sexo da pessoa (obrigatório)
            email TEXT -- Email da pessoa (opcional)
        )
    """)

    # Salva as alterações no banco de dados
    conexao.commit()

    # Fecha a conexão com o banco de dados
    conexao.close()

# Função para popular as pessoas no banco de dados
def popular_tabela():
    # Conecta ao banco de dados PostgreSQL
    conexao = obter_conexao_postgresql()

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()

    # Lista de dados para inserir
    pessoas = [
        ('João Silva', 30, 'Masculino', 'joao.silva@exemplo.com'),
        ('Maria Oliveira', 25, 'Feminino', 'maria.oliveira@exemplo.com'),
        ('Pedro Santos', 40, 'Masculino', None),
        ('Ana Costa', 35, 'Feminino', 'ana.costa@exemplo.com'),
        ('Lucas Lima', 28, 'Masculino', 'lucas.lima@exemplo.com'),
    ]

    # Inserir os dados na tabela
    cursor.executemany("""
        INSERT INTO pessoas (nome, idade, sexo, email)
        VALUES (%s, %s, %s, %s)
    """, pessoas)

    # Salva as alterações no banco de dados
    conexao.commit()

    # Fecha a conexão com o banco
    conexao.close()

    print("Tabela 'pessoas' populada com sucesso!")

# Função para listar as pessoas no banco de dados
def listar_pessoas_banco():
    # Conecta ao banco de dados PostgreSQL
    conexao = obter_conexao_postgresql()

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()

    # Executa a consulta para obter todas as pessoas da tabela
    cursor.execute('SELECT * FROM pessoas')
    # Recupera todas as linhas do resultado da consulta
    pessoas = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    conexao.close()

    # Transforma os resultados em uma lista de dicionários para facilitar a resposta em JSON
    return [
        {
            'id': pessoa[0], # ID da pessoa
            'nome': pessoa[1], # Nome da pessoa
            'idade': pessoa[2], # Idade da pessoa
            'sexo': pessoa[3], # Sexo da pessoa
            'email': pessoa[4], # Email da pessoa (pode ser None se não informado)
        }
        for pessoa in pessoas
    ]

# Função para inserir uma nova pessoa no banco de dados
def criar_pessoa_banco(nome: str, idade: int, sexo: str, email: str = None):
    # Conecta ao banco de dados PostgreSQL
    conexao = obter_conexao_postgresql()

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()

    # Insere a pessoa na tabela 'pessoas'
    cursor.execute("""
        INSERT INTO pessoas (nome, idade, sexo, email)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (nome, idade, sexo, email))
    # No PostgreSQL, para obter o ID gerado por um INSERT, é necessário usar a cláusula RETURNING id.
    # Isso permite que o banco de dados retorne o valor do campo especificado (geralmente a chave primária) imediatamente após a inserção,
    # sem a necessidade de uma consulta adicional.
    # Se você não usar o RETURNING, será necessário fazer outra consulta para recuperar o ID,
    # como buscando o maior id ou usando outra lógica

    # Salva as alterações no banco de dados
    conexao.commit()

    # Obtém o ID da nova pessoa criada
    id_pessoa = cursor.fetchone()[0]

    # Fecha a conexão com o banco
    conexao.close()

    return id_pessoa

# Função para buscar uma pessoa no banco de dados pelo ID
def buscar_pessoa_por_id(id: int):
    # Conecta ao banco de dados PostgreSQL
    conexao = obter_conexao_postgresql()

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()

    # Executa a consulta SQL para buscar a pessoa pelo ID fornecido
    # O '%s' é usado como marcador de posição para evitar SQL Injection
    cursor.execute("SELECT id, nome, idade, sexo, email FROM pessoas WHERE id = %s", (id,))

    # Obtém o resultado da consulta (se houver) como uma tupla
    pessoa = cursor.fetchone()

    # Fecha a conexão com o banco de dados
    conexao.close()

    # Verifica se a pessoa foi encontrada
    if pessoa:
        # Retorna os dados da pessoa como um dicionário
        return {
            'id': pessoa[0], # ID da pessoa
            'nome': pessoa[1], # Nome da pessoa
            'idade': pessoa[2], # Idade da pessoa
            'sexo': pessoa[3], # Sexo da pessoa
            'email': pessoa[4] if pessoa[4] else None, # Email ou None se for nulo
        }

    # Retorna None se nenhuma pessoa for encontrada
    return None

def deletar_pessoa_banco(id: int):
    # Conecta ao banco de dados PostgreSQL
    conexao = obter_conexao_postgresql()

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()

    # Executa uma consulta para verificar se a pessoa com o ID fornecido existe
    cursor.execute('SELECT * FROM pessoas WHERE id = %s', (id,))

    # Obtém o resultado da consulta (None se não encontrar)
    pessoa = cursor.fetchone()

    if not pessoa:
        # Fecha a conexão antes de levantar a exceção
        conexao.close()
        raise ValueError(f"Pessoa com ID {id} não encontrada.")

    # Executa o comando para deletar a pessoa com o ID fornecido
    cursor.execute('DELETE FROM pessoas WHERE id = %s', (id,))
    # Confirma as alterações realizadas no banco de dados
    conexao.commit()

    # Fecha a conexão com o banco de dados para liberar recursos
    conexao.close()

# Função para editar os dados de uma pessoa no banco de dados
def editar_pessoa_banco(id: int, nome: str, idade: int, sexo: str, email: str = None):
    # Conecta ao banco de dados PostgreSQL
    conexao = obter_conexao_postgresql()

    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE pessoas
        SET nome = %s, idade = %s, sexo = %s, email = %s
        WHERE id = %s
    """, (nome, idade, sexo, email, id))

    # Confirma as alterações realizadas no banco de dados
    conexao.commit()

    # Fecha a conexão com o banco de dados para liberar recursos
    conexao.close()