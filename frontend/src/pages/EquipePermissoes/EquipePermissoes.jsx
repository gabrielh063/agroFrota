import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../../api/api";
import { useAuth } from "../../contexts/AuthContext";
import { nomePerfil } from "../../utils/perfilLabels";
import "./EquipePermissoes.css";

function EquipePermissoes() {
    const { permissoes = [], usuario } = useAuth();
    const podeCriar = permissoes.includes("USUARIO_CRIAR");
    const podeEditar = permissoes.includes("USUARIO_EDITAR");
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
    const [form, setForm] = useState({ nome: "", username: "", senha: "", perfil_id: "" });

    const carregar = useCallback(async () => {
        try {
            const [usuariosResponse, perfisResponse] = await Promise.all([
                api.get("/api/usuarios/", { params: { apenas_ativos: true } }),
                podeVerPerfis ? api.get("/api/perfis/") : Promise.resolve({ data: { data: [] } }),
            ]);
            const perfisList = perfisResponse.data.data || [];
            setErro("");
            setUsuarios(usuariosResponse.data.data || []);
            setPerfis(perfisList);

            if (podeVerPermissoes) {
                const permissionResults = await Promise.all(perfisList.map(async (profile) => {
                    const result = await api.get(`/api/perfis/${profile.id}/permissoes`);
                    return [profile.id, result.data.data || []];
                }));
                setPermissoesPorPerfil(Object.fromEntries(permissionResults));
            } else if (perfilAtualId) {
                setPermissoesPorPerfil({ [perfilAtualId]: permissoes.map((codigo) => ({ codigo })) });
            }
        } catch (requestError) {
            setErro(requestError.response?.data?.message || "Não foi possível carregar a equipe e os perfis permitidos para sua conta.");
            setUsuarios([]);
        }
    }, [podeVerPerfis, podeVerPermissoes, perfilAtualId, permissoes]);

    useEffect(() => { carregar(); }, [carregar]);

    const carregando = usuarios === null;
    const perfisAtivos = useMemo(() => perfis.filter((profile) => profile.ativo), [perfis]);
    const limparForm = () => {
        setEditando(null);
        setForm({ nome: "", username: "", senha: "", perfil_id: "" });
    };

    function editarUsuario(user) {
        setEditando(user);
        setForm({ nome: user.nome, username: user.username, senha: "", perfil_id: String(user.perfil_id) });
        setMensagem("");
        setErro("");
    }

    async function salvar(event) {
        event.preventDefault();
        setSalvando(true);
        setErro("");
        setMensagem("");
        const payload = {
            nome: form.nome.trim(),
            username: form.username.trim(),
            perfil_id: Number(form.perfil_id),
        };
        if (!editando) payload.senha = form.senha;
        try {
            if (editando) {
                await api.put(`/api/usuarios/${editando.id}`, payload);
                setMensagem("Usuário atualizado.");
            } else {
                await api.post("/api/usuarios/", payload);
                setMensagem("Usuário criado.");
            }
            limparForm();
            await carregar();
        } catch (requestError) {
            setErro(requestError.response?.data?.message || "A operação foi recusada. Confira as permissões e os dados informados.");
        } finally {
            setSalvando(false);
        }
    }

    return (
        <div className="team-page">
            <header className="team-header">
                <span className="team-eyebrow"><i className="bi bi-shield-check" /> ADMINISTRAÇÃO</span>
                <h1>Equipe e Permissões</h1>
                <p>Consulte os usuários do tenant, seus perfis e as permissões efetivas definidas pela matriz de acesso.</p>
                <span className="team-current-role">Seu perfil: <strong>{usuario?.perfil_nome || "Perfil autenticado"}</strong></span>
            </header>

            {mensagem && <div className="team-notice team-success" role="status">{mensagem}</div>}
            {erro && <div className="team-notice team-error" role="alert">{erro}</div>}

            {(podeCriar || (editando && podeEditar)) && (
                <section className="team-form-card" aria-labelledby="team-form-heading">
                    <div className="team-section-heading">
                        <div><h2 id="team-form-heading">{editando ? "Editar usuário" : "Adicionar usuário"}</h2><p>O servidor confere sua autorização e o escopo do perfil selecionado.</p></div>
                        {editando && <button type="button" className="team-secondary" onClick={limparForm}>Cancelar edição</button>}
                    </div>
                    <form className="team-form" onSubmit={salvar}>
                        <label>Nome<input required maxLength={150} value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} /></label>
                        <label>Usuário<input required maxLength={80} autoComplete="off" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label>
                        {!editando && <label>Senha temporária<input required minLength={6} maxLength={128} type="password" autoComplete="new-password" value={form.senha} onChange={(event) => setForm({ ...form, senha: event.target.value })} /><small>Compartilhe a senha por um canal privado.</small></label>}
                        <label>Perfil<select required value={form.perfil_id} onChange={(event) => setForm({ ...form, perfil_id: event.target.value })}><option value="">Selecione um perfil</option>{perfisAtivos.map((profile) => <option key={profile.id} value={profile.id}>{profile.nome}</option>)}</select></label>
                        <div className="team-form-actions"><button type="submit" disabled={salvando || !form.perfil_id}>{salvando ? "Salvando…" : editando ? "Salvar alterações" : "Criar usuário"}</button></div>
                    </form>
                </section>
            )}

            <section className="team-list-card" aria-labelledby="team-list-heading">
                        <div className="team-section-heading"><div><h2 id="team-list-heading">Usuários ativos</h2><p>{carregando ? "Carregando…" : `${usuarios.length} usuários no tenant`}</p></div><button type="button" className="team-secondary" onClick={() => { setUsuarios(null); carregar(); }} disabled={carregando}>Atualizar</button></div>
                {carregando ? <div className="team-empty" role="status">Carregando equipe…</div> : usuarios.length === 0 ? <div className="team-empty">Nenhum usuário ativo encontrado.</div> : (
                    <div className="team-table-wrap"><table className="team-table"><thead><tr><th scope="col">Pessoa</th><th scope="col">Perfil</th><th scope="col">Permissões efetivas</th>{podeEditar && <th scope="col">Ações</th>}</tr></thead>
                        <tbody>{usuarios.map((user) => {
                            const profile = perfis.find((item) => item.id === user.perfil_id);
                            const permissions = permissoesPorPerfil[user.perfil_id];
                            return <tr key={user.id}>
                                <td><strong>{user.nome}</strong><span>@{user.username}</span></td>
                                <td><span className="team-role-chip">{nomePerfil(profile?.nome || (user.id === usuario?.id ? usuario.perfil_nome : "Perfil sem acesso de consulta"))}</span></td>
                                <td>{permissions ? <details className="team-permissions"><summary>{permissions.length} permissões</summary><ul>{permissions.map((permission) => <li key={permission.codigo}>{permission.codigo}</li>)}</ul></details> : <span className="team-muted">Consulta restrita pela sua permissão atual.</span>}</td>
                                {podeEditar && <td><button type="button" className="team-edit" onClick={() => editarUsuario(user)} aria-label={`Editar ${user.nome}`}>Editar</button></td>}
                            </tr>;
                        })}</tbody>
                    </table></div>
                )}
            </section>
        </div>
    );
}

export default EquipePermissoes;
