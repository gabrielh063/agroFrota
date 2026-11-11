"""Indexação local e recuperação limitada ao Vault Markdown do AgroFrota."""
import hashlib
import os
import re
import sqlite3
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[1] / "knowledge"
INDEX_PATH = Path(os.getenv(
    "AGRO_AI_INDEX_PATH",
    str(Path(__file__).resolve().parents[1] / "instance" / "vault.sqlite3"),
)).expanduser().resolve()
MAX_FILES = 200
MAX_CHARS_PER_SECTION = 2400
MAX_CONTEXT_CHARS = 7200
_STOPWORDS = {
    "que", "para", "com", "uma", "uns", "das", "dos", "por", "sobre", "qual", "quais",
    "como", "devo", "antes", "depois", "estao", "está", "estão", "de", "da", "do", "e", "o", "a", "um", "em",
}


def _sections(markdown: str):
    heading = "Introdução"
    lines = []
    for line in markdown.splitlines():
        if line.startswith("#"):
            if lines and "\n".join(lines).strip():
                yield heading, "\n".join(lines).strip()
            heading = line.lstrip("# ").strip()[:180] or "Seção"
            lines = []
        else:
            lines.append(line)
    if lines and "\n".join(lines).strip():
        yield heading, "\n".join(lines).strip()


def _connect():
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(INDEX_PATH, timeout=5)
    db.execute("PRAGMA journal_mode=WAL")
    try:
        db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(path UNINDEXED, section UNINDEXED, body, tokenize='unicode61 remove_diacritics 2')")
        db.execute("CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, sha256 TEXT NOT NULL)")
    except sqlite3.OperationalError as exc:
        db.close()
        raise RuntimeError("Esta instalação do SQLite não oferece FTS5.") from exc
    return db


def indexar_vault():
    """Atualiza apenas arquivos Markdown dentro da raiz autorizada."""
    root = VAULT_ROOT.resolve()
    paths = sorted(root.rglob("*.md")) if root.is_dir() else []
    paths = [p for p in paths if p.is_file() and p.resolve().is_relative_to(root)][:MAX_FILES]
    db = _connect()
    try:
        existentes = {row[0]: row[1] for row in db.execute("SELECT path, sha256 FROM files")}
        atuais = set()
        for path in paths:
            relativo = path.resolve().relative_to(root).as_posix()
            atuais.add(relativo)
            texto = path.read_text(encoding="utf-8")
            digest = hashlib.sha256(texto.encode("utf-8")).hexdigest()
            if existentes.get(relativo) == digest:
                continue
            db.execute("DELETE FROM chunks WHERE path = ?", (relativo,))
            db.execute("DELETE FROM files WHERE path = ?", (relativo,))
            for titulo, conteudo in _sections(texto):
                # Seções longas são divididas em janelas previsíveis e limitadas.
                for inicio in range(0, len(conteudo), MAX_CHARS_PER_SECTION):
                    corpo = conteudo[inicio:inicio + MAX_CHARS_PER_SECTION]
                    db.execute("INSERT INTO chunks(path, section, body) VALUES (?, ?, ?)",
                               (relativo, titulo, corpo))
            db.execute("INSERT INTO files(path, sha256) VALUES (?, ?)", (relativo, digest))
        for obsoleto in set(existentes) - atuais:
            db.execute("DELETE FROM chunks WHERE path = ?", (obsoleto,))
            db.execute("DELETE FROM files WHERE path = ?", (obsoleto,))
        db.commit()
        return len(paths)
    finally:
        db.close()


def recuperar(pergunta: str, limite: int = 5):
    indexar_vault()
    tokens = [token for token in re.findall(r"[\wÀ-ÿ]{3,}", pergunta.lower())
              if token not in _STOPWORDS][:12]
    if not tokens:
        return []
    # FTS query is composed only from extracted alphanumeric tokens.
    query = " OR ".join('"' + token.replace('"', '') + '"' for token in tokens)
    db = _connect()
    try:
        rows = db.execute(
            "SELECT path, section, snippet(chunks, 2, '[', ']', ' … ', 18), rank "
            "FROM chunks WHERE chunks MATCH ? ORDER BY rank LIMIT ?",
            (query, max(1, min(limite, 8))),
        ).fetchall()
    finally:
        db.close()
    saida, tamanho = [], 0
    for path, section, snippet, _rank in rows:
        item = {"arquivo": path, "secao": section, "trecho": snippet}
        serializado = f"[{path} — {section}]\n{snippet}"
        if tamanho + len(serializado) > MAX_CONTEXT_CHARS:
            break
        saida.append(item)
        tamanho += len(serializado)
    return saida


def contexto_fontes(fontes):
    return "\n\n".join(f"[{f['arquivo']} — {f['secao']}]\n{f['trecho']}" for f in fontes)
