"""Testes de CRUD e consultas usando o Firestore falso em memória."""

import unittest

from pydantic import ValidationError

from app.models import AlunoCreate, AlunoUpdate
from app.repository import AlunoRepository
from tests.fake_firestore import FakeFirestore

DADOS_ANA = {
    "nome": "Ana",
    "turma": "3DSB",
    "dataNascimento": "2009-05-15",
    "ativo": True,
}

DADOS_BRUNO = {
    "nome": "Bruno",
    "turma": "2AM",
    "dataNascimento": "2010-01-20",
    "ativo": False,
}


class AlunoRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = AlunoRepository(FakeFirestore())

    def test_crud_completo(self) -> None:
        criado = self.repositorio.criar(AlunoCreate(**DADOS_ANA))
        self.assertTrue(criado.id)
        self.assertEqual(criado.nome, "Ana")

        encontrado = self.repositorio.buscar_por_id(criado.id)
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.dataNascimento, "2009-05-15")

        atualizado = self.repositorio.atualizar(
            criado.id, AlunoUpdate(turma="4DSA", ativo=False)
        )
        self.assertEqual(atualizado.turma, "4DSA")
        self.assertFalse(atualizado.ativo)
        self.assertEqual(atualizado.nome, "Ana")  # campo não enviado permanece

        self.assertTrue(self.repositorio.excluir(criado.id))
        self.assertIsNone(self.repositorio.buscar_por_id(criado.id))
        self.assertFalse(self.repositorio.excluir(criado.id))

    def test_listagem_e_consultas(self) -> None:
        self.repositorio.criar(AlunoCreate(**DADOS_ANA))
        self.repositorio.criar(AlunoCreate(**DADOS_BRUNO))

        self.assertEqual(len(self.repositorio.listar_todos()), 2)

        por_turma = self.repositorio.listar_por_turma("3DSB")
        self.assertEqual(len(por_turma), 1)
        self.assertEqual(por_turma[0].nome, "Ana")

        por_data = self.repositorio.listar_por_data_nascimento("2010-01-20")
        self.assertEqual(len(por_data), 1)
        self.assertEqual(por_data[0].nome, "Bruno")

        combinado = self.repositorio.consultar(
            turma="3DSB", data_nascimento="2009-05-15"
        )
        self.assertEqual(len(combinado), 1)

        vazio = self.repositorio.consultar(
            turma="3DSB", data_nascimento="2010-01-20"
        )
        self.assertEqual(vazio, [])

    def test_atualizar_inexistente(self) -> None:
        self.assertIsNone(
            self.repositorio.atualizar("id-que-nao-existe", AlunoUpdate(nome="X"))
        )

    def test_validacao_de_data(self) -> None:
        with self.assertRaises(ValidationError):
            AlunoCreate(**{**DADOS_ANA, "dataNascimento": "15-05-2009"})
        with self.assertRaises(ValueError):
            self.repositorio.listar_por_data_nascimento("2009-02-30")


if __name__ == "__main__":
    unittest.main()
