import re
import os
from typing import Set, List
from src.database import add_known_words, get_known_words
from src.anki_client import check_connection, get_all_notes_from_deck

def clean_html_and_sound(text: str) -> str:
    """Remove tags HTML e marcações de áudio [sound:...]."""
    text = re.sub(r'\[sound:[^\]]+\]', '', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    return text

def extract_words_from_text(raw_text: str) -> Set[str]:
    """Extrai todas as palavras em inglês válidas a partir de um texto limpo."""
    cleaned = clean_html_and_sound(raw_text)
    # Seleciona apenas palavras com letras de a-z com 2 ou mais caracteres
    words = re.findall(r'\b[a-zA-Z]{2,}\b', cleaned.lower())
    return set(words)

def extract_vocabulary_from_anki_deck(deck_name: str = "Inglês") -> int:
    """Puxa todas as notas do baralho diretamente do Anki Desktop via AnkiConnect."""
    if not check_connection():
        print("❌ Anki Desktop não está acessível no momento.")
        return 0

    print(f"🔍 buscando notas do baralho '{deck_name}' no Anki...")
    notes = get_all_notes_from_deck(deck_name)
    all_words = set()

    for note in notes:
        fields = note.get("fields", {})
        for field_info in fields.values():
            val = field_info.get("value", "")
            all_words.update(extract_words_from_text(val))

    added_count = add_known_words(list(all_words))
    print(f"✅ Extração concluída! {len(all_words)} palavras únicas encontradas. {added_count} novas palavras adicionadas ao banco.")
    return added_count

def extract_vocabulary_from_file(file_path: str) -> int:
    """Extrai palavras conhecidas a partir de um arquivo de texto exportado (.txt)."""
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return 0

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    words = extract_words_from_text(content)
    added_count = add_known_words(list(words))
    print(f"✅ Extração do arquivo concluída! {len(words)} palavras encontradas. {added_count} novas palavras adicionadas ao banco.")
    return added_count

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extract_vocabulary_from_file(sys.argv[1])
    else:
        extract_vocabulary_from_anki_deck()
