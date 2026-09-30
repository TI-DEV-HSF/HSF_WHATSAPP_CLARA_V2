"""Cliente da Evolution API v2 (WhatsApp sem navegador)."""

import requests

EVENTOS_WEBHOOK = ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]


class EvolutionError(RuntimeError):
    pass


class EvolutionClient:
    def __init__(self, config):
        self.base = config.EVOLUTION_URL.rstrip("/")
        self.instancia = config.EVOLUTION_INSTANCE
        self.config = config
        self.sessao = requests.Session()
        self.sessao.headers.update({"apikey": config.EVOLUTION_API_KEY})

    def _req(self, metodo, caminho, **kw):
        r = self.sessao.request(metodo, f"{self.base}{caminho}", timeout=30, **kw)
        if r.status_code >= 400:
            raise EvolutionError(f"{metodo} {caminho} -> HTTP {r.status_code}: {r.text[:300]}")
        return r.json() if r.content else {}

    def estado(self):
        """'open' = conectado; 'connecting'/'close' = precisa QR Code; None = instância não existe."""
        try:
            return self._req("GET", f"/instance/connectionState/{self.instancia}")["instance"]["state"]
        except EvolutionError as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def criar_instancia(self):
        return self._req("POST", "/instance/create", json={
            "instanceName": self.instancia,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True,
            "groupsIgnore": True,
            "rejectCall": True,
            "msgCall": "Este número é apenas para lembretes de consulta. Ligue (21)3294-4500.",
        })

    def qrcode(self):
        """Retorna o QR Code como data URI base64 (para escanear com o celular)."""
        return self._req("GET", f"/instance/connect/{self.instancia}").get("base64")

    def configurar_webhook(self):
        return self._req("POST", f"/webhook/set/{self.instancia}", json={"webhook": {
            "enabled": True,
            "url": self.config.WEBHOOK_URL_EVOLUTION,
            "headers": {"x-clara-token": self.config.WEBHOOK_TOKEN},
            "byEvents": False,
            "base64": False,
            "events": EVENTOS_WEBHOOK,
        }})

    def enviar_texto(self, numero, texto, delay_ms=1200):
        """delay_ms: tempo que o WhatsApp mostra 'digitando...' antes de enviar."""
        r = self._req("POST", f"/message/sendText/{self.instancia}",
                      json={"number": numero, "text": texto, "delay": delay_ms})
        return (r.get("key") or {}).get("id")
