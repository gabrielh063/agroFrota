"""Interpretação determinística de agendamentos na demonstração acadêmica.

O modelo de linguagem não tem autorização para escolher recursos, ações ou horários.
Este módulo aceita apenas pedidos explícitos com OS numerada e horário claro.
"""
import re
import unicodedata
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo('America/Sao_Paulo')
_DIAS = {'segunda': 0, 'terca': 1, 'quarta': 2, 'quinta': 3, 'sexta': 4,
         'sabado': 5, 'domingo': 6}
_NUMEROS = {'uma': 1, 'duas': 2, 'tres': 3, 'quatro': 4, 'cinco': 5,
            'seis': 6, 'sete': 7, 'oito': 8}


def _normalizar(valor):
    valor = unicodedata.normalize('NFKD', valor.lower())
    return ''.join(c for c in valor if not unicodedata.combining(c))


def _dia_solicitado(mensagem, agora):
    if 'depois de amanha' in mensagem:
        return agora.date() + timedelta(days=2)
    if re.search(r'\bamanha\b', mensagem):
        return agora.date() + timedelta(days=1)
    if re.search(r'\bhoje\b', mensagem):
        return agora.date()
    match = re.search(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', mensagem)
    if match:
        try:
            return datetime(int(match[3]), int(match[2]), int(match[1])).date()
        except ValueError:
            return None
    match = re.search(r'\b(segunda|terca|quarta|quinta|sexta|sabado|domingo)(?:-feira)?\b', mensagem)
    if match:
        delta = (_DIAS[match[1]] - agora.weekday()) % 7
        return agora.date() + timedelta(days=delta or 7)
    return None


def eh_pedido_agendamento(mensagem):
    texto = _normalizar(mensagem.strip())
    # Perguntas sobre como usar a agenda não são comandos de agendamento.
    if re.match(r'^(como|quais|qual|quando|onde|porque|por que|me explique|explique)\b', texto):
        return False
    return bool(re.search(r'\b(?:agende|agendar|marque|marcar|reserve|reservar|programe|programar)\b', texto))


def extrair_pedido_agendamento(mensagem, agora=None):
    """Retorna None para consultas ou um dicionário com campos e eventual erro.

    Horários são extraídos *somente* do texto do usuário, nunca do JSON do LLM.
    """
    if not eh_pedido_agendamento(mensagem):
        return None
    agora = agora or datetime.now(TZ).replace(tzinfo=None)
    texto = _normalizar(mensagem)
    os_match = re.search(r'\b(?:os|ordem\s+de\s+servico)\s*(?:numero|n[.oº°]|#|:)?\s*#?\s*(\d{1,7})\b', texto)
    if not os_match:
        return {'erro': 'Para agendar, informe uma OS existente pelo número (ex.: OS 12).'}
    numero_os = int(os_match[1])
    dia = _dia_solicitado(texto, agora)
    if dia is None:
        return {'erro': 'Informe a data: hoje, amanhã, sexta-feira ou DD/MM/AAAA.'}
    horarios = list(re.finditer(r'\b(?:as|pelas)\s+(\d{1,2})(?:(?::(\d{2}))|(?:h(\d{2})?))?\b', texto))
    if not horarios:
        return {'erro': 'Informe o horário, por exemplo: às 14h ou às 14:30.'}
    primeiro = horarios[0]
    hora = int(primeiro[1])
    minuto = int(primeiro[2] or primeiro[3] or 0)
    if hora > 23 or minuto > 59:
        return {'erro': 'Horário inválido. Use um horário de 00:00 a 23:59.'}
    inicio = datetime.combine(dia, datetime.min.time()).replace(hour=hora, minute=minuto)
    duracao = re.search(r'\bpor\s+(uma|duas|tres|quatro|cinco|seis|sete|oito|\d{1,2})\s*(?:horas?|h)\b', texto)
    if duracao:
        horas = _NUMEROS.get(duracao[1]) if duracao[1] in _NUMEROS else int(duracao[1])
        fim = inicio + timedelta(hours=horas)
    elif len(horarios) > 1:
        segundo = horarios[1]
        h2, m2 = int(segundo[1]), int(segundo[2] or segundo[3] or 0)
        if h2 > 23 or m2 > 59:
            return {'erro': 'Horário final inválido.'}
        fim = inicio.replace(hour=h2, minute=m2)
    else:
        fim = inicio + timedelta(hours=2)
    if inicio <= agora or inicio > agora + timedelta(days=365):
        return {'erro': 'Informe um horário futuro, dentro dos próximos 12 meses.'}
    if not timedelta(minutes=15) <= fim - inicio <= timedelta(hours=8):
        return {'erro': 'O período deve durar entre 15 minutos e 8 horas.'}
    return {'numero_os': numero_os, 'inicio': inicio, 'fim': fim, 'erro': None}


def alegacao_agendamento_realizado(resposta):
    texto = _normalizar(resposta)
    return bool(re.search(
        r'\b(?:agendamento\s+(?:realizado|confirmado|efetuado|concluido|criado)|'
        r'(?:ja\s+)?agendei|reserva\s+(?:realizada|confirmada)|'
        r'servico\s+(?:agendado|marcado))\b', texto
    ))
