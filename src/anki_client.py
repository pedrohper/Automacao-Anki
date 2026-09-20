import os
import base64
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
ANKI_DECK_NAME = os.getenv("ANKI_DECK_NAME", "Inglês")
ANKI_MODEL_NAME = os.getenv("ANKI_MODEL_NAME", "Basic")

def invoke_anki(action: str, params: Optional[Dict[str, Any]] = None, url: str = ANKI_CONNECT_URL) -> Dict[str, Any]:
    """Helper genérico para chamadas à API REST do AnkiConnect."""
    payload = {
        "action": action,
        "version": 6
    }
    if params:
        payload["params"] = params
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        res_json = response.json()
        if res_json.get("error"):
            raise RuntimeError(f"AnkiConnect retornou erro: {res_json['error']}")
        return res_json
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Não foi possível conectar ao AnkiConnect em {url}. Certifique-se de que o Anki Desktop está aberto. Detalhes: {e}")

def check_connection(url: str = ANKI_CONNECT_URL) -> bool:
    """Verifica se o AnkiConnect está ativo."""
    try:
        res = invoke_anki("version", url=url)
        return res.get("result") is not None
    except Exception:
        return False

def get_deck_names(url: str = ANKI_CONNECT_URL) -> List[str]:
    """Retorna a lista de baralhos existentes no Anki."""
    res = invoke_anki("deckNames", url=url)
    return res.get("result", [])

def get_model_names(url: str = ANKI_CONNECT_URL) -> List[str]:
    """Retorna a lista de modelos de nota existentes no Anki."""
    res = invoke_anki("modelNames", url=url)
    return res.get("result", [])

def resolve_best_model(requested_model: str = ANKI_MODEL_NAME, url: str = ANKI_CONNECT_URL) -> str:
    """Resolve o melhor nome de modelo de nota compatível com a instalação do Anki (ex: 'Basic', 'Básico', etc.)."""
    try:
        available = get_model_names(url=url)
        if requested_model in available:
            return requested_model
        if "Basic" in available:
            return "Basic"
        if "Básico" in available:
            return "Básico"
        for m in available:
            if "básico" in m.lower() or "basic" in m.lower():
                return m
        if available:
            return available[0]
    except Exception:
        pass
    return requested_model

def create_deck(deck_name: str, url: str = ANKI_CONNECT_URL) -> int:
    """Cria um novo baralho ou sub-baralho no Anki se ainda não existir."""
    res = invoke_anki("createDeck", {"deck": deck_name}, url=url)
    return res.get("result")

def get_model_fields(model_name: str, url: str = ANKI_CONNECT_URL) -> List[str]:
    """Retorna a lista de campos do modelo especificado (ex: ['Front', 'Back'] ou ['Frente', 'Verso'])."""
    res = invoke_anki("modelFieldNames", {"modelName": model_name}, url=url)
    return res.get("result", [])

def store_media_file(filename: str, file_path: str, url: str = ANKI_CONNECT_URL) -> str:
    """Envia um arquivo de áudio ou mídia local para a pasta de mídias do Anki."""
    with open(file_path, "rb") as f:
        encoded_data = base64.b64encode(f.read()).decode("utf-8")
    
    params = {
        "filename": filename,
        "data": encoded_data
    }
    res = invoke_anki("storeMediaFile", params, url=url)
    return res.get("result", filename)

def add_note(
    front_content: str,
    back_content: str,
    deck_name: str = ANKI_DECK_NAME,
    model_name: str = ANKI_MODEL_NAME,
    tags: Optional[List[str]] = None,
    url: str = ANKI_CONNECT_URL
) -> int:
    """
    Cria uma nova nota/card no Anki. Garante que o baralho exista e mapeia os campos automaticamente.
    """
    if tags is None:
        tags = ["Automação", "VibeCode"]

    # Garantir que o baralho exista
    try:
        create_deck(deck_name, url=url)
    except Exception:
        pass

    # Resolver modelo real disponível no Anki
    target_model = resolve_best_model(model_name, url=url)

    # Descobrir campos do modelo para garantir compatibilidade
    fields = {}
    try:
        model_fields = get_model_fields(target_model, url=url)
        if len(model_fields) >= 2:
            fields[model_fields[0]] = front_content
            fields[model_fields[1]] = back_content
        else:
            fields = {"Front": front_content, "Back": back_content}
    except Exception:
        fields = {"Front": front_content, "Back": back_content}

    note_params = {
        "note": {
            "deckName": deck_name,
            "modelName": target_model,
            "fields": fields,
            "tags": tags,
            "options": {
                "allowDuplicate": True
            }
        }
    }

    res = invoke_anki("addNote", note_params, url=url)
    return res.get("result")

def get_all_notes_from_deck(deck_name: str = ANKI_DECK_NAME, url: str = ANKI_CONNECT_URL) -> List[Dict[str, Any]]:
    """Busca todas as notas de um baralho no Anki."""
    query_res = invoke_anki("findNotes", {"query": f'deck:"{deck_name}"'}, url=url)
    note_ids = query_res.get("result", [])
    if not note_ids:
        return []
    
    info_res = invoke_anki("notesInfo", {"notes": note_ids}, url=url)
    return info_res.get("result", [])

if __name__ == "__main__":
    if check_connection():
        print("[OK] Conexao com o AnkiConnect bem-sucedida!")
        print("Baralhos disponiveis:", get_deck_names())
        print("Modelos disponiveis:", get_model_names())
    else:
        print("[AVISO] Nao foi possivel conectar ao AnkiConnect.")
