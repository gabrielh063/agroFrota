import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/api';
import './AssistenteIA.css';

const EXEMPLOS = [
  { icon: 'bi-speedometer2', label: 'Consultar disponibilidade', description: 'Confira quais recursos estão prontos para a operação.', prompt: 'Quais máquinas estão disponíveis para operação?' },
  { icon: 'bi-clipboard-plus', label: 'Criar ordem de serviço', description: 'Registre um serviço para uma máquina ou equipamento.', prompt: 'Crie uma OS para revisar o trator disponível.' },
  { icon: 'bi-wrench-adjustable-circle', label: 'Planejar manutenção', description: 'Consulte serviços pendentes e organize as próximas intervenções.', prompt: 'Quais máquinas estão em manutenção e quais ordens estão abertas?' },
  { icon: 'bi-calendar2-week', label: 'Agendar serviço', description: 'Escolha recurso, data e horário antes de confirmar.', prompt: 'Quero agendar uma manutenção preventiva para amanhã usando um trator disponível.' },
];
const BOAS_VINDAS = [{ origem: 'ia', texto: 'Olá! Posso ajudar você a consultar sua frota, organizar serviços, criar ordens de serviço e planejar agendamentos. Por onde deseja começar?' }];

function dataBonita(value) {
  if (!value) return 'Sem agendamento';
  const [day, time = ''] = value.split('T');
  const [year, month, date] = day.split('-');
  return `${date}/${month}/${year}${time ? ` às ${time}` : ''}`;
}

export default function AssistenteIA() {
  const [mensagem, setMensagem] = useState('');
  const [historico, setHistorico] = useState(BOAS_VINDAS);
  const [proposta, setProposta] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState('');

  async function abrirRecente() {
    setCarregando(true);
    try {
      const { data: list } = await api.get('/api/assistente/conversas');
      const recent = list.conversas?.[0];
      if (!recent) {
        const { data } = await api.post('/api/assistente/conversas');
        setConversationId(data.conversation_id);
        setHistorico(BOAS_VINDAS);
        setProposta(null);
      } else {
        const { data } = await api.get(`/api/assistente/conversas/${recent.id}`);
        setConversationId(data.conversation_id);
        setHistorico(data.historico?.length ? data.historico : BOAS_VINDAS);
        setProposta(data.proposta_pendente || null);
      }
    } catch (requestError) {
      console.error('Falha ao abrir histórico operacional:', requestError);
      setErro('Não foi possível carregar o histórico. Verifique sua conexão e tente novamente.');
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => { abrirRecente(); }, []);

  async function novaConversa() {
    setCarregando(true);
    setProposta(null);
    try {
      const { data } = await api.post('/api/assistente/conversas');
      setConversationId(data.conversation_id);
      setHistorico(BOAS_VINDAS);
      setErro('');
    } catch (requestError) {
      console.error('Falha ao iniciar conversa operacional:', requestError);
      setErro('Não foi possível iniciar uma nova conversa. Verifique sua conexão e tente novamente.');
    } finally {
      setCarregando(false);
    }
  }

  async function enviar(text = mensagem) {
    const prompt = text.trim();
    if (!prompt || carregando) return;
    setCarregando(true);
    setMensagem('');
    setErro('');
    try {
      let id = conversationId;
      if (!id) {
        const { data } = await api.post('/api/assistente/conversas');
        id = data.conversation_id;
        setConversationId(id);
      }
      const { data } = await api.post('/api/assistente/mensagem',
        { mensagem: prompt, conversation_id: id }, { timeout: 120000 });
      if (data.historico) setHistorico(data.historico);
      setProposta(data.proposta || null);
    } catch (requestError) {
      console.error('Falha ao processar solicitação operacional:', requestError);
      setErro('Não foi possível processar a solicitação. Verifique sua conexão e tente novamente.');
    } finally {
      setCarregando(false);
    }
  }

  async function confirmar() {
    if (!proposta || carregando) return;
    setCarregando(true);
    setErro('');
    try {
      const { data } = await api.post('/api/assistente/confirmar',
        { proposta_id: proposta.id, codigo: proposta.codigo, conversation_id: conversationId }, { timeout: 30000 });
      if (data.operacao === 'AGENDAR_OS') setHistorico((items) => [...items, { origem: 'ia', texto: data.message, resultado: data.resultado }]);
      else if (data.os_id) setHistorico((items) => [...items, { origem: 'ia', texto: `✅ OS #${data.os_numero} criada.${data.agendamento_id ? ` Agendamento #${data.agendamento_id} confirmado.` : ''}`, resultado: data.resultado }]);
      else setHistorico((items) => [...items, { origem: 'ia', texto: data.message || 'Operação confirmada.', resultado: data.resultado }]);
      setProposta(null);
    } catch (requestError) {
      console.error('Falha ao confirmar operação:', requestError);
      setErro('Não foi possível confirmar a operação agora. Confira Ordens de serviço e Calendário antes de tentar novamente; uma confirmação repetida retorna o mesmo resultado se o registro já foi criado.');
    } finally {
      setCarregando(false);
    }
  }

  async function cancelarProposta() {
    setProposta(null);
    await enviar('Cancela essa proposta');
  }

  const dadosProposta = proposta?.dados || proposta || {};
  const agendaExistente = proposta?.operacao === 'AGENDAR_OS';
  const temConversa = Boolean(proposta) || historico.some((item) =>
    item.origem === 'usuario' || item.resultado || item.opcoes_recurso?.length || item.fontes?.length || item.texto !== BOAS_VINDAS[0].texto
  );
  const mostrarInicio = !temConversa;

  return (
    <section className="agro-ai-page">
      <header className="agro-ai-header">
        <div><span className="agro-ai-eyebrow">OPERAÇÕES</span><h1><i className="bi bi-chat-square-text" /> Central de Operações</h1>
          <p>Consulte informações da frota, planeje serviços e acompanhe ordens de serviço em um só lugar.</p></div>
        {!mostrarInicio && <div className="agro-ai-header-actions"><button type="button" className="agro-ai-new" onClick={novaConversa} disabled={carregando}><i className="bi bi-plus-lg" /> Nova conversa</button></div>}
      </header>

      {mostrarInicio ? <div className="operations-start">
        <div className="operations-start-intro">
          <span className="operations-start-mark"><i className="bi bi-calendar2-check" /></span>
          <span className="agro-ai-eyebrow">PLANEJAMENTO DA FROTA</span>
          <h2>O que você precisa fazer hoje?</h2>
          <p>Consulte sua frota, organize serviços e acompanhe suas operações.</p>
        </div>
        <div className="operations-task-grid">
          {EXEMPLOS.map(({ icon, label, description, prompt }) => <button className="operations-task-card" type="button" key={label} onClick={() => enviar(prompt)} disabled={carregando}>
            <span className="operations-task-icon"><i className={`bi ${icon}`} /></span>
            <span className="operations-task-copy"><strong>{label}</strong><small>{description}</small></span>
            <i className="bi bi-arrow-up-right operations-task-arrow" aria-hidden="true" />
          </button>)}
        </div>
        {erro && <div className="agro-ai-inline-error" role="alert">{erro}</div>}
        {carregando && <p className="operations-start-loading"><span className="spinner-border spinner-border-sm" aria-hidden="true" /> Preparando a Central…</p>}
        <form onSubmit={(event) => { event.preventDefault(); enviar(); }} className="agro-ai-form operations-start-form">
          <input aria-label="Descreva o que precisa consultar ou planejar" value={mensagem} onChange={(event) => setMensagem(event.target.value)} maxLength={800} placeholder="Escreva uma solicitação ou escolha uma ação acima…" disabled={carregando} />
          <button type="submit" disabled={!mensagem.trim() || carregando}><i className="bi bi-arrow-up" /><span>Enviar</span></button>
        </form>
        <p className="operations-start-note"><i className="bi bi-shield-check" /> Ordens e agendamentos só são registrados após sua confirmação.</p>
      </div> : <section className="operations-workspace" aria-label="Planejamento operacional">
        <div className="operations-session-bar"><span><i className="bi bi-chat-square-text" /> Conversa operacional</span><span className="operations-session-status"><i /> Histórico salvo</span></div>
        <div className="agro-ai-messages" aria-live="polite" aria-busy={carregando}>
          {historico.map((item, index) => (
            <div key={`${index}-${item.origem}`} className={`agro-ai-message agro-ai-${item.origem}`}>
              <span className="agro-ai-message-label">{item.origem === 'usuario' ? 'Você' : 'Central de Operações'}</span>
              <div className="agro-ai-bubble">{item.texto}</div>
              {item.fontes?.length > 0 && <small className="agro-ai-sources">Referências: {item.fontes.map((f) => f.secao ? `${f.arquivo} · ${f.secao}` : f.arquivo).join('; ')}</small>}
              {item.opcoes_recurso?.length > 0 && <div className="agro-ai-options">{item.opcoes_recurso.map((option, i) => <button key={option.id} type="button" onClick={() => enviar(`Quero o ${i === 0 ? 'primeiro' : i === 1 ? 'segundo' : `${i + 1}º`} recurso`)}>{option.identificacao} · {option.modelo}<i className="bi bi-arrow-right" /></button>)}</div>}
              {item.resultado?.os_id && <Link className="agro-ai-result-link" to={`/ordens-servico/${item.resultado.os_id}`}><i className="bi bi-clipboard-check" /> Abrir OS #{item.resultado.os_numero}</Link>}
              {item.resultado?.agendamento_id && <Link className="agro-ai-result-link" to="/calendario"><i className="bi bi-calendar3" /> Ver calendário</Link>}
            </div>
          ))}
          {carregando && <p className="agro-ai-loading"><span className="spinner-border spinner-border-sm" aria-hidden="true" /> Processando solicitação…</p>}
        </div>
        {proposta && <div className="agro-ai-proposal">
          <div className="agro-ai-proposal-heading"><span className="agro-ai-proposal-icon"><i className={`bi ${agendaExistente ? 'bi-calendar-check' : 'bi-clipboard-check'}`} /></span><span><small>REVISÃO NECESSÁRIA</small><strong>{agendaExistente ? 'Proposta de agendamento' : 'Proposta de ordem de serviço'}</strong></span><em>Não gravada</em></div>
          {agendaExistente ? <div className="agro-ai-proposal-grid"><div><small>Ordem de serviço</small><strong>#{dadosProposta.os_numero} · {dadosProposta.os_titulo}</strong></div></div> : <div className="agro-ai-proposal-grid">
            <div><small>Título</small><strong>{dadosProposta.titulo || 'Não informado'}</strong></div>
            <div><small>Tipo e prioridade</small><strong>{dadosProposta.tipo || 'Serviço'} · {dadosProposta.prioridade || 'Média'}</strong></div>
            <div><small>Máquina ou equipamento</small><strong>{dadosProposta.recurso_identificacao || 'A definir'}</strong></div>
            <div><small>Estado inicial</small><strong>Aberta</strong></div>
            {dadosProposta.descricao && <div className="proposal-description"><small>Descrição</small><strong>{dadosProposta.descricao}</strong></div>}
          </div>}
          {(proposta.inicio || dadosProposta.inicio) && <div className="agro-ai-proposal-date"><i className="bi bi-calendar3" /><span><small>Data e horário</small><strong>{dataBonita(proposta.inicio || dadosProposta.inicio)}{(proposta.fim || dadosProposta.fim) && ` – ${dataBonita(proposta.fim || dadosProposta.fim)}`}</strong></span></div>}
          <div className="agro-ai-proposal-footer"><p>Ao confirmar, as permissões e a disponibilidade serão verificadas novamente.</p><div className="agro-ai-actions"><button type="button" onClick={confirmar} disabled={carregando}><i className="bi bi-check-lg" /> Confirmar operação</button><button type="button" className="agro-ai-secondary" onClick={cancelarProposta} disabled={carregando}>Cancelar</button></div></div>
        </div>}
        {erro && <div className="agro-ai-inline-error" role="alert">{erro}</div>}
        <form onSubmit={(event) => { event.preventDefault(); enviar(); }} className="agro-ai-form operations-conversation-form">
          <input aria-label="Descreva o que precisa consultar ou planejar" value={mensagem} onChange={(event) => setMensagem(event.target.value)} maxLength={800} placeholder="Continue a solicitação ou descreva uma nova tarefa…" disabled={carregando} />
          <button type="submit" disabled={!mensagem.trim() || carregando}><i className="bi bi-arrow-up" /><span>Enviar</span></button>
        </form>
      </section>}
      <p className="agro-ai-disclaimer"><i className="bi bi-info-circle" /> Orientações técnicas apoiam a consulta. Siga o manual do fabricante e a avaliação de profissionais capacitados.</p>
    </section>
  );
}
