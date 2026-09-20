"""Biblioteca local de materiais para dar contexto aos próximos estudos."""

import hashlib
import os
import re
import sqlite3
from datetime import datetime
from typing import List

from src.database import DEFAULT_DB_PATH


def _connect():
    os.makedirs(os.path.dirname(DEFAULT_DB_PATH), exist_ok=True)
    return sqlite3.connect(DEFAULT_DB_PATH)


def init_context_library() -> None:
    with _connect() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS study_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                source_type TEXT NOT NULL,
                content TEXT NOT NULL,
                added_at TIMESTAMP NOT NULL
            )"""
        )


def save_context(title: str, content: str, source_type: str = "material") -> bool:
    """Salva o material uma vez; retorna se ele foi incluído nesta chamada."""
    normalized = re.sub(r"\s+", " ", content).strip()
    if len(normalized) < 80:
        return False
    init_context_library()
    fingerprint = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    with _connect() as connection:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO study_contexts (fingerprint, title, source_type, content, added_at) VALUES (?, ?, ?, ?, ?)",
            (fingerprint, title.strip() or "Material sem título", source_type, content.strip(), datetime.now()),
        )
        return cursor.rowcount > 0


def _terms(text: str) -> set[str]:
    ignored = {"para", "como", "uma", "com", "por", "que", "dos", "das", "não", "sobre", "the", "and", "this", "from"}
    return {word.lower() for word in re.findall(r"[\wÀ-ÿ]{4,}", text) if word.lower() not in ignored}


def find_relevant_context(query: str, max_chars: int = 9000) -> str:
    """Recupera trechos locais por sobreposição de termos, sem enviar a biblioteca inteira."""
    init_context_library()
    query_terms = _terms(query)
    if not query_terms:
        return ""
    with _connect() as connection:
        rows = connection.execute("SELECT title, content FROM study_contexts ORDER BY added_at DESC").fetchall()

    ranked = []
    for title, content in rows:
        chunks = [content[index:index + 1800] for index in range(0, len(content), 1400)]
        for chunk in chunks:
            score = len(query_terms & _terms(chunk))
            if score:
                ranked.append((score, title, chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)

    selected, used = [], 0
    for _, title, chunk in ranked[:8]:
        item = f"[Biblioteca: {title}]\n{chunk.strip()}"
        if used + len(item) > max_chars:
            break
        selected.append(item)
        used += len(item)
    return "\n\n---\n\n".join(selected)


def context_count() -> int:
    init_context_library()
    with _connect() as connection:
        return int(connection.execute("SELECT COUNT(*) FROM study_contexts").fetchone()[0])
