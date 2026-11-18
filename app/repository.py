"""Camada de persistência da coleção `alunos` no Cloud Firestore."""

from __future__ import annotations

from typing import Optional

from .config import get_db
from .models import AlunoCreate, AlunoOut, AlunoUpdate, validar_data_nascimento

COLECAO = "alunos"


class AlunoRepository:
    """Implementa CREATE, READ, UPDATE, DELETE e consultas filtradas."""

    def __init__(self, db=None):
        """`db` pode ser injetado para testes; por padrão usa o Firestore real."""
        self._db = db

    @property
    def db(self):
        if self._db is None:
            self._db = get_db()
        return self._db

    @staticmethod
    def _para_aluno(doc) -> AlunoOut:
        return AlunoOut(id=doc.id, **(doc.to_dict() or {}))

    # ------------------------------------------------------------------ CRUD
    def criar(self, aluno: AlunoCreate) -> AlunoOut:
        dados = aluno.model_dump()
        _, referencia = self.db.collection(COLECAO).add(dados)
        return AlunoOut(id=referencia.id, **dados)

    def buscar_por_id(self, aluno_id: str) -> Optional[AlunoOut]:
        doc = self.db.collection(COLECAO).document(aluno_id).get()
        return self._para_aluno(doc) if doc.exists else None

    def listar_todos(self) -> list[AlunoOut]:
        return [self._para_aluno(doc) for doc in self.db.collection(COLECAO).stream()]

    def atualizar(self, aluno_id: str, alteracoes: AlunoUpdate) -> Optional[AlunoOut]:
        referencia = self.db.collection(COLECAO).document(aluno_id)
        if not referencia.get().exists:
            return None

        dados = alteracoes.model_dump(exclude_unset=True, exclude_none=True)
        if dados:
            referencia.update(dados)
        return self.buscar_por_id(aluno_id)

    def excluir(self, aluno_id: str) -> bool:
        referencia = self.db.collection(COLECAO).document(aluno_id)
        if not referencia.get().exists:
            return False
        referencia.delete()
        return True

    # -------------------------------------------------------------- Consultas
    def listar_por_turma(self, turma: str) -> list[AlunoOut]:
        return self.consultar(turma=turma)

    def listar_por_data_nascimento(self, data_nascimento: str) -> list[AlunoOut]:
        return self.consultar(data_nascimento=data_nascimento)

    def consultar(
        self,
        turma: Optional[str] = None,
        data_nascimento: Optional[str] = None,
    ) -> list[AlunoOut]:
        """Filtra por turma e/ou data de nascimento (os dois filtros são opcionais)."""
        consulta = self.db.collection(COLECAO)

        if turma:
            consulta = consulta.where("turma", "==", turma)
        if data_nascimento:
            consulta = consulta.where(
                "dataNascimento", "==", validar_data_nascimento(data_nascimento)
            )

        return [self._para_aluno(doc) for doc in consulta.stream()]
