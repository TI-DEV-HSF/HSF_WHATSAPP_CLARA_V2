
# -*- coding: utf-8 -*-
import time
import pyperclip
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

class WhatsAppPage:
    """
    Abstrai a interação com a página do WhatsApp Web, encapsulando seletores e ações do Selenium.
    Isso torna o código principal mais limpo e facilita a manutenção quando a interface do WhatsApp muda.
    """

    # --- Seletores (centralizados para fácil manutenção) ---
    UNREAD_FILTER_BUTTON = (By.XPATH, '//*[@id="side"]/div[2]/button[2]')
    CONVERSATION_PANE = (By.ID, 'pane-side')
    FIRST_UNREAD_CONVERSATION = (By.XPATH, '//*[@id="pane-side"]/div/div/div/div[1]/div/div/div/div[2]')
    LAST_INCOMING_MESSAGE_BUBBLE = (By.CSS_SELECTOR, "div[class*='message-in']")
    LAST_OUTGOING_MESSAGE_BUBBLE = (By.CSS_SELECTOR, "div[class*='message-out']")
    MESSAGE_INPUT_BOX = (By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/div/p') # XPATH pode variar, este é um exemplo comum

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20) # Wait de 20 segundos padrão

    def open_whatsapp(self):
        """Navega para a página do WhatsApp Web."""
        self.driver.get("https://web.whatsapp.com")

    def filter_unread_chats(self):
        """Clica no botão para filtrar conversas não lidas."""
        try:
            unread_button = self.wait.until(
                EC.element_to_be_clickable(self.UNREAD_FILTER_BUTTON)
            )
            unread_button.click()
            return True
        except TimeoutException:
            print("Erro: Botão de filtro de não lidas não encontrado.")
            return False

    def has_unread_conversations(self):
        """Verifica se a lista de conversas não lidas está vazia."""
        try:
            pane = self.wait.until(
                EC.visibility_of_element_located(self.CONVERSATION_PANE)
            )
            # Se o texto específico aparecer, não há conversas não lidas.
            if "Nenhuma conversa não lida" in pane.text:
                return False
            return True
        except TimeoutException:
            # Se o painel não carregar, assume que não há conversas para processar.
            return False

    def open_first_unread_conversation(self):
        """Clica na primeira conversa da lista de não lidas."""
        try:
            first_chat = self.wait.until(
                EC.element_to_be_clickable(self.FIRST_UNREAD_CONVERSATION)
            )
            chat_header_text = first_chat.text
            first_chat.click()
            return chat_header_text
        except TimeoutException:
            print("Erro: Nenhuma conversa não lida encontrada para abrir.")
            return None

    def get_last_incoming_message(self):
        """Retorna o texto da última mensagem recebida."""
        try:
            # Espera que pelo menos uma mensagem 'message-in' esteja presente
            self.wait.until(EC.presence_of_element_located(self.LAST_INCOMING_MESSAGE_BUBBLE))
            # Pega todos os elementos e retorna o texto do último
            last_message_element = self.driver.find_elements(*self.LAST_INCOMING_MESSAGE_BUBBLE)[-1]
            return last_message_element.text
        except (TimeoutException, NoSuchElementException, IndexError):
            print("Erro: Nenhuma mensagem recebida encontrada.")
            return None

    def get_last_outgoing_message(self):
        """Retorna o texto da última mensagem enviada."""
        try:
            self.wait.until(EC.presence_of_element_located(self.LAST_OUTGOING_MESSAGE_BUBBLE))
            last_message_element = self.driver.find_elements(*self.LAST_OUTGOING_MESSAGE_BUBBLE)[-1]
            return last_message_element.text
        except (TimeoutException, NoSuchElementException, IndexError):
            print("Erro: Nenhuma mensagem enviada encontrada.")
            return None

    def send_message(self, message: str):
        """Digita e envia uma mensagem na conversa aberta."""
        try:
            message_box = self.wait.until(
                EC.element_to_be_clickable(self.MESSAGE_INPUT_BOX)
            )
            
            # Usar pyperclip para colar mensagens com quebras de linha
            pyperclip.copy(message)
            message_box.send_keys(Keys.CONTROL, 'v')
            time.sleep(0.5)
            message_box.send_keys(Keys.ENTER)
            return True
        except TimeoutException:
            print("Erro: Caixa de texto para envio de mensagem não encontrada.")
            return False

