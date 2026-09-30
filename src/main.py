"""
CLARA v2 - envio de lembretes de consulta via WhatsApp (Evolution API).

  python src\\main.py             envia (respeitando MODO_TESTE do .env)
  python src\\main.py --simular   só consulta o TASY e mostra o que seria enviado

As respostas dos pacientes são tratadas por src\\webhook_server.py.
"""

import random
import sys
import time

from config import config
from database import Database
from evolution_client import EvolutionClient, EvolutionError
from mensagem import montar_mensagem
from tasy_connector import TasyConnector
from telefone import normalizar_celular

HORIZONTE_HORAS = 48


def montar_fila(agendamentos, db):
    validos = [a for a in agendamentos if a["celular"]]
    print(f"📋 Agendamentos: {len(agendamentos)} | celular válido: {len(validos)} "
          f"| sem celular: {len(agendamentos) - len(validos)}")

    if config.MODO_TESTE:
        destino = normalizar_celular(config.TELEFONE_TESTE)
        if not destino:
            raise SystemExit("❌ MODO_TESTE ligado mas TELEFONE_TESTE inválido no config/.env")
        print(f"🧪 MODO TESTE: até {config.LIMITE_TESTE} mensagens, TODAS para {destino}. TASY não é alterado.")
        return [(a, destino) for a in validos[: config.LIMITE_TESTE]]

    pendentes = [a for a in validos if not db.ja_enviado(a["nr_seq_agenda"])]
    print(f"🚨 MODO PRODUÇÃO: {len(pendentes)} pacientes reais receberão mensagem "
          f"({len(validos) - len(pendentes)} já enviados antes)")
    return [(a, a["celular"]) for a in pendentes]


def main(simular=False):
    print("=" * 60)
    print("CLARA v2 - Lembretes de consulta")
    print("=" * 60)

    db = Database(config.DB_PATH)
    tasy = TasyConnector(config)
    if not tasy.conectar():
        return False
    try:
        agendamentos = tasy.buscar_agendamentos_proximos(HORIZONTE_HORAS)
    finally:
        tasy.desconectar()

    fila = montar_fila(agendamentos, db)
    if simular:
        print(f"🔎 SIMULAÇÃO: {len(fila)} mensagens seriam enviadas. Nada foi enviado.")
        return True
    if not fila:
        print("⚠️ Nada a enviar")
        return True

    evo = EvolutionClient(config)
    estado = evo.estado()
    if estado != "open":
        print(f"❌ WhatsApp não conectado na Evolution (estado: {estado}). Rode src\\evolution_setup.py")
        return False

    modo = "TESTE" if config.MODO_TESTE else "PRODUCAO"
    enviados = 0
    for i, (agenda, destino) in enumerate(fila):
        if i:
            # Intervalo variável entre envios reduz o risco de bloqueio do número
            time.sleep(random.uniform(config.INTERVALO_MIN_S, config.INTERVALO_MAX_S))
        try:
            message_id = evo.enviar_texto(destino, montar_mensagem(agenda, teste=config.MODO_TESTE))
        except EvolutionError as e:
            print(f"❌ Agenda {agenda['nr_seq_agenda']}: {e}")
            continue
        db.registrar_envio(agenda, destino, modo, message_id)
        enviados += 1
        print(f"✅ [{i + 1}/{len(fila)}] agenda {agenda['nr_seq_agenda']} -> {destino}")

    print(f"\n📤 {enviados}/{len(fila)} mensagens enviadas")
    return True


if __name__ == "__main__":
    sys.exit(0 if main(simular="--simular" in sys.argv) else 1)
