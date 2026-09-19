"""
Script utilitário para gerar os baralhos completos em arquivos .apkg oficial do Anki
na pasta `data/`:
- `data/Cargill_Flashcards.apkg`
- `data/ESAMC_Sistemas_Informacao.apkg`
- `data/SENAI_Aprendizagem_Completo.apkg`
"""

import os
import sys

# Adicionar raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preset_data import CARGILL_CARDS, ESAMC_CARDS, ESAMC_TI_CARDS, ESAMC_ADM_CARDS, get_all_senai_cards_flat
from src.apkg_service import export_cards_to_apkg

def generate_all():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)

    # 1. Cargill
    cargill_apkg = os.path.join(data_dir, "Cargill_Flashcards.apkg")
    export_cards_to_apkg("Cargill::Geral & EHS", CARGILL_CARDS, output_path=cargill_apkg)
    print(f"[OK] Baralho da Cargill gerado: {cargill_apkg} ({len(CARGILL_CARDS)} cards)")

    # 2. ESAMC (Organizado em 2 Eixos)
    esamc_apkg = os.path.join(data_dir, "ESAMC_Sistemas_Informacao.apkg")
    export_cards_to_apkg("ESAMC::TI e Gestão", ESAMC_CARDS, output_path=esamc_apkg)
    print(f"[OK] Baralho da ESAMC gerado: {esamc_apkg} ({len(ESAMC_CARDS)} cards - Eixo TI: {len(ESAMC_TI_CARDS)}, Eixo ADM: {len(ESAMC_ADM_CARDS)})")

    # 3. SENAI Completo
    senai_flat = get_all_senai_cards_flat()
    senai_apkg = os.path.join(data_dir, "SENAI_Aprendizagem_Completo.apkg")
    export_cards_to_apkg("SENAI::Aprendizagem Administrativa Completo", senai_flat, output_path=senai_apkg)
    print(f"[OK] Baralho do SENAI Completo gerado: {senai_apkg} ({len(senai_flat)} cards)")

if __name__ == "__main__":
    generate_all()
