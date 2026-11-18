"""Modelos de dados e validações da coleção `alunos`."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

FORMATO_DATA = "AAAA-MM-DD"


def validar_data_nascimento(valor: str) -> str:
    """Valida uma data no formato AAAA-MM-DD e a devolve normalizada."""
    try:
        return date.fromisoformat(valor).isoformat()
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"dataNascimento deve ser uma data válida no formato {FORMATO_DATA}."
        ) from exc


class AlunoBase(BaseModel):
    """Campos obrigatórios de um aluno."""

    nome: str = Field(..., min_length=1, max_length=120)
    turma: str = Field(..., min_length=1, max_length=40)
    dataNascimento: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    ativo: bool = True

    @field_validator("dataNascimento")
    @classmethod
    def _data_valida(cls, valor: str) -> str:
        return validar_data_nascimento(valor)


class AlunoCreate(AlunoBase):
    """Dados enviados no cadastro de um aluno."""


class AlunoUpdate(BaseModel):
    """Campos opcionais para atualização parcial de um aluno."""

    nome: Optional[str] = Field(default=None, min_length=1, max_length=120)
    turma: Optional[str] = Field(default=None, min_length=1, max_length=40)
    dataNascimento: Optional[str] = Field(
        default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    ativo: Optional[bool] = None

    @field_validator("dataNascimento")
    @classmethod
    def _data_valida(cls, valor: Optional[str]) -> Optional[str]:
        if valor is None:
            return None
        return validar_data_nascimento(valor)


class AlunoOut(AlunoBase):
    """Aluno retornado pelo Firestore, incluindo o ID do documento."""

    id: str
