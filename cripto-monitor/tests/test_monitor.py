import unittest

from monitor import analise
from monitor.__main__ import coletar
from monitor.binance import assinar
from monitor.config import carregar_config
from monitor.indicadores import ema, rsi, sma

CFG = carregar_config()
DIA_MS = 86_400_000
AGORA_MS = 2_000_000_000_000


def velas(closes, passo_ms=DIA_MS):
    """Velas já fechadas, terminando antes de AGORA_MS."""
    n = len(closes)
    return [{"abertura_ms": AGORA_MS - (n - i + 1) * passo_ms, "open": c, "high": c * 1.01, "low": c * 0.99,
             "close": c, "fechamento_ms": AGORA_MS - (n - i) * passo_ms - 1} for i, c in enumerate(closes)]


def ticker(preco, minima=None, var=-1.0):
    return {"lastPrice": str(preco), "lowPrice": str(minima or preco * 0.98),
            "highPrice": str(preco * 1.02), "priceChangePercent": str(var)}


class TestIndicadores(unittest.TestCase):
    def test_sma_ema_rsi(self):
        self.assertEqual(sma([1, 2, 3, 4], 2), 3.5)
        self.assertIsNone(sma([1], 2))
        self.assertAlmostEqual(ema([1] * 10, 5), 1.0)
        self.assertEqual(rsi(list(range(1, 30)), 14), 100.0)
        self.assertLess(rsi(list(range(30, 1, -1)), 14), 1)


class TestAssinatura(unittest.TestCase):
    def test_exemplo_documentacao_binance(self):
        secret = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
        query = ("symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1"
                 "&recvWindow=5000&timestamp=1499827319559")
        self.assertEqual(assinar(query, secret),
                         "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71")


class TestSinal(unittest.TestCase):
    def _btc(self, preco, minima=None, mm200s=68000, fech_sem=65000):
        semanal = velas([mm200s] * 200 + [fech_sem], 7 * DIA_MS)
        return analise.estado_btc(ticker(preco, minima), semanal, velas([preco] * 30), AGORA_MS)

    def test_atencao_perto_de_60k(self):
        sinal, motivos = analise.classificar_sinal(self._btc(61560), CFG)
        self.assertEqual(sinal, analise.ATENCAO)
        self.assertTrue(any("US$ 60.000" in m for m in motivos))

    def test_acao_quando_ordem_tocada(self):
        sinal, motivos = analise.classificar_sinal(self._btc(59000, minima=57900), CFG)
        self.assertEqual(sinal, analise.ACAO)
        self.assertIn("US$ 58.000", motivos[0])

    def test_manter_longe_dos_niveis(self):
        sinal, _ = analise.classificar_sinal(self._btc(70500, mm200s=65000), CFG)
        self.assertEqual(sinal, analise.MANTER)

    def test_confirmacao(self):
        btc = self._btc(82000, mm200s=68000, fech_sem=81000)
        self.assertTrue(btc["semana_acima_mm200s"])
        sinal, motivos = analise.classificar_sinal(btc, CFG)
        self.assertEqual(sinal, analise.ACAO)
        self.assertTrue(any("confirmação" in m for m in motivos))

    def test_vela_aberta_ignorada_na_mm200s(self):
        semanal = velas([100.0] * 200, 7 * DIA_MS)
        semanal.append({"abertura_ms": AGORA_MS, "open": 1, "high": 1, "low": 1, "close": 1,
                        "fechamento_ms": AGORA_MS + 7 * DIA_MS})
        btc = analise.estado_btc(ticker(100), semanal, velas([100] * 30), AGORA_MS)
        self.assertEqual(btc["mm200s"], 100.0)


class TestCarteira(unittest.TestCase):
    PRECOS = {"BTCUSDT": 61560.0, "NEARUSDT": 4.12, "USDTBRL": 5.97, "LDOUSDT": 1.0, "BIOBTC": 0.0000005}

    def test_avaliacao_e_pnl(self):
        cart = analise.avaliar_carteira({"BTC": 0.08, "NEAR": 48.19, "USDT": 10, "XYZ": 5, "LDBTC": 0.001},
                                        self.PRECOS, CFG)
        por_ativo = {p["ativo"]: p for p in cart["posicoes"]}
        self.assertAlmostEqual(por_ativo["NEAR"]["pnl_pct"], (4.12 / 5.71 - 1) * 100)
        self.assertIn("XYZ", cart["sem_preco"])
        self.assertAlmostEqual(cart["total_brl"], cart["total_usd"] * 5.97)

    def test_preco_via_par_btc_e_ldo_nao_confundido(self):
        self.assertAlmostEqual(analise.preco_usd("BIO", self.PRECOS), 0.0000005 * 61560)
        self.assertEqual(analise.preco_usd("LDO", self.PRECOS), 1.0)

    def test_ordens_em_brl_convertidas(self):
        ordens = [{"symbol": "BTCBRL", "side": "BUY", "price": str(58000 * 5.97), "origQty": "0.0001",
                   "executedQty": "0"}]
        res = analise.conferir_ordens(ordens, self.PRECOS, CFG)
        self.assertEqual(res["niveis_sem_ordem"], [52000, 46000])


class TestAlertas(unittest.TestCase):
    def test_nao_repete_alerta(self):
        memoria = {}
        alertas = [("tocou_58000", "x")]
        self.assertEqual(len(analise.filtrar_novos(alertas, memoria, agora=1000)), 1)
        self.assertEqual(len(analise.filtrar_novos(alertas, memoria, agora=2000)), 0)
        self.assertEqual(len(analise.filtrar_novos(alertas, memoria, agora=1000 + 13 * 3600)), 1)


class FakeBinance:
    api_key = "x"

    def precos(self):
        return {"BTCUSDT": 61560.0, "ETHUSDT": 2430.0, "ETHBTC": 0.0395, "USDTBRL": 5.97, "SOLUSDT": 120.0}

    def ticker_24h(self, symbol=None):
        if symbol:
            return ticker(61560, 61428, -1.26)
        return [{"symbol": "SOLUSDT", "quoteVolume": "1000"}, {"symbol": "PEPEUSDT", "quoteVolume": "9999"},
                {"symbol": "ETHUSDT", "quoteVolume": "5000"}]

    def klines(self, symbol, interval, limit):
        if symbol == "BTCUSDT" and interval == "1w":
            return velas([68000] * 200 + [65351], 7 * DIA_MS)
        if symbol == "BTCUSDT":
            return velas([74000 - i * 400 for i in range(60)])
        if symbol == "SOLUSDT":
            return velas([80 + i for i in range(60)])
        return velas([0.04 - i * 0.0001 for i in range(60)] if symbol == "ETHBTC" else [100] * 60)

    def saldos(self):
        return {"BTC": 0.08, "ETH": 0.065, "NEAR": 48.19}

    def saldos_earn_flexivel(self):
        return {"USDT": 5.0}

    def ordens_abertas(self):
        return []


class TestFluxoCompleto(unittest.TestCase):
    def test_relatorio(self):
        import monitor.analise as a
        original = a.velas_fechadas
        a.velas_fechadas = lambda v, agora_ms=None: original(v, AGORA_MS)
        try:
            dados = coletar(FakeBinance(), CFG, com_conta=True, com_radar=True)
        finally:
            a.velas_fechadas = original
        texto = analise.formatar_relatorio(dados["btc"], dados["sinal"], dados["motivos"], CFG,
                                           dados["carteira"], dados["ordens"], dados["radar"], dados["eth_btc"])
        self.assertIn("Sinal: ATENÇÃO", texto)
        self.assertIn("Sem ordem nos níveis do plano", texto)
        self.assertIn("SOL: OBSERVAR", texto)       # forte vs BTC, mas BTC abaixo da MM200s
        self.assertNotIn("PEPE:", texto)            # memecoin ignorada
        self.assertIn("temporada de BTC", texto)


if __name__ == "__main__":
    unittest.main()
