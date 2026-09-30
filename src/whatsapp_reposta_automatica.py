from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import time
import pyautogui
import pyperclip

if __name__ == "__main__":
    try:
        print(f'\n\n\n\n\n')
        print(f'================================ __name__ == "__main__" ================================\n')
        print('============================== try:')                
        chave = True
        contador = 1
        
        while chave:
            time.sleep(5)
            print(f'While inicio\ncontador = {contador}')
            #tudo = 147,197
            pyautogui.click(147,197)
            #print("pyautogui.click(147,197)")
            time.sleep(3)
            
            #não lidas = 226, 198
            pyautogui.click(234,191)
            #print("pyautogui.click(234,191)")
            time.sleep(3)
            
            #pyautogui.click(324,370)
            #print("pyautogui.click(324,370)")
            #time.sleep(3)
            
            #último chat não lido - chat não lido
            pyautogui.click(316,278)
            #print("pyautogui.click(324,370)")
            time.sleep(3)
            
            #mensagem = 1234,976
            pyautogui.click(824,985)
            #print("pyautogui.click(824,985)")
            time.sleep(3)
            
            #pyautogui.click(824,985)/informac  <--Removida linha extra
            #print("pyautogui.click(824,985)") <---Removida linha extra
            time.sleep(4)
            
            pyperclip.copy("/informac")
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2)
            
            pyautogui.hotkey('enter')
            #print('pyautogui.hotkey("enter")')
            time.sleep(3)
            pyautogui.hotkey('enter')
            #print('pyautogui.hotkey("enter")')
            time.sleep(3)
            print(f'Mensagem enviada = {contador}')
            
            if contador == 1 :  # Exemplo: o loop encerra depois de 2 iterações
                chave = False
            
            contador += 1  # Incrementa o contador a cada iteração
            
            
        print("Loop encerrado!\n\n\n\n\n")
    except Exception as erro:
        print(f'================================ __name__ == "__main__"\nException Error: \n{erro}')