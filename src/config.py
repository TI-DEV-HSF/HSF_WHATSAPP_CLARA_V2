import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "config" / ".env")

class Config:
    # TASY Oracle
    TASY_USER = os.getenv("TASY_USER", "TASY")
    TASY_PASSWORD = os.getenv("TASY_PASSWORD", "")
    TASY_DSN = os.getenv("TASY_DSN", "192.168.5.9:1521/TASYPRD")

    # WhatsApp
    WHATSAPP_PROFILE = os.getenv(
        "WHATSAPP_PROFILE", str(Path(__file__).parent.parent / "profile" / "wpp")
    )
    WHATSAPP_TIMEOUT = int(os.getenv("WHATSAPP_TIMEOUT", "30"))

    # Evolution API
    EVOLUTION_URL = os.getenv("EVOLUTION_URL", "http://localhost:8080")
    EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
    EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "clara_teste")
    INTERVALO_MIN_S = int(os.getenv("INTERVALO_MIN_S", "8"))
    INTERVALO_MAX_S = int(os.getenv("INTERVALO_MAX_S", "20"))

    # Receptor de respostas (webhook chamado pela Evolution)
    WEBHOOK_PORTA = int(os.getenv("WEBHOOK_PORTA", "8765"))
    WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")
    WEBHOOK_URL_EVOLUTION = os.getenv(
        "WEBHOOK_URL_EVOLUTION", f"http://host.docker.internal:{WEBHOOK_PORTA}/webhook/evolution"
    )

    # Modo teste: ligado a menos que o .env diga MODO_TESTE=false
    MODO_TESTE = os.getenv("MODO_TESTE", "true").strip().lower() != "false"
    TELEFONE_TESTE = os.getenv("TELEFONE_TESTE", "").strip()
    LIMITE_TESTE = int(os.getenv("LIMITE_TESTE", "3"))

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    DB_PATH = BASE_DIR / "data" / "clara.db"
    DATA_DIR = BASE_DIR / "data"

    # Create dirs
    for d in [LOGS_DIR, DATA_DIR]:
        d.mkdir(exist_ok=True, parents=True)

config = Config()
