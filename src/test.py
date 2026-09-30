from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os

import time
import pyautogui

#if __name__ == "__main__":
#    try:
#        print(f'\n\n\n\n\n\n\n\n')
#        print(f'================================ __name__ == "__main__" ================================\n')
#        
#        print('============================== try:')                
#        #tela toda:
#        driver = webdriver.Chrome()
#        options = Options()
#        options.add_argument("--start-maximized")
#        
#        dir_path = os.getcwd()
#        profile = os.path.join(dir_path, "profile", "wpp")
#        options.add_argument(r"user-data-dir={}".format(profile))
#        
#        driver = webdriver.Chrome(options=options)
#        driver.get("https://web.whatsapp.com")
#        print('driver.get("https://web.whatsapp.com")')
#        title = driver.title
#        driver.implicitly_wait(10)
#        time.sleep(240)
#            
#    except Exception as erro:
#        print(f'================================ __name__ == "__main__"\nException Error: \n{erro}')
def digitar_letra_por_letra(frase):
    """
    Digita uma frase letra por letra, com um intervalo entre cada digitação.

    Args:
        frase (str): A frase a ser digitada.
        intervalo (float, opcional): O intervalo em segundos entre cada digitação. 
                                   Padrão é 0.1 segundos.
    """
    intervalo = 0.1
    for letra in frase:
        pyautogui.write(letra)
        time.sleep(intervalo)


if __name__ == "__main__":
    try:
        print(f'\n\n\n\n\n\n\n\n')
        print(f'================================ __name__ == "__main__" ================================\n')
        print('============================== try:')                
        chave = True
        contador = 1
        while chave:
            time.sleep(5)
            
            #tudo = 147,197
            pyautogui.click(147,197)
            print("pyautogui.click(147,197)")
            time.sleep(3)
            
            #não lidas = 226, 198
            pyautogui.click(234,191)
            print("pyautogui.click(234,191)")
            time.sleep(3)
            
            pyautogui.click(324,370)
            print("pyautogui.click(324,370)")
            time.sleep(3)
            
            #mensagem = 1234,976
            pyautogui.click(824,985)
            print("pyautogui.click(824,985)")
            time.sleep(3)
            
            pyautogui.click(824,985)
            print("pyautogui.click(824,985)")
            time.sleep(4)
            
            #digitar_letra_por_letra('/informac')
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2)
            
            pyautogui.hotkey('enter')
            print('pyautogui.hotkey("enter")')
            time.sleep(3)
            pyautogui.hotkey('enter')
            print('pyautogui.hotkey("enter")')
            time.sleep(3)
            
            contador += 1
            if contador == 1:
                time.sleep(5)
                break
            
    except Exception as erro:
        print(f'================================ __name__ == "__main__"\nException Error: \n{erro}')