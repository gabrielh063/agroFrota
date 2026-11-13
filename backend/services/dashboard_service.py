from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.tenant.indisponibilidade import Indisponibilidade
from models.tenant.maquina import Maquina
from models.tenant.equipamento import Equipamento
from models.tenant.ordem_servico import OrdemServico
from services.os_policy import consulta_os


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

    maquinas = list(session.scalars(select(Maquina)).all())

    equipamentos = list(session.scalars(select(Equipamento)).all())

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

    status_por_ativo = {}

    for registro in indisponibilidades_ativas:

        if registro.maquina_id is not None:

            chave = ("maquina", registro.maquina_id)
            novo = "manutencao" if registro.tipo == "MANUTENCAO" else "indisponivel"
            if chave not in status_por_ativo or novo == "manutencao":
                status_por_ativo[chave] = novo

        if registro.equipamento_id is not None:

            chave = ("equipamento", registro.equipamento_id)
            novo = "manutencao" if registro.tipo == "MANUTENCAO" else "indisponivel"
            if chave not in status_por_ativo or novo == "manutencao":
                status_por_ativo[chave] = novo

    quantidade_maquinas = len(maquinas)
    quantidade_equipamentos = len(equipamentos)

    contagens = {"operando": 0, "manutencao": 0, "indisponivel": 0, "inativo": 0}
    for tipo, ativos in (("maquina", maquinas), ("equipamento", equipamentos)):
        for ativo in ativos:
            status = status_por_ativo.get((tipo, ativo.id))
            if not ativo.ativo or str(ativo.status).upper() in {"INATIVO", "INATIVA", "DESATIVADO"}:
                status = "inativo"
            elif status is None:
                valor = str(ativo.status).upper()
                if valor in {"MANUTENCAO", "EM_MANUTENCAO"}:
                    status = "manutencao"
                elif valor in {"INDISPONIVEL", "PARADO", "PARADA", "INOPERANTE"}:
                    status = "indisponivel"
                else:
                    status = "operando"
            contagens[status] += 1

    total_ativos = quantidade_maquinas + quantidade_equipamentos
    operando = contagens["operando"]
    manutencao = contagens["manutencao"]
    indisponivel = contagens["indisponivel"]
    inativo = contagens["inativo"]
    base_operacional = total_ativos - inativo

    # ---------------------------------------------------------
    # PERCENTUAIS
    # ---------------------------------------------------------

    def percentual(valor: int) -> float:

        if base_operacional == 0:
            return 0.0

        return round(
            (valor / base_operacional) * 100,
            2,
        )

    # ---------------------------------------------------------
    # RETORNO
    # ---------------------------------------------------------

    return {
        "total_ativos": total_ativos,
        "base_operacional": base_operacional,

        "maquinas": quantidade_maquinas,

        "equipamentos": quantidade_equipamentos,

        "operando": operando,

        "manutencao": manutencao,

        "indisponivel": indisponivel,
        "inativo": inativo,

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


def obter_atividade_servicos(session: Session, contexto, meses: int = 12) -> list[dict]:
    """Retorna OS criadas por mês, no escopo que o usuário pode visualizar."""
    from datetime import datetime

    agora = datetime.utcnow()
    inicio = datetime(agora.year, agora.month, 1)
    for _ in range(meses - 1):
        inicio = inicio.replace(day=1) - timedelta(days=1)
        inicio = inicio.replace(day=1)
    consulta = consulta_os(session, contexto, "OS.VISUALIZAR", select(OrdemServico))
    ordens = session.execute(consulta.where(OrdemServico.criado_em >= inicio)).scalars().unique().all()
    contagens = {}
    for ordem in ordens:
        chave = (ordem.criado_em.year, ordem.criado_em.month)
        contagens[chave] = contagens.get(chave, 0) + 1
    resultado = []
    cursor = datetime(agora.year, agora.month, 1)
    for _ in range(meses):
        resultado.append({"ano": cursor.year, "mes": cursor.month,
                          "quantidade": contagens.get((cursor.year, cursor.month), 0)})
        cursor = cursor.replace(day=1) - timedelta(days=1)
        cursor = cursor.replace(day=1)
    resultado.reverse()
    return resultado
