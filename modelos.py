from pydantic import BaseModel

class Pessoa(BaseModel):
    nome: str
    idade: int
    sexo: str
    email: str | None = None # Atributo opcional