"""Carrega config.json e o arquivo .env (sem dependências externas)."""

from __future__ import annotations

import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def carregar_env(caminho: Path = RAIZ / ".env") -> None:
    """Lê linhas CHAVE=valor para os.environ, sem sobrescrever variáveis já definidas."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def carregar_config(caminho: Path = RAIZ / "config.json") -> dict:
    return json.loads(caminho.read_text(encoding="utf-8"))
