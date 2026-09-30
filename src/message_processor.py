# -*- coding: utf-8 -*-
import re
from dataclasses import dataclass

@dataclass
class Reply:
    """Representa uma ação de resposta a ser tomada pelo bot."""
    action: str  # Ex: 'CONFIRM', 'SEND_DEFAULT', 'DO_NOTHING'
    message: str | None = None

# Conjunto de palavras que consideramos como uma confirmação positiva.
PALAVRAS_CONFIRMACAO = {"1", "sim", "confirmado", "confirmo", "confirmar"}

def _extract_time_from_message(message_text: str) -> tuple[int, int] | None:
    """Extrai a hora (HH:MM) do final de uma string de mensagem."""
    if not message_text:
        return None
    
    # Procura por um padrão HH:MM no final da última linha da mensagem
    match = re.search(r'(\d{1,2}:\d{2})$', message_text.splitlines()[-1])
    if match:
        hora_str, minuto_str = match.group(1).split(':')
        return int(hora_str), int(minuto_str)
    return None

def process_conversation(incoming_message: str, outgoing_message: str | None) -> Reply:
    """
    Processa as mensagens de uma conversa e decide a ação a ser tomada.

    Args:
        incoming_message: O texto completo da última mensagem recebida.
        outgoing_message: O texto completo da última mensagem enviada (pode ser None).

    Returns:
        Um objeto Reply com a ação a ser tomada.
    """
    # 1. Extrair horários
    incoming_time = _extract_time_from_message(incoming_message)
    outgoing_time = _extract_time_from_message(outgoing_message) if outgoing_message else None

    # Se não for possível extrair a hora da mensagem recebida, não faz nada.
    if not incoming_time:
        return Reply(action='DO_NOTHING')

    # 2. Comparar horários para ver se a mensagem recebida é nova
    is_new_message = True
    if outgoing_time and incoming_time:
        h_in, m_in = incoming_time
        h_out, m_out = outgoing_time
        # Se a mensagem enviada for mais recente ou no mesmo minuto, a recebida não é nova.
        if h_out > h_in or (h_out == h_in and m_out >= m_in):
            is_new_message = False

    if not is_new_message:
        return Reply(action='DO_NOTHING')

    # 3. Analisar o conteúdo da nova mensagem
    # Remove a hora e limpa a mensagem para análise
    message_content = re.sub(r'\s*\d{1,2}:\d{2}$', '', incoming_message).strip().lower()
    message_words = set(message_content.split())

    # Verifica se é uma confirmação
    if not PALAVRAS_CONFIRMACAO.isdisjoint(message_words):
        # Verifica se a mensagem anterior era um lembrete de agendamento
        if outgoing_message and any(term in outgoing_message for term in ["gostaríamos de lembrar", "esta agendado"]):
            reply_message = (
                "Paz & Bem!\n\n"
                "Agendamento *CONFIRMADO!*\n\n"
                "Para maiores informações, pedimos que ligue para o telefone fixo: *(21)3294-4500*\n\n"
                "Hospital São Francisco na Providência de Deus agradece seu contato."
            )
            return Reply(action='CONFIRM', message=reply_message)

    # 4. Se não for uma confirmação válida ou se a lógica não se aplicar, envia resposta padrão
    default_message = (
        "Olá! Sou o atendente virtual *Chico*.\n\n"
        "Paz & Bem!\n\n"
        "Para maiores informações, por favor, ligue para o telefone fixo: *(21)3294-4500*\n\n"
        "Hospital São Francisco na Providência de Deus agradece seu contato."
    )
    return Reply(action='SEND_DEFAULT', message=default_message)
