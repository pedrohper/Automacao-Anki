import os
import re
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from src.utils import extract_json_from_llm_text

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

DEFAULT_SUBJECTS = [
    # SENAI (14 Matérias)
    "SENAI: Fundamentos dos Processos Administrativos",
    "SENAI: Fundamentos dos Processos Financeiros",
    "SENAI: Fundamentos dos Processos de Gestão de Pessoas",
    "SENAI: Fundamentos de Logística",
    "SENAI: Fundamentos da Qualidade",
    "SENAI: Informática",
    "SENAI: Planejamento e Organização do Trabalho",
    "SENAI: Raciocínio Lógico e Análise de Dados",
    "SENAI: Transformação Digital no Setor Industrial",
    "SENAI: Saúde e Segurança do Trabalho",
    "SENAI: Fundamentos da Leitura de Desenhos Técnicos e Metrologia",
    "SENAI: Práticas Inovadoras",
    "SENAI: Fundamentos da Comunicação e Informação",
    "SENAI: Relações Socioprofissionais, Cidadania e Ética",
    # ESAMC
    "ESAMC: Sistemas de Informação em Administração (ERP / TI)",
    # Cargill
    "Cargill: Visão Geral, Valores & Operações",
    "Cargill: EHS & Segurança do Trabalho (Life Saving Rules)",
    # Outros
    "Estrutura de Dados",
    "Cálculo II",
    "Estatística I"
]


def extract_text_from_file(file_path: str) -> str:
    """Extrai o texto de um arquivo PDF, TXT ou MD."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            extracted_text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    extracted_text.append(t)
            return "\n".join(extracted_text)
        except Exception as e:
            raise RuntimeError(f"Erro ao ler arquivo PDF: {e}")

    elif ext in [".txt", ".md", ".csv", ".log"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Formato de arquivo não suportado: {ext}. Envie .pdf, .txt ou .md.")

def generate_college_flashcards(subject: str, content: str, num_cards: int = 10) -> List[Dict[str, str]]:
    """
    Gera flashcards acadêmicos de pergunta e resposta a partir do conteúdo de uma aula usando DeepSeek,
    com suporte a blocos de código C++/Python formatados e caixas de fórmulas matemáticas.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key == "sua_chave_api_aqui":
        raise ValueError("DEEPSEEK_API_KEY não foi configurada. Insira sua chave real no arquivo .env!")

    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    max_chars = 12000
    truncated_content = content[:max_chars] if len(content) > max_chars else content

    context_instruction = ""
    subj_lower = subject.lower()

    if "esamc" in subj_lower or "sistemas de informação" in subj_lower:
        context_instruction = (
            "\n⚠️ REGRA CRÍTICA PARA DISCIPLINA ESAMC (ADMINISTRAÇÃO DE EMPRESAS):\n"
            "Esta disciplina é de GESTÃO DE SISTEMAS DE INFORMAÇÃO EM ADM (Administração de Empresas).\n"
            "Foque EXCLUSIVAMENTE em: ERP (SAP, TOTVS), CRM, SCM, BI (Dashboards/Analytics), Governança de TI (COBIT/ITIL), Segurança da Informação Corporativa, Alinhamento de TI com Estratégia de Negócios e Processos Organizacionais.\n"
            "NÃO GERE de forma alguma conteúdos de desenvolvimento/engenharia de software pura, tais como: sintaxe de linguagem (JavaScript, Node.js, Python, C++), frameworks web (React, NestJS, Virtual DOM), estruturas de dados de código (Listas Encadeadas, Nós, Ponteiros, Big-O) ou tratamento de exceções de código.\n"
        )
    elif "senai" in subj_lower:
        context_instruction = (
            "\n⚠️ REGRA PARA DISCIPLINA SENAI (APRENDIZAGEM ADMINISTRATIVA):\n"
            "Foque em rotinas administrativas, processos de escritório/indústria, 5S, qualidade, logística, finanças e segurança do trabalho (NRs/EPIs).\n"
        )
    elif "cargill" in subj_lower:
        context_instruction = (
            "\n⚠️ REGRA PARA MÓDULO CARGILL:\n"
            "Foque na empresa Cargill: Propósito, Valores, EHS (Regras de Ouro de Segurança), Parada de Segurança (Stop Work Authority), Originação e Logística de Commodities.\n"
        )

    system_prompt = (
        "Você é um professor universitário e tutor acadêmico especialista em memorização ativa e flashcards do Anki.\n"
        "Sua função é transformar materiais de aula em flashcards didáticos com excelente formatação visual HTML.\n"
        f"{context_instruction}\n"
        "REGRAS DE FORMATAÇÃO DIDÁTICA PARA O CAMPO 'back':\n"
        "1. Para trechos técnicos ou tabelas, use formatação clara.\n"
        "2. Para fórmulas matemáticas, equações ou conceitos-chave (Finanças, Estatística), envolva em:\n"
        "   <div style='background:#313244; color:#89b4fa; padding:8px; border-left:4px solid #89b4fa; margin:6px 0; border-radius:3px;'><b>Fórmula/Conceito:</b> resultado aqui</div>\n"
        "3. Use negrito <b>texto</b> para dar destaque às palavras mais importantes.\n"
        "Responda EXCLUSIVAMENTE em formato JSON (uma lista de objetos JSON)."
    )

    user_prompt = f"""
Disciplina Universitária: "{subject}"
Material da Aula / Contexto:
---
{truncated_content}
---

INSTRUÇÕES:
1. Gere aproximadamente {num_cards} flashcards no formato Pergunta / Resposta respeitando RIGOROSAMENTE o escopo da disciplina "{subject}".
2. Frente (campo "front"): Pergunta clara, problema prático ou desafio conceitual da matéria.
3. Verso (campo "back"): Resposta direta com a explicação e destaques em <b>negrito</b>.

Responda ESTRITAMENTE uma lista JSON válida (sem texto adicional):
[
    {{
        "front": "Pergunta ou conceito da disciplina",
        "back": "Resposta clara com <b>destaque</b>"
    }}
]
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
    cards = extract_json_from_llm_text(raw_text)
    return cards

if __name__ == "__main__":
    sample = "Em Cálculo II, a derivada parcial de f(x,y) = x^2 * y em relação a x é fx = 2xy."
    try:
        cards = generate_college_flashcards("Cálculo II", sample, num_cards=1)
        print("Card gerado com formatação:", json.dumps(cards, ensure_ascii=True))
    except Exception as e:
        print(e)
