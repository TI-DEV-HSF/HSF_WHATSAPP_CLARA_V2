import pandas as pd
import pytest
from main import filtrar_agendamentos_para_envio, eh_celular

# Este "fixture" intercepta a chamada à função de log durante os testes,
# evitando que o arquivo log.txt seja modificado. As saídas irão para o console.
@pytest.fixture(autouse=True)
def mock_registrar_log(monkeypatch):
    """Impede que os testes escrevam no arquivo de log real."""
    monkeypatch.setattr("main.registrar_log", lambda texto: print(f"LOG_TESTE: {texto}"))

def test_validacao_de_numeros_de_celular():
    """Testa a função auxiliar `eh_celular` para garantir que ela funciona como esperado."""
    assert eh_celular("21998175736") is True, "Celular válido com DDD"
    assert eh_celular("(21) 99817-5736") is True, "Celular válido com formatação"
    assert eh_celular("5521998175736") is True, "Celular válido com código do país"
    assert eh_celular("2125558989") is False, "Deve rejeitar telefone fixo"
    assert eh_celular("998175736") is False, "Deve rejeitar celular sem DDD"
    assert eh_celular("texto_qualquer") is False, "Deve rejeitar texto"
    assert eh_celular("") is False, "Deve rejeitar string vazia"

def test_filtrar_agendamentos_com_dados_validos_e_invalidos():
    """
    Testa o cenário principal da função de filtragem.
    Garante que apenas agendamentos com números de celular válidos sejam mantidos.
    """
    # 1. Preparação (Arrange): Cria um DataFrame de exemplo
    dados_teste = {
        'NR_SEQ_AGENDA': [1, 2, 3, 4, 5],
        'NM_PACIENTE': ['Paciente Válido 1', 'Paciente Fixo', 'Paciente Válido 2', 'Paciente Sem DDD', 'Paciente Vazio'],
        'TELEFONE': [
            '21999998888',  # Válido
            '2122223333',   # Inválido (fixo)
            '11988887777',  # Válido
            '99999999',     # Inválido (sem DDD)
            ''              # Inválido (vazio)
        ]
    }
    df_teste = pd.DataFrame(dados_teste)

    # 2. Ação (Act): Executa a função que queremos testar
    df_resultado = filtrar_agendamentos_para_envio(df_teste)

    # 3. Verificação (Assert): Confere se o resultado é o esperado
    assert len(df_resultado) == 2, "Deveriam restar apenas 2 agendamentos válidos"
    assert 'Paciente Válido 1' in df_resultado['NM_PACIENTE'].values
    assert 'Paciente Válido 2' in df_resultado['NM_PACIENTE'].values

def test_filtrar_com_dataframe_vazio_ou_nulo():
    """Testa se a função lida corretamente com entradas vazias ou nulas."""
    df_vazio = pd.DataFrame(columns=['NR_SEQ_AGENDA', 'TELEFONE'])
    assert filtrar_agendamentos_para_envio(df_vazio).empty, "Deve retornar DataFrame vazio para entrada vazia"
    assert filtrar_agendamentos_para_envio(None).empty, "Deve retornar DataFrame vazio para entrada nula"