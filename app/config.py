"""Configuração e inicialização do Firebase Admin SDK."""

from __future__ import annotations

import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv é opcional
    pass


class _EmulatorCredential(credentials.Base):
    """Credencial 'vazia' usada apenas quando o emulador local está ativo."""

    def get_credential(self):
        from google.auth.credentials import AnonymousCredentials

        return AnonymousCredentials()


def _project_id() -> str | None:
    return (
        os.getenv("FIRESTORE_PROJECT_ID")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
    )


def inicializar_firebase() -> None:
    """Inicializa o Firebase Admin SDK uma única vez por processo."""
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass

    options: dict[str, str] = {}
    project_id = _project_id()
    if project_id:
        options["projectId"] = project_id

    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        # O emulador não exige credenciais reais.
        options.setdefault("projectId", "demo-sla")
        credencial = _EmulatorCredential()
    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        # O próprio SDK encontra a credencial padrão da aplicação.
        credencial = None
    else:
        caminho = Path(
            os.getenv("SERVICE_ACCOUNT_KEY", "serviceAccountKey.json")
        ).expanduser()
        if not caminho.is_file():
            raise RuntimeError(
                "Não foi possível encontrar as credenciais do Firebase.\n"
                "Configure SERVICE_ACCOUNT_KEY no arquivo .env, defina "
                "GOOGLE_APPLICATION_CREDENTIALS ou use o emulador "
                "(FIRESTORE_EMULATOR_HOST). Veja o README.md."
            )
        credencial = credentials.Certificate(str(caminho))

    firebase_admin.initialize_app(credencial, options or None)


def get_db():
    """Retorna um cliente do Firestore com o app já inicializado."""
    inicializar_firebase()
    return firestore.client()
