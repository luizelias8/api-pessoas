from fastapi import FastAPI, status, HTTPException
from banco_dados import *
from modelos import Pessoa

# Inicializa o aplicativo FastAPI
app = FastAPI()

# Garante que o banco de dados e a tabela existam ao iniciar o servidor
criar_tabela()

# Rota GET para listar todas as pessoas
@app.get('/pessoas')
def listar_pessoas():
    # Chama a função que consulta o banco de dados e retorna a lista de pessoas
    return listar_pessoas_banco()

# Rota POST para criar uma nova pessoa
@app.post('/pessoas', status_code=status.HTTP_201_CREATED)
def criar_pessoa(pessoa: Pessoa):
    # Chama a função para criar a pessoa no banco
    id_pessoa = criar_pessoa_banco(
        nome=pessoa.nome,
        idade=pessoa.idade,
        sexo=pessoa.sexo,
        email=pessoa.email
    )

    # Retorna os dados completos da pessoa, incluindo o id gerado
    return {'id': id_pessoa, **pessoa.model_dump()}

# Rota GET para buscar uma pessoa pelo ID
@app.get('/pessoas/{id}')
def obter_pessoa(id: int):
    # Chama a função que busca a pessoa no banco de dados pelo ID
    pessoa = buscar_pessoa_por_id(id)

    # Verifica se a pessoa foi encontrada no banco de dados
    if pessoa:
        # Retorna os dados da pessoa como resposta JSON com status 200 (padrão do FastAPI)
        return pessoa

    # Caso a pessoa não seja encontrada, retorna uma mensagem de erro com status 404
    raise HTTPException(status_code=404, detail=f"Pessoa com ID {id} não encontrada.")

# Rota DELETE para deletar uma pessoa pelo ID
@app.delete('/pessoas/{id}')
def deletar_pessoa(id: int):
    try:
        # Chama a função do banco de dados para deletar a pessoa com o ID fornecido
        deletar_pessoa_banco(id)
    except ValueError as e:
        # Se a pessoa não for encontrada no banco, um ValueError é levantado
        # A exceção é convertida em um erro HTTP 404 com a mensagem de erro
        raise HTTPException(status_code=404, detail=str(e))

    # Se a exclusão for bem-sucedida, retorna uma mensagem de sucesso
    return {'mensagem': f'Pessoa com ID {id} foi deletada com sucesso.'}

# Rota PUT para editar uma pessoa
@app.put('/pessoas/{id}')
def editar_pessoa(id: int, pessoa: Pessoa):
    try:
        # Chama a função de editar no banco de dados
        editar_pessoa_banco(id, pessoa.nome, pessoa.idade, pessoa.sexo, pessoa.email)
        return {'mensagem': 'Pessoa atualizada com sucesso!'}
    except Exception as e:
        # Levanta uma exceção se ocorrer algum erro no banco de dados
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar pessoa: {str(e)}")