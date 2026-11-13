import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../../api/api";
import { useAuth } from "../../contexts/AuthContext";
import { nomePerfil } from "../../utils/perfilLabels";
import "./EquipePermissoes.css";

function EquipePermissoes() {
    const { permissoes = [], usuario } = useAuth();
    const podeCriar = permissoes.includes("USUARIO_CRIAR");
    const podeEditar = permissoes.includes("USUARIO_EDITAR");
    const podeDesativar = permissoes.includes("USUARIO_DESATIVAR");
    const podeVerPerfis = permissoes.includes("PERFIL_VISUALIZAR");
    const podeVerPermissoes = permissoes.includes("PERFIL_PERMISSAO_GERENCIAR");
    const perfilAtualId = usuario?.perfil_id;
    const [usuarios, setUsuarios] = useState(null);
    const [perfis, setPerfis] = useState([]);
    const [permissoesPorPerfil, setPermissoesPorPerfil] = useState({});
    const [salvando, setSalvando] = useState(false);
    const [erro, setErro] = useState("");
    const [mensagem, setMensagem] = useState("");
    const [editando, setEditando] = useState(null);
    const [busca, setBusca] = useState("");
    const [filtroPerfil, setFiltroPerfil] = useState("todos");
    const [filtroSituacao, setFiltroSituacao] = useState("ativos");
    const [form, setForm] = useState({ nome: "", username: "", email: "", senha: "", perfil_id: "" });

    const carregar = useCallback(async () => {
        try {
            const [usuariosResponse, perfisResponse] = await Promise.all([
                api.get("/api/usuarios/", { params: { apenas_ativos: false } }),
                podeVerPerfis ? api.get("/api/perfis/") : Promise.resolve({ data: { data: [] } }),
            ]);
            const perfisList = perfisResponse.data.data || [];
            setErro("");
            setUsuarios(usuariosResponse.data.data || []);
            setPerfis(perfisList);
            if (podeVerPermissoes) {
                const results = await Promise.all(perfisList.map(async (profile) => {
                    const result = await api.get(`/api/perfis/${profile.id}/permissoes`);
                    return [profile.id, result.data.data || []];
                }));
                setPermissoesPorPerfil(Object.fromEntries(results));
            } else if (perfilAtualId) {
                setPermissoesPorPerfil({ [perfilAtualId]: permissoes.map((codigo) => ({ codigo })) });
            }
        } catch (requestError) {
            setErro(requestError.response?.status === 403
                ? "Sua conta pode consultar a equipe, mas não tem autorização para uma das informações solicitadas."
                : requestError.response?.data?.message || "Não foi possível carregar a equipe. Tente novamente.");
            setUsuarios([]);
        }
    }, [podeVerPerfis, podeVerPermissoes, perfilAtualId, permissoes]);

    useEffect(() => { carregar(); }, [carregar]);

    const carregando = usuarios === null;
    const perfisAtivos = useMemo(() => perfis.filter((profile) => profile.ativo), [perfis]);
    const usuariosFiltrados = useMemo(() => (usuarios || []).filter((user) => {
        const termo = busca.trim().toLocaleLowerCase();
        const perfil = perfis.find((item) => item.id === user.perfil_id);
        const correspondeBusca = !termo || `${user.nome} ${user.username}`.toLocaleLowerCase().includes(termo);
        const correspondePerfil = filtroPerfil === "todos" || String(user.perfil_id) === filtroPerfil;
        const correspondeSituacao = filtroSituacao === "todos" || (filtroSituacao === "ativos" ? user.ativo : !user.ativo);
        return correspondeBusca && correspondePerfil && correspondeSituacao && (filtroPerfil === "todos" || Boolean(perfil));
    }), [usuarios, busca, filtroPerfil, filtroSituacao, perfis]);

    const limparForm = () => {
        setEditando(null);
        setForm({ nome: "", username: "", email: "", senha: "", perfil_id: "" });
    };

    function editarUsuario(user) {
        setEditando(user);
        setForm({ nome: user.nome, username: user.username, email: user.email || "", senha: "", perfil_id: String(user.perfil_id) });
        setMensagem("");
        setErro("");
    }

    async function salvar(event) {
        event.preventDefault();
        setSalvando(true);
        setErro("");
        setMensagem("");
        const payload = { nome: form.nome.trim(), username: form.username.trim(), email: form.email.trim() || null, perfil_id: Number(form.perfil_id) };
        if (!editando) payload.senha = form.senha;
        try {
            if (editando) {
                await api.put(`/api/usuarios/${editando.id}`, payload);
                setMensagem("Usuário atualizado. As permissões serão verificadas novamente no próximo acesso.");
            } else {
                await api.post("/api/usuarios/", payload);
                setMensagem("Usuário criado.");
            }
            limparForm();
            await carregar();
        } catch (requestError) {
            setErro(requestError.response?.status === 403
                ? "Ação bloqueada: seu perfil não pode executar esta alteração."
                : requestError.response?.data?.message || "A operação foi recusada. Confira as permissões e os dados informados.");
        } finally { setSalvando(false); }
    }

    async function alterarSituacao(user) {
        const ativar = !user.ativo;
        const acao = ativar ? "ativar" : "desativar";
        if (!window.confirm(`Confirma ${acao} a conta de ${user.nome}?`)) return;
        setSalvando(true);
        setErro("");
        setMensagem("");
        try {
            await api.patch(`/api/usuarios/${user.id}/${ativar ? "ativar" : "desativar"}`);
            setMensagem(`Conta de ${user.nome} ${ativar ? "ativada" : "desativada"}.`);
            await carregar();
        } catch (requestError) {
            setErro(requestError.response?.status === 403
                ? "Ação bloqueada: seu perfil não pode alterar esta conta."
                : requestError.response?.data?.message || "Não foi possível alterar a situação da conta.");
        } finally { setSalvando(false); }
    }

    return (
        <div className="team-page">
            <header className="team-header">
                <span className="team-eyebrow"><i className="bi bi-shield-check" /> ADMINISTRAÇÃO</span>
                <h1>Equipe e Permissões</h1>
                <p>Consulte contas, perfis e permissões efetivas definidas pela matriz de acesso.</p>
                <span className="team-current-role">Seu perfil: <strong>{usuario?.perfil_nome || "Perfil autenticado"}</strong></span>
            </header>

            {mensagem && <div className="team-notice team-success" role="status">{mensagem}</div>}
            {erro && <div className="team-notice team-error" role="alert">{erro}<button type="button" onClick={() => { setUsuarios(null); carregar(); }}>Tentar novamente</button></div>}
            {!podeCriar && !podeEditar && !podeDesativar && <div className="team-notice" role="status">Acesso somente para consulta: seu perfil não pode criar, editar ou ativar contas.</div>}

            {(podeCriar || (editando && podeEditar)) && (
                <section className="team-form-card" aria-labelledby="team-form-heading">
                    <div className="team-section-heading">
                        <div><h2 id="team-form-heading">{editando ? "Editar usuário" : "Adicionar usuário"}</h2><p>O servidor confere sua autorização e o escopo do perfil selecionado.</p></div>
                        {editando && <button type="button" className="team-secondary" onClick={limparForm}>Cancelar edição</button>}
                    </div>
                    <form className="team-form" onSubmit={salvar}>
                        <label>Nome<input required maxLength={150} value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} /></label>
                        <label>Usuário<input required maxLength={80} autoComplete="off" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label>
                        <label>E-mail (opcional)<input type="email" maxLength={255} autoComplete="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label>
                        {!editando && <label>Senha temporária<input required minLength={6} maxLength={128} type="password" autoComplete="new-password" value={form.senha} onChange={(event) => setForm({ ...form, senha: event.target.value })} /><small>Compartilhe a senha por um canal privado.</small></label>}
                        <label>Perfil<select required value={form.perfil_id} onChange={(event) => setForm({ ...form, perfil_id: event.target.value })}><option value="">Selecione um perfil</option>{perfisAtivos.map((profile) => <option key={profile.id} value={profile.id}>{nomePerfil(profile.nome)}</option>)}</select></label>
                        <div className="team-form-actions"><button type="submit" disabled={salvando || !form.perfil_id}>{salvando ? "Salvando…" : editando ? "Salvar alterações" : "Criar usuário"}</button></div>
                    </form>
                </section>
            )}

            <section className="team-list-card" aria-labelledby="team-list-heading">
                <div className="team-section-heading"><div><h2 id="team-list-heading">Contas da empresa</h2><p>{carregando ? "Carregando…" : `${usuariosFiltrados.length} de ${usuarios.length} contas`}</p></div><button type="button" className="team-secondary" onClick={() => { setUsuarios(null); carregar(); }} disabled={carregando}>Atualizar</button></div>
                <div className="team-filters">
                    <label>Buscar por nome ou usuário<input type="search" value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Nome ou username" /></label>
                    <label>Perfil<select value={filtroPerfil} onChange={(event) => setFiltroPerfil(event.target.value)}><option value="todos">Todos os perfis</option>{perfis.map((profile) => <option key={profile.id} value={String(profile.id)}>{nomePerfil(profile.nome)}</option>)}</select></label>
                    <label>Situação<select value={filtroSituacao} onChange={(event) => setFiltroSituacao(event.target.value)}><option value="ativos">Ativos</option><option value="inativos">Inativos</option><option value="todos">Todos</option></select></label>
                </div>
                {carregando ? <div className="team-empty" role="status">Carregando equipe…</div> : usuariosFiltrados.length === 0 ? <div className="team-empty">Nenhuma conta corresponde aos filtros.</div> : (
                    <div className="team-table-wrap"><table className="team-table"><thead><tr><th scope="col">Pessoa</th><th scope="col">Perfil e situação</th><th scope="col">Permissões efetivas</th>{(podeEditar || podeDesativar) && <th scope="col">Ações</th>}</tr></thead>
                        <tbody>{usuariosFiltrados.map((user) => {
                            const profile = perfis.find((item) => item.id === user.perfil_id);
                            const permissions = permissoesPorPerfil[user.perfil_id];
                            return <tr key={user.id}>
                                <td><strong>{user.nome}</strong><span>@{user.username}</span>{user.email && <span>{user.email}</span>}</td>
                                <td><span className="team-role-chip">{nomePerfil(profile?.nome || (user.id === usuario?.id ? usuario.perfil_nome : "Perfil sem acesso de consulta"))}</span><span className={`team-status ${user.ativo ? "is-active" : "is-inactive"}`}>{user.ativo ? "Ativo" : "Inativo"}</span></td>
                                <td>{permissions ? <details className="team-permissions"><summary>{permissions.length} permissões</summary><ul>{permissions.map((permission) => <li key={permission.codigo}>{permission.codigo}</li>)}</ul></details> : <span className="team-muted">Consulta restrita pela sua permissão atual.</span>}</td>
                                {(podeEditar || podeDesativar) && <td className="team-actions">{podeEditar && <button type="button" className="team-edit" onClick={() => editarUsuario(user)} aria-label={`Editar ${user.nome}`}>Editar</button>}{podeDesativar && <button type="button" className="team-secondary" disabled={salvando} onClick={() => alterarSituacao(user)}>{user.ativo ? "Desativar" : "Ativar"}</button>}</td>}
                            </tr>;
                        })}</tbody>
                    </table></div>
                )}
            </section>
        </div>
    );
}

export default EquipePermissoes;
