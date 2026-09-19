import os
import json
import re
from typing import Set, Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

from src.utils import extract_json_from_llm_text

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

def generate_card_with_deepseek(target_word: str, known_words: Set[str], multi_meaning: bool = True) -> List[Dict[str, Any]]:
    """Gera os cards com suporte a múltiplos significados e detecção automática de Falsos Cognatos."""
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key == "sua_chave_api_aqui":
        raise ValueError("DEEPSEEK_API_KEY não foi configurada. Insira sua chave real no arquivo .env!")

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    known_sample = ", ".join(list(known_words)[:300]) if known_words else "palavras básicas cotidianas"

    system_prompt = (
        "Você é um tutor especialista em ensino de inglês baseado na metodologia Comprehensible Input (i+1).\n"
        "Sua tarefa é criar conteúdo para flashcards do Anki focados em EXATAMENTE UMA palavra nova por frase.\n"
        "Todas as outras palavras da frase DEVEM ser simples, comuns ou pertencer ao vocabulário já conhecido do aluno.\n"
        "REGRAS DE FALSOS COGNATOS (FALSOS AMIGOS):\n"
        "Verifique se a palavra em inglês parece uma palavra em português mas significa algo totalmente diferente (ex: actually, pretend, attend, push, intend, novel, custom, fabric, exit, injury).\n"
        "Se a palavra FOR um falso cognato, no campo 'explanation' você DEVE incluir a seguinte caixa visual em HTML:\n"
        "<div style='background:#f38ba8; color:#11111b; padding:6px; margin-top:6px; border-radius:4px; font-weight:bold;'>⚠️ Cuidado: Falso Amigo! '{target_word}' NÃO significa 'palavra em PT parecida'. Significa 'tradução real'.</div>\n"
        "Responda EXCLUSIVAMENTE uma lista JSON válida (array de objetos)."
    )

    instructions_sense = (
        "Se a palavra tiver mais de 1 significado comum/importante (ex: run = correr vs administrar vs rodar programa), "
        "retorne até 3 objetos na lista JSON, 1 para cada significado diferente."
        if multi_meaning else
        "Retorne exatamente 1 objeto na lista JSON para o significado mais comum."
    )

    user_prompt = f"""
Palavra-alvo (nova palavra): "{target_word}"

Exemplo de vocabulário que o aluno JÁ CONHECE:
[{known_sample}]

REGRAS DE GERAÇÃO:
1. {instructions_sense}
2. Para cada significado, crie 1 frase natural em inglês contendo a palavra "{target_word}".
3. Regra i+1: APENAS a palavra "{target_word}" pode ser nova/desafiadora na frase.
4. No campo "meaning", forneça a tradução direta no formato: "{target_word} = significado em português (contexto)".
5. No campo "explanation", forneça o contexto e, se for falso cognato, inclua a caixa de alerta visual.

Responda ESTRITAMENTE a lista JSON no seguinte formato (sem texto adicional):
[
    {{
        "sentence": "Frase em inglês no contexto",
        "target_word": "{target_word}",
        "meaning": "{target_word} = tradução",
        "explanation": "Contexto e alerta de falso amigo se aplicável"
    }}
]
"""

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        parsed = extract_json_from_llm_text(content)
        if isinstance(parsed, dict):
            return [parsed]
        return parsed
    except Exception as e:
        err_msg = str(e)
        if "Insufficient Balance" in err_msg or "402" in err_msg:
            raise RuntimeError("❌ A chave da API do DeepSeek está sem saldo. Recarregue a conta no painel da DeepSeek.")
        raise e

def generate_card_content(target_word: str, known_words: Set[str], multi_meaning: bool = True) -> List[Dict[str, Any]]:
    return generate_card_with_deepseek(target_word, known_words, multi_meaning=multi_meaning)

if __name__ == "__main__":
    try:
        cards = generate_card_content("actually", {"i", "like", "it"})
        print("Resultado para 'actually':")
        print(json.dumps(cards, indent=2, ensure_ascii=False))
    except Exception as e:
        print(e)
