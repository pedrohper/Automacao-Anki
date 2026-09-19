# 🎴 Automação de Flashcards para Anki (Inglês & Faculdade)

Aplicação desktop em Python com interface gráfica moderna para automação e geração inteligente de flashcards do **Anki** alimentada pela API do **DeepSeek**, com síntese de áudio nativa, suporte a múltiplos formatos de estudo e exportação direta em arquivos `.apkg`.

---

## ✨ Funcionalidades Principais

### 🔤 1. Módulo de Inglês (Metodologia i+1)
- **Método Comprehensible Input (i+1)**: Cria frases contextuais onde apenas a palavra-alvo é nova, utilizando o banco de palavras conhecidas do usuário.
- **Áudio Nativo Automático**: Gera pronúncia em MP3 usando vozes neurais da biblioteca `edge-tts` e anexa diretamente ao card no Anki.
- **Múltiplos Sentidos**: Opção para gerar 1 card por significado caso a palavra possua múltiplos usos comuns (ex: *run* = correr, administrar, rodar programa).
- **Detecção de Falsos Cognatos**: Identifica automaticamente "falsos amigos" (ex: *actually*, *pretend*, *attend*) e insere um alerta visual destacado no verso do card.

### 🎓 2. Módulo Acadêmico / Faculdade
- **Suporte a Múltiplos Formatos**: Lê conteúdos de arquivos **PDF**, **TXT**, **MD**, links de **sites/artigos** e transcrições de **vídeos do YouTube**.
- **Formatação Didática Visual**:
  - Trechos de código em C++, Python, Java formatados em blocos sintáticos.
  - Fórmulas matemáticas, equações e conceitos de Cálculo/Estatística destacados em caixas visuais.

### 📦 3. Envio Direto ao Anki ou Exportação `.apkg`
- **AnkiConnect**: Envia os cards gerados em tempo real para o Anki Desktop via API REST.
- **Exportação Offline (.apkg)**: Gera arquivos `.apkg` oficiais do Anki (usando `genanki`) com IDs determinísticos, permitindo importar manualmente em qualquer dispositivo.

### 📜 4. Histórico Local & Banco de Vocabulário
- Banco de dados SQLite (`known_words.db`) integrado para armazenar todas as palavras aprendidas e evitar cards duplicados.

---

## 📋 Pré-requisitos

1. **Python 3.8+** instalado.
2. **Chave de API da DeepSeek**: Cadastre-se na [Plataforma DeepSeek](https://platform.deepseek.com/) e obtenha uma chave de API.
3. *(Opcional)* **Anki Desktop**: Se quiser sincronização direta, instale o add-on **AnkiConnect** no Anki:
   - No Anki Desktop, vá em `Ferramentas` -> `Notas/Extensões` -> `Obter extenções...`
   - Insira o código: `2055492159`
   - Reinicie o Anki.

---

## 🚀 Passo a Passo de Instalação

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Criar Ambiente Virtual e Instalar Dependências
No terminal do Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Copie o arquivo de exemplo `.env.example` para criar seu arquivo `.env`:
```bash
copy .env.example .env
```
Abra o arquivo `.env` e insira sua chave da API da DeepSeek:
```env
DEEPSEEK_API_KEY=sk-sua-chave-real-aqui
```

---

## 💻 Como Usar

### Opção A: Executar via Duplo Clique (Windows)
Dê um duplo clique no arquivo **`executar.bat`**. O script detectará seu ambiente virtual e abrirá a interface automaticamente.

### Opção B: Executar via Terminal
Com o ambiente virtual ativado, execute:
```bash
python gui.py
```

---

## 🛠️ Estrutura do Projeto

```
.
├── .env.example        # Modelo de variáveis de ambiente
├── .gitignore          # Arquivos e diretórios ignorados pelo Git
├── executar.bat        # Script de inicialização facilitada no Windows
├── gui.py              # Interface gráfica principal (Tkinter)
├── main.py             # Script CLI / fluxo principal de geração
├── requirements.txt    # Dependências do projeto
├── README.md           # Documentação do projeto
└── src/
    ├── anki_client.py  # Integração REST com a API do AnkiConnect
    ├── apkg_service.py # Exportador de baralhos .apkg (genanki)
    ├── college_service.py # Processador de aulas/PDFs/URLs via LLM
    ├── database.py     # Gerenciador do banco SQLite (vocabulário e histórico)
    ├── extractor.py    # Extração de vocabulário de notas do Anki e textos
    ├── llm_service.py  # Geração de frases i+1 e cognatos via DeepSeek
    ├── tts_service.py  # Gerador de áudio via Edge-TTS
    ├── url_service.py  # Extrator de transcrições do YouTube e conteúdo Web
    └── utils.py        # Parsers utilitários e extração de JSON
```

---

## 📄 Licença

Este projeto é de código aberto sob a licença [MIT](LICENSE). Sinta-se livre para usar, modificar e distribuir!
