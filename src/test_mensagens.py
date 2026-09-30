# c:\Pietro\Projetos\HSF_WHATSAPP_CLARA\test_mensagens.py
import pandas as pd
import pytest
from datetime import datetime
from main import construir_mensagem_lembrete, envia_lembrete_whatsapp

# Este "fixture" intercepta a chamada à função de log durante os testes.
@pytest.fixture(autouse=True)
def mock_registrar_log(monkeypatch):
    """Impede que os testes escrevam no arquivo de log real."""
    monkeypatch.setattr("main.registrar_log", lambda texto: print(f"LOG_TESTE: {texto}"))

# --- Teste de Unidade para a Lógica de Construção da Mensagem ---
def test_construir_mensagem_lembrete_corretamente():
    """
    Garante que a função que cria a mensagem de lembrete
    formata os dados exatamente como esperado.
    Este teste é rápido e confiável.
    """
    # 1. Preparação (Arrange)
    dados_teste = {
        'NM_PACIENTE': 'Maria da Silva',
        'DT_AGENDA': datetime(2024, 10, 28, 15, 30),
        'DS_ESPECIALIDADE': 'CARDIOLOGIA',
        'NM_MEDICO_RESP': 'Dr. João Souza'
    }
    linha_teste = pd.Series(dados_teste)

    mensagem_esperada = [
        "*Lembrete de Agendamento*",
        "Paz e bem, *Maria da Silva*!",
        "",
        "Este é um lembrete do seu agendamento para amanhã, dia *28/10/2024 às 15:30*.",
        "Especialidade: *CARDIOLOGIA*",
        "Com Dr(a).: *Dr. João Souza*",
        "",
        "Caso precise cancelar, por favor, entre em contato pelo telefone: *(21) 3294-4500*.",
        "_Esta é uma mensagem automática, não responda._"
    ]

    # 2. Ação (Act)
    mensagem_gerada = construir_mensagem_lembrete(linha_teste)

    # 3. Verificação (Assert)
    assert mensagem_gerada == mensagem_esperada

# --- Teste de Integração com Mocks para as Ações de Envio ---
def test_envia_lembrete_whatsapp_chama_automacao_corretamente(mocker):
    """
    Verifica se a função `envia_lembrete_whatsapp` chama as funções de automação
    (webbrowser, pyautogui, pyperclip) na ordem e com os parâmetros corretos.
    Este teste "simula" as ações sem de fato executá-las.
    """
    # 1. Preparação (Arrange)
    # Substitui as funções reais por "espiões" (Mocks)
    mock_webbrowser = mocker.patch("main.webbrowser.open")
    mock_pyautogui_click = mocker.patch("main.pyautogui.click")
    mock_pyautogui_hotkey = mocker.patch("main.pyautogui.hotkey")
    mock_pyautogui_press = mocker.patch("main.pyautogui.press")
    mock_pyperclip = mocker.patch("main.pyperclip.copy")
    mocker.patch("main.time.sleep") # Também simulamos o sleep para o teste ser instantâneo

    # Cria um DataFrame de exemplo para a função processar
    df_teste = pd.DataFrame([{
        'TELEFONE': '21987654321',
        'NM_PACIENTE': 'Carlos Pereira',
        'DT_AGENDA': datetime(2024, 10, 29, 9, 0),
        'DS_ESPECIALIDADE': 'OFTALMOLOGIA',
        'NM_MEDICO_RESP': 'Dra. Ana Costa'
    }])

    # Pega a mensagem esperada para tornar o teste mais robusto
    mensagem_esperada = construir_mensagem_lembrete(df_teste.iloc[0])

    # 2. Ação (Act)
    envia_lembrete_whatsapp(df_teste)

    # 3. Verificação (Assert)
    # Verifica se o navegador foi aberto com a URL correta
    mock_webbrowser.assert_called_once_with("https://web.whatsapp.com/send?phone=21987654321")

    # Verifica se o clique inicial foi feito
    mock_pyautogui_click.assert_called_once_with(1078, 1003)

    # Verifica se o pyperclip foi chamado para cada linha da mensagem
    assert mock_pyperclip.call_count == len(mensagem_esperada)

    # Verifica se a primeira coisa copiada foi o título
    mock_pyperclip.assert_any_call("*Lembrete de Agendamento*")
    # Verifica se a última coisa copiada foi o rodapé
    mock_pyperclip.assert_any_call("_Esta é uma mensagem automática, não responda._")

    # Verifica se a tecla 'enter' foi pressionada no final para enviar
    mock_pyautogui_press.assert_called_once_with('enter')

    # Verifica se a aba foi fechada no final
    mock_pyautogui_hotkey.assert_any_call('ctrl', 'w')
