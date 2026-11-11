import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { buscarCapacidade, buscarAtividade } from "../../api/dashboardService";
import { listarOrdensServico } from "../../api/ordemServicoService";
import { listarMaquinas } from "../../api/maquinaService";
import { listarEquipamentos } from "../../api/equipamentoService";
import { listarAgendamentos } from "../../api/calendarioService";
import DashboardCard from "../../components/DashboardCard/DashboardCard";
import "./Home.css";

const MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
const FINALIZADOS = new Set(["CONCLUIDA", "CANCELADA"]);
const demo = import.meta.env.VITE_AGROFROTA_DEMO === "true";

function texto(valor = "") { return valor.toLowerCase().replaceAll("_", " ").replace(/^\w/, (c) => c.toUpperCase()); }
function dataPt(valor) { return valor ? new Intl.DateTimeFormat("pt-BR").format(new Date(valor)) : "Sem prazo informado"; }

function Donut({ capacidade }) {
    const rows = [
        { label: "Operando", value: capacidade?.operando || 0, color: "#59b86a" },
        { label: "Em manutenção", value: capacidade?.manutencao || 0, color: "#e59a3d" },
        { label: "Indisponíveis", value: capacidade?.indisponivel || 0, color: "#27aaa4" },
        { label: "Inativos", value: capacidade?.inativo || 0, color: "#46524a" },
    ];
    const total = rows.reduce((sum, item) => sum + item.value, 0);
    let offset = 0;
    const circles = rows.map((item) => {
        const dash = total ? item.value / total * 100 : 0;
        const current = <circle key={item.label} cx="60" cy="60" r="44" fill="none" stroke={item.color} strokeWidth="13" strokeDasharray={`${dash} ${100 - dash}`} strokeDashoffset={-offset} pathLength="100" />;
        offset += dash;
        return current;
    });
    return <div className="donut-wrap"><div className="donut-visual"><svg className="donut-chart" viewBox="0 0 120 120" role="img" aria-label={`Status de ${total} ativos`}><circle cx="60" cy="60" r="44" fill="none" stroke="#1d2920" strokeWidth="13" />{circles}</svg><div className="donut-center"><strong>{total}</strong><span>ativos totais</span></div></div><ul className="donut-legend">{rows.map((item) => <li key={item.label}><i style={{ background: item.color }} /><span>{item.label}</span><b>{item.value}</b></li>)}</ul></div>;
}

function ActivityChart({ activity }) {
    const max = Math.max(1, ...activity.map((item) => item.quantidade));
    const temDados = activity.some((item) => item.quantidade > 0);
    return <div className="activity-chart" aria-label="Ordens de serviço criadas por mês">
        {!temDados ? <div className="chart-empty">Sem histórico de ordens de serviço para este período.</div> : <>
            <div className="bar-grid">{activity.map((item) => <div className="bar-column" key={`${item.ano}-${item.mes}`} title={`${MESES[item.mes - 1]} ${item.ano}: ${item.quantidade} OS`}><div className="bar-track"><span className="activity-bar" style={{ height: `${Math.max(3, item.quantidade / max * 100)}%` }} /></div><small>{MESES[item.mes - 1]}</small></div>)}</div>
            <div className="chart-footnote">Ordens de serviço registradas por mês <b>{activity.reduce((sum, item) => sum + item.quantidade, 0)} no período</b></div>
        </>}
    </div>;
}

export default function Home() {
    const navigate = useNavigate();
    const [capacidade, setCapacidade] = useState(null);
    const [ordens, setOrdens] = useState([]);
    const [maquinas, setMaquinas] = useState([]);
    const [equipamentos, setEquipamentos] = useState([]);
    const [atividade, setAtividade] = useState([]);
    const [agendamentos, setAgendamentos] = useState([]);
    const [periodo, setPeriodo] = useState(12);
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState("");

    const carregarDashboard = useCallback(async () => {
        setCarregando(true); setErro("");
        try {
            const [cap, os, maq, equip, hist, agenda] = await Promise.all([
                buscarCapacidade(), listarOrdensServico(), listarMaquinas({ incluirInativas: true }),
                listarEquipamentos({ incluirInativos: true }), buscarAtividade(periodo), listarAgendamentos(),
            ]);
            setCapacidade(cap.capacidade);
            setOrdens(os.ordens_servico || []);
            setMaquinas(maq.data || []);
            setEquipamentos(equip.data || []);
            setAtividade(hist.atividade || []);
            setAgendamentos(agenda.agendamentos || []);
        } catch (error) {
            console.error("Erro ao carregar dashboard:", error);
            setErro("Não foi possível carregar os dados do painel. Confira suas permissões e tente novamente.");
        } finally { setCarregando(false); }
    }, [periodo]);
    useEffect(() => { carregarDashboard(); }, [carregarDashboard]);

    const abertas = useMemo(() => ordens.filter((o) => o.ativo && !FINALIZADOS.has(o.status)).sort((a, b) => new Date(a.prazo || "9999") - new Date(b.prazo || "9999")), [ordens]);
    const preventivas = ordens.filter((o) => o.tipo === "MANUTENCAO" && o.ativo && !FINALIZADOS.has(o.status)).length;
    const concluidas = ordens.filter((o) => o.status === "CONCLUIDA").length;
    const total = capacidade?.total_ativos || 0;
    const baseOperacional = capacidade?.base_operacional ?? total;
    const pct = (n) => baseOperacional ? Math.round(n / baseOperacional * 100) : null;
    const agora = new Date();
    const fimSemana = new Date(agora);
    fimSemana.setDate(fimSemana.getDate() + 7);
    const agendamentosFuturos = agendamentos.filter((a) => a.status !== "CANCELADO" && new Date(a.inicio) > agora && new Date(a.inicio) < fimSemana).length;
    const ativosLabel = `${capacidade?.maquinas || 0} máquinas · ${capacidade?.equipamentos || 0} equipamentos`;
    function nomeAtivo(os) {
        if (os.maquina_id) { const m = maquinas.find((x) => x.id === os.maquina_id); if (m) return `${m.fabricante} ${m.modelo} · ${m.identificacao}`; }
        if (os.equipamento_id) { const e = equipamentos.find((x) => x.id === os.equipamento_id); if (e) return `${e.identificacao} · ${e.nome}`; }
        return "Ativo não identificado";
    }
    const dataHoje = new Intl.DateTimeFormat("pt-BR", { weekday: "long", day: "numeric", month: "long", year: "numeric" }).format(new Date());

    return <div className="home-page">
        <div className="home-topline"><span>Operações <i>/</i> <b>Visão geral</b></span><div><time>{dataHoje}</time>{demo && <span className="demo-badge"><i /> DADOS FICTÍCIOS · DEMONSTRAÇÃO</span>}</div></div>
        <header className="home-header"><div><span className="eyebrow">GESTÃO OPERACIONAL</span><h1>Painel de controle</h1><p>Visão geral da frota, manutenções e ordens de serviço.</p></div><button className="home-new-os" onClick={() => navigate("/ordens-servico/nova")}><i className="bi bi-plus-lg" /> Nova ordem de serviço</button></header>
        {carregando ? <section className="dashboard-loading"><span className="spinner-border spinner-border-sm" />Carregando indicadores...</section> : erro ? <section className="home-error" role="alert"><i className="bi bi-exclamation-circle" />{erro}<button onClick={carregarDashboard}>Tentar novamente</button></section> : <>
            <section className="dashboard-cards">
                <DashboardCard titulo="Ativos cadastrados" valor={total} descricao={ativosLabel} icone="bi-truck" />
                <DashboardCard titulo="Frota em operação" valor={capacidade?.operando ?? 0} descricao={!total ? "Sem ativos cadastrados" : baseOperacional ? `${pct(capacidade?.operando || 0)}% da base operacional` : "Sem ativos operacionais"} icone="bi-activity" variante="operando" />
                <DashboardCard titulo="Em manutenção" valor={capacidade?.manutencao ?? 0} descricao={`${capacidade?.indisponivel || 0} indisponíveis`} icone="bi-wrench-adjustable" variante="manutencao" />
                <DashboardCard titulo="Ordens em aberto" valor={abertas.length} descricao={`${agendamentosFuturos} agendadas para esta semana`} icone="bi-clipboard-check" variante="os" />
            </section>
            <section className="dashboard-middle">
                <article className="panel activity-panel"><div className="panel-heading"><div><h2>Atividade de serviços</h2><p>Ordens de serviço registradas nos últimos {periodo} meses</p></div><select aria-label="Período do histórico" value={periodo} onChange={(event) => setPeriodo(Number(event.target.value))}><option value={3}>Últimos 3 meses</option><option value={6}>Últimos 6 meses</option><option value={12}>Últimos 12 meses</option></select></div><ActivityChart activity={atividade} /></article>
                <article className="panel status-panel"><div className="panel-heading"><div><h2>Status operacional</h2><p>Distribuição dos ativos cadastrados</p></div><span>{new Intl.DateTimeFormat("pt-BR", { month: "long", year: "numeric" }).format(new Date())}</span></div><Donut capacidade={capacidade} /></article>
            </section>
            <section className="dashboard-bottom">
                <article className="panel orders-panel"><div className="panel-heading"><div><h2>Ordens de serviço recentes</h2><p>Acompanhe as atividades prioritárias da operação</p></div><button onClick={() => navigate("/ordens-servico")}>Ver todas <i className="bi bi-arrow-right" /></button></div>
                    {abertas.length ? <div className="recent-orders">{abertas.slice(0, 5).map((os) => <button className="recent-order" key={os.id} onClick={() => navigate(`/ordens-servico/${os.id}`)}><div><small>#{os.numero}</small><strong>{os.titulo}</strong><span>{nomeAtivo(os)} · {texto(os.tipo)}</span></div><div className="order-meta"><span className={`status-badge status-${os.status.toLowerCase()}`}>{texto(os.status)}</span><small>Prazo {dataPt(os.prazo)}</small></div></button>)}</div> : <div className="panel-empty">Nenhuma ordem em aberto no momento.</div>}
                </article>
                <article className="panel metrics-panel"><div className="panel-heading"><div><h2>Indicadores de manutenção</h2><p>Acompanhamento com dados disponíveis</p></div></div>
                    <Metric label="Ordens de manutenção abertas" value={preventivas} max={ordens.length} detail={ordens.length ? `${preventivas} de ${ordens.length} OS visíveis` : "Dados insuficientes"} />
                    <Metric label="Serviços concluídos no prazo" value={null} detail="Dados insuficientes · conclusão não registra data" />
                    <Metric label="Disponibilidade da frota" value={baseOperacional ? capacidade?.percentual_operando : null} percent detail={capacidade ? (baseOperacional ? "Ativos operando ÷ base operacional (inativos excluídos)" : "Sem ativos operacionais") : "Dados insuficientes"} />
                    <Metric label="Ordens concluídas" value={concluidas} max={null} detail="Total de OS concluídas visíveis (todo o histórico)" />
                </article>
            </section>
        </>}
    </div>;
}

function Metric({ label, value, max, percent = false, detail }) {
    const width = value == null ? 0 : percent ? Math.max(0, Math.min(100, value)) : max ? Math.max(0, Math.min(100, value / max * 100)) : null;
    return <div className="metric-row"><div className="metric-label"><span>{label}</span><b>{value == null ? "—" : `${value}${percent ? "%" : ""}${max ? ` / ${max}` : ""}`}</b></div><div className={`metric-track ${width == null ? "metric-unknown" : ""}`}><i style={{ width: width == null ? "0%" : `${width}%` }} /></div><small>{detail}</small></div>;
}
