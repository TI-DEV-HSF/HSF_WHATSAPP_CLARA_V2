"""
WhatsApp Web Sender usando Selenium (sem API paga).
"""

import time
from datetime import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

PAINEL_CONVERSAS = (By.ID, "pane-side")
CAIXA_MENSAGEM = (By.XPATH, "//footer//div[@contenteditable='true']")


class WhatsAppSender:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.logado = False

    def iniciar_browser(self):
        print("🌐 Iniciando Chrome com WhatsApp Web...")
        options = Options()
        options.add_argument(f"user-data-dir={self.config.WHATSAPP_PROFILE}")
        options.add_argument("--start-maximized")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get("https://web.whatsapp.com/")
        print("⏳ Se aparecer o QR Code, escaneie pelo celular (até 2 minutos)...")

        try:
            WebDriverWait(self.driver, 120).until(EC.presence_of_element_located(PAINEL_CONVERSAS))
            self.logado = True
            print("✅ Logado no WhatsApp Web!")
            return True
        except TimeoutException:
            print("❌ Login não concluído (QR Code não escaneado)")
            return False

    def enviar_mensagem(self, telefone, mensagem):
        """telefone no formato 55DDD9XXXXXXXX. Retorna dict com ok/erro."""
        resultado = {"telefone": telefone, "timestamp": datetime.now().isoformat()}
        if not self.logado:
            return {**resultado, "ok": False, "erro": "Não logado no WhatsApp"}

        try:
            self.driver.get(f"https://web.whatsapp.com/send?phone={telefone}&text={quote(mensagem)}")
            # Número sem WhatsApp abre um aviso em vez da conversa e cai no timeout
            caixa = WebDriverWait(self.driver, self.config.WHATSAPP_TIMEOUT).until(
                EC.element_to_be_clickable(CAIXA_MENSAGEM)
            )
            time.sleep(1)
            caixa.send_keys(Keys.ENTER)
            time.sleep(2)
            print(f"✅ Mensagem enviada para {telefone}")
            return {**resultado, "ok": True}
        except TimeoutException:
            print(f"⚠️ Conversa não abriu para {telefone} (número sem WhatsApp?)")
            return {**resultado, "ok": False, "erro": "Conversa não abriu (sem WhatsApp ou inválido)"}
        except WebDriverException as e:
            print(f"❌ Erro ao enviar para {telefone}: {e.msg}")
            return {**resultado, "ok": False, "erro": e.msg}

    def fechar(self):
        if self.driver:
            self.driver.quit()
            print("✅ Navegador fechado")


if __name__ == "__main__":
    from config import config

    whatsapp = WhatsAppSender(config)
    if whatsapp.iniciar_browser():
        input("Logado. Pressione ENTER para fechar...")
    whatsapp.fechar()
