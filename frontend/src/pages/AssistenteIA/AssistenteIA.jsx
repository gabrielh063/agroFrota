import { useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/api';
import './AssistenteIA.css';

const EXEMPLOS = [
  'Quais máquinas estão paradas e quais OS estão abertas?',
  'Qual a diferença entre manutenção preventiva e corretiva?',
  'O que devo verificar antes de operar um trator?',
  'Quais serviços estão com prioridade urgente?',
  'Agende a OS número 1 para amanhã às 14h por duas horas.',
];

const inicial = [{ origem: 'ia', texto: 'Olá! Sou a assistente agrícola do AgroFrota. Posso explicar manutenção de máquinas, consultar sua frota e propor agendamentos de ordens de serviço existentes.' }];

function dataBonita(valor) {
  if (!valor) return '';
  const [dia, hora] = valor.split('T');
  const [ano, mes, data] = dia.split('-');
  return `${data}/${mes}/${ano}, ${hora}`;
}

export default function AssistenteIA() {
  const [mensagem, setMensagem] = useState('');
  const [historico, setHistorico] = useState(inicial);
  const [proposta, setProposta] = useState(null);
  const [carregando, setCarregando] = useState(false);

  const adicionar = (origem, texto, fontes = []) => setHistorico((itens) => [...itens, { origem, texto, fontes }]);

  async function enviar(texto = mensagem) {
    const pergunta = texto.trim();
    if (!pergunta || carregando) return;
    setCarregando(true);
    setMensagem('');
    setProposta(null);
    adicionar('usuario', pergunta);
    try {
      const { data } = await api.post('/api/assistente/mensagem', { mensagem: pergunta }, { timeout: 120000 });
      adicionar('ia', data.resposta || 'Não consegui responder.', [...(data.fontes || []), ...(data.fontes_operacionais || []).map((arquivo) => ({ arquivo, secao: "" }))]);
      if (data.proposta) setProposta(data.proposta);
    } catch (erro) {
      adicionar('erro', erro.response?.data?.message || 'A assistente não respondeu. Confira se Ollama e backend estão ligados.');
    } finally {
      setCarregando(false);
    }
  }

  async function confirmar() {
    if (!proposta || carregando) return;
    setCarregando(true);
    const atual = proposta;
    setProposta(null);
    try {
      const { data } = await api.post('/api/assistente/confirmar', { codigo: atual.codigo }, { timeout: 30000 });
      adicionar('ia', `✅ ${data.message} Registro #${data.agendamento.id}. Confira no calendário.`);
    } catch (erro) {
      adicionar('erro', erro.response?.data?.message || 'Não foi possível confirmar. Consulte o calendário antes de tentar novamente.');
    } finally {
      setCarregando(false);
    }
  }

  return (
    <section className="agro-ai-page">
      <header className="agro-ai-header">
        <div><h1><i className="bi bi-robot" /> Assistente AgroFrota</h1>
          <p>Conhecimento agrícola, consultas da sua frota e agendamentos com confirmação.</p></div>
        <span className="agro-ai-tag">IA local · demonstração acadêmica</span>
      </header>

      <div className="agro-ai-layout">
        <section className="agro-ai-chat" aria-label="Conversa com o assistente">
          <div className="agro-ai-messages" aria-live="polite">
            {historico.map((m, i) => (
              <div key={i} className={`agro-ai-bubble agro-ai-${m.origem}`}>
                {m.texto}
                {m.fontes?.length > 0 && <small className="agro-ai-sources">Fontes: {m.fontes.map((f) => f.secao ? `${f.arquivo} · ${f.secao}` : f.arquivo).join('; ')}</small>}
              </div>
            ))}
            {carregando && <p className="agro-ai-loading">Analisando a solicitação...</p>}
          </div>
          {proposta && (
            <div className="agro-ai-proposal">
              <strong><i className="bi bi-calendar-check" /> Confirmar agendamento?</strong>
              <p><b>OS #{proposta.os_numero}</b> · {proposta.os_titulo}</p>
              <p>{dataBonita(proposta.inicio)} até {dataBonita(proposta.fim)}</p>
              {proposta.duracao_padrao && <small>Duração sugerida de 2 horas; o usuário não informou horário final.</small>}
              <small>Proposta válida por até 5 minutos. Conflitos serão verificados antes da gravação.</small>
              <div className="agro-ai-actions">
                <button type="button" onClick={confirmar} disabled={carregando}>Confirmar no AgroFrota</button>
                <button type="button" className="agro-ai-secondary" onClick={() => { setProposta(null); adicionar('ia', 'Proposta descartada. Nada foi agendado.'); }}>Cancelar</button>
              </div>
            </div>
          )}
          <form onSubmit={(e) => { e.preventDefault(); enviar(); }} className="agro-ai-form">
            <input aria-label="Mensagem para o assistente" value={mensagem}
              onChange={(e) => setMensagem(e.target.value)} maxLength={800}
              placeholder="Ex.: Agende a OS 3 amanhã às 14h..." disabled={carregando} />
            <button type="submit" disabled={!mensagem.trim() || carregando}><i className="bi bi-send" /> Enviar</button>
          </form>
        </section>

        <aside className="agro-ai-help">
          <h2>Experimente perguntar</h2>
          {EXEMPLOS.map((t) => <button type="button" key={t} onClick={() => enviar(t)} disabled={carregando}>{t}</button>)}
          <p>Para agendar, informe uma <b>ordem de serviço aberta</b> e um dia e horário futuros. A assistente não cria OS automaticamente.</p>
          <p>Confira em <Link to="/ordens-servico">Ordens de serviço</Link> e <Link to="/calendario">Calendário</Link>.</p>
          <p className="agro-ai-disclaimer">Respostas técnicas são orientativas. Consulte o manual do fabricante e profissionais capacitados.</p>
        </aside>
      </div>
    </section>
  );
}
