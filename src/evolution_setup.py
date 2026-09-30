"""
Prepara a instância do CLARA na Evolution API: cria (se preciso), liga o webhook
e mostra o QR Code até o WhatsApp conectar.

  python src\\evolution_setup.py
"""

import base64
import os
import time

from config import config
from evolution_client import EvolutionClient

QR_ARQUIVO = config.DATA_DIR / "qrcode_whatsapp.png"


def main():
    evo = EvolutionClient(config)
    estado = evo.estado()
    if estado is None:
        print(f"🆕 Criando instância '{config.EVOLUTION_INSTANCE}'...")
        evo.criar_instancia()
        estado = evo.estado()

    evo.configurar_webhook()
    print(f"🔗 Webhook -> {config.WEBHOOK_URL_EVOLUTION}")

    if estado == "open":
        print("✅ WhatsApp já conectado")
        return

    fim = time.time() + 180
    while time.time() < fim:
        qr = evo.qrcode()
        if qr:
            QR_ARQUIVO.write_bytes(base64.b64decode(qr.split(",", 1)[-1]))
            os.startfile(QR_ARQUIVO)
            print(f"📱 Escaneie o QR Code ({QR_ARQUIVO}) em WhatsApp > Aparelhos conectados")
        for _ in range(20):
            time.sleep(2)
            if evo.estado() == "open":
                QR_ARQUIVO.unlink(missing_ok=True)
                print("✅ WhatsApp conectado!")
                return
        print("🔄 QR Code expirou, gerando outro...")
    print("❌ Tempo esgotado. Rode de novo quando estiver com o celular em mãos.")


if __name__ == "__main__":
    main()
