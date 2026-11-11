import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/api';
import './AssistenteIA.css';

const EXEMPLOS = [
  { label: 'Consultar disponibilidade da frota', prompt: 'Quais máquinas estão disponíveis para operação?' },
  { label: 'Ver ordens de serviço urgentes', prompt: 'Quais serviços estão com prioridade urgente?' },
  { label: 'Consultar recomendações técnicas', prompt: 'O que devo verificar antes de operar um trator?' },
  { label: 'Planejar um serviço', prompt: 'Quero agendar uma colheita de silagem amanhã usando um trator disponível.' },
  { label: 'Criar ordem de serviço', prompt: 'Crie uma OS para revisar o trator disponível.' },
];
const BOAS_VINDAS = [{ origem: 'ia', texto: 'Olá! Posso ajudar você a consultar sua frota, organizar serviços, criar ordens de serviço e planejar agendamentos. Por onde deseja começar?' }];

function textoOperacional(value = '') {
  return (typeof value === 'string' ? value : '')
    .replace(/assistente\s+ia/gi, 'Central de Operações')
    .replace(/inteligência artificial/gi, 'processamento automatizado')
    .replace(/powered\s+by\s+ai/gi, 'AgroFrota')
    .replace(/\b(ollama|llama|gpt|llm|rag|fts5)\b/gi, 'serviço operacional')
    .replace(/\bvault\b/gi, 'base documental')
    .replace(/\bia\b/gi, 'processamento automatizado');
}

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
      setErro('Não foi possível confirmar a operação. Confira as informações e tente novamente.');
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

  return (
    <section className="agro-ai-page">
      <header className="agro-ai-header">
        <div><span className="agro-ai-eyebrow">OPERAÇÕES</span><h1><i className="bi bi-chat-square-text" /> Central de Operações</h1>
          <p>Consulte informações da frota, planeje serviços e acompanhe ordens de serviço em um só lugar.</p></div>
        <div className="agro-ai-header-actions">
          <button type="button" className="agro-ai-new" onClick={novaConversa} disabled={carregando}><i className="bi bi-plus-lg" /> Nova conversa</button></div>
      </header>

      <div className="agro-ai-layout">
        <section className="agro-ai-chat" aria-label="Central de Operações">
          <div className="agro-ai-messages" aria-live="polite" aria-busy={carregando}>
            {historico.map((item, index) => (
              <div key={`${index}-${item.origem}`} className={`agro-ai-bubble agro-ai-${item.origem}`}>
                {textoOperacional(item.texto)}
                {item.fontes?.length > 0 && <small className="agro-ai-sources">Referências: {item.fontes.map((f) => f.secao ? `${textoOperacional(f.arquivo)} · ${textoOperacional(f.secao)}` : textoOperacional(f.arquivo)).join('; ')}</small>}
                {item.opcoes_recurso?.length > 0 && <div className="agro-ai-options">{item.opcoes_recurso.map((option, i) => <button key={option.id} type="button" onClick={() => enviar(`Quero o ${i === 0 ? 'primeiro' : i === 1 ? 'segundo' : `${i + 1}º`} recurso`)}>{option.identificacao} · {option.modelo}</button>)}</div>}
                {item.resultado?.os_id && <Link className="agro-ai-result-link" to={`/ordens-servico/${item.resultado.os_id}`}>Abrir OS #{item.resultado.os_numero}</Link>}
                {item.resultado?.agendamento_id && <Link className="agro-ai-result-link" to="/calendario">Ver calendário</Link>}
              </div>
            ))}
            {carregando && <p className="agro-ai-loading"><span className="spinner-border spinner-border-sm" aria-hidden="true" /> Processando solicitação…</p>}
          </div>
          {proposta && (
            <div className="agro-ai-proposal">
              <strong><i className={`bi ${agendaExistente ? 'bi-calendar-check' : 'bi-clipboard-check'}`} /> {agendaExistente ? 'Proposta de agendamento' : 'Proposta de ordem de serviço'}</strong>
              {agendaExistente ? <p><b>OS #{dadosProposta.os_numero}</b> · {dadosProposta.os_titulo}</p> : <>
                <p><b>Título:</b> {dadosProposta.titulo}</p>
                <p><b>Tipo:</b> {dadosProposta.tipo} · <b>Prioridade:</b> {dadosProposta.prioridade}</p>
                <p><b>Recurso:</b> {dadosProposta.recurso_identificacao}</p>
                <p><b>Descrição:</b> {dadosProposta.descricao}</p>
                <p><b>Status inicial:</b> ABERTA</p>
              </>}
              {(proposta.inicio || dadosProposta.inicio) && <p><b>Período:</b> {dataBonita(proposta.inicio || dadosProposta.inicio)} – {dataBonita(proposta.fim || dadosProposta.fim)}</p>}
              <small>Esta proposta ainda não foi gravada. Ao confirmar, as permissões e a disponibilidade serão verificadas novamente.</small>
              <div className="agro-ai-actions">
                <button type="button" onClick={confirmar} disabled={carregando}>Confirmar operação</button>
                <button type="button" className="agro-ai-secondary" onClick={cancelarProposta} disabled={carregando}>Cancelar</button>
              </div>
            </div>
          )}
          {erro && <div className="agro-ai-inline-error" role="alert">{erro}</div>}
          <form onSubmit={(event) => { event.preventDefault(); enviar(); }} className="agro-ai-form">
            <input aria-label="Descreva o que precisa consultar ou planejar" value={mensagem} onChange={(event) => setMensagem(event.target.value)} maxLength={800}
              placeholder="Ex.: Preciso revisar um trator amanhã…" disabled={carregando} />
            <button type="submit" disabled={!mensagem.trim() || carregando}><i className="bi bi-send" /> Enviar</button>
          </form>
        </section>

        <aside className="agro-ai-help">
          <h2>Ações rápidas</h2>
          {EXEMPLOS.map(({ label, prompt }) => <button type="button" key={label} onClick={() => enviar(prompt)} disabled={carregando}><i className="bi bi-arrow-up-right" />{label}</button>)}
          <p>As ordens e os agendamentos só são registrados após sua confirmação.</p>
          <p>Confira <Link to="/ordens-servico">Ordens de serviço</Link> e <Link to="/calendario">Calendário</Link>.</p>
          <p className="agro-ai-disclaimer">Orientações técnicas são apoio à consulta. Siga o manual do fabricante e a inspeção de profissionais capacitados.</p>
        </aside>
      </div>
    </section>
  );
}
