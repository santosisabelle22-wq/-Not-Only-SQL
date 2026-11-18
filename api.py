"""Ponto de entrada da API: `uvicorn api:app --reload`."""

from app.rest_api import app

__all__ = ["app"]
