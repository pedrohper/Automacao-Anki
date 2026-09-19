import asyncio
import os
import re
import edge_tts
from dotenv import load_dotenv

load_dotenv()

DEFAULT_VOICE = os.getenv("TTS_VOICE", "en-US-ChristopherNeural")

async def generate_audio_file_async(text: str, output_path: str, voice: str = DEFAULT_VOICE) -> str:
    """Gera um arquivo .mp3 a partir de um texto usando a biblioteca edge-tts."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path

def generate_audio_file(text: str, output_path: str, voice: str = DEFAULT_VOICE) -> str:
    """Wrapper síncrono para gerar o áudio de forma segura em qualquer thread."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(generate_audio_file_async(text, output_path, voice))

def get_audio_filename(target_word: str) -> str:
    """Gera um nome limpo e único para o arquivo de áudio no Anki."""
    clean_word = re.sub(r'[^a-zA-Z0-9]', '_', target_word.lower().strip())
    return f"tts_vibe_{clean_word}.mp3"

if __name__ == "__main__":
    test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test_audio.mp3")
    try:
        generate_audio_file("The system has high throughput.", test_path)
        print(f"Áudio de teste gerado em: {test_path}")
        if os.path.exists(test_path):
            os.remove(test_path)
    except Exception as e:
        print(f"Erro ao gerar áudio: {e}")
