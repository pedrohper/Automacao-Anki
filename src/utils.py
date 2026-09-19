import re
import json
from typing import List, Any

def parse_word_list(raw_input: str) -> List[str]:
    """
    Parser inteligente que extrai palavras limpas a partir de qualquer texto colado.
    Suporta:
    - Uma palavra por linha
    - Listas numeradas (1. word, 2) word)
    - Marcadores de tópico (• word, - word, * word)
    - Palavras separadas por vírgulas, ponto-e-vírgula ou espaços
    """
    if not raw_input or not raw_input.strip():
        return []

    # 1. Limpar marcadores de lista numerada ou tópicos no início das linhas
    cleaned = re.sub(r'^\s*[\d\.\-\*\•\)]+\s*', '', raw_input, flags=re.MULTILINE)
    
    # 2. Substituir quebras de linha, vírgulas e ponto-e-vírgula por delimitadores
    tokens = re.split(r'[\n\r,;\t]+', cleaned)
    
    words = []
    seen = set()

    for token in tokens:
        # Limpar espaços e pontuações extras nas bordas
        w = token.strip().strip('"\'`()[]{}')
        
        # Se contiver espaços internos (ex: phrasal verb como "spill the beans"), mantém a expressão
        if w:
            w_lower = w.lower()
            if w_lower not in seen:
                seen.add(w_lower)
                words.append(w)

    return words

def extract_json_from_llm_text(text: str) -> Any:
    """
    Extrai e faz o parse de JSON retornado por LLMs de forma robusta,
    removendo blocos de código Markdown ou textos explicativos extras.
    """
    cleaned = text.strip()
    
    # Remover blocos markdown do tipo ```json ... ``` ou ``` ... ```
    if "```" in cleaned:
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned).strip()

    # Tentar o parse direto
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Procurar o primeiro array JSON [...] no texto
    array_match = re.search(r'\[\s*\{.*\}\s*\]', cleaned, re.DOTALL)
    if array_match:
        try:
            return json.loads(array_match.group(0))
        except json.JSONDecodeError:
            pass

    # Procurar o primeiro objeto JSON {...} no texto
    object_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if object_match:
        try:
            return json.loads(object_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Não foi possível extrair um JSON válido da resposta do modelo:\n{text[:200]}...")

if __name__ == "__main__":
    sample = """
    1. throughput
    - deadlock
    • latency
    middleware, scalability; concurrency
    "spill the beans"
    """
    res = parse_word_list(sample)
    print("Palavras extraídas:", res)

