#!/usr/bin/env python3
"""
CLARA v2 - Sistema de Notificações via WhatsApp
Entry point para execução da orquestração
"""

import sys
from pathlib import Path
from config import config
from database import Database
from tasy_connector import TasyConnector
from whatsapp_sender import WhatsAppSender
from response_monitor import ResponseMonitor

print("="*60)
print("CLARA v2 - Sistema de Notificações")
print("="*60)

def main():
    try:
        # 1. Testar database
        db = Database(config.DB_PATH)
        print(f"✅ Database: {config.DB_PATH}")

        # 2. Testar config
        print(f"✅ TASY DSN: {config.TASY_DSN}")
        print(f"✅ WhatsApp Profile: {config.WHATSAPP_PROFILE}")
        print(f"✅ Logs Dir: {config.LOGS_DIR}")

        # 3. Conectar ao TASY
        print(f"\n🔗 Conectando ao TASY...")
        tasy = TasyConnector(config)

        if not tasy.conectar():
            print("❌ Erro: Verifique credenciais em config/.env")
            return False

        # 4. Buscar agendamentos
        agendamentos = tasy.buscar_agendamentos_proximos(48)

        if not agendamentos:
            print("⚠️ Nenhum agendamento encontrado")
            tasy.desconectar()
            return True

        # 5. Iniciar WhatsApp Sender
        print(f"\n📱 Iniciando WhatsApp Sender...")
        whatsapp = WhatsAppSender(config)

        if not whatsapp.iniciar_browser():
            print("❌ Erro ao conectar WhatsApp")
            tasy.desconectar()
            return False

        # 6. Enviar notificações
        print(f"\n📤 Enviando {len(agendamentos)} notificações...")
        enviados = 0

        for agenda in agendamentos:
            msg = f"Olá {agenda['nm_paciente']}, confirme sua consulta respondendo com '1' ou 'SIM'"
            resultado = whatsapp.enviar_mensagem(agenda['telefone'], msg)

            if resultado['ok']:
                db.inserir(agenda)
                enviados += 1

            # Pequena pausa entre envios
            import time
            time.sleep(1)

        print(f"\n✅ {enviados} mensagens enviadas!")

        # 7. Monitorar respostas (opcional)
        print(f"\n🔍 Monitorando respostas por 5 minutos...")
        monitor = ResponseMonitor(config)

        if monitor.iniciar_browser():
            confirmados = monitor.verificar_todas_respostas(agendamentos[:3])  # Testar com 3 primeiros

            # Atualizar TASY com confirmações
            for confirm in confirmados:
                tasy.atualizar_status_confirmado(confirm['nr_seq_agenda'])

            monitor.fechar()

        # 8. Limpeza
        whatsapp.fechar()
        tasy.desconectar()

        print("\n✅ CLARA v2 EXECUTADO COM SUCESSO!")
        return True

    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
