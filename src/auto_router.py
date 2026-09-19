"""
Módulo Roteador Inteligente (Seção Geral - Auto-Direcionamento).
Recebe um texto/resumo colado pelo usuário, identifica o assunto (Inglês, SENAI, ESAMC, Cargill ou Geral)
e gera os flashcards direcionando automaticamente para o baralho correto no Anki.
"""

from typing import Dict, Any, List
import os
import json
from openai import OpenAI

from src.college_service import generate_college_flashcards
from src.utils import extract_json_from_llm_text

DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

def auto_route_and_generate(content: str, num_cards: int = 8) -> Dict[str, Any]:
    """
    Analisa o conteúdo colado no Módulo Geral, identifica a categoria/deck e gera os flashcards.
    
    Retorna um dicionário:
    {
        "category": "SENAI" | "Cargill" | "ESAMC" | "Inglês" | "Geral",
        "deck_name": "SENAI::Fundamentos dos Processos Administrativos",
        "cards": [ {"front": "...", "back": "..."}, ... ]
    }
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key == "sua_chave_api_aqui":
        raise ValueError("DEEPSEEK_API_KEY não foi configurada no arquivo .env!")

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    system_prompt = (
        "Você é um tutor acadêmico e assistente de organização de Anki.\n"
        "Sua tarefa é analisar o texto fornecido pelo usuário e:\n"
        "1. Identificar a qual categoria o texto pertence:\n"
        "   - 'Cargill' (se for sobre a empresa Cargill, cultura, segurança EHS, agronegócio, commodities).\n"
        "   - 'ESAMC' (se for sobre Sistemas de Informação em Administração, ERP/SAP, CRM, SCM, BI, Governança de TI/COBIT, Gestão Estratégica de TI).\n"
        "   - 'SENAI' (se for sobre rotinas administrativas, segurança do trabalho, qualidade 5S, desenhos técnicos, logística, finanças, gestão de pessoas, RH ou informática operacional).\n"
        "   - 'Inglês' (se for lista de palavras ou frases em inglês).\n"
        "   - 'Geral' (para outros assuntos gerais).\n"
        "2. Determinar o nome exato do baralho Anki recomendado (ex: 'Cargill::Geral', 'ESAMC::Sistemas_Informacao', 'SENAI::Processos_Administrativos', 'Inglês', 'Geral').\n"
        "3. Gerar flashcards em formato Pergunta (front) e Resposta (back) didáticos em HTML.\n\n"
        "Responda EXCLUSIVAMENTE em formato JSON com a seguinte estrutura:\n"
        "{\n"
        '  "category": "SENAI | Cargill | ESAMC | Inglês | Geral",\n'
        '  "deck_name": "NomeDoBaralhoNoAnki",\n'
        '  "cards": [\n'
        '    {"front": "Pergunta ou conceito", "back": "Resposta clara com <b>destaque</b>"}\n'
        '  ]\n'
        "}"
    )

    user_prompt = f"""
Texto para análise e geração de flashcards:
---
{content[:8000]}
---

Gere aproximadamente {num_cards} flashcards didáticos e classifique a categoria/deck.
"""

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )

    raw_text = response.choices[0].message.content.strip()
    result = extract_json_from_llm_text(raw_text)

    if isinstance(result, dict) and "cards" in result:
        return result
    elif isinstance(result, list):
        return {
            "category": "Geral",
            "deck_name": "Geral",
            "cards": result
        }
    else:
        # Fallback genérico se a resposta não for o dict esperado
        cards = generate_college_flashcards("Geral", content, num_cards=num_cards)
        return {
            "category": "Geral",
            "deck_name": "Geral",
            "cards": cards
        }
