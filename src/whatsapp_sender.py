"""
WhatsApp Web Sender usando Selenium
Envia notificações via WhatsApp Web (sem API pagas)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime

class WhatsAppSender:
    """Envia mensagens via WhatsApp Web (Selenium)"""

    def __init__(self, config):
        self.config = config
        self.driver = None
        self.logado = False

    def iniciar_browser(self):
        """Inicia o navegador Chrome com WhatsApp Web"""
        print("🌐 Iniciando navegador Chrome...")

        options = Options()
        options.add_argument(f"user-data-dir={self.config.WHATSAPP_PROFILE}")
        options.add_argument("--start-maximized")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        # Abrir WhatsApp Web
        self.driver.get("https://web.whatsapp.com/")
        print("✅ Chrome aberto com WhatsApp Web")
        print("⏳ Aguarde scan do QR Code (se não estiver logado)...")
        print("   Tem 30 segundos para escanear...")

        # Aguardar login
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@title='Chats']"))
            )
            self.logado = True
            print("✅ Logado com sucesso no WhatsApp Web!")
            return True
        except:
            print("❌ Falha no login - QR Code não escaneado")
            return False

    def enviar_mensagem(self, telefone, mensagem):
        """
        Envia mensagem para um número de WhatsApp

        Args:
            telefone: Número no formato 5511999999999 (com código país)
            mensagem: Texto da mensagem

        Returns:
            dict com status e detalhes
        """
        if not self.logado:
            return {
                'ok': False,
                'erro': 'Não logado no WhatsApp',
                'timestamp': datetime.now().isoformat()
            }

        try:
            # Formatar URL do WhatsApp
            url = f"https://web.whatsapp.com/send?phone={telefone}&text={mensagem}"
            self.driver.get(url)

            # Aguardar carregamento
            time.sleep(3)

            # Procurar botão "Enviar"
            try:
                botao_enviar = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Enviar']"))
                )
                botao_enviar.click()

                print(f"✅ Mensagem enviada para {telefone}")
                return {
                    'ok': True,
                    'telefone': telefone,
                    'timestamp': datetime.now().isoformat()
                }
            except:
                print(f"⚠️ Botão enviar não encontrado para {telefone}")
                return {
                    'ok': False,
                    'erro': 'Botão enviar não encontrado',
                    'telefone': telefone,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            print(f"❌ Erro ao enviar para {telefone}: {str(e)}")
            return {
                'ok': False,
                'erro': str(e),
                'telefone': telefone,
                'timestamp': datetime.now().isoformat()
            }

    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("✅ Navegador fechado")

# Teste rápido
if __name__ == "__main__":
    from config import config

    whatsapp = WhatsAppSender(config)

    # Iniciar
    if whatsapp.iniciar_browser():
        # Teste com número fictício (não envia de verdade)
        # resultado = whatsapp.enviar_mensagem("555511999999999", "Teste CLARA")
        # print(resultado)

        print("\n✅ WhatsApp sender pronto!")
        print("   Agora integre com database.py e main.py")

        input("Pressione ENTER para fechar...")
        whatsapp.fechar()
    else:
        print("❌ Falha ao conectar WhatsApp Web")
