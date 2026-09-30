"""Interpretação da resposta do paciente e textos de retorno (mesmos do CLARA v1)."""

import re
import unicodedata

PALAVRAS_CONFIRMACAO = {"1", "sim", "confirmado", "confirmo", "confirmar", "confirma"}

MSG_CONFIRMADO = (
    "Paz & Bem!\n\n"
    "Agendamento *CONFIRMADO!*\n\n"
    "Para maiores informações, pedimos que ligue para o telefone fixo: *(21)3294-4500*\n\n"
    "Hospital São Francisco na Providência de Deus agradece seu contato."
)

MSG_PADRAO = (
    "Olá! Sou o atendente virtual *Chico*.\n\n"
    "Paz & Bem!\n\n"
    "Para maiores informações, por favor, ligue para o telefone fixo: *(21)3294-4500*\n\n"
    "Hospital São Francisco na Providência de Deus agradece seu contato."
)


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def eh_confirmacao(texto):
    palavras = set(re.findall(r"\w+", _sem_acento(texto or "").lower()))
    if "nao" in palavras:
        return False
    return not PALAVRAS_CONFIRMACAO.isdisjoint(palavras)
