"""Interface única para analisar materiais, revisar o plano e enviar ao Anki."""

import html
import os
import re
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.anki_client import add_note, check_connection, create_deck, get_deck_names, refresh_anki_gui
from src.auto_router import auto_route_and_generate
from src.college_service import extract_text_from_file
from src.context_library import context_count, find_relevant_context, init_context_library, save_context
from src.database import get_recent_cards, init_db, record_card
from src.deck_structure import missing_recommended_decks


class AnkiAutomationGUI:
    """Uma única jornada: material -> plano de revisão -> conferência -> Anki."""

    BG = "#11111b"
    SURFACE = "#1e1e2e"
    CARD = "#313244"
    TEXT = "#cdd6f4"
    MUTED = "#a6adc8"
    BLUE = "#89b4fa"
    GREEN = "#a6e3a1"
    YELLOW = "#f9e2af"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Anki Studio — revisão com contexto")
        self.root.geometry("1020x790")
        self.root.minsize(900, 680)
        self.root.configure(bg=self.BG)
        self.attached_file = ""
        self.available_decks: list[str] = []
        self.plan: dict = {}
        self._configure_style()
        init_db()
        init_context_library()
        self._build_ui()
        self.refresh_connection()

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Deck.TCombobox", fieldbackground="#181825", background="#45475a", foreground=self.TEXT)
        style.map("Deck.TCombobox", fieldbackground=[("readonly", "#181825")], foreground=[("readonly", self.TEXT)])
        style.configure("History.Treeview", background="#181825", foreground=self.TEXT, fieldbackground="#181825", rowheight=26)
        style.configure("History.Treeview.Heading", background="#45475a", foreground=self.TEXT, font=("Segoe UI", 9, "bold"))

    def _label(self, parent, text, size=10, bold=False, fg=None, **kwargs):
        return tk.Label(parent, text=text, font=("Segoe UI", size, "bold" if bold else "normal"), bg=parent.cget("bg"), fg=fg or self.TEXT, **kwargs)

    def _button(self, parent, text, command, primary=False, **kwargs):
        font = kwargs.pop("font", ("Segoe UI", 10, "bold"))
        padx = kwargs.pop("padx", 14)
        pady = kwargs.pop("pady", 8)
        return tk.Button(
            parent, text=text, command=command, cursor="hand2", bd=0,
            font=font, padx=padx, pady=pady,
            bg=self.GREEN if primary else "#45475a", fg="#11111b" if primary else self.TEXT,
            activebackground="#94e2d5" if primary else "#585b70", activeforeground="#11111b" if primary else self.TEXT,
            **kwargs,
        )

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.BG, padx=24, pady=16)
        header.pack(fill="x")
        self._label(header, "ANKI STUDIO", size=18, bold=True, fg=self.BLUE).pack(side="left")
        self._label(header, "Material → contexto → revisão → Anki", size=10, fg=self.MUTED).pack(side="left", padx=14, pady=(5, 0))
        self.status_label = self._label(header, "Verificando Anki…", size=9, fg=self.YELLOW)
        self.status_label.pack(side="right", pady=(5, 0))

        content = tk.Frame(self.root, bg=self.BG, padx=24)
        content.pack(fill="both", expand=True)

        input_card = tk.Frame(content, bg=self.SURFACE, padx=16, pady=14)
        input_card.pack(fill="x")
        self._label(input_card, "O que você quer aprender ou revisar?", size=12, bold=True).pack(anchor="w")
        self._label(
            input_card,
            "Cole suas anotações, uma transcrição, um resumo ou uma lista de termos. A IA lê o contexto e escolhe o baralho mais específico disponível.",
            size=9, fg=self.MUTED, wraplength=900, justify="left",
        ).pack(anchor="w", pady=(3, 10))

        tools = tk.Frame(input_card, bg=self.SURFACE)
        tools.pack(fill="x", pady=(0, 6))
        self._button(tools, "Anexar PDF, TXT ou MD", self.attach_file, font=("Segoe UI", 9, "bold"), padx=10, pady=5).pack(side="left")
        self.file_label = self._label(tools, "Nenhum arquivo anexado", size=9, fg=self.MUTED)
        self.file_label.pack(side="left", padx=10)
        self.save_context_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            tools, text="Guardar na biblioteca de contexto", variable=self.save_context_var,
            bg=self.SURFACE, fg=self.MUTED, selectcolor="#181825", activebackground=self.SURFACE,
            activeforeground=self.TEXT, font=("Segoe UI", 9),
        ).pack(side="right", padx=10)
        self._button(tools, "Limpar", self.clear_material, font=("Segoe UI", 9, "bold"), padx=10, pady=5).pack(side="right")

        self.material = scrolledtext.ScrolledText(
            input_card, height=9, wrap="word", font=("Segoe UI", 10), bg="#181825", fg=self.TEXT,
            insertbackground=self.TEXT, relief="flat", padx=10, pady=10,
        )
        self.material.pack(fill="x")

        action_row = tk.Frame(input_card, bg=self.SURFACE, pady=12)
        action_row.pack(fill="x")
        self._label(
            action_row,
            "A IA define a quantidade necessária para cobrir o material.",
            size=9,
            fg=self.MUTED,
        ).pack(side="left")
        self.analyze_button = self._button(action_row, "Analisar e montar revisão", self.analyze_material, primary=True)
        self.analyze_button.pack(side="right")

        self.plan_card = tk.Frame(content, bg=self.SURFACE, padx=16, pady=14)
        self.plan_card.pack(fill="both", expand=True, pady=(14, 0))
        plan_head = tk.Frame(self.plan_card, bg=self.SURFACE)
        plan_head.pack(fill="x")
        self._label(plan_head, "Plano de revisão", size=12, bold=True).pack(side="left")
        self.history_button = self._button(plan_head, "Histórico", self.show_history, font=("Segoe UI", 9, "bold"), padx=10, pady=5)
        self.history_button.pack(side="right")
        self.plan_status = self._label(plan_head, "Envie um material para começar.", size=9, fg=self.MUTED)
        self.plan_status.pack(side="right", padx=12)

        self.summary = self._label(self.plan_card, "", size=10, fg=self.TEXT, justify="left", anchor="w", wraplength=900)
        self.summary.pack(fill="x", pady=(8, 6))

        destination = tk.Frame(self.plan_card, bg=self.CARD, padx=10, pady=8)
        destination.pack(fill="x", pady=(0, 8))
        self._label(destination, "Destino no Anki", size=9, bold=True, fg=self.BLUE).pack(side="left")
        self.deck_value = tk.StringVar()
        self.deck_picker = ttk.Combobox(destination, textvariable=self.deck_value, state="readonly", style="Deck.TCombobox", width=46)
        self.deck_picker.pack(side="left", padx=12, fill="x", expand=True)
        self._button(destination, "Atualizar baralhos", self.refresh_connection, primary=True, font=("Segoe UI", 8, "bold"), padx=8, pady=4).pack(side="right")
        self._button(destination, "Criar estrutura base", self.create_study_structure, font=("Segoe UI", 8, "bold"), padx=8, pady=4).pack(side="right", padx=(0, 6))

        self.preview = scrolledtext.ScrolledText(
            self.plan_card, height=11, wrap="word", font=("Segoe UI", 10), bg="#181825", fg=self.TEXT,
            state="disabled", relief="flat", padx=10, pady=10,
        )
        self.preview.pack(fill="both", expand=True)

        send_row = tk.Frame(self.plan_card, bg=self.SURFACE)
        send_row.pack(fill="x", pady=(10, 0))
        self.send_button = self._button(send_row, "Enviar cards aprovados ao Anki", self.send_to_anki, primary=True, state="disabled")
        self.send_button.pack(side="right")
        self._label(send_row, "Você pode trocar o destino acima antes de enviar.", size=9, fg=self.MUTED).pack(side="right", padx=12, pady=10)

    def _ui(self, callback, *args):
        self.root.after(0, lambda: callback(*args))

    def _set_preview(self, text: str):
        self.preview.config(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert("1.0", text)
        self.preview.config(state="disabled")

    def refresh_connection(self):
        if check_connection():
            try:
                self.available_decks = get_deck_names()
                self.status_label.config(text=f"Anki conectado · {len(self.available_decks)} baralhos", fg=self.GREEN)
                selected_deck = self.deck_value.get().strip()
                self.deck_picker["values"] = self.available_decks
                if selected_deck and selected_deck not in self.available_decks:
                    self.deck_value.set("")
                if self.plan:
                    self.plan_status.config(text=f"Lista atualizada: {len(self.available_decks)} baralhos disponíveis.", fg=self.GREEN)
            except Exception as error:
                self.status_label.config(text=f"Falha ao ler baralhos: {error}", fg=self.YELLOW)
        else:
            self.available_decks = []
            self.status_label.config(text="Abra o Anki Desktop com AnkiConnect", fg=self.YELLOW)

    def create_study_structure(self):
        """Cria apenas os baralhos recomendados que ainda não existirem."""
        if not check_connection():
            messagebox.showwarning("Anki não conectado", "Abra o Anki Desktop com o AnkiConnect para criar a estrutura.")
            return
        self.refresh_connection()
        missing = missing_recommended_decks(self.available_decks)
        if not missing:
            messagebox.showinfo("Estrutura pronta", "Os baralhos recomendados já existem no Anki.")
            return
        try:
            for deck in missing:
                create_deck(deck)
            self.refresh_connection()
            self.deck_picker["values"] = self.available_decks
            self.plan_status.config(text=f"Estrutura criada: {len(missing)} novos baralhos.", fg=self.GREEN)
        except Exception as error:
            messagebox.showerror("Falha ao criar baralhos", str(error))

    def attach_file(self):
        path = filedialog.askopenfilename(
            title="Escolha o material de estudo",
            filetypes=[("Materiais suportados", "*.pdf;*.txt;*.md"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self.attached_file = path
            self.file_label.config(text=f"Anexado: {os.path.basename(path)}", fg=self.GREEN)

    def clear_material(self):
        self.attached_file = ""
        self.file_label.config(text="Nenhum arquivo anexado", fg=self.MUTED)
        self.material.delete("1.0", tk.END)

    def _get_material(self) -> str:
        text = self.material.get("1.0", tk.END).strip()
        if self.attached_file:
            text_from_file = extract_text_from_file(self.attached_file)
            text = f"{text_from_file}\n\n--- Observações adicionadas pelo aluno ---\n{text}" if text else text_from_file
        return text

    def analyze_material(self):
        if not check_connection():
            messagebox.showwarning("Anki não conectado", "Abra o Anki Desktop com o AnkiConnect. Assim a IA escolhe entre os seus baralhos reais.")
            return
        try:
            text = self._get_material()
        except Exception as error:
            messagebox.showerror("Não foi possível ler o arquivo", str(error))
            return
        if not text:
            messagebox.showwarning("Material vazio", "Cole um texto ou anexe um PDF, TXT ou MD.")
            return

        self.refresh_connection()
        self.analyze_button.config(state="disabled", text="Lendo contexto e organizando…")
        self.plan_status.config(text="A IA está preparando a revisão…", fg=self.YELLOW)
        self.send_button.config(state="disabled")
        reference_context = find_relevant_context(text)
        source_title = os.path.basename(self.attached_file) if self.attached_file else "Material colado"
        should_save_context = self.save_context_var.get()

        def worker():
            try:
                plan = auto_route_and_generate(
                    text,
                    self.available_decks,
                    max_cards=40,
                    reference_context=reference_context,
                )
                if should_save_context:
                    save_context(source_title, text, "arquivo" if self.attached_file else "texto")
                self._ui(self.show_plan, plan)
            except Exception as error:
                self._ui(self.show_analysis_error, str(error))

        threading.Thread(target=worker, daemon=True).start()

    def show_analysis_error(self, error: str):
        self.analyze_button.config(state="normal", text="Analisar e montar revisão")
        self.plan_status.config(text="Não foi possível montar o plano.", fg="#f38ba8")
        messagebox.showerror("Erro na análise", error)

    def show_plan(self, plan: dict):
        self.plan = plan
        self.analyze_button.config(state="normal", text="Analisar e montar revisão")
        cards = plan.get("cards", [])
        if not cards:
            self.plan_status.config(text="O material não trouxe conteúdo suficiente para cards confiáveis.", fg=self.YELLOW)
            self._set_preview("A IA preferiu não completar lacunas com suposições. Acrescente mais contexto ao material e tente de novo.")
            return

        suggested = plan.get("suggested_deck_name", "")
        selected = plan.get("deck_name") or suggested
        deck_values = list(self.available_decks)
        if suggested and suggested not in deck_values:
            deck_values.append(suggested)
        self.deck_picker["values"] = deck_values
        self.deck_value.set(selected if selected else "")

        confidence = round(float(plan.get("confidence", 0)) * 100)
        self.summary.config(
            text=(f"{plan.get('subject', 'Assunto a revisar')} · nível {plan.get('level', 'não identificado')} · "
                  f"confiança do roteamento: {confidence}%\n"
                  f"{plan.get('routing_reason', '')}\n"
                  f"Contexto de estudo: {plan.get('study_note', '')}\n"
                  f"Cobertura: {plan.get('coverage_summary', '')}\n"
                  f"Biblioteca local: {context_count()} material(is) salvos para dar contexto às próximas revisões.")
        )
        preview_lines = []
        for index, card in enumerate(cards, 1):
            front = re.sub(r"<[^>]+>", "", card["front"])
            back = re.sub(r"<[^>]+>", "", html.unescape(card["back"]))
            preview_lines.append(f"{index}. {front}\n   {back}\n")
        self._set_preview("\n".join(preview_lines))
        self.plan_status.config(text=f"{len(cards)} cards prontos para revisão.", fg=self.GREEN)
        self.send_button.config(state="normal", text=f"Enviar {len(cards)} cards ao Anki")

    def send_to_anki(self):
        cards = self.plan.get("cards", [])
        deck_name = self.deck_value.get().strip()
        if not cards or not deck_name:
            messagebox.showwarning("Plano incompleto", "Gere os cards e escolha um baralho antes de enviar.")
            return
        if not check_connection():
            messagebox.showwarning("Anki desconectado", "Abra o Anki Desktop antes de enviar os cards.")
            return

        self.send_button.config(state="disabled", text="Enviando…")
        self.plan_status.config(text=f"Enviando para {deck_name}…", fg=self.YELLOW)

        def worker():
            created, failures = 0, []
            tags = ["Automação", "Revisão guiada", *self.plan.get("tags", [])]
            for card in cards:
                try:
                    add_note(card["front"], card["back"], deck_name=deck_name, tags=tags)
                    record_card(self.plan.get("subject", "Geral"), card["front"], card["back"])
                    created += 1
                except Exception as error:
                    failures.append(str(error))
            self._ui(self.finish_send, created, failures, deck_name)

        threading.Thread(target=worker, daemon=True).start()

    def finish_send(self, created: int, failures: list[str], deck_name: str):
        refresh_anki_gui()
        if failures:
            self.plan_status.config(text=f"{created} cards enviados; {len(failures)} falharam.", fg=self.YELLOW)
            self.send_button.config(state="disabled", text="Envio concluído com pendências")
            messagebox.showwarning("Envio parcial", "\n".join(failures[:2]))
        else:
            self.plan_status.config(text=f"{created} cards enviados para {deck_name}.", fg=self.GREEN)
            self.send_button.config(state="disabled", text=f"✅ {created} cards enviados ao Anki")
            messagebox.showinfo("Cards Enviados!", f"✅ {created} flashcards foram criados e adicionados ao baralho '{deck_name}' no seu Anki Desktop com sucesso!\n\nVerifique a lista no seu Anki Desktop.")

    def show_history(self):
        window = tk.Toplevel(self.root)
        window.title("Histórico de cards")
        window.geometry("900x440")
        window.configure(bg=self.SURFACE)
        columns = ("data", "assunto", "frente", "verso")
        tree = ttk.Treeview(window, columns=columns, show="headings", style="History.Treeview")
        for column, title, width in [("data", "Data", 120), ("assunto", "Assunto", 150), ("frente", "Frente", 300), ("verso", "Verso", 300)]:
            tree.heading(column, text=title)
            tree.column(column, width=width, anchor="w")
        for _, subject, front, back, created_at in get_recent_cards(100):
            tree.insert("", "end", values=(created_at, subject, re.sub(r"<[^>]+>", "", front)[:120], re.sub(r"<[^>]+>", "", back)[:120]))
        tree.pack(fill="both", expand=True, padx=14, pady=14)


if __name__ == "__main__":
    app_root = tk.Tk()
    AnkiAutomationGUI(app_root)
    app_root.mainloop()
