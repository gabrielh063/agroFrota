from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.tenant.indisponibilidade import Indisponibilidade
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento


def _calcular_horas_sobrepostas(
    inicio: datetime,
    fim: datetime | None,
    inicio_periodo: datetime,
    fim_periodo: datetime,
    agora: datetime,
) -> float:
    """
    Calcula somente o tempo da indisponibilidade
    que está dentro do período analisado.
    """

    inicio_real = max(inicio, inicio_periodo)

    fim_real = fim if fim is not None else agora

    fim_real = min(fim_real, fim_periodo)

    if fim_real <= inicio_real:
        return 0.0

    segundos = (
        fim_real - inicio_real
    ).total_seconds()

    return round(segundos / 3600, 2)


def obter_dashboard_indisponibilidade(
    session: Session,
    inicio_periodo: datetime | None = None,
    fim_periodo: datetime | None = None,
) -> dict:

    agora = datetime.utcnow()

    # Sem período informado, usamos o dia atual.
    if inicio_periodo is None:
        inicio_periodo = datetime(
            agora.year,
            agora.month,
            agora.day,
        )

    if fim_periodo is None:
        fim_periodo = agora

    if fim_periodo <= inicio_periodo:
        raise ValueError(
            "O fim do período deve ser posterior ao início."
        )

    consulta = select(Indisponibilidade)

    registros = list(
        session.scalars(consulta).all()
    )

    total = len(registros)

    ativas = sum(
        1
        for registro in registros
        if registro.status == "ATIVA"
    )

    finalizadas = sum(
        1
        for registro in registros
        if registro.status == "FINALIZADA"
    )

    canceladas = sum(
        1
        for registro in registros
        if registro.status == "CANCELADA"
    )

    registros_validos = [
        registro
        for registro in registros
        if registro.status != "CANCELADA"
    ]

    tempo_total_parado_horas = round(
        sum(
            _calcular_horas_sobrepostas(
                registro.inicio,
                registro.fim,
                inicio_periodo,
                fim_periodo,
                agora,
            )
            for registro in registros_validos
        ),
        2,
    )

    # ---------------------------------------------------------
    # CAPACIDADE DA FROTA
    # ---------------------------------------------------------

    maquinas = list(
        session.scalars(
            select(Maquina)
        ).all()
    )

    equipamentos = list(
        session.scalars(
            select(Equipamento)
        ).all()
    )

    quantidade_maquinas = len(maquinas)
    quantidade_equipamentos = len(equipamentos)

    quantidade_ativos = (
        quantidade_maquinas
        + quantidade_equipamentos
    )

    tempo_periodo_horas = round(
        (
            fim_periodo - inicio_periodo
        ).total_seconds() / 3600,
        2,
    )

    horas_disponiveis_frota = round(
        quantidade_ativos * tempo_periodo_horas,
        2,
    )

    if horas_disponiveis_frota > 0:
        percentual_disponibilidade = round(
            (
                (
                    horas_disponiveis_frota
                    - tempo_total_parado_horas
                )
                / horas_disponiveis_frota
            ) * 100,
            2,
        )

        percentual_disponibilidade = max(
            0,
            min(
                100,
                percentual_disponibilidade,
            ),
        )
    else:
        percentual_disponibilidade = 0.0

    # ---------------------------------------------------------
    # INDICADORES POR TIPO
    # ---------------------------------------------------------

    por_tipo = {}

    for registro in registros:
        if registro.tipo not in por_tipo:
            por_tipo[registro.tipo] = {
                "quantidade": 0,
                "horas_paradas": 0.0,
            }

        por_tipo[registro.tipo]["quantidade"] += 1

        if registro.status != "CANCELADA":
            horas = _calcular_horas_sobrepostas(
                registro.inicio,
                registro.fim,
                inicio_periodo,
                fim_periodo,
                agora,
            )

            por_tipo[registro.tipo]["horas_paradas"] += horas

    for dados in por_tipo.values():
        dados["horas_paradas"] = round(
            dados["horas_paradas"],
            2,
        )

    # ---------------------------------------------------------
    # DETALHAMENTO POR MÁQUINA
    # ---------------------------------------------------------

    maquinas_dashboard = []

    for maquina in maquinas:
        registros_maquina = [
            registro
            for registro in registros_validos
            if registro.maquina_id == maquina.id
        ]

        horas_paradas = round(
            sum(
                _calcular_horas_sobrepostas(
                    registro.inicio,
                    registro.fim,
                    inicio_periodo,
                    fim_periodo,
                    agora,
                )
                for registro in registros_maquina
            ),
            2,
        )

        capacidade_maquina = tempo_periodo_horas

        if capacidade_maquina > 0:
            disponibilidade_maquina = round(
                (
                    (
                        capacidade_maquina
                        - horas_paradas
                    )
                    / capacidade_maquina
                ) * 100,
                2,
            )

            disponibilidade_maquina = max(
                0,
                min(
                    100,
                    disponibilidade_maquina,
                ),
            )
        else:
            disponibilidade_maquina = 0.0

        maquinas_dashboard.append({
            "id": maquina.id,
            "identificacao": maquina.identificacao,
            "modelo": maquina.modelo,
            "fabricante": maquina.fabricante,
            "horas_paradas": horas_paradas,
            "quantidade_indisponibilidades": len(
                registros_maquina
            ),
            "percentual_disponibilidade": (
                disponibilidade_maquina
            ),
        })

    return {
        "total": total,
        "ativas": ativas,
        "finalizadas": finalizadas,
        "canceladas": canceladas,

        "quantidade_maquinas": quantidade_maquinas,
        "quantidade_equipamentos": quantidade_equipamentos,
        "quantidade_ativos": quantidade_ativos,

        "inicio_periodo": inicio_periodo,
        "fim_periodo": fim_periodo,

        "tempo_periodo_horas": tempo_periodo_horas,

        "horas_disponiveis_frota": (
            horas_disponiveis_frota
        ),

        "tempo_total_parado_horas": (
            tempo_total_parado_horas
        ),

        "percentual_disponibilidade": (
            percentual_disponibilidade
        ),

        "por_tipo": por_tipo,

        "maquinas": maquinas_dashboard,
    }
    
    
def obter_capacidade_patio(
    session: Session,
) -> dict:
    """
    Retorna a capacidade instalada e a situação
    operacional dos ativos do pátio.
    """

    maquinas = list(
        session.scalars(
            select(Maquina)
        ).all()
    )

    equipamentos = list(
        session.scalars(
            select(Equipamento)
        ).all()
    )

    quantidade_maquinas = len(maquinas)
    quantidade_equipamentos = len(equipamentos)

    total_ativos = (
        quantidade_maquinas
        + quantidade_equipamentos
    )

    # ---------------------------------------------------------
    # INDISPONIBILIDADES ATIVAS
    # ---------------------------------------------------------

    indisponibilidades_ativas = list(
        session.scalars(
            select(Indisponibilidade).where(
                Indisponibilidade.status == "ATIVA"
            )
        ).all()
    )

    maquinas_indisponiveis = {
        registro.maquina_id
        for registro in indisponibilidades_ativas
        if registro.maquina_id is not None
    }

    equipamentos_indisponiveis = {
        registro.equipamento_id
        for registro in indisponibilidades_ativas
        if registro.equipamento_id is not None
    }

    # ---------------------------------------------------------
    # CONTAGEM OPERACIONAL
    # ---------------------------------------------------------

    indisponivel = (
        len(maquinas_indisponiveis)
        + len(equipamentos_indisponiveis)
    )

    maquinas_manutencao = {
        registro.maquina_id
        for registro in indisponibilidades_ativas
        if (
            registro.tipo == "MANUTENCAO"
            and registro.maquina_id is not None
        )
    }

    equipamentos_manutencao = {
        registro.equipamento_id
        for registro in indisponibilidades_ativas
        if (
            registro.tipo == "MANUTENCAO"
            and registro.equipamento_id is not None
        )
    }

    manutencao = (
        len(maquinas_manutencao)
        + len(equipamentos_manutencao)
    )

    operando = max(
        total_ativos - indisponivel,
        0,
    )

    # ---------------------------------------------------------
    # PERCENTUAIS
    # ---------------------------------------------------------

    if total_ativos > 0:
        percentual_operando = round(
            (operando / total_ativos) * 100,
            2,
        )

        percentual_manutencao = round(
            (manutencao / total_ativos) * 100,
            2,
        )

        percentual_indisponivel = round(
            (indisponivel / total_ativos) * 100,
            2,
        )
    else:
        percentual_operando = 0.0
        percentual_manutencao = 0.0
        percentual_indisponivel = 0.0

    return {
        "total_ativos": total_ativos,
        "maquinas": quantidade_maquinas,
        "equipamentos": quantidade_equipamentos,

        "operando": operando,
        "manutencao": manutencao,
        "indisponivel": indisponivel,

        "percentual_operando": percentual_operando,
        "percentual_manutencao": percentual_manutencao,
        "percentual_indisponivel": percentual_indisponivel,
    }
    
    
def obter_capacidade_patio(
    session: Session,
) -> dict:
    """
    Retorna a capacidade instalada atual do pátio.

    A classificação dos ativos é exclusiva:

    - MANUTENCAO
    - INDISPONIVEL
    - OPERANDO

    Uma indisponibilidade ativa tem prioridade sobre
    o status cadastrado do ativo.
    """

    # ---------------------------------------------------------
    # ATIVOS
    # ---------------------------------------------------------

    maquinas = list(
        session.scalars(
            select(Maquina)
        ).all()
    )

    equipamentos = list(
        session.scalars(
            select(Equipamento).where(
                Equipamento.ativo.is_(True)
            )
        ).all()
    )

    # ---------------------------------------------------------
    # INDISPONIBILIDADES ATIVAS
    # ---------------------------------------------------------

    indisponibilidades_ativas = list(
        session.scalars(
            select(Indisponibilidade).where(
                Indisponibilidade.status == "ATIVA"
            )
        ).all()
    )

    ids_maquinas_manutencao = set()
    ids_maquinas_indisponiveis = set()

    ids_equipamentos_manutencao = set()
    ids_equipamentos_indisponiveis = set()

    for registro in indisponibilidades_ativas:

        if registro.maquina_id is not None:

            if registro.tipo == "MANUTENCAO":
                ids_maquinas_manutencao.add(
                    registro.maquina_id
                )

            else:
                ids_maquinas_indisponiveis.add(
                    registro.maquina_id
                )

        if registro.equipamento_id is not None:

            if registro.tipo == "MANUTENCAO":
                ids_equipamentos_manutencao.add(
                    registro.equipamento_id
                )

            else:
                ids_equipamentos_indisponiveis.add(
                    registro.equipamento_id
                )

    # ---------------------------------------------------------
    # CLASSIFICAÇÃO DAS MÁQUINAS
    # ---------------------------------------------------------

    quantidade_maquinas_operando = 0
    quantidade_maquinas_manutencao = 0
    quantidade_maquinas_indisponiveis = 0

    for maquina in maquinas:

        if maquina.id in ids_maquinas_manutencao:

            quantidade_maquinas_manutencao += 1

        elif maquina.id in ids_maquinas_indisponiveis:

            quantidade_maquinas_indisponiveis += 1

        elif getattr(maquina, "status", None) == "MANUTENCAO":

            quantidade_maquinas_manutencao += 1

        else:

            quantidade_maquinas_operando += 1

    # ---------------------------------------------------------
    # CLASSIFICAÇÃO DOS EQUIPAMENTOS
    # ---------------------------------------------------------

    quantidade_equipamentos_operando = 0
    quantidade_equipamentos_manutencao = 0
    quantidade_equipamentos_indisponiveis = 0

    for equipamento in equipamentos:

        if equipamento.id in ids_equipamentos_manutencao:

            quantidade_equipamentos_manutencao += 1

        elif equipamento.id in ids_equipamentos_indisponiveis:

            quantidade_equipamentos_indisponiveis += 1

        elif getattr(equipamento, "status", None) == "MANUTENCAO":

            quantidade_equipamentos_manutencao += 1

        elif getattr(equipamento, "status", None) == "INATIVO":

            quantidade_equipamentos_indisponiveis += 1

        else:

            quantidade_equipamentos_operando += 1

    # ---------------------------------------------------------
    # TOTAIS
    # ---------------------------------------------------------

    quantidade_maquinas = len(maquinas)
    quantidade_equipamentos = len(equipamentos)

    total_ativos = (
        quantidade_maquinas
        + quantidade_equipamentos
    )

    operando = (
        quantidade_maquinas_operando
        + quantidade_equipamentos_operando
    )

    manutencao = (
        quantidade_maquinas_manutencao
        + quantidade_equipamentos_manutencao
    )

    indisponivel = (
        quantidade_maquinas_indisponiveis
        + quantidade_equipamentos_indisponiveis
    )

    # ---------------------------------------------------------
    # PERCENTUAIS
    # ---------------------------------------------------------

    def percentual(valor: int) -> float:

        if total_ativos == 0:
            return 0.0

        return round(
            (valor / total_ativos) * 100,
            2,
        )

    # ---------------------------------------------------------
    # RETORNO
    # ---------------------------------------------------------

    return {
        "total_ativos": total_ativos,

        "maquinas": quantidade_maquinas,

        "equipamentos": quantidade_equipamentos,

        "operando": operando,

        "manutencao": manutencao,

        "indisponivel": indisponivel,

        "percentual_operando": percentual(
            operando
        ),

        "percentual_manutencao": percentual(
            manutencao
        ),

        "percentual_indisponivel": percentual(
            indisponivel
        ),
    }