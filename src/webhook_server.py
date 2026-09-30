"""
Receptor de respostas dos pacientes. A Evolution API chama POST /webhook/evolution
a cada mensagem recebida; aqui decidimos se é confirmação e respondemos.

  python src\\webhook_server.py
"""

import hmac
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from config import config
from database import Database
from evolution_client import EvolutionClient
from respostas import MSG_CONFIRMADO, MSG_PADRAO, eh_confirmacao
from tasy_connector import TasyConnector
from telefone import normalizar_celular

CAMINHO = "/webhook/evolution"
db = Database(config.DB_PATH)
evolution = EvolutionClient(config)


def numero_remetente(key):
    jid = key.get("remoteJid") or ""
    # Contas novas chegam como LID (id interno); o número real vem em remoteJidAlt
    if jid.endswith("@lid"):
        jid = key.get("remoteJidAlt") or ""
    if not jid.endswith("@s.whatsapp.net"):
        return None
    return normalizar_celular(jid.split("@")[0])


def texto_da_mensagem(msg):
    msg = msg or {}
    return (msg.get("conversation")
            or (msg.get("extendedTextMessage") or {}).get("text")
            or (msg.get("buttonsResponseMessage") or {}).get("selectedDisplayText")
            or "").strip()


def confirmar_no_tasy(nr_seq_agenda):
    if config.MODO_TESTE:
        print(f"   🧪 MODO TESTE: TASY não alterado (confirmaria agenda {nr_seq_agenda})")
        return False
    tasy = TasyConnector(config)
    if not tasy.conectar():
        return False
    try:
        return tasy.atualizar_status_confirmado(nr_seq_agenda)
    finally:
        tasy.desconectar()


def processar_mensagem(data):
    key = data.get("key") or {}
    if key.get("fromMe"):
        return
    numero = numero_remetente(key)
    texto = texto_da_mensagem(data.get("message"))
    if not numero or not texto:
        return

    envio = db.envio_pendente(numero)
    if envio is None:
        print(f"↩️  {numero}: mensagem ignorada (nenhum lembrete pendente para este número)")
        return

    if eh_confirmacao(texto):
        print(f"✅ {numero} CONFIRMOU a agenda {envio['nr_seq_agenda']}")
        no_tasy = confirmar_no_tasy(envio["nr_seq_agenda"])
        db.registrar_resposta(envio["id"], texto, confirmou=True, confirmado_tasy=no_tasy)
        evolution.enviar_texto(numero, MSG_CONFIRMADO)
    else:
        print(f"💬 {numero} respondeu sem confirmar (agenda {envio['nr_seq_agenda']})")
        ja_orientado = envio["resposta"] is not None
        db.registrar_resposta(envio["id"], texto, confirmou=False)
        if not ja_orientado:
            evolution.enviar_texto(numero, MSG_PADRAO)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.rstrip("/") != CAMINHO:
            return self._responder(404)
        token = self.headers.get("x-clara-token", "")
        if not config.WEBHOOK_TOKEN or not hmac.compare_digest(token, config.WEBHOOK_TOKEN):
            return self._responder(401)

        tamanho = int(self.headers.get("Content-Length") or 0)
        try:
            corpo = json.loads(self.rfile.read(tamanho) or b"{}")
        except json.JSONDecodeError:
            return self._responder(400)
        self._responder(200)

        evento = (corpo.get("event") or "").lower()
        try:
            if evento == "connection.update":
                print(f"🔌 Conexão WhatsApp: {(corpo.get('data') or {}).get('state')}")
            elif evento == "messages.upsert":
                data = corpo.get("data")
                for item in data if isinstance(data, list) else [data or {}]:
                    processar_mensagem(item)
        except Exception as e:
            print(f"❌ Erro ao processar {evento}: {type(e).__name__}: {e}")

    def _responder(self, status):
        self.send_response(status)
        self.end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if not config.WEBHOOK_TOKEN:
        raise SystemExit("❌ Defina WEBHOOK_TOKEN no config/.env")
    modo = "🧪 TESTE (TASY não é alterado)" if config.MODO_TESTE else "🚨 PRODUÇÃO (confirma no TASY)"
    print(f"👂 Aguardando respostas em http://0.0.0.0:{config.WEBHOOK_PORTA}{CAMINHO} | {modo}")
    ThreadingHTTPServer(("0.0.0.0", config.WEBHOOK_PORTA), Handler).serve_forever()
