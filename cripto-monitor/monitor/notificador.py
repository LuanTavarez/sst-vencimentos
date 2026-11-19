"""Envio de mensagens pelo Telegram (bot próprio, gratuito). Sem Telegram, imprime no terminal."""

from __future__ import annotations

import json
import os
import urllib.request


def enviar(texto: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        print(texto)
        return False
    ok = True
    # Limite do Telegram: 4096 caracteres por mensagem
    for i in range(0, len(texto), 4000):
        dados = json.dumps({"chat_id": chat_id, "text": texto[i:i + 4000],
                            "disable_web_page_preview": True}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=dados,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                ok = ok and json.loads(resp.read().decode()).get("ok", False)
        except Exception as e:  # noqa: BLE001 - notificação nunca deve derrubar o monitor
            print(f"[telegram] falha ao enviar: {e}\n{texto}")
            ok = False
    return ok
