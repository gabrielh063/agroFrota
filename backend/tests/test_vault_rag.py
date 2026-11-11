from services import vault_rag


def test_indexa_e_recupera_com_arquivo_e_secao(monkeypatch, tmp_path):
    raiz = tmp_path / "knowledge"
    (raiz / "tratores").mkdir(parents=True)
    (raiz / "tratores" / "operacao.md").write_text(
        "# Inspeção pré-operacional\n\nConfira visualmente vazamentos e proteções antes de operar.",
        encoding="utf-8",
    )
    monkeypatch.setattr(vault_rag, "VAULT_ROOT", raiz)
    monkeypatch.setattr(vault_rag, "INDEX_PATH", tmp_path / "private" / "index.sqlite3")

    assert vault_rag.indexar_vault() == 1
    fontes = vault_rag.recuperar("o que verificar antes de operar o trator?")
    assert fontes
    assert fontes[0]["arquivo"] == "tratores/operacao.md"
    assert fontes[0]["secao"] == "Inspeção pré-operacional"


def test_reindexacao_incremental_e_remocao_obsoleta(monkeypatch, tmp_path):
    raiz = tmp_path / "knowledge"
    raiz.mkdir()
    doc = raiz / "manutencao.md"
    doc.write_text("# Preventiva\n\nUse o manual do equipamento.", encoding="utf-8")
    monkeypatch.setattr(vault_rag, "VAULT_ROOT", raiz)
    monkeypatch.setattr(vault_rag, "INDEX_PATH", tmp_path / "private" / "index.sqlite3")

    vault_rag.indexar_vault()
    db = vault_rag._connect()
    antes = db.execute("SELECT rowid FROM chunks").fetchall()
    db.close()
    vault_rag.indexar_vault()
    db = vault_rag._connect()
    depois = db.execute("SELECT rowid FROM chunks").fetchall()
    db.close()
    assert depois == antes

    doc.write_text("# Preventiva\n\nConsulte o histórico e o manual da máquina.", encoding="utf-8")
    vault_rag.indexar_vault()
    assert "histórico" in " ".join(f["trecho"] for f in vault_rag.recuperar("histórico da máquina"))
    doc.unlink()
    vault_rag.indexar_vault()
    assert vault_rag.recuperar("histórico da máquina") == []


def test_nao_indexa_arquivo_fora_do_vault(monkeypatch, tmp_path):
    raiz = tmp_path / "knowledge"
    raiz.mkdir()
    externo = tmp_path / "segredo.md"
    externo.write_text("segredo fora do vault", encoding="utf-8")
    (raiz / "atalho.md").symlink_to(externo)
    monkeypatch.setattr(vault_rag, "VAULT_ROOT", raiz)
    monkeypatch.setattr(vault_rag, "INDEX_PATH", tmp_path / "private" / "index.sqlite3")

    assert vault_rag.indexar_vault() == 0
    assert vault_rag.recuperar("segredo fora do vault") == []


def test_recuperacao_tecnica_nao_traz_procedimento_de_agendamento(monkeypatch, tmp_path):
    raiz = vault_rag.VAULT_ROOT
    monkeypatch.setattr(vault_rag, "INDEX_PATH", tmp_path / "private" / "index.sqlite3")
    monkeypatch.setattr(vault_rag, "VAULT_ROOT", raiz)

    fontes = vault_rag.recuperar("O que devo verificar antes de operar um trator?")
    arquivos = {fonte["arquivo"] for fonte in fontes}
    assert "tratores/operacao-segura.md" in arquivos
    assert "procedimentos/agendamento.md" not in arquivos
