"""Análise pedagógica e roteamento de materiais para os baralhos do Anki."""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from src.utils import extract_json_from_llm_text

load_dotenv()

LLM_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def _clean_decks(deck_names: List[str]) -> List[str]:
    """Remove duplicatas antes de mostrar os baralhos ao modelo."""
    return sorted({name.strip() for name in deck_names if name and name.strip()})


def _normalize_cards(cards: Any) -> List[Dict[str, str]]:
    """Aceita somente cartões completos e limita campos para a nota Basic do Anki."""
    if not isinstance(cards, list):
        return []

    clean_cards = []
    for card in cards:
        if not isinstance(card, dict):
            continue
        front = str(card.get("front", "")).strip()
        back = str(card.get("back", "")).strip()
        if front and back:
            clean_cards.append({"front": front, "back": back})
    return clean_cards


def _confidence(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def auto_route_and_generate(
    content: str,
    available_decks: List[str] | None = None,
    max_cards: int = 40,
    reference_context: str = "",
) -> Dict[str, Any]:
    """Analisa um material, escolhe um baralho real e produz cards de revisão ativa.

    O modelo só pode selecionar um nome presente em ``available_decks``. Quando não
    houver um baralho adequado, ele propõe um nome, que a interface apresenta ao
    usuário antes de qualquer envio ao Anki.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key == "sua_chave_api_aqui":
        raise ValueError("DEEPSEEK_API_KEY não foi configurada no arquivo .env!")
    if not content or not content.strip():
        raise ValueError("Envie um texto ou arquivo com conteúdo para estudar.")

    client = OpenAI(api_key=api_key, base_url=LLM_BASE_URL)
    decks = _clean_decks(available_decks or [])
    deck_options = "\n".join(f"- {deck}" for deck in decks) or "(nenhum baralho disponível no Anki)"
    material = content.strip()[:30000]

    system_prompt = """
Você é um professor particular criterioso e organizador de conhecimento no Anki.
Sua missão é transformar SOMENTE o material fornecido em uma revisão que também
ensine. Primeiro identifique o assunto, o nível e os conceitos que valem revisão.
Depois escolha o baralho mais específico entre os nomes oferecidos.

REGRAS DE ROTEAMENTO
- `deck_name` deve ser exatamente um dos baralhos disponíveis ou uma string vazia.
- Escolha pela matéria e pelo tópico, não por uma palavra solta.
- Se não existir baralho adequado, use `deck_name` vazio e sugira um nome curto em
  `suggested_deck_name`. Nunca invente que um baralho já existe.
- Dê uma razão objetiva e uma confiança de 0 a 1.

REGRAS PEDAGÓGICAS
- Faça cartões de recuperação ativa: uma pergunta precisa por ideia. Evite cartões
  vagos, listas enormes e perguntas cuja resposta esteja na própria frente.
- Preserve contexto suficiente: no verso explique a ideia primeiro, depois dê um
  exemplo, consequência, comparação ou miniaplicação quando isso ajudar.
- Não crie fatos, fórmulas, datas ou exemplos específicos que não estejam no
  material. Quando o material estiver incompleto, gere menos cartões em vez de
  preencher lacunas com suposições.
- Use português claro; mantenha termos técnicos originais entre parênteses quando
  forem úteis. HTML permitido: <b>, <br>, <ul>, <li>, <code>.
- `study_note` deve ensinar em 1 ou 2 frases o núcleo do material e servir de
  contexto para a pessoa revisar os cartões.

Responda somente JSON válido neste formato:
{
  "subject": "matéria e tópico detectados",
  "level": "iniciante | intermediário | avançado | não identificado",
  "deck_name": "baralho existente ou vazio",
  "suggested_deck_name": "nome sugerido ou vazio",
  "routing_reason": "por que esse baralho é o melhor destino",
  "confidence": 0.0,
  "study_note": "síntese didática curta",
  "coverage_summary": "quais partes relevantes do material foram cobertas",
  "tags": ["tags curtas"],
  "cards": [{"front": "pergunta", "back": "resposta contextualizada"}]
}
""".strip()

    user_prompt = f"""
BARALHOS DISPONÍVEIS NO ANKI:
{deck_options}

MATERIAL PARA ANALISAR:
---
{material}
---

CONTEXTO DE APOIO DA BIBLIOTECA LOCAL:
---
{reference_context[:9000] or "(não há contexto relacionado salvo)"}
---

Use o contexto de apoio apenas para esclarecer terminologia, matéria e conexões
que já apareçam no material principal. Os flashcards devem continuar baseados no
material principal; não transforme notas antigas em fatos novos do card.

DECIDA A QUANTIDADE DE CARDS:
- Escolha a menor quantidade que cubra as ideias centrais e distintas do material.
- Não receba uma meta artificial de quantidade: material curto pode gerar poucos
  cards; material amplo deve cobrir cada módulo ou tópico importante.
- Una detalhes que só fazem sentido juntos, mas não esconda várias ideias soltas
  dentro do mesmo card.
- Para Exatas, priorize conceitos, fórmulas, interpretação e passos que possam ser
  recuperados mentalmente. Não crie exercícios longos que exijam caderno.
- Nunca gere mais de {max(1, min(max_cards, 60))} cards nesta execução. Se esse
  teto impedir a cobertura adequada, explique isso em `coverage_summary`.

Antes de gerar, raciocine internamente sobre a organização; na resposta retorne
apenas o JSON.
""".strip()

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    result = extract_json_from_llm_text(response.choices[0].message.content.strip())
    if not isinstance(result, dict):
        raise ValueError("A IA não retornou o plano de estudo esperado.")

    selected_deck = str(result.get("deck_name", "")).strip()
    if selected_deck not in decks:
        selected_deck = ""

    tags = result.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    return {
        "subject": str(result.get("subject", "Assunto a revisar")).strip(),
        "level": str(result.get("level", "não identificado")).strip(),
        "deck_name": selected_deck,
        "suggested_deck_name": str(result.get("suggested_deck_name", "")).strip(),
        "routing_reason": str(result.get("routing_reason", "Sem justificativa retornada.")).strip(),
        "confidence": _confidence(result.get("confidence", 0.0)),
        "study_note": str(result.get("study_note", "")).strip(),
        "coverage_summary": str(result.get("coverage_summary", "")).strip(),
        "tags": [str(tag).strip() for tag in tags[:8] if str(tag).strip()],
        "cards": _normalize_cards(result.get("cards")),
    }
