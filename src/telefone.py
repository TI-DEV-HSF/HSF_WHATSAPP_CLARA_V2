"""
Normalização do campo NR_TELEFONE do TASY para o formato do WhatsApp (55 + DDD + 9 dígitos).

Formatos encontrados no TASY: 'M: (21)988887777 R: (21) 22223333', '21 98888-7777',
'21988887777 21977776666', '(21)98888777 / 21988887777', etc.
"""

import re

_SEPARADORES = re.compile(r"\b[MRC]:|/|\bou\b", re.IGNORECASE)


def _celular_de_digitos(d):
    if len(d) in (12, 13) and d.startswith("55"):
        d = d[2:]
    if len(d) == 12 and d.startswith("0"):
        d = d[1:]
    # Celular antigo sem o 9 (anterior à migração da ANATEL)
    if len(d) == 10 and d[2] in "6789":
        d = d[:2] + "9" + d[2:]
    if len(d) == 11 and d[0] != "0" and d[1] != "0" and d[2] == "9":
        return "55" + d
    return None


def _candidatos(trecho):
    d = re.sub(r"\D", "", trecho)
    if len(d) <= 13:
        return [d]
    # Dois números colados no mesmo trecho: '21988887777 21977776666'
    return [d[:11], d[11:], d[:10], d[10:]]


def normalizar_celular(bruto):
    """Retorna '55DDD9XXXXXXXX' do primeiro celular válido (prioriza o 'M:'), ou None."""
    if not bruto:
        return None
    texto = str(bruto)
    m = re.search(r"M:(.*?)(?=\b[RC]:|$)", texto, re.IGNORECASE)
    trechos = ([m.group(1)] if m else []) + _SEPARADORES.split(texto)

    for trecho in trechos:
        for d in _candidatos(trecho):
            celular = _celular_de_digitos(d)
            if celular:
                return celular
    return None
