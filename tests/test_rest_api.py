"""Testes da API REST com o repositório falso (sem Firebase)."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

import app.rest_api as rest_api
from app.repository import AlunoRepository
from tests.fake_firestore import FakeFirestore

ANA = {
    "nome": "Ana",
    "turma": "3DSB",
    "dataNascimento": "2009-05-15",
    "ativo": True,
}

BRUNO = {
    "nome": "Bruno",
    "turma": "2AM",
    "dataNascimento": "2010-01-20",
    "ativo": False,
}


class RestApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self._repositorio_original = rest_api.repositorio
        rest_api.repositorio = AlunoRepository(FakeFirestore())
        self.client = TestClient(rest_api.app)

    def tearDown(self) -> None:
        rest_api.repositorio = self._repositorio_original

    def test_crud_pela_api(self) -> None:
        resposta = self.client.post("/alunos", json=ANA)
        self.assertEqual(resposta.status_code, 201)
        aluno_id = resposta.json()["id"]

        self.assertEqual(len(self.client.get("/alunos").json()), 1)
        self.assertEqual(
            self.client.get(f"/alunos/{aluno_id}").json()["nome"], "Ana"
        )

        atualizado = self.client.patch(f"/alunos/{aluno_id}", json={"turma": "4DSA"})
        self.assertEqual(atualizado.status_code, 200)
        self.assertEqual(atualizado.json()["turma"], "4DSA")

        self.assertEqual(self.client.delete(f"/alunos/{aluno_id}").status_code, 204)
        self.assertEqual(self.client.get(f"/alunos/{aluno_id}").status_code, 404)

    def test_consultas(self) -> None:
        self.client.post("/alunos", json=ANA)
        self.client.post("/alunos", json=BRUNO)

        self.assertEqual(len(self.client.get("/alunos?turma=3DSB").json()), 1)
        self.assertEqual(len(self.client.get("/alunos/turma/2AM").json()), 1)
        self.assertEqual(
            len(self.client.get("/alunos/data-nascimento/2009-05-15").json()), 1
        )
        self.assertEqual(
            len(
                self.client.get(
                    "/alunos?turma=3DSB&dataNascimento=2009-05-15"
                ).json()
            ),
            1,
        )

    def test_erros_de_validacao_e_busca(self) -> None:
        self.assertEqual(
            self.client.post("/alunos", json={**ANA, "dataNascimento": "15-05-2009"}).status_code,
            422,
        )
        self.assertEqual(
            self.client.get("/alunos?dataNascimento=2009-02-30").status_code, 422
        )
        self.assertEqual(self.client.get("/alunos/id-inexistente").status_code, 404)


if __name__ == "__main__":
    unittest.main()
