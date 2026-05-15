"""
patch_titlebar.py — Adiciona barra de titulo customizada ao SICRO
Execute: python patch_titlebar.py
"""
from pathlib import Path

main_path = Path("main.py")
main = main_path.read_text(encoding="utf-8")

# Adiciona classe TitleBar e metodos de drag antes do AppSicro
old_appsicro = "class AppSicro(tk.Tk):"

new_titlebar = '''class TitleBar:
    """Barra de titulo customizada — substitui a barra padrao do Windows."""

    def __init__(self, janela, titulo="SICRO PCI/AP"):
        from tema import (
            FUNDO_PAINEL, DOURADO, TEXTO_PRIMARIO,
            TEXTO_TERCIARIO, FUNDO_HOVER
        )
        self._win = janela
        self._drag_x = 0
        self._drag_y = 0

        bar = tk.Frame(janela, bg=FUNDO_PAINEL, height=32)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Faixa dourada topo
        tk.Frame(janela, bg=DOURADO, height=4).pack(fill="x", side="top")
        # Reempacota: dourada em cima, bar embaixo
        bar.pack_forget()
        tk.Frame(janela, bg=DOURADO, height=4).pack(fill="x")
        bar = tk.Frame(janela, bg=FUNDO_PAINEL, height=32)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Logo + titulo
        esq = tk.Frame(bar, bg=FUNDO_PAINEL)
        esq.pack(side="left", padx=14, fill="y")
        tk.Label(esq, text="SICRO", font=("Segoe UI", 11, "bold"),
                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side="left")
        tk.Label(esq, text="  Sistema de Croquis Periciais",
                 font=("Segoe UI", 8),
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(side="left")

        # Botoes de controle
        dir_ = tk.Frame(bar, bg=FUNDO_PAINEL)
        dir_.pack(side="right", fill="y")

        def _btn(parent, texto, cmd, hover_cor="#C42B2B", fg=TEXTO_PRIMARIO):
            b = tk.Button(parent, text=texto,
                          font=("Segoe UI", 11),
                          bg=FUNDO_PAINEL, fg=fg,
                          activebackground=hover_cor,
                          activeforeground=TEXTO_PRIMARIO,
                          relief="flat", bd=0,
                          padx=14, pady=4,
                          cursor="hand2",
                          command=cmd)
            b.pack(side="left", fill="y")
            return b

        _btn(dir_, "─", self._minimizar,  hover_cor=FUNDO_HOVER)
        self._btn_max = _btn(dir_, "□", self._maximizar, hover_cor=FUNDO_HOVER)
        _btn(dir_, "✕", self._fechar,     hover_cor="#C42B2B")

        # Drag para mover janela (so funciona fora do modo zoomed)
        for w in [bar, esq] + list(esq.winfo_children()):
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<B1-Motion>",       self._drag_move)
            w.bind("<Double-Button-1>", self._maximizar)

    def _drag_start(self, e):
        if self._win.state() == "zoomed": return
        self._drag_x = e.x_root - self._win.winfo_x()
        self._drag_y = e.y_root - self._win.winfo_y()

    def _drag_move(self, e):
        if self._win.state() == "zoomed": return
        self._win.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    def _minimizar(self):
        self._win.iconify()

    def _maximizar(self, event=None):
        if self._win.state() == "zoomed":
            self._win.state("normal")
            self._btn_max.config(text="□")
        else:
            self._win.state("zoomed")
            self._btn_max.config(text="❐")

    def _fechar(self):
        self._win.destroy()


class AppSicro(tk.Tk):'''

if old_appsicro in main:
    main = main.replace(old_appsicro, new_titlebar, 1)
    print("TitleBar class ok")
else:
    print("ERRO: class AppSicro nao encontrado")

# Adiciona TitleBar no __init__ do AppSicro, apos overrideredirect
old_after_override = (
    "        # Remove barra de titulo padrao do Windows\n"
    "        self.overrideredirect(True)\n"
    "        # Restaura maximize/minimize via bind de teclado\n"
    "        self.bind('<Escape>', lambda e: self.state('normal'))\n"
)
new_after_override = (
    "        # Remove barra de titulo padrao do Windows\n"
    "        self.overrideredirect(True)\n"
    "        # Barra de titulo customizada do SICRO\n"
    "        self._titlebar = TitleBar(self)\n"
    "        # Atalhos de teclado\n"
    "        self.bind('<Escape>',  lambda e: self.state('normal'))\n"
    "        self.bind('<F11>',     lambda e: self._titlebar._maximizar())\n"
    "        self.bind('<Alt-F4>', lambda e: self.destroy())\n"
)

if old_after_override in main:
    main = main.replace(old_after_override, new_after_override, 1)
    print("TitleBar init ok")
else:
    print("AVISO: patch override nao encontrado — adicionando TitleBar manualmente")
    old_ttk = "        ttk.Style(self).theme_use(\"clam\")\n"
    if old_ttk in main:
        main = main.replace(
            old_ttk,
            old_ttk +
            "        self.overrideredirect(True)\n"
            "        self._titlebar = TitleBar(self)\n"
            "        self.bind('<F11>', lambda e: self._titlebar._maximizar())\n",
            1
        )
        print("TitleBar init adicionado via fallback")

main_path.write_text(main, encoding="utf-8")

import ast
try:
    ast.parse(main)
    print("Sintaxe main.py OK")
except SyntaxError as e:
    print(f"ERRO sintaxe: {e}")

print("\nControles:")
print("  Minimizar:  botao  ─")
print("  Maximizar:  botao  □  ou  F11")
print("  Restaurar:  botao  ❐  ou  F11")
print("  Fechar:     botao  ✕  ou  Alt+F4")
print("\nRode: python main.py")