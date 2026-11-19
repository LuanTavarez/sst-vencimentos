"""Cliente mínimo e SOMENTE LEITURA da API Spot da Binance (só biblioteca padrão).

Nenhum método deste módulo cria, altera ou cancela ordens, nem faz saques:
o cliente só envia requisições GET. Mesmo assim, gere a chave de API na
Binance apenas com a permissão "Habilitar leitura" (Enable Reading).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URLS = (
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
)


class BinanceError(RuntimeError):
    pass


def assinar(query: str, secret: str) -> str:
    """Assinatura HMAC-SHA256 exigida nos endpoints privados."""
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()


class Binance:
    def __init__(self, api_key: str = "", api_secret: str = "", base_urls=BASE_URLS, timeout: int = 15):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_urls = tuple(base_urls)
        self.timeout = timeout

    # ------------------------------------------------------------------ HTTP
    def _get(self, path: str, params: dict | None = None, assinado: bool = False):
        params = dict(params or {})
        headers = {"User-Agent": "cripto-monitor/1.0"}
        if assinado:
            if not (self.api_key and self.api_secret):
                raise BinanceError("BINANCE_API_KEY/BINANCE_API_SECRET não configurados")
            params["timestamp"] = int(time.time() * 1000)
            params.setdefault("recvWindow", 10000)
            query = urllib.parse.urlencode(params)
            query += "&signature=" + assinar(query, self.api_secret)
            headers["X-MBX-APIKEY"] = self.api_key
        else:
            query = urllib.parse.urlencode(params)

        ultimo_erro = None
        for base in self.base_urls:
            url = f"{base}{path}" + (f"?{query}" if query else "")
            req = urllib.request.Request(url, headers=headers, method="GET")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                corpo = e.read().decode(errors="replace")
                if e.code == 451:
                    raise BinanceError(
                        "Binance recusou a região do servidor (HTTP 451). Rode o monitor no seu "
                        "computador no Brasil ou num servidor fora dos EUA."
                    ) from e
                if e.code in (400, 401):
                    raise BinanceError(f"Erro da Binance ({e.code}): {corpo}") from e
                ultimo_erro = BinanceError(f"HTTP {e.code} em {base}: {corpo}")
            except (urllib.error.URLError, TimeoutError) as e:
                ultimo_erro = BinanceError(f"Falha de rede em {base}: {e}")
        raise ultimo_erro or BinanceError("Falha desconhecida")

    # --------------------------------------------------------- Dados públicos
    def klines(self, symbol: str, interval: str, limit: int = 500) -> list[dict]:
        bruto = self._get("/api/v3/klines", {"symbol": symbol, "interval": interval, "limit": limit})
        return [
            {
                "abertura_ms": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "fechamento_ms": k[6],
            }
            for k in bruto
        ]

    def ticker_24h(self, symbol: str | None = None):
        params = {"symbol": symbol} if symbol else None
        return self._get("/api/v3/ticker/24hr", params)

    def precos(self) -> dict[str, float]:
        """Último preço de todos os pares, ex.: {"BTCUSDT": 61560.0, ...}."""
        return {p["symbol"]: float(p["price"]) for p in self._get("/api/v3/ticker/price")}

    # ------------------------------------------------------ Dados da conta
    def saldos(self) -> dict[str, float]:
        """Saldo Spot (livre + bloqueado em ordens) por moeda."""
        conta = self._get("/api/v3/account", {"omitZeroBalances": "true"}, assinado=True)
        saldos: dict[str, float] = {}
        for b in conta.get("balances", []):
            total = float(b["free"]) + float(b["locked"])
            if total > 0:
                saldos[b["asset"]] = saldos.get(b["asset"], 0.0) + total
        return saldos

    def saldos_earn_flexivel(self) -> dict[str, float]:
        """Posições no Simple Earn Flexível (ex.: BIO, USDT). Vazio se a chave não tiver acesso."""
        try:
            dados = self._get("/sapi/v1/simple-earn/flexible/position", {"size": 100}, assinado=True)
        except BinanceError:
            return {}
        saldos: dict[str, float] = {}
        for p in dados.get("rows", []):
            saldos[p["asset"]] = saldos.get(p["asset"], 0.0) + float(p.get("totalAmount", 0))
        return saldos

    def ordens_abertas(self, symbol: str | None = None) -> list[dict]:
        params = {"symbol": symbol} if symbol else None
        return self._get("/api/v3/openOrders", params, assinado=True)
