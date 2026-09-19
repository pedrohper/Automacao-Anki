import re
import requests
from bs4 import BeautifulSoup
from typing import Optional

def extract_youtube_video_id(url: str) -> Optional[str]:
    """Extrai o ID de um vídeo do YouTube a partir de qualquer formato de URL."""
    patterns = [
        r'(?:v=|\/)([\w-]{11})(?:\?|&|#|$)',
        r'youtu\.be\/([\w-]{11})',
        r'youtube\.com\/embed\/([\w-]{11})',
        r'youtube\.com\/shorts\/([\w-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def fetch_youtube_transcript(url_or_id: str) -> str:
    """Extrai a legenda/transcrição de uma videoaula do YouTube."""
    video_id = extract_youtube_video_id(url_or_id) or url_or_id.strip()
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        # Tenta buscar em Português ou Inglês
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en', 'pt-BR'])
        text_chunks = [item['text'] for item in transcript_list]
        return "\n".join(text_chunks)
    except Exception as e:
        raise RuntimeError(f"Não foi possível obter a transcrição do YouTube. Erro: {e}")

def fetch_website_text(url: str) -> str:
    """Lê e extrai o conteúdo de texto limpo de uma página web ou documentação."""
    if not url.startswith("http"):
        url = "https://" + url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Remover scripts, estilos, cabeçalhos e rodapés irrelevantes
        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.decompose()

        # Tentar pegar a tag article ou os parágrafos principais
        article = soup.find("article") or soup.find("main") or soup.body
        if not article:
            return ""

        paragraphs = article.find_all(["p", "h1", "h2", "h3", "li"])
        text_lines = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
        
        return "\n".join(text_lines)
    except Exception as e:
        raise RuntimeError(f"Erro ao ler página da web ({url}): {e}")

def fetch_content_from_url(url: str) -> str:
    """Detecta automaticamente se a URL é do YouTube ou de um site e extrai o texto."""
    if "youtube.com" in url or "youtu.be" in url:
        return fetch_youtube_transcript(url)
    else:
        return fetch_website_text(url)

if __name__ == "__main__":
    test_yt = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        print("Testando extração do YouTube...")
        txt = fetch_youtube_transcript(test_yt)
        print("Extrato da transcrição:", txt[:150])
    except Exception as e:
        print("Erro teste YT:", e)
