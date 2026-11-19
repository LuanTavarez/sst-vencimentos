"""Regras do plano: sinal do BTC, carteira, ordens, radar de altcoins e alertas."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from .indicadores import distancia, ema, rsi, sma, variacao

ESTAVEIS = {"USDT", "USDC", "FDUSD", "TUSD", "USDP", "DAI"}
MANTER, ATENCAO, ACAO = "MANTER PLANO", "ATENÇÃO", "AÇÃO"
FUSO_BR = timezone(timedelta(hours=-3))


# ------------------------------------------------------------------- BTC
def velas_fechadas(velas: list[dict], agora_ms: int | None = None) -> list[dict]:
    """Remove a vela ainda aberta (a da semana/dia corrente)."""
    agora_ms = agora_ms or int(time.time() * 1000)
    return [v for v in velas if v["fechamento_ms"] < agora_ms]


def estado_btc(ticker: dict, semanal: list[dict], diario: list[dict], agora_ms: int | None = None) -> dict:
    preco = float(ticker["lastPrice"])
    semanas = velas_fechadas(semanal, agora_ms)
    dias = velas_fechadas(diario, agora_ms)
    fechamentos_sem = [v["close"] for v in semanas]
    mm200s = sma(fechamentos_sem, 200)
    topo = max(v["high"] for v in semanal) if semanal else preco
    fech_semanal = fechamentos_sem[-1] if fechamentos_sem else None
    return {
        "preco": preco,
        "minima_24h": float(ticker["lowPrice"]),
        "maxima_24h": float(ticker["highPrice"]),
        "var_24h": float(ticker["priceChangePercent"]),
        "var_7d": variacao(preco, dias[-7]["close"]) if len(dias) >= 7 else None,
        "mm200s": mm200s,
        "fechamento_semanal": fech_semanal,
        "semana_acima_mm200s": bool(mm200s and fech_semanal and fech_semanal > mm200s),
        "fechamento_diario": dias[-1]["close"] if dias else None,
        "topo": topo,
        "queda_do_topo": variacao(preco, topo),
        "rsi_semanal": rsi(fechamentos_sem, 14),
    }


def classificar_sinal(btc: dict, cfg: dict) -> tuple[str, list[str]]:
    """Aplica as regras do plano e devolve (sinal, motivos)."""
    preco = btc["preco"]
    acao, atencao = [], []

    for nivel in cfg["ordens_compra_btc"]:
        if btc["minima_24h"] <= nivel:
            acao.append(f"mínima de 24h tocou {_usd(nivel)}: ordem provavelmente executada, confira em Ordens")
    if btc["semana_acima_mm200s"] and preco >= cfg["confirmacao_btc"]:
        acao.append("confirmação de fundo: semana fechou acima da MM200s e preço acima de "
                    f"{_usd(cfg['confirmacao_btc'])} (usar a parcela de 20%)")
    if btc["fechamento_diario"] and btc["fechamento_diario"] < cfg["ordem_extra_btc"]:
        acao.append(f"fechamento diário abaixo de {_usd(cfg['ordem_extra_btc'])}: rever o plano com calma, sem vender no pânico")

    limite = cfg["distancia_atencao_pct"]
    for nivel in sorted(set(cfg["ordens_compra_btc"] + cfg["suportes_btc"]), reverse=True):
        d = distancia(preco, nivel)
        if -limite <= d < 0:
            atencao.append(f"a {_pct(abs(d))}% de {_usd(nivel)}")
    if btc["mm200s"]:
        d = distancia(preco, btc["mm200s"])
        if 0 < d <= limite:
            atencao.append(f"a {_pct(d)}% de recuperar a MM200s ({_usd(btc['mm200s'])})")

    if acao:
        return ACAO, acao
    if atencao:
        return ATENCAO, atencao
    return MANTER, ["nenhum nível do plano por perto"]


def nivel_mais_proximo(preco: float, cfg: dict, mm200s: float | None) -> tuple[str, float]:
    niveis = {f"ordem {n / 1000:.0f}k": n for n in cfg["ordens_compra_btc"]}
    niveis.update({f"suporte {n / 1000:.1f}k": n for n in cfg["suportes_btc"]})
    niveis.update({f"resistência {n / 1000:.0f}k": n for n in cfg["resistencias_btc"]})
    if mm200s:
        niveis["MM200s"] = mm200s
    nome = min(niveis, key=lambda k: abs(niveis[k] - preco))
    return nome, distancia(preco, niveis[nome])


# --------------------------------------------------------------- Carteira
def preco_usd(ativo: str, precos: dict[str, float]) -> float | None:
    if ativo in ESTAVEIS:
        return 1.0
    if ativo == "BRL":
        return 1 / precos["USDTBRL"] if precos.get("USDTBRL") else None
    if f"{ativo}USDT" in precos:
        return precos[f"{ativo}USDT"]
    if f"{ativo}BTC" in precos and "BTCUSDT" in precos:
        return precos[f"{ativo}BTC"] * precos["BTCUSDT"]
    # Ativos antigos do Earn aparecem como "LD" + moeda (ex.: LDBTC)
    if ativo.startswith("LD") and len(ativo) > 2:
        return preco_usd(ativo[2:], precos)
    return None


def avaliar_carteira(saldos: dict[str, float], precos: dict[str, float], cfg: dict) -> dict:
    usdtbrl = precos.get("USDTBRL")
    medios = cfg["precos_medios_usd"]
    posicoes, sem_preco = [], []
    for ativo, qtd in saldos.items():
        p = preco_usd(ativo, precos)
        if p is None:
            sem_preco.append(ativo)
            continue
        valor = qtd * p
        if valor < 1:  # poeira
            continue
        base = ativo[2:] if ativo.startswith("LD") and ativo[2:] in medios else ativo
        medio = medios.get(base)
        posicoes.append({
            "ativo": base,
            "quantidade": qtd,
            "preco": p,
            "valor_usd": valor,
            "valor_brl": valor * usdtbrl if usdtbrl else None,
            "preco_medio": medio,
            "pnl_pct": variacao(p, medio) if medio else None,
            "pnl_usd": (p - medio) * qtd if medio else None,
        })
    posicoes.sort(key=lambda x: x["valor_usd"], reverse=True)
    total = sum(x["valor_usd"] for x in posicoes)
    for x in posicoes:
        x["peso_pct"] = x["valor_usd"] / total * 100 if total else 0
    return {
        "posicoes": posicoes,
        "total_usd": total,
        "total_brl": total * usdtbrl if usdtbrl else None,
        "usdtbrl": usdtbrl,
        "sem_preco": sem_preco,
    }


def conferir_ordens(ordens: list[dict], precos: dict[str, float], cfg: dict) -> dict:
    """Compara as ordens de compra de BTC abertas com os níveis do plano."""
    usdtbrl = precos.get("USDTBRL")
    compras = []
    for o in ordens:
        if not o["symbol"].startswith("BTC") or o["side"] != "BUY":
            continue
        preco = float(o["price"])
        preco_usd_ = preco / usdtbrl if o["symbol"] == "BTCBRL" and usdtbrl else preco
        compras.append({"symbol": o["symbol"], "preco": preco, "preco_usd": preco_usd_,
                        "quantidade": float(o["origQty"]) - float(o["executedQty"])})
    faltando = [n for n in cfg["ordens_compra_btc"]
                if not any(abs(c["preco_usd"] / n - 1) <= 0.03 for c in compras)]
    return {"compras_btc": compras, "niveis_sem_ordem": faltando}


# ------------------------------------------------------------------ Radar
def radar_altcoins(velas_por_par: dict[str, list[dict]], btc_diario: list[dict],
                   btc_acima_mm200s: bool, cfg: dict) -> list[dict]:
    """Força relativa contra o BTC em 28 dias + tendência (EMA 50) + RSI."""
    btc_closes = [v["close"] for v in btc_diario]
    if len(btc_closes) < 29:
        return []
    btc_28d = variacao(btc_closes[-1], btc_closes[-29])
    ignorar = set(cfg["radar"]["ignorar"])
    resultado = []
    for par, velas in velas_por_par.items():
        moeda = par[:-4]
        closes = [v["close"] for v in velas]
        if moeda in ignorar or len(closes) < 51:
            continue
        ret_28d = variacao(closes[-1], closes[-29])
        forca = ret_28d - btc_28d
        media50 = ema(closes, 50)
        r = rsi(closes, 14)
        if forca <= 0 or media50 is None or closes[-1] <= media50:
            continue
        candidata = btc_acima_mm200s and r is not None and r < 70
        resultado.append({
            "moeda": moeda,
            "preco": closes[-1],
            "ret_28d": ret_28d,
            "forca_vs_btc": forca,
            "rsi": r,
            "classe": "CANDIDATA" if candidata else "OBSERVAR",
        })
    resultado.sort(key=lambda x: x["forca_vs_btc"], reverse=True)
    return resultado[: cfg["radar"]["max_resultados"]]


def pares_para_radar(tickers: list[dict], cfg: dict) -> list[str]:
    ignorar = set(cfg["radar"]["ignorar"]) | ESTAVEIS
    pares = [t for t in tickers if t["symbol"].endswith("USDT") and t["symbol"][:-4] not in ignorar
             and not t["symbol"][:-4].endswith(("UP", "DOWN", "BULL", "BEAR"))]
    pares.sort(key=lambda t: float(t["quoteVolume"]), reverse=True)
    return [t["symbol"] for t in pares[: cfg["radar"]["top_por_volume"]]]


# ---------------------------------------------------------------- Alertas
def gerar_alertas(btc: dict, carteira: dict | None, cfg: dict) -> list[tuple[str, str]]:
    """Alertas instantâneos para o modo watch: lista de (chave, mensagem)."""
    alertas = []
    preco = btc["preco"]
    for nivel in sorted(set(cfg["ordens_compra_btc"] + cfg["suportes_btc"] + [cfg["ordem_extra_btc"]])):
        if btc["minima_24h"] <= nivel:
            extra = " Sua ordem pode ter executado: confira em Ordens." if nivel in cfg["ordens_compra_btc"] else ""
            alertas.append((f"tocou_{nivel}", f"AÇÃO: BTC tocou {_usd(nivel)} (agora {_usd(preco)}).{extra}"))
        elif -cfg["distancia_atencao_pct"] <= distancia(preco, nivel) < 0:
            alertas.append((f"perto_{nivel}", f"ATENÇÃO: BTC {_usd(preco)}, a {_pct(abs(distancia(preco, nivel)))}% de {_usd(nivel)}."))
    if btc["mm200s"] and preco >= btc["mm200s"]:
        alertas.append(("acima_mm200s", f"BTC voltou acima da MM200s ({_usd(btc['mm200s'])}). Espere o fechamento semanal."))
    if preco >= cfg["confirmacao_btc"]:
        alertas.append(("acima_confirmacao", f"BTC acima de {_usd(cfg['confirmacao_btc'])}. Se a semana fechar acima da MM200s, use a parcela de confirmação."))
    for alvo in cfg["alvos_venda_btc"]:
        if preco >= alvo:
            alertas.append((f"alvo_{alvo}", f"BTC atingiu o alvo de venda {_usd(alvo)}. Execute o degrau do plano."))
    if btc["var_24h"] <= -cfg["watch"]["queda_forte_24h_pct"]:
        alertas.append(("queda_forte", f"Queda forte: BTC {_pct(btc['var_24h'])}% em 24h ({_usd(preco)}). Não venda no pânico; siga as ordens."))
    if carteira:
        limite = cfg["alerta_preco_medio_pct"]
        for p in carteira["posicoes"]:
            if p["ativo"] != "BTC" and p["pnl_pct"] is not None and p["pnl_pct"] >= -limite:
                alertas.append((f"medio_{p['ativo']}", f"{p['ativo']} a {_pct(p['pnl_pct'], sinal=True)}% do seu preço médio. Plano: vender e passar para BTC."))
    return alertas


def filtrar_novos(alertas: list[tuple[str, str]], memoria: dict, horas_espera: float = 12,
                  agora: float | None = None) -> list[tuple[str, str]]:
    """Evita repetir o mesmo alerta antes de `horas_espera` horas."""
    agora = agora or time.time()
    novos = [(k, m) for k, m in alertas if k not in memoria or agora - memoria[k] >= horas_espera * 3600]
    for k, _ in novos:
        memoria[k] = agora
    return novos


# --------------------------------------------------------------- Relatório
def _usd(v: float | None) -> str:
    if v is None:
        return "n/d"
    casas = 0 if v >= 1000 else 2 if v >= 1 else 4 if v >= 0.01 else 8
    return f"US$ {v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(v: float, casas: int = 1, sinal: bool = False) -> str:
    return f"{v:{'+' if sinal else ''}.{casas}f}".replace(".", ",")


def _brl(v: float | None) -> str:
    if v is None:
        return "n/d"
    return f"R$ {v:,.0f}".replace(",", ".")


def formatar_relatorio(btc: dict, sinal: str, motivos: list[str], cfg: dict,
                       carteira: dict | None = None, ordens: dict | None = None,
                       radar: list[dict] | None = None, eth_btc: dict | None = None) -> str:
    agora = datetime.now(FUSO_BR)
    nome, dist = nivel_mais_proximo(btc["preco"], cfg, btc["mm200s"])
    linhas = [
        f"MONITOR CRIPTO - {agora:%d/%m %H:%M} (Brasília)",
        f"Sinal: {sinal}",
        "",
        f"BTC {_usd(btc['preco'])} | 24h {_pct(btc['var_24h'], sinal=True)}% | 7d "
        + (f"{_pct(btc['var_7d'], sinal=True)}%" if btc["var_7d"] is not None else "n/d"),
        f"Faixa 24h: {_usd(btc['minima_24h'])} - {_usd(btc['maxima_24h'])}",
        f"MM200s: {_usd(btc['mm200s'])} | última semana fechou {'ACIMA' if btc['semana_acima_mm200s'] else 'ABAIXO'}",
        f"Do topo ({_usd(btc['topo'])}): {_pct(btc['queda_do_topo'])}% | RSI semanal: "
        + (f"{btc['rsi_semanal']:.0f}" if btc["rsi_semanal"] is not None else "n/d"),
        f"Nível mais próximo: {nome} ({_pct(dist, sinal=True)}%)",
        "Motivos: " + "; ".join(motivos),
    ]
    if ordens is not None:
        linhas.append("")
        if ordens["compras_btc"]:
            txt = ", ".join(f"{_usd(c['preco_usd'])}" for c in ordens["compras_btc"])
            linhas.append(f"Ordens de compra BTC abertas: {txt}")
        else:
            linhas.append("Ordens de compra BTC abertas: nenhuma")
        if ordens["niveis_sem_ordem"]:
            linhas.append("Sem ordem nos níveis do plano: " + ", ".join(f"{_usd(n)}" for n in ordens["niveis_sem_ordem"]))
    if carteira:
        linhas += ["", f"Carteira: {_usd(carteira['total_usd'])} ({_brl(carteira['total_brl'])})"]
        for p in carteira["posicoes"]:
            pnl = f"{_pct(p['pnl_pct'], 0, sinal=True)}% vs médio" if p["pnl_pct"] is not None else "sem preço médio"
            linhas.append(f"- {p['ativo']}: {_usd(p['valor_usd'])} ({_pct(p['peso_pct'], 0)}%) | {pnl}")
        if carteira["sem_preco"]:
            linhas.append("Sem preço na Binance (não somados): " + ", ".join(carteira["sem_preco"]))
    if eth_btc:
        linhas += ["", f"ETH/BTC {eth_btc['preco']:.5f} ({_pct(eth_btc['var_30d'], sinal=True)}% em 30d): "
                   + ("altcoins ganhando força" if eth_btc["var_30d"] > 0 else "temporada de BTC")]
    if radar is not None:
        linhas.append("Radar de altcoins (força vs BTC em 28d, acima da EMA50):")
        if radar:
            for r in radar:
                linhas.append(f"- {r['moeda']}: {r['classe']} | {_pct(r['ret_28d'], 0, sinal=True)}% em 28d "
                              f"({r['forca_vs_btc']:+.0f} p.p. vs BTC) | RSI {r['rsi']:.0f}")
        else:
            linhas.append("- nenhuma altcoin forte contra o BTC agora")
    linhas += ["", "Lembretes: sem alavancagem; não vender no pânico; aporte de R$ 100 às segundas.",
               "Análise educativa, não recomendação de investimento."]
    return "\n".join(linhas)
