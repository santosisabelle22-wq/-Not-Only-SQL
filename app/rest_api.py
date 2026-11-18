"""API REST (FastAPI) para o CRUD de alunos no Firestore."""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status

from .models import AlunoCreate, AlunoOut, AlunoUpdate
from .repository import AlunoRepository

app = FastAPI(
    title="CRUD de Alunos - Firebase Cloud Firestore",
    version="1.0.0",
    description="Atividade prática de NoSQL: CREATE, READ, UPDATE, DELETE e consultas.",
)

repositorio = AlunoRepository()


def _nao_encontrado() -> None:
    raise HTTPException(status_code=404, detail="Aluno não encontrado.")


@app.get("/", tags=["informações"])
def raiz() -> Dict[str, str]:
    return {
        "mensagem": "API de alunos com Cloud Firestore",
        "documentação": "/docs",
    }


@app.post(
    "/alunos",
    response_model=AlunoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["alunos"],
    summary="CREATE - cadastrar aluno",
)
def criar_aluno(aluno: AlunoCreate) -> AlunoOut:
    return repositorio.criar(aluno)


@app.get(
    "/alunos",
    response_model=List[AlunoOut],
    tags=["alunos"],
    summary="READ - listar alunos (com filtros opcionais)",
)
def listar_alunos(
    turma: Optional[str] = Query(default=None, description="Filtrar pela turma"),
    dataNascimento: Optional[str] = Query(
        default=None, description="Filtrar pela data no formato AAAA-MM-DD"
    ),
) -> List[AlunoOut]:
    try:
        return repositorio.consultar(turma=turma, data_nascimento=dataNascimento)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@app.get(
    "/alunos/turma/{turma}",
    response_model=List[AlunoOut],
    tags=["consultas"],
    summary="Consultar alunos por turma",
)
def listar_por_turma(turma: str) -> List[AlunoOut]:
    return repositorio.listar_por_turma(turma)


@app.get(
    "/alunos/data-nascimento/{data_nascimento}",
    response_model=List[AlunoOut],
    tags=["consultas"],
    summary="Consultar alunos por data de nascimento",
)
def listar_por_data_nascimento(data_nascimento: str) -> List[AlunoOut]:
    try:
        return repositorio.listar_por_data_nascimento(data_nascimento)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@app.get(
    "/alunos/{aluno_id}",
    response_model=AlunoOut,
    tags=["alunos"],
    summary="READ - buscar aluno pelo ID do documento",
)
def buscar_aluno(aluno_id: str) -> AlunoOut:
    aluno = repositorio.buscar_por_id(aluno_id)
    if aluno is None:
        _nao_encontrado()
    return aluno


@app.put(
    "/alunos/{aluno_id}",
    response_model=AlunoOut,
    tags=["alunos"],
    summary="UPDATE - atualizar aluno",
)
@app.patch(
    "/alunos/{aluno_id}",
    response_model=AlunoOut,
    tags=["alunos"],
    summary="UPDATE - atualizar parcialmente o aluno",
)
def atualizar_aluno(aluno_id: str, alteracoes: AlunoUpdate) -> AlunoOut:
    aluno = repositorio.atualizar(aluno_id, alteracoes)
    if aluno is None:
        _nao_encontrado()
    return aluno


@app.delete(
    "/alunos/{aluno_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["alunos"],
    summary="DELETE - excluir aluno",
)
def excluir_aluno(aluno_id: str) -> None:
    if not repositorio.excluir(aluno_id):
        _nao_encontrado()
