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
