#09/12/2024
#@PLima
#Codigo para fazer com que o Selenium continue com o whatsapp logado:

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import time


if __name__ == "__main__":
    try:
        print(f'\n\n\n\n\n\n\n\n')
        print(f'================================ __name__ == "__main__" ================================\n')
        
        print('============================== try:')                
        #tela toda:
        driver = webdriver.Chrome()
        options = Options()
        
        #Janela maximizada:
        options.add_argument("--start-maximized")
        
        #Pegando profile logado no chrome:
        dir_path = os.getcwd()
        profile = os.path.join(dir_path, "profile", "wpp")
        options.add_argument(r"user-data-dir={}".format(profile))
        
        #carregando drive com as opcoes
        driver = webdriver.Chrome(options=options)
        driver.get("https://web.whatsapp.com")
        print('driver.get("https://web.whatsapp.com")')
        title = driver.title
        driver.implicitly_wait(10)
        time.sleep(240)
            
    except Exception as erro:
        print(f'================================ __name__ == "__main__"\nException Error: \n{erro}')