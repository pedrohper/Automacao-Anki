import os
import re
import sys
import tempfile
from typing import List
from dotenv import load_dotenv

from src.database import (
    init_db,
    get_known_words,
    add_known_word,
    is_word_known,
    record_card
)
from src.llm_service import generate_card_content
from src.tts_service import generate_audio_file, get_audio_filename
from src.anki_client import (
    check_connection,
    store_media_file,
    add_note,
    get_deck_names
)
from src.extractor import (
    extract_vocabulary_from_anki_deck,
    extract_vocabulary_from_file
)

load_dotenv()

DECK_NAME = os.getenv("ANKI_DECK_NAME", "Inglês")
MODEL_NAME = os.getenv("ANKI_MODEL_NAME", "Basic")

def format_card_html(sentence: str, target_word: str, meaning: str, explanation: str) -> tuple[str, str]:
    """Formata o HTML para a Frente e Verso do card."""
    pattern = re.compile(re.escape(target_word), re.IGNORECASE)
    
    def replace_func(match):
        matched_text = match.group(0)
        return f"<b>{matched_text}</b>"
        
    front_sentence = pattern.sub(replace_func, sentence)

    back_html = f"<b>{meaning}</b>"
    if explanation and explanation.strip():
        back_html += f"<br><small style='color: #666;'>{explanation.strip()}</small>"

    return front_sentence, back_html

def process_single_word(word: str, deck_name: str = DECK_NAME, model_name: str = MODEL_NAME, multi_meaning: bool = True) -> bool:
    """Fluxo completo para gerar e enviar flashcards de uma palavra (com suporte a múltiplos significados)."""
    word_clean = word.lower().strip()
    if not word_clean:
        return False

    print(f"\n==========================================")
    print(f"🎯 Processando palavra: '{word_clean}'")
    print(f"==========================================")

    known_words = get_known_words()
    
    print("🤖 Solicitando geração de frases i+1 para a API do DeepSeek...")
    try:
        cards_data = generate_card_content(word_clean, known_words, multi_meaning=multi_meaning)
    except Exception as e:
        print(f"❌ Erro na API do DeepSeek: {e}")
        return False

    if not cards_data:
        print("❌ Nenhum card foi retornado.")
        return False

    print(f"💡 {len(cards_data)} significado(s) identificado(s) para '{word_clean}':")

    created_any = False
    for idx, data in enumerate(cards_data, 1):
        sentence = data.get("sentence", "")
        target = data.get("target_word", word_clean)
        meaning = data.get("meaning", "")
        explanation = data.get("explanation", "")

        print(f"\n  [Sentido {idx}/{len(cards_data)}]")
        print(f"   • Frase: \"{sentence}\"")
        print(f"   • Significado: {meaning}")

        front_text, back_html = format_card_html(sentence, target, meaning, explanation)
        
        # Nome único do áudio se houver múltiplos significados
        audio_suffix = f"_{idx}" if len(cards_data) > 1 else ""
        audio_filename = get_audio_filename(f"{target}{audio_suffix}")
        temp_dir = tempfile.gettempdir()
        temp_audio_path = os.path.join(temp_dir, audio_filename)

        try:
            generate_audio_file(sentence, temp_audio_path)
            store_media_file(audio_filename, temp_audio_path)
            
            front_with_audio = f"{front_text} [sound:{audio_filename}]"
            
            note_id = add_note(
                front_content=front_with_audio,
                back_content=back_html,
                deck_name=deck_name,
                model_name=model_name,
                tags=["Inglês", "Automação", "VibeCode"]
            )
            print(f"   ✅ Card {idx} enviado ao Anki! (ID: {note_id})")
            record_card(target, sentence, meaning)
            created_any = True
        except Exception as e:
            print(f"   ❌ Erro ao enviar card {idx}: {e}")
        finally:
            if os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                except Exception:
                    pass

    add_known_word(word_clean)
    return created_any

if __name__ == "__main__":
    init_db()
    if len(sys.argv) > 1:
        process_single_word(sys.argv[1])
    else:
        print("Uso: python main.py <palavra>")
