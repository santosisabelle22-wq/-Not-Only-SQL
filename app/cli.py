"""Interface de linha de comando (menu no terminal)."""

from __future__ import annotations

from pydantic import ValidationError

from .models import AlunoCreate, AlunoOut, AlunoUpdate
from .repository import AlunoRepository


def _linha() -> None:
    print("-" * 78)


def _ler_obrigatorio(mensagem: str) -> str:
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Campo obrigatório. Tente novamente.")


def _ler_sim_nao(mensagem: str, permitir_vazio: bool = False) -> str:
    while True:
        valor = input(mensagem).strip().lower()
        if valor == "" and permitir_vazio:
            return ""
        if valor in ("s", "sim"):
            return "s"
        if valor in ("n", "nao", "não"):
            return "n"
        print("Digite 's' ou 'n'.")


def _coletar_criacao() -> AlunoCreate:
    print("\n--- CREATE: cadastrar aluno ---")
    while True:
        try:
            return AlunoCreate(
                nome=_ler_obrigatorio("Nome: "),
                turma=_ler_obrigatorio("Turma: "),
                dataNascimento=_ler_obrigatorio(
                    "Data de nascimento (AAAA-MM-DD): "
                ),
                ativo=_ler_sim_nao("Ativo? [s/n]: ") == "s",
            )
        except ValidationError as erro:
            print(f"Dados inválidos: {erro.errors()[0]['msg']}")


def _coletar_atualizacao() -> AlunoUpdate:
    print("\n--- UPDATE: atualizar aluno (Enter = manter valor atual) ---")
    while True:
        dados: dict = {}
        nome = input("Nome: ").strip()
        turma = input("Turma: ").strip()
        data = input("Data de nascimento (AAAA-MM-DD): ").strip()
        ativo = _ler_sim_nao("Ativo? [s/n] (Enter = manter): ", permitir_vazio=True)

        if nome:
            dados["nome"] = nome
        if turma:
            dados["turma"] = turma
        if data:
            dados["dataNascimento"] = data
        if ativo == "s":
            dados["ativo"] = True
        elif ativo == "n":
            dados["ativo"] = False

        try:
            return AlunoUpdate(**dados)
        except ValidationError as erro:
            print(f"Dados inválidos: {erro.errors()[0]['msg']}")


def _mostrar(alunos: list[AlunoOut]) -> None:
    if not alunos:
        print("\nNenhum aluno encontrado.")
        return

    print(
        f"\n{'ID':<24} {'Nome':<24} {'Turma':<10} "
        f"{'Nascimento':<12} {'Ativo'}"
    )
    _linha()
    for aluno in alunos:
        print(
            f"{aluno.id:<24} {aluno.nome[:24]:<24} {aluno.turma[:10]:<10} "
            f"{aluno.dataNascimento:<12} {'sim' if aluno.ativo else 'não'}"
        )
    _linha()
    print(f"Total: {len(alunos)} aluno(s)")


def _exibir_menu() -> None:
    print("\n" + "=" * 60)
    print("  CRUD DE ALUNOS - FIREBASE CLOUD FIRESTORE")
    print("=" * 60)
    print("  1 - Cadastrar aluno (CREATE)")
    print("  2 - Listar todos os alunos (READ)")
    print("  3 - Buscar aluno por ID")
    print("  4 - Atualizar aluno (UPDATE)")
    print("  5 - Excluir aluno (DELETE)")
    print("  6 - Consultar por turma")
    print("  7 - Consultar por data de nascimento")
    print("  8 - Consultar por turma E data")
    print("  0 - Sair")
    print("-" * 60)


def main() -> None:
    repositorio = AlunoRepository()

    try:
        while True:
            _exibir_menu()
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    aluno = repositorio.criar(_coletar_criacao())
                    print(f"\nAluno cadastrado. ID do documento: {aluno.id}")

                elif opcao == "2":
                    _mostrar(repositorio.listar_todos())

                elif opcao == "3":
                    aluno = repositorio.buscar_por_id(
                        _ler_obrigatorio("ID do aluno: ")
                    )
                    _mostrar([aluno] if aluno else [])

                elif opcao == "4":
                    aluno_id = _ler_obrigatorio("ID do aluno: ")
                    aluno = repositorio.atualizar(
                        aluno_id, _coletar_atualizacao()
                    )
                    if aluno:
                        print("\nAluno atualizado:")
                        _mostrar([aluno])
                    else:
                        print("\nAluno não encontrado.")

                elif opcao == "5":
                    aluno_id = _ler_obrigatorio("ID do aluno: ")
                    if repositorio.excluir(aluno_id):
                        print("\nAluno excluído com sucesso.")
                    else:
                        print("\nAluno não encontrado.")

                elif opcao == "6":
                    turma = _ler_obrigatorio("Turma: ")
                    _mostrar(repositorio.listar_por_turma(turma))

                elif opcao == "7":
                    data = _ler_obrigatorio("Data de nascimento (AAAA-MM-DD): ")
                    _mostrar(repositorio.listar_por_data_nascimento(data))

                elif opcao == "8":
                    turma = input("Turma (Enter = qualquer): ").strip() or None
                    data = (
                        input("Data AAAA-MM-DD (Enter = qualquer): ").strip() or None
                    )
                    _mostrar(repositorio.consultar(turma=turma, data_nascimento=data))

                elif opcao == "0":
                    print("\nAté logo!")
                    break

                else:
                    print("\nOpção inválida. Escolha de 0 a 8.")

            except ValidationError as erro:
                print(f"\nDados inválidos: {erro.errors()[0]['msg']}")
            except ValueError as erro:
                print(f"\nErro: {erro}")
            except RuntimeError as erro:
                print(f"\nErro de configuração: {erro}")
                break
            except Exception as erro:  # falha de rede/permissão do Firestore
                print(f"\nErro ao acessar o Firestore: {erro}")

            input("\nPressione Enter para continuar...")

    except KeyboardInterrupt:
        print("\n\nSaindo...")
