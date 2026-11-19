"""Indicadores técnicos simples, sem dependências externas."""

from __future__ import annotations


def sma(valores: list[float], periodo: int) -> float | None:
    if len(valores) < periodo or periodo <= 0:
        return None
    return sum(valores[-periodo:]) / periodo


def ema(valores: list[float], periodo: int) -> float | None:
    if len(valores) < periodo or periodo <= 0:
        return None
    k = 2 / (periodo + 1)
    atual = sum(valores[:periodo]) / periodo
    for v in valores[periodo:]:
        atual = v * k + atual * (1 - k)
    return atual


def rsi(valores: list[float], periodo: int = 14) -> float | None:
    """RSI de Wilder."""
    if len(valores) <= periodo:
        return None
    ganhos = perdas = 0.0
    for i in range(1, periodo + 1):
        d = valores[i] - valores[i - 1]
        ganhos += max(d, 0)
        perdas += max(-d, 0)
    media_g, media_p = ganhos / periodo, perdas / periodo
    for i in range(periodo + 1, len(valores)):
        d = valores[i] - valores[i - 1]
        media_g = (media_g * (periodo - 1) + max(d, 0)) / periodo
        media_p = (media_p * (periodo - 1) + max(-d, 0)) / periodo
    if media_p == 0:
        return 100.0
    return 100 - 100 / (1 + media_g / media_p)


def variacao(atual: float, anterior: float) -> float:
    """Variação percentual de `anterior` para `atual`."""
    return (atual / anterior - 1) * 100 if anterior else 0.0


def distancia(preco: float, nivel: float) -> float:
    """Quanto (%) o preço precisa andar para chegar ao nível (negativo = abaixo)."""
    return (nivel / preco - 1) * 100 if preco else 0.0
