import sqlite3
import os
from datetime import datetime
from typing import Set, List, Optional, Tuple, Dict, Any

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "known_words.db")

def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Inicializa as tabelas do banco de dados SQLite."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS known_words (
                word TEXT PRIMARY KEY COLLATE NOCASE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS known_phrases (
                phrase TEXT PRIMARY KEY COLLATE NOCASE,
                meaning TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS card_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_word TEXT NOT NULL,
                sentence TEXT NOT NULL,
                meaning TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_known_word(word: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Adiciona uma palavra individual ao banco de conhecidas."""
    w_clean = word.lower().strip()
    if not w_clean:
        return False
    
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO known_words (word, added_at) VALUES (?, ?)",
            (w_clean, datetime.now())
        )
        affected = cursor.rowcount > 0
        conn.commit()
        return affected

def add_known_words(words: List[str], db_path: str = DEFAULT_DB_PATH) -> int:
    """Adiciona uma lista de palavras conhecidas em lote."""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        count = 0
        for w in words:
            w_clean = w.lower().strip()
            if w_clean:
                cursor.execute(
                    "INSERT OR IGNORE INTO known_words (word, added_at) VALUES (?, ?)",
                    (w_clean, datetime.now())
                )
                if cursor.rowcount > 0:
                    count += 1
        conn.commit()
        return count

def get_known_words(db_path: str = DEFAULT_DB_PATH) -> Set[str]:
    """Retorna o conjunto de todas as palavras conhecidas."""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT word FROM known_words")
        words = {row[0].lower() for row in cursor.fetchall()}
        return words

def is_word_known(word: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Verifica se uma palavra já consta como conhecida."""
    w_clean = word.lower().strip()
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM known_words WHERE word = ?", (w_clean,))
        return cursor.fetchone() is not None

def record_card(target_word: str, sentence: str, meaning: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """Registra o card gerado no histórico."""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO card_history (target_word, sentence, meaning, created_at) VALUES (?, ?, ?, ?)",
            (target_word.lower().strip(), sentence, meaning, datetime.now())
        )
        conn.commit()

def get_recent_cards(limit: int = 100, db_path: str = DEFAULT_DB_PATH) -> List[Tuple[int, str, str, str, str]]:
    """Retorna a lista de cards recentemente gerados no histórico (id, palavra, frase/frente, significado/verso, data)."""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, target_word, sentence, meaning, strftime('%d/%m/%Y %H:%M', created_at) FROM card_history ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()
