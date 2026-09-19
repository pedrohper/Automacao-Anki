import sys
import os
import io
import re

# Redirecionar sys.stdout e sys.stderr para evitar falhas ao rodar com pythonw (onde stdout é None)
class DummyStream(io.StringIO):
    def write(self, s):
        pass
    def flush(self):
        pass

if sys.stdout is None:
    sys.stdout = DummyStream()
if sys.stderr is None:
    sys.stderr = DummyStream()

import threading
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import init_db, get_known_words, get_recent_cards, is_word_known, record_card
from src.anki_client import check_connection, add_note
from src.extractor import extract_vocabulary_from_anki_deck
from src.college_service import extract_text_from_file, generate_college_flashcards, DEFAULT_SUBJECTS
from src.url_service import fetch_content_from_url
from src.apkg_service import export_cards_to_apkg
from src.utils import parse_word_list
from src.preset_data import CARGILL_CARDS, ESAMC_CARDS, get_all_senai_cards_flat, SENAI_SUBJECTS_CARDS
from src.auto_router import auto_route_and_generate
from main import process_single_word

SENAI_DISCIPLINES = list(SENAI_SUBJECTS_CARDS.keys())

class AnkiAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎴 Automação de Flashcards Anki (5 Seções Principais)")
        self.root.geometry("820x740")
        self.root.resizable(False, False)

        # Tema Dark Mode Moderno
        self.bg_color = "#1e1e2e"
        self.card_bg = "#2b2b3d"
        self.text_color = "#cdd6f4"
        self.accent_color = "#89b4fa"
        self.btn_bg = "#a6e3a1"
        self.btn_fg = "#11111b"

        self.root.configure(bg=self.bg_color)

        # Estilos do Notebook e Treeview
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background='#313244', foreground='#cdd6f4', padding=[10, 6], font=('Segoe UI', 9, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#45475a')], foreground=[('selected', '#89b4fa')])

        style.configure("Treeview", background="#181825", foreground="#cdd6f4", fieldbackground="#181825", rowheight=24, font=('Segoe UI', 9))
        style.configure("Treeview.Heading", background="#313244", foreground="#89b4fa", font=('Segoe UI', 9, 'bold'))

        init_db()
        self.attached_files = {"senai": "", "esamc": "", "cargill": "", "geral": ""}
        self.setup_ui()
        self.update_status()

    def setup_ui(self):
        # Título Principal
        title_label = tk.Label(
            self.root,
            text="🎴 Automação de Flashcards Anki",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(pady=(8, 2))

        # Sistema de Abas (Geral Primeiro + Demais Seções + Histórico)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=False, padx=10, pady=(5, 5))

        # Seção 1: Geral (Auto-Direcionamento em Primeiro Lugar)
        self.tab_geral = tk.Frame(self.notebook, bg=self.card_bg, padx=12, pady=10)
        self.notebook.add(self.tab_geral, text="⚡ Geral (Auto-Deck)")
        self.setup_geral_tab()

        # Seção 2: Inglês
        self.tab_english = tk.Frame(self.notebook, bg=self.card_bg, padx=12, pady=10)
        self.notebook.add(self.tab_english, text="🔤 Inglês")
        self.setup_english_tab()

        # Seção 3: SENAI
        self.tab_senai = tk.Frame(self.notebook, bg=self.card_bg, padx=12, pady=10)
        self.notebook.add(self.tab_senai, text="🏭 SENAI")
        self.setup_senai_tab()

        # Seção 4: ESAMC
        self.tab_esamc = tk.Frame(self.notebook, bg=self.card_bg, padx=12, pady=10)
        self.notebook.add(self.tab_esamc, text="🎓 ESAMC (Sistemas)")
        self.setup_esamc_tab()

        # Seção 5: Cargill
        self.tab_cargill = tk.Frame(self.notebook, bg=self.card_bg, padx=12, pady=10)
        self.notebook.add(self.tab_cargill, text="🏢 Cargill")
        self.setup_cargill_tab()

        # Seção Extra: Histórico
        self.tab_history = tk.Frame(self.notebook, bg=self.card_bg, padx=10, pady=10)
        self.notebook.add(self.tab_history, text="📜 Histórico")
        self.setup_history_tab()


        # Log e Progresso Compartilhado
        log_frame = tk.Frame(self.root, bg=self.bg_color)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(5, 8))

        log_label = tk.Label(
            log_frame,
            text="Progresso em Tempo Real:",
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        log_label.pack(anchor="w", pady=(0, 2))

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 9),
            bg="#11111b",
            fg="#a6e3a1",
            height=6,
            bd=0
        )
        self.log_area.pack(fill="both", expand=True)

    # ---------------------------------------------------------
    # SEÇÃO 1: INGLÊS
    # ---------------------------------------------------------
    def setup_english_tab(self):
        lbl = tk.Label(
            self.tab_english,
            text="Cole sua lista de palavras em inglês (uma por linha, vírgulas ou espaços):",
            font=("Segoe UI", 9, "bold"),
            bg=self.card_bg,
            fg=self.text_color
        )
        lbl.pack(anchor="w", pady=(0, 3))

        self.txt_words = scrolledtext.ScrolledText(
            self.tab_english,
            font=("Consolas", 10),
            bg="#181825",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            height=6,
            bd=1,
            relief="solid"
        )
        self.txt_words.pack(fill="x", pady=(0, 6))

        opt_frame = tk.Frame(self.tab_english, bg=self.card_bg)
        opt_frame.pack(fill="x", pady=(0, 6))

        self.var_multi_meaning = tk.BooleanVar(value=True)
        chk_multi = tk.Checkbutton(
            opt_frame,
            text="✨ Detectar Múltiplos Significados (gerar 1 card por sentido)",
            variable=self.var_multi_meaning,
            font=("Segoe UI", 9),
            bg=self.card_bg,
            fg=self.text_color,
            selectcolor="#181825"
        )
        chk_multi.pack(anchor="w")

        self.var_check_dup = tk.BooleanVar(value=True)
        chk_dup = tk.Checkbutton(
            opt_frame,
            text="🔍 Avisar se a palavra já constar no banco de vocabulário",
            variable=self.var_check_dup,
            font=("Segoe UI", 9),
            bg=self.card_bg,
            fg=self.text_color,
            selectcolor="#181825"
        )
        chk_dup.pack(anchor="w")

        btn_row = tk.Frame(self.tab_english, bg=self.card_bg)
        btn_row.pack(fill="x", pady=(0, 6))

        self.btn_generate_eng = tk.Button(
            btn_row,
            text="🚀 Criar e Enviar para o Anki (Baralho Inglês)",
            font=("Segoe UI", 10, "bold"),
            bg=self.btn_bg,
            fg=self.btn_fg,
            bd=0,
            cursor="hand2",
            command=self.on_click_generate_english
        )
        self.btn_generate_eng.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 5))

        btn_export_eng = tk.Button(
            btn_row,
            text="📦 Exportar .apkg",
            font=("Segoe UI", 9, "bold"),
            bg="#f9e2af",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.export_apkg_action("Inglês")
        )
        btn_export_eng.pack(side="right", ipady=5, ipadx=8)

        sub_frame = tk.Frame(self.tab_english, bg=self.card_bg)
        sub_frame.pack(fill="x")

        self.lbl_known = tk.Label(
            sub_frame,
            text="Vocabulário Conhecido: ...",
            font=("Segoe UI", 9, "italic"),
            bg=self.card_bg,
            fg="#a6adc8"
        )
        self.lbl_known.pack(side="left")

        btn_sync = tk.Button(
            sub_frame,
            text="🔄 Sincronizar Vocabulário do Anki",
            font=("Segoe UI", 8),
            bg="#45475a",
            fg="#cdd6f4",
            bd=0,
            cursor="hand2",
            command=self.on_click_sync
        )
        btn_sync.pack(side="right")

    # ---------------------------------------------------------
    # SEÇÃO 2: SENAI
    # ---------------------------------------------------------
    def setup_senai_tab(self):
        row_preset = tk.Frame(self.tab_senai, bg="#181825", padx=8, pady=6)
        row_preset.pack(fill="x", pady=(0, 8))

        lbl_p = tk.Label(row_preset, text="⚡ Baralho Completo SENAI:", font=("Segoe UI", 9, "bold"), bg="#181825", fg="#89b4fa")
        lbl_p.pack(side="left")

        btn_send_senai_preset = tk.Button(
            row_preset,
            text="🚀 Enviar 31 Flashcards de Revisão para o Anki",
            font=("Segoe UI", 8, "bold"),
            bg="#a6e3a1",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.send_preset_to_anki("SENAI")
        )
        btn_send_senai_preset.pack(side="left", padx=8)

        btn_exp_senai = tk.Button(
            row_preset,
            text="📦 Baixar .apkg SENAI",
            font=("Segoe UI", 8, "bold"),
            bg="#f9e2af",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.export_preset_apkg("SENAI")
        )
        btn_exp_senai.pack(side="right")

        row1 = tk.Frame(self.tab_senai, bg=self.card_bg)
        row1.pack(fill="x", pady=(0, 4))

        lbl_subj = tk.Label(row1, text="Disciplina SENAI:", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_color)
        lbl_subj.pack(anchor="w")

        self.combo_senai = ttk.Combobox(self.tab_senai, values=SENAI_DISCIPLINES, font=("Segoe UI", 9), state="normal")
        self.combo_senai.set(SENAI_DISCIPLINES[0])
        self.combo_senai.pack(fill="x", pady=(0, 6))

        # Anexar / URL
        row_files = tk.Frame(self.tab_senai, bg=self.card_bg)
        row_files.pack(fill="x", pady=(0, 4))

        btn_attach = tk.Button(
            row_files,
            text="📁 Anexar PDF / Slide / TXT",
            font=("Segoe UI", 8, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.on_click_attach_file("senai")
        )
        btn_attach.pack(side="left")

        self.lbl_file_senai = tk.Label(row_files, text="Nenhum arquivo", font=("Segoe UI", 8, "italic"), bg=self.card_bg, fg="#a6adc8")
        self.lbl_file_senai.pack(side="left", padx=6)

        lbl_text = tk.Label(self.tab_senai, text="Ou cole o resumo / texto da aula:", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_color)
        lbl_text.pack(anchor="w", pady=(4, 2))

        self.txt_senai = scrolledtext.ScrolledText(self.tab_senai, font=("Consolas", 9), bg="#181825", fg="#cdd6f4", height=4, bd=1, relief="solid")
        self.txt_senai.pack(fill="x", pady=(0, 6))

        btn_gen_senai = tk.Button(
            self.tab_senai,
            text="⚡ Gerar Flashcards da Aula (SENAI) via IA",
            font=("Segoe UI", 9, "bold"),
            bg=self.btn_bg,
            fg=self.btn_fg,
            bd=0,
            cursor="hand2",
            command=lambda: self.on_click_generate_custom("SENAI", self.combo_senai.get(), self.txt_senai, "senai")
        )
        btn_gen_senai.pack(fill="x", ipady=5)

    # ---------------------------------------------------------
    # SEÇÃO 3: ESAMC
    # ---------------------------------------------------------
    def setup_esamc_tab(self):
        row_preset = tk.Frame(self.tab_esamc, bg="#181825", padx=8, pady=6)
        row_preset.pack(fill="x", pady=(0, 8))

        lbl_p = tk.Label(row_preset, text="⚡ Baralho Completo ESAMC (Sistemas):", font=("Segoe UI", 9, "bold"), bg="#181825", fg="#89b4fa")
        lbl_p.pack(side="left")

        btn_send_esamc_preset = tk.Button(
            row_preset,
            text="🚀 Enviar Flashcards de ERP/TI para o Anki",
            font=("Segoe UI", 8, "bold"),
            bg="#a6e3a1",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.send_preset_to_anki("ESAMC")
        )
        btn_send_esamc_preset.pack(side="left", padx=8)

        btn_exp_esamc = tk.Button(
            row_preset,
            text="📦 Baixar .apkg ESAMC",
            font=("Segoe UI", 8, "bold"),
            bg="#f9e2af",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.export_preset_apkg("ESAMC")
        )
        btn_exp_esamc.pack(side="right")

        lbl_t = tk.Label(self.tab_esamc, text="Eixo da Faculdade (ESAMC):", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.accent_color)
        lbl_t.pack(anchor="w", pady=(0, 2))

        self.combo_esamc_axis = ttk.Combobox(
            self.tab_esamc,
            values=[
                "ESAMC: Eixo TI & Programação (CC / SI / Software)",
                "ESAMC: Eixo Gestão & Negócios (ADM / ERP / BI)"
            ],
            font=("Segoe UI", 9),
            state="readonly"
        )
        self.combo_esamc_axis.set("ESAMC: Eixo TI & Programação (CC / SI / Software)")
        self.combo_esamc_axis.pack(fill="x", pady=(0, 6))

        row_files = tk.Frame(self.tab_esamc, bg=self.card_bg)
        row_files.pack(fill="x", pady=(0, 4))

        btn_attach = tk.Button(
            row_files,
            text="📁 Anexar PDF / Slide / Resumo",
            font=("Segoe UI", 8, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.on_click_attach_file("esamc")
        )
        btn_attach.pack(side="left")

        self.lbl_file_esamc = tk.Label(row_files, text="Nenhum arquivo", font=("Segoe UI", 8, "italic"), bg=self.card_bg, fg="#a6adc8")
        self.lbl_file_esamc.pack(side="left", padx=6)

        lbl_text = tk.Label(self.tab_esamc, text="Cole o resumo ou notas da aula ESAMC:", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_color)
        lbl_text.pack(anchor="w", pady=(4, 2))

        self.txt_esamc = scrolledtext.ScrolledText(self.tab_esamc, font=("Consolas", 9), bg="#181825", fg="#cdd6f4", height=4, bd=1, relief="solid")
        self.txt_esamc.pack(fill="x", pady=(0, 6))

        btn_gen_esamc = tk.Button(
            self.tab_esamc,
            text="⚡ Gerar Flashcards da Aula (ESAMC) via IA",
            font=("Segoe UI", 9, "bold"),
            bg=self.btn_bg,
            fg=self.btn_fg,
            bd=0,
            cursor="hand2",
            command=lambda: self.on_click_generate_custom("ESAMC", self.combo_esamc_axis.get(), self.txt_esamc, "esamc")
        )
        btn_gen_esamc.pack(fill="x", ipady=5)

    # ---------------------------------------------------------
    # SEÇÃO 4: CARGILL
    # ---------------------------------------------------------
    def setup_cargill_tab(self):
        row_preset = tk.Frame(self.tab_cargill, bg="#181825", padx=8, pady=6)
        row_preset.pack(fill="x", pady=(0, 8))

        lbl_p = tk.Label(row_preset, text="⚡ Baralho Completo Cargill:", font=("Segoe UI", 9, "bold"), bg="#181825", fg="#89b4fa")
        lbl_p.pack(side="left")

        btn_send_cargill_preset = tk.Button(
            row_preset,
            text="🚀 Enviar Flashcards (Empresa, EHS, Valores) para o Anki",
            font=("Segoe UI", 8, "bold"),
            bg="#a6e3a1",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.send_preset_to_anki("Cargill")
        )
        btn_send_cargill_preset.pack(side="left", padx=8)

        btn_exp_cargill = tk.Button(
            row_preset,
            text="📦 Baixar .apkg Cargill",
            font=("Segoe UI", 8, "bold"),
            bg="#f9e2af",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.export_preset_apkg("Cargill")
        )
        btn_exp_cargill.pack(side="right")

        lbl_t = tk.Label(self.tab_cargill, text="Cargill: Aprendizados, Treinamentos, EHS & Procedimentos", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.accent_color)
        lbl_t.pack(anchor="w", pady=(0, 4))

        row_files = tk.Frame(self.tab_cargill, bg=self.card_bg)
        row_files.pack(fill="x", pady=(0, 4))

        btn_attach = tk.Button(
            row_files,
            text="📁 Anexar PDF / Procedimento / Documento",
            font=("Segoe UI", 8, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.on_click_attach_file("cargill")
        )
        btn_attach.pack(side="left")

        self.lbl_file_cargill = tk.Label(row_files, text="Nenhum arquivo", font=("Segoe UI", 8, "italic"), bg=self.card_bg, fg="#a6adc8")
        self.lbl_file_cargill.pack(side="left", padx=6)

        lbl_text = tk.Label(self.tab_cargill, text="Cole seus aprendizados ou tópicos da Cargill:", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_color)
        lbl_text.pack(anchor="w", pady=(4, 2))

        self.txt_cargill = scrolledtext.ScrolledText(self.tab_cargill, font=("Consolas", 9), bg="#181825", fg="#cdd6f4", height=5, bd=1, relief="solid")
        self.txt_cargill.pack(fill="x", pady=(0, 6))

        btn_gen_cargill = tk.Button(
            self.tab_cargill,
            text="⚡ Gerar Flashcards da Cargill via IA",
            font=("Segoe UI", 9, "bold"),
            bg=self.btn_bg,
            fg=self.btn_fg,
            bd=0,
            cursor="hand2",
            command=lambda: self.on_click_generate_custom("Cargill", "Cargill Operações & EHS", self.txt_cargill, "cargill")
        )
        btn_gen_cargill.pack(fill="x", ipady=5)

    # ---------------------------------------------------------
    # SEÇÃO 5: GERAL (AUTO-DIRECIONAMENTO)
    # ---------------------------------------------------------
    def setup_geral_tab(self):
        lbl_desc = tk.Label(
            self.tab_geral,
            text="⚡ Cole qualquer texto rápido aqui! A IA identifica o assunto (SENAI, ESAMC, Cargill, Inglês ou Geral) e envia para o deck certo!",
            font=("Segoe UI", 9, "bold"),
            bg=self.card_bg,
            fg="#89b4fa",
            wraplength=760,
            justify="left"
        )
        lbl_desc.pack(anchor="w", pady=(0, 6))

        row_files = tk.Frame(self.tab_geral, bg=self.card_bg)
        row_files.pack(fill="x", pady=(0, 4))

        btn_attach = tk.Button(
            row_files,
            text="📁 Anexar Qualquer Arquivo (PDF / TXT)",
            font=("Segoe UI", 8, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            bd=0,
            cursor="hand2",
            command=lambda: self.on_click_attach_file("geral")
        )
        btn_attach.pack(side="left")

        self.lbl_file_geral = tk.Label(row_files, text="Nenhum arquivo", font=("Segoe UI", 8, "italic"), bg=self.card_bg, fg="#a6adc8")
        self.lbl_file_geral.pack(side="left", padx=6)

        self.txt_geral = scrolledtext.ScrolledText(self.tab_geral, font=("Consolas", 9), bg="#181825", fg="#cdd6f4", height=7, bd=1, relief="solid")
        self.txt_geral.pack(fill="x", pady=(0, 8))

        self.btn_gen_geral = tk.Button(
            self.tab_geral,
            text="🚀 Processar Texto e Auto-Direcionar para o Deck Correto no Anki",
            font=("Segoe UI", 10, "bold"),
            bg=self.btn_bg,
            fg=self.btn_fg,
            bd=0,
            cursor="hand2",
            command=self.on_click_auto_route_geral
        )
        self.btn_gen_geral.pack(fill="x", ipady=6)

    # ---------------------------------------------------------
    # SEÇÃO EXTRA: HISTÓRICO DE CARDS
    # ---------------------------------------------------------
    def setup_history_tab(self):
        top_bar = tk.Frame(self.tab_history, bg=self.card_bg)
        top_bar.pack(fill="x", pady=(0, 6))

        lbl_hist = tk.Label(top_bar, text="Histórico de Cards Gerados no Banco:", font=("Segoe UI", 9, "bold"), bg=self.card_bg, fg=self.text_color)
        lbl_hist.pack(side="left")

        btn_refresh = tk.Button(
            top_bar,
            text="🔄 Atualizar Lista",
            font=("Segoe UI", 8, "bold"),
            bg="#45475a",
            fg="#cdd6f4",
            bd=0,
            cursor="hand2",
            command=self.load_history_data
        )
        btn_refresh.pack(side="right")

        columns = ("id", "date", "word", "sentence", "meaning")
        self.tree_history = ttk.Treeview(self.tab_history, columns=columns, show="headings", height=9)

        self.tree_history.heading("id", text="ID")
        self.tree_history.heading("date", text="Data/Hora")
        self.tree_history.heading("word", text="Palavra / Matéria")
        self.tree_history.heading("sentence", text="Frente")
        self.tree_history.heading("meaning", text="Verso")

        self.tree_history.column("id", width=35, anchor="center")
        self.tree_history.column("date", width=110, anchor="center")
        self.tree_history.column("word", width=130, anchor="w")
        self.tree_history.column("sentence", width=220, anchor="w")
        self.tree_history.column("meaning", width=200, anchor="w")

        self.tree_history.pack(fill="both", expand=True)
        self.load_history_data()

    # ---------------------------------------------------------
    # AÇÕES E LÓGICA DE NEGÓCIO
    # ---------------------------------------------------------
    def load_history_data(self):
        for item in self.tree_history.get_children():
            self.tree_history.delete(item)
        
        rows = get_recent_cards(limit=80)
        for r in rows:
            sentence_clean = re.sub(r'<[^>]+>', ' ', r[2])
            meaning_clean = re.sub(r'<[^>]+>', ' ', r[3])
            self.tree_history.insert("", "end", values=(r[0], r[4], r[1], sentence_clean[:40], meaning_clean[:35]))

    def log(self, message: str):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def update_status(self):
        known = get_known_words()
        self.lbl_known.config(text=f"Vocabulário Conhecido: {len(known)} palavras")
        
        if check_connection():
            self.log("🟢 Conectado ao Anki Desktop via AnkiConnect.")
        else:
            self.log("⚠️ Anki Desktop não detectado! Abra o Anki para enviar ou use a exportação de arquivos .apkg.")

    def validate_api_key(self) -> bool:
        key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not key or key == "sua_chave_api_aqui":
            messagebox.showwarning(
                "Configuração Necessária",
                "A chave da API do DeepSeek não foi configurada!\n\n"
                "Edite o arquivo .env no diretório do projeto e insira sua chave:\n"
                "DEEPSEEK_API_KEY=sk-sua-chave-real"
            )
            return False
        return True

    def on_click_attach_file(self, section_key: str):
        file_path = filedialog.askopenfilename(
            title="Selecionar Arquivo",
            filetypes=[("Arquivos Suportados", "*.pdf;*.txt;*.md"), ("Arquivos PDF", "*.pdf"), ("Arquivos de Texto", "*.txt;*.md"), ("Todos os Arquivos", "*.*")]
        )
        if file_path:
            self.attached_files[section_key] = file_path
            filename = os.path.basename(file_path)
            label_widget = getattr(self, f"lbl_file_{section_key}", None)
            if label_widget:
                label_widget.config(text=f"📎 Anexado: {filename}", fg="#a6e3a1")
            self.log(f"📁 Arquivo anexado [{section_key.upper()}]: {file_path}")

    # Enviar Baralho Predefinido com 1 clique (SENAI, ESAMC, Cargill)
    def send_preset_to_anki(self, category: str):
        if category == "SENAI":
            cards = get_all_senai_cards_flat()
            deck_name = "SENAI::Aprendizagem Administrativa Completo"
        elif category == "ESAMC":
            cards = ESAMC_CARDS
            deck_name = "ESAMC::Sistemas de Informação"
        elif category == "Cargill":
            cards = CARGILL_CARDS
            deck_name = "Cargill::Geral e EHS"
        else:
            return

        if not check_connection():
            messagebox.showwarning("Anki Desconectado", "Abra o Anki Desktop para enviar diretamente ou use a opção de baixar o arquivo .apkg!")
            return

        def worker():
            self.log(f"\n🚀 Enviando baralho completo de revisão '{deck_name}' ({len(cards)} cards) para o Anki...")
            created = 0
            for c in cards:
                try:
                    add_note(
                        front_content=c["front"],
                        back_content=c["back"],
                        deck_name=deck_name,
                        tags=[category, "Revisão", "Automação"]
                    )
                    record_card(category, c["front"], c["back"])
                    created += 1
                except Exception as e:
                    self.log(f" ❌ Erro ao enviar card: {e}")
            self.log(f"✅ Sucesso! {created} cards enviados para o baralho '{deck_name}' no Anki!")
            self.root.after(0, self.load_history_data)

        threading.Thread(target=worker, daemon=True).start()

    def export_preset_apkg(self, category: str):
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        file_map = {
            "SENAI": ("SENAI_Aprendizagem_Completo.apkg", "SENAI::Aprendizagem Completo", get_all_senai_cards_flat()),
            "ESAMC": ("ESAMC_Sistemas_Informacao.apkg", "ESAMC::Sistemas de Informação", ESAMC_CARDS),
            "Cargill": ("Cargill_Flashcards.apkg", "Cargill::Geral e EHS", CARGILL_CARDS)
        }

        if category not in file_map:
            return

        fname, deck_name, cards = file_map[category]
        save_path = filedialog.asksaveasfilename(
            title=f"Salvar Baralho .apkg ({category})",
            defaultextension=".apkg",
            filetypes=[("Baralho do Anki (*.apkg)", "*.apkg")],
            initialfile=fname
        )
        if save_path:
            try:
                export_cards_to_apkg(deck_name, cards, output_path=save_path)
                messagebox.showinfo("Sucesso", f"Baralho .apkg salvo em:\n{save_path}")
                self.log(f"📦 Baralho .apkg salvo: {save_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar .apkg: {e}")

    # Geração Dinâmica via IA para seções específicas
    def on_click_generate_custom(self, category: str, subject: str, text_widget: scrolledtext.ScrolledText, section_key: str):
        if not self.validate_api_key():
            return

        text_content = text_widget.get("1.0", tk.END).strip()
        attached_path = self.attached_files.get(section_key, "")

        if attached_path:
            try:
                self.log(f"\n📖 Lendo arquivo anexado [{section_key.upper()}]...")
                file_text = extract_text_from_file(attached_path)
                text_content = file_text + "\n\n" + text_content
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao ler arquivo: {e}")
                return

        if not text_content.strip():
            messagebox.showwarning("Aviso", "Anexe um arquivo (PDF/TXT) ou cole o resumo/texto da aula!")
            return

        deck_name = f"{category}::{subject}"

        def worker():
            try:
                self.log(f"\n🧠 Gerando flashcards para '{deck_name}' via DeepSeek...")
                cards = generate_college_flashcards(f"{category}: {subject}", text_content, num_cards=8)
                self.log(f"💡 {len(cards)} cards gerados! Enviando ao Anki...")

                created_count = 0
                for c in cards:
                    front = c.get("front", "")
                    back = c.get("back", "")
                    if front and back:
                        add_note(
                            front_content=front,
                            back_content=back,
                            deck_name=deck_name,
                            tags=[category, subject, "Automação"]
                        )
                        record_card(category, front, back)
                        created_count += 1
                        self.log(f"  • Card: \"{front[:40]}...\"")

                self.log(f"✅ {created_count} cards adicionados a '{deck_name}'!")
            except Exception as e:
                self.log(f"❌ Erro ao gerar cards: {e}")
            finally:
                self.root.after(0, self.load_history_data)

        threading.Thread(target=worker, daemon=True).start()

    # Roteamento Automático Seção Geral
    def on_click_auto_route_geral(self):
        if not self.validate_api_key():
            return

        text_content = self.txt_geral.get("1.0", tk.END).strip()
        attached_path = self.attached_files.get("geral", "")

        if attached_path:
            try:
                self.log(f"\n📖 Lendo arquivo anexado na seção Geral...")
                file_text = extract_text_from_file(attached_path)
                text_content = file_text + "\n\n" + text_content
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao ler arquivo: {e}")
                return

        if not text_content.strip():
            messagebox.showwarning("Aviso", "Cole um resumo ou anexe um arquivo na seção Geral!")
            return

        self.btn_gen_geral.config(state="disabled", text="⏳ Analisando e Classificando via IA...")

        def worker():
            try:
                self.log(f"\n⚡ Roteador Inteligente ativado: analisando o conteúdo...")
                res = auto_route_and_generate(text_content, num_cards=8)

                category = res.get("category", "Geral")
                deck_name = res.get("deck_name", "Geral")
                cards = res.get("cards", [])

                self.log(f"🎯 Assunto Detectado: Categoria '{category}' -> Baralho Target: '{deck_name}'")
                self.log(f"💡 {len(cards)} flashcards gerados! Enviando ao Anki...")

                created_count = 0
                for c in cards:
                    front = c.get("front", "")
                    back = c.get("back", "")
                    if front and back:
                        add_note(
                            front_content=front,
                            back_content=back,
                            deck_name=deck_name,
                            tags=[category, "AutoDeck", "Automação"]
                        )
                        record_card(category, front, back)
                        created_count += 1
                        self.log(f"  • Card: \"{front[:40]}...\"")

                self.log(f"✅ Concluído! {created_count} cards direcionados para '{deck_name}'!")
            except Exception as e:
                self.log(f"❌ Erro no Roteador Inteligente: {e}")
            finally:
                self.root.after(0, self.finish_geral_route)

        threading.Thread(target=worker, daemon=True).start()

    def finish_geral_route(self):
        self.btn_gen_geral.config(state="normal", text="🚀 Processar Texto e Auto-Direcionar para o Deck Correto no Anki")
        self.txt_geral.delete("1.0", tk.END)
        self.load_history_data()

    # Lógica de Inglês
    def on_click_generate_english(self):
        if not self.validate_api_key():
            return

        raw_text = self.txt_words.get("1.0", tk.END).strip()
        words = parse_word_list(raw_text)

        if not words:
            messagebox.showwarning("Aviso", "Cole pelo menos uma palavra em inglês!")
            return

        multi_sense = self.var_multi_meaning.get()
        check_dup = self.var_check_dup.get()

        self.btn_generate_eng.config(state="disabled", text="⏳ Gerando...")
        self.txt_words.delete("1.0", tk.END)

        def worker():
            for word in words:
                if check_dup and is_word_known(word):
                    self.log(f"ℹ️ A palavra '{word}' já consta no seu banco de vocabulário.")

                self.log(f"\n🔍 Processando palavra: '{word}'...")
                try:
                    success = process_single_word(word, multi_meaning=multi_sense)
                    if success:
                        self.log(f"✅ Cards da palavra '{word}' criados no Anki!")
                    else:
                        self.log(f"❌ Falha ao criar card para '{word}'.")
                except Exception as e:
                    self.log(f"❌ Erro: {e}")
            
            self.root.after(0, self.finish_english_generate)

        threading.Thread(target=worker, daemon=True).start()

    def finish_english_generate(self):
        self.btn_generate_eng.config(state="normal", text="🚀 Criar e Enviar para o Anki (Baralho Inglês)")
        self.update_status()
        self.load_history_data()

    def export_apkg_action(self, subject: str):
        rows = get_recent_cards(limit=100)
        if not rows:
            messagebox.showwarning("Aviso", "Não há cards no histórico recente para exportar!")
            return

        save_path = filedialog.asksaveasfilename(
            title="Salvar Baralho .apkg",
            defaultextension=".apkg",
            filetypes=[("Baralho do Anki (*.apkg)", "*.apkg")],
            initialfile=f"{subject or 'Baralho_Anki'}.apkg"
        )
        if not save_path:
            return

        cards_list = [{"front": r[2], "back": r[3]} for r in rows]

        try:
            export_cards_to_apkg(subject or "Inglês", cards_list, output_path=save_path)
            messagebox.showinfo("Exportado!", f"Baralho .apkg salvo em:\n{save_path}")
            self.log(f"📦 Baralho .apkg exportado para: {save_path}")
        except Exception as e:
            messagebox.showerror("Erro de Exportação", f"Erro: {e}")

    def on_click_sync(self):
        def worker():
            self.log("\n🔄 Sincronizando vocabulário do Anki...")
            try:
                count = extract_vocabulary_from_anki_deck()
                self.log(f"✅ Sincronização concluída! {count} novas palavras adicionadas.")
            except Exception as e:
                self.log(f"❌ Erro ao sincronizar: {e}")
            self.root.after(0, self.update_status)

        threading.Thread(target=worker, daemon=True).start()

def launch():
    root = tk.Tk()
    app = AnkiAutomationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch()
