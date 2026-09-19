import os
import zlib
import genanki
from typing import List, Dict, Any, Optional

# Modelo genérico do genanki para Front e Back com suporte a HTML
BASIC_MODEL_ID = 1607392319
basic_model = genanki.Model(
    BASIC_MODEL_ID,
    'VibeCode Model',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Front}}',
            'afmt': '{{Front}}<hr id="answer">{{Back}}',
        },
    ],
    css="""
    .card {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 16px;
        text-align: center;
        color: #111;
        background-color: #fcfcfc;
    }
    b { color: #1e66f5; }
    code { font-family: monospace; }
    """
)

def export_cards_to_apkg(deck_name: str, cards: List[Dict[str, str]], media_files: Optional[List[str]] = None, output_path: str = "baralho.apkg") -> str:
    """
    Exporta uma lista de cards (cada um com 'front' e 'back') diretamente em um arquivo .apkg oficial do Anki.
    Gera um ID determinístico baseado no nome do baralho para atualizar decks existentes sem duplicar.
    """
    deck_id = (zlib.crc32(deck_name.encode("utf-8")) & 0x7FFFFFFF) or 1607392320
    deck = genanki.Deck(deck_id, deck_name)

    for c in cards:
        front = c.get("front", "")
        back = c.get("back", "")
        if front and back:
            note = genanki.Note(
                model=basic_model,
                fields=[front, back]
            )
            deck.add_note(note)

    package = genanki.Package(deck)
    if media_files:
        package.media_files = [f for f in media_files if os.path.exists(f)]

    package.write_to_file(output_path)
    return output_path

if __name__ == "__main__":
    test_cards = [
        {"front": "What is throughput?", "back": "<b>throughput</b> = vazão de processamento"},
        {"front": "O que é deadlock?", "back": "<b>deadlock</b> = impasse em sistemas operacionais"}
    ]
    out = export_cards_to_apkg("Teste::Exemplo", test_cards, output_path="data/teste.apkg")
    print(f"Baralho .apkg exportado com sucesso em: {out}")
    if os.path.exists(out):
        os.remove(out)
