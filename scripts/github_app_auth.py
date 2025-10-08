#!/usr/bin/env python3
"""
Helper para autenticação via GitHub App.

Gera JWT assinado com a chave privada do App e troca por um
installation access token, que é o token usado nas chamadas à API.
"""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Optional

import jwt  # PyJWT
import requests


GITHUB_API_URL = "https://api.github.com"


def _read_private_key_from_env_or_path() -> str:
    """
    Lê a chave privada do GitHub App.
    Prioridade:
      1. GITHUB_APP_PRIVATE_KEY (conteúdo PEM bruto ou base64)
      2. GITHUB_APP_PRIVATE_KEY_PATH (caminho para arquivo .pem)
    """
    key_inline = os.getenv("GITHUB_APP_PRIVATE_KEY")
    if key_inline:
        # Permitir que venha em base64
        stripped = key_inline.strip()
        if "BEGIN" in stripped:
            return stripped
        try:
            return base64.b64decode(stripped).decode("utf-8")
        except Exception:
            # Se não for base64 válido, usar como está
            return stripped

    key_path = os.getenv("GITHUB_APP_PRIVATE_KEY_PATH")
    if not key_path:
        raise RuntimeError(
            "Missing GITHUB_APP_PRIVATE_KEY or GITHUB_APP_PRIVATE_KEY_PATH"
        )
    path = Path(key_path).expanduser()
    if not path.exists():
        raise RuntimeError(f"Private key file not found: {path}")
    return path.read_text(encoding="utf-8")


def _create_app_jwt(app_id: str, private_key_pem: str) -> str:
    """
    Cria um JWT RS256 com expiração curta (60s) para o GitHub App.
    """
    now = int(time.time())
    payload = {
        "iat": now - 5,  # pequena folga de clock skew
        "exp": now + 55,
        "iss": app_id,
    }
    token = jwt.encode(payload, private_key_pem, algorithm="RS256")
    # PyJWT>=2 retorna str
    return token


def _create_installation_token(app_jwt: str, installation_id: str) -> str:
    """
    Troca o JWT do App por um installation access token.
    """
    url = f"{GITHUB_API_URL}/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.post(url, headers=headers)
    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"Failed to create installation token ({resp.status_code}): {resp.text}"
        )
    data = resp.json()
    return data["token"]


def get_github_app_installation_token() -> str:
    """
    Obtém um installation token usando envs:
      - GITHUB_APP_ID
      - GITHUB_APP_INSTALLATION_ID
      - GITHUB_APP_PRIVATE_KEY ou GITHUB_APP_PRIVATE_KEY_PATH
    """
    app_id = os.getenv("GITHUB_APP_ID")
    installation_id = os.getenv("GITHUB_APP_INSTALLATION_ID")
    if not app_id or not installation_id:
        raise RuntimeError("Missing GITHUB_APP_ID or GITHUB_APP_INSTALLATION_ID")

    private_key_pem = _read_private_key_from_env_or_path()
    app_jwt = _create_app_jwt(app_id, private_key_pem)
    return _create_installation_token(app_jwt, installation_id)


