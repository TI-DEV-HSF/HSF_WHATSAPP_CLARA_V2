"""
Monitor de Respostas WhatsApp
Verifica se pacientes responderam à notificação
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time

class ResponseMonitor:
    """Monitora respostas dos pacientes no WhatsApp"""

    def __init__(self, config):
        self.config = config
        self.driver = None
        self.logado = False
        self.respostas = {}

    def iniciar_browser(self):
        """Inicia navegador para monitorar respostas"""
        print("🌐 Iniciando monitor de respostas...")

        options = Options()
        options.add_argument(f"user-data-dir={self.config.WHATSAPP_PROFILE}")
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=options)

        self.driver.get("https://web.whatsapp.com/")

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@title='Chats']"))
            )
            self.logado = True
            print("✅ Monitor iniciado com sucesso!")
            return True
        except:
            print("❌ Falha ao conectar monitor")
            return False

    def verificar_resposta(self, numero_paciente, keywords=None):
        """
        Verifica se houve resposta do paciente

        Args:
            numero_paciente: Número do paciente em formato internacional
            keywords: Lista de palavras-chave para confirmar (ex: ['sim', '1', 'confirmado'])

        Returns:
            dict com status e mensagem recebida
        """
        if not self.logado:
            return {
                'respondeu': False,
                'erro': 'Monitor não logado'
            }

        if keywords is None:
            keywords = ['sim', '1', 'confirmado', 'yes', 'ok']

        try:
            # Navegar para conversa do paciente
            url = f"https://web.whatsapp.com/send?phone={numero_paciente}"
            self.driver.get(url)
            time.sleep(2)

            # Procurar últimas mensagens
            try:
                mensagens = self.driver.find_elements(
                    By.XPATH,
                    "//div[@class='message' and @data-dir='incoming']"
                )

                if mensagens:
                    # Pegar última mensagem recebida
                    ultima_msg = mensagens[-1].text.lower()

                    # Verificar keywords
                    respondeu = any(kw in ultima_msg for kw in keywords)

                    return {
                        'respondeu': respondeu,
                        'numero': numero_paciente,
                        'mensagem': ultima_msg,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'respondeu': False,
                        'numero': numero_paciente,
                        'razao': 'Nenhuma mensagem recebida'
                    }

            except Exception as e:
                return {
                    'respondeu': False,
                    'erro': str(e),
                    'numero': numero_paciente
                }

        except Exception as e:
            print(f"❌ Erro ao verificar resposta: {str(e)}")
            return {
                'respondeu': False,
                'erro': str(e)
            }

    def verificar_todas_respostas(self, pacientes):
        """
        Verifica respostas de múltiplos pacientes

        Args:
            pacientes: Lista de dicts com 'numero' do paciente

        Returns:
            Lista de respostas
        """
        respostas = []

        for paciente in pacientes:
            print(f"🔍 Verificando {paciente.get('nm_paciente')}...")

            resposta = self.verificar_resposta(paciente.get('celular'))
            resposta['nm_paciente'] = paciente.get('nm_paciente')
            resposta['nr_seq_agenda'] = paciente.get('nr_seq_agenda')

            respostas.append(resposta)
            time.sleep(1)  # Intervalo entre verificações

        confirmados = [r for r in respostas if r.get('respondeu')]
        print(f"\n✅ {len(confirmados)} pacientes confirmaram")

        return confirmados

    def fechar(self):
        """Fecha o monitor"""
        if self.driver:
            self.driver.quit()
            print("✅ Monitor fechado")

# Teste
if __name__ == "__main__":
    from config import config

    monitor = ResponseMonitor(config)

    if monitor.iniciar_browser():
        print("\n✅ Monitor pronto para verificar respostas!")
        print("   Adicione números de pacientes para testar")

        input("Pressione ENTER para fechar...")
        monitor.fechar()
