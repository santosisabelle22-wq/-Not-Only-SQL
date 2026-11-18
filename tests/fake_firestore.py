"""Firestore em memória, usado apenas nos testes (sem credenciais reais)."""

from __future__ import annotations

from uuid import uuid4


class Snapshot:
    def __init__(self, doc_id: str, dados: dict | None):
        self.id = doc_id
        self._dados = dados

    @property
    def exists(self) -> bool:
        return self._dados is not None

    def to_dict(self) -> dict | None:
        return dict(self._dados) if self._dados is not None else None


class DocumentReference:
    def __init__(self, documentos: dict, doc_id: str):
        self._documentos = documentos
        self.id = doc_id

    def get(self) -> Snapshot:
        return Snapshot(self.id, self._documentos.get(self.id))

    def set(self, dados: dict) -> None:
        self._documentos[self.id] = dict(dados)

    def update(self, dados: dict) -> None:
        if self.id not in self._documentos:
            raise KeyError(self.id)
        self._documentos[self.id].update(dados)

    def delete(self) -> None:
        self._documentos.pop(self.id, None)


class Query:
    def __init__(self, documentos: dict, filtros: tuple = ()):
        self._documentos = documentos
        self._filtros = filtros

    def where(self, campo: str, operador: str, valor) -> "Query":
        return Query(self._documentos, (*self._filtros, (campo, operador, valor)))

    def stream(self):
        for doc_id, dados in self._documentos.items():
            if all(
                dados.get(campo) == valor
                for campo, operador, valor in self._filtros
                if operador == "=="
            ):
                yield Snapshot(doc_id, dados)


class CollectionReference:
    def __init__(self, documentos: dict):
        self._documentos = documentos

    def add(self, dados: dict):
        doc_id = uuid4().hex
        self._documentos[doc_id] = dict(dados)
        return None, DocumentReference(self._documentos, doc_id)

    def document(self, doc_id: str) -> DocumentReference:
        return DocumentReference(self._documentos, doc_id)

    def where(self, campo: str, operador: str, valor) -> Query:
        return Query(self._documentos).where(campo, operador, valor)

    def stream(self):
        return Query(self._documentos).stream()


class FakeFirestore:
    def __init__(self):
        self._colecoes: dict[str, dict] = {}

    def collection(self, nome: str) -> CollectionReference:
        return CollectionReference(self._colecoes.setdefault(nome, {}))
