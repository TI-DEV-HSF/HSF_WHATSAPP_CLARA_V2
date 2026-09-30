"""Texto do lembrete, mesmo conteúdo do CLARA v1 (atendente virtual Chico)."""

from datetime import datetime

TELEFONE_CENTRAL = "(21)3294-4500"


def _formatar_data(dt_agenda):
    try:
        return datetime.strptime(str(dt_agenda), "%d/%m/%Y %H:%M").strftime("%d-%m-%Y às %H:%M")
    except ValueError:
        return str(dt_agenda)


def montar_mensagem(agenda, teste=False):
    linhas = [
        "*Paz e bem!*",
        "Eu sou o atendente virtual *Chico.*",
        "",
        f"Prezado(a) *{agenda['nm_paciente']}*,",
        f"gostaríamos de lembrar que no dia: {_formatar_data(agenda['dt_agenda'])}",
        f"está agendado *{(agenda.get('ds_agenda') or '').strip()}*",
        f"na especialidade *{agenda.get('ds_especialidade') or ''}*",
        f"com dr(a): *{agenda.get('nm_medico_resp') or ''}*",
        "",
        "Caso precise cancelar ou reagendar, por favor ligue para o telefone fixo:",
        f"*{TELEFONE_CENTRAL}*",
        "",
        "Para confirmar, por favor envie de volta o número *1*",
    ]
    if teste:
        linhas = ["🧪 *[TESTE CLARA v2 — o paciente NÃO recebeu esta mensagem]*", ""] + linhas
    return "\n".join(linhas)
