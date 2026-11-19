"""Uso:
    python -m monitor relatorio            relatório completo (envia no Telegram se configurado)
    python -m monitor relatorio --sem-conta  só dados públicos, sem chave da Binance
    python -m monitor watch                fica rodando e manda alertas na hora
    python -m monitor teste-telegram       manda uma mensagem de teste
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from . import analise, notificador
from .binance import Binance, BinanceError
from .config import RAIZ, carregar_config, carregar_env
from .indicadores import variacao

ARQUIVO_MEMORIA = RAIZ / "estado.json"


def _cliente() -> Binance:
    return Binance(os.environ.get("BINANCE_API_KEY", ""), os.environ.get("BINANCE_API_SECRET", ""))


def coletar(bn: Binance, cfg: dict, com_conta: bool, com_radar: bool) -> dict:
    precos = bn.precos()
    ticker = bn.ticker_24h("BTCUSDT")
    semanal = bn.klines("BTCUSDT", "1w", 1000)
    diario = bn.klines("BTCUSDT", "1d", 60)
    btc = analise.estado_btc(ticker, semanal, diario)
    sinal, motivos = analise.classificar_sinal(btc, cfg)
    dados = {"btc": btc, "sinal": sinal, "motivos": motivos, "precos": precos,
             "carteira": None, "ordens": None, "radar": None, "eth_btc": None}

    if com_conta:
        saldos = bn.saldos()
        for ativo, qtd in bn.saldos_earn_flexivel().items():
            saldos[ativo] = saldos.get(ativo, 0.0) + qtd
        dados["carteira"] = analise.avaliar_carteira(saldos, precos, cfg)
        dados["ordens"] = analise.conferir_ordens(bn.ordens_abertas(), precos, cfg)

    if com_radar:
        eth = [v["close"] for v in analise.velas_fechadas(bn.klines("ETHBTC", "1d", 31))]
        if len(eth) >= 30:
            dados["eth_btc"] = {"preco": precos.get("ETHBTC", eth[-1]), "var_30d": variacao(eth[-1], eth[-30])}
        pares = analise.pares_para_radar(bn.ticker_24h(), cfg)
        velas = {}
        for par in pares:
            try:
                velas[par] = analise.velas_fechadas(bn.klines(par, "1d", 60))
            except BinanceError:
                continue
        dados["radar"] = analise.radar_altcoins(velas, analise.velas_fechadas(diario),
                                                btc["semana_acima_mm200s"], cfg)
    return dados


def cmd_relatorio(args, cfg) -> int:
    bn = _cliente()
    com_conta = not args.sem_conta and bool(bn.api_key)
    dados = coletar(bn, cfg, com_conta, not args.sem_radar)
    texto = analise.formatar_relatorio(dados["btc"], dados["sinal"], dados["motivos"], cfg,
                                       dados["carteira"], dados["ordens"], dados["radar"], dados["eth_btc"])
    if not com_conta:
        texto += "\n(Sem dados da conta: configure BINANCE_API_KEY e BINANCE_API_SECRET no .env)"
    notificador.enviar(texto)
    return 0


def _ler_memoria() -> dict:
    try:
        return json.loads(ARQUIVO_MEMORIA.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def cmd_watch(args, cfg) -> int:
    bn = _cliente()
    intervalo = cfg["watch"]["intervalo_min"] * 60
    print(f"Monitorando a cada {cfg['watch']['intervalo_min']} min. Ctrl+C para parar.")
    while True:
        try:
            dados = coletar(bn, cfg, com_conta=bool(bn.api_key), com_radar=False)
            memoria = _ler_memoria()
            novos = analise.filtrar_novos(analise.gerar_alertas(dados["btc"], dados["carteira"], cfg), memoria)
            for _, msg in novos:
                notificador.enviar(msg)
            ARQUIVO_MEMORIA.write_text(json.dumps(memoria))
        except BinanceError as e:
            print(f"[binance] {e}", file=sys.stderr)
        if args.uma_vez:
            return 0
        time.sleep(intervalo)


def main(argv=None) -> int:
    carregar_env()
    cfg = carregar_config()
    p = argparse.ArgumentParser(prog="monitor", description="Monitor cripto (somente leitura)")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("relatorio")
    r.add_argument("--sem-conta", action="store_true", help="não usa a chave da Binance")
    r.add_argument("--sem-radar", action="store_true", help="pula o radar de altcoins")
    w = sub.add_parser("watch")
    w.add_argument("--uma-vez", action="store_true", help="faz uma checagem e sai (para agendador)")
    sub.add_parser("teste-telegram")
    args = p.parse_args(argv)

    try:
        if args.cmd == "relatorio":
            return cmd_relatorio(args, cfg)
        if args.cmd == "watch":
            return cmd_watch(args, cfg)
        ok = notificador.enviar("Monitor Cripto conectado. Você vai receber os alertas aqui.")
        print("Telegram OK" if ok else "Telegram não configurado ou falhou (veja acima).")
        return 0 if ok else 1
    except BinanceError as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
