import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/api';
import './AssistenteIA.css';

const EXEMPLOS = [
  'Quais máquinas estão paradas e quais OS estão abertas?',
  'Quais serviços estão com prioridade urgente?',
  'O que devo verificar antes de operar um trator?',
  'Quero agendar uma colheita de silagem amanhã usando um trator disponível.',
  'Crie uma OS para revisar o trator disponível.',
];
const BOAS_VINDAS = [{ origem: 'ia', texto: 'Olá! Posso consultar sua frota, explicar procedimentos do Vault e ajudar a preparar uma OS ou agendamento. As gravações só acontecem depois da sua confirmação.' }];

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
      setErro(requestError.response?.data?.message || 'Não foi possível abrir o histórico da conversa.');
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
      setErro(requestError.response?.data?.message || 'Não foi possível iniciar uma conversa.');
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
      setErro(requestError.response?.data?.message || 'A assistente não respondeu. Confira o backend e o Ollama.');
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
      setErro(requestError.response?.data?.message || 'Não foi possível confirmar. Confira a proposta e o calendário.');
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
        <div><h1><i className="bi bi-robot" /> Assistente AgroFrota</h1>
          <p>Converse sobre a frota, prepare ordens e planeje serviços.</p></div>
        <div className="agro-ai-header-actions"><span className="agro-ai-tag">IA local · operações confirmadas pelo usuário</span>
          <button type="button" className="agro-ai-new" onClick={novaConversa} disabled={carregando}><i className="bi bi-plus-lg" /> Nova conversa</button></div>
      </header>

      <div className="agro-ai-layout">
        <section className="agro-ai-chat" aria-label="Conversa com o assistente">
          <div className="agro-ai-messages" aria-live="polite">
            {historico.map((item, index) => (
              <div key={`${index}-${item.origem}`} className={`agro-ai-bubble agro-ai-${item.origem}`}>
                {item.texto}
                {item.fontes?.length > 0 && <small className="agro-ai-sources">Fontes: {item.fontes.map((f) => f.secao ? `${f.arquivo} · ${f.secao}` : f.arquivo).join('; ')}</small>}
                {item.opcoes_recurso?.length > 0 && <div className="agro-ai-options">{item.opcoes_recurso.map((option, i) => <button key={option.id} type="button" onClick={() => enviar(`Quero o ${i === 0 ? 'primeiro' : i === 1 ? 'segundo' : `${i + 1}º`} recurso`)}>{option.identificacao} · {option.modelo}</button>)}</div>}
                {item.resultado?.os_id && <Link className="agro-ai-result-link" to={`/ordens-servico/${item.resultado.os_id}`}>Abrir OS #{item.resultado.os_numero}</Link>}
                {item.resultado?.agendamento_id && <Link className="agro-ai-result-link" to="/calendario">Ver calendário</Link>}
              </div>
            ))}
            {carregando && <p className="agro-ai-loading">Consultando registros e contexto...</p>}
          </div>
          {proposta && (
            <div className="agro-ai-proposal">
              <strong><i className="bi bi-clipboard-check" /> {agendaExistente ? 'Proposta de agendamento' : 'Nova ordem de serviço'}</strong>
              {agendaExistente ? <p><b>OS #{dadosProposta.os_numero}</b> · {dadosProposta.os_titulo}</p> : <>
                <p><b>Título:</b> {dadosProposta.titulo}</p>
                <p><b>Tipo:</b> {dadosProposta.tipo} · <b>Prioridade:</b> {dadosProposta.prioridade}</p>
                <p><b>Recurso:</b> {dadosProposta.recurso_identificacao}</p>
                <p><b>Descrição:</b> {dadosProposta.descricao}</p>
                <p><b>Status inicial:</b> ABERTA</p>
              </>}
              {(proposta.inicio || dadosProposta.inicio) && <p><b>Período:</b> {dataBonita(proposta.inicio || dadosProposta.inicio)} – {dataBonita(proposta.fim || dadosProposta.fim)}</p>}
              <small>Proposta válida por até cinco minutos. A confirmação revalida permissões e conflitos. Nada foi gravado ainda.</small>
              <div className="agro-ai-actions">
                <button type="button" onClick={confirmar} disabled={carregando}>Confirmar operação</button>
                <button type="button" className="agro-ai-secondary" onClick={cancelarProposta} disabled={carregando}>Cancelar proposta</button>
              </div>
            </div>
          )}
          {erro && <div className="agro-ai-inline-error" role="alert">{erro}</div>}
          <form onSubmit={(event) => { event.preventDefault(); enviar(); }} className="agro-ai-form">
            <input aria-label="Mensagem para o assistente" value={mensagem} onChange={(event) => setMensagem(event.target.value)} maxLength={800}
              placeholder="Ex.: Preciso revisar um trator amanhã..." disabled={carregando} />
            <button type="submit" disabled={!mensagem.trim() || carregando}><i className="bi bi-send" /> Enviar</button>
          </form>
        </section>

        <aside className="agro-ai-help">
          <h2>Experimente perguntar</h2>
          {EXEMPLOS.map((text) => <button type="button" key={text} onClick={() => enviar(text)} disabled={carregando}>{text}</button>)}
          <p>O assistente consulta dados do seu tenant. Ordens e agendamentos só são persistidos depois da confirmação.</p>
          <p>Confira <Link to="/ordens-servico">Ordens de serviço</Link> e <Link to="/calendario">Calendário</Link>.</p>
          <p className="agro-ai-disclaimer">Orientações técnicas são apoio à consulta. Siga o manual do fabricante e a inspeção de profissionais capacitados.</p>
        </aside>
      </div>
    </section>
  );
}
