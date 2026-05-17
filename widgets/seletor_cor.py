"""
widgets/seletor_cor.py — Seletor de cor customizado no tema SICRO
Paleta de cores pre-definidas + campo hex manual.

Uso:
    from widgets.seletor_cor import escolher_cor
    nova = escolher_cor(parent, cor_atual="#FF1A1A")
    if nova:   # retorna "#RRGGBB" ou None se cancelou
        ...
"""
import tkinter as tk
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))

from tema import (
    FUNDO_BASE, FUNDO_PAINEL, FUNDO_CARD, FUNDO_HOVER,
    DOURADO, AZUL_BORDA, AZUL_MEDIO, AZUL_CLARO,
    TEXTO_PRIMARIO, TEXTO_SECUNDARIO, TEXTO_TERCIARIO,
    FONTE_H3, FONTE_BODY, FONTE_BODY_BOLD, FONTE_SMALL,
    FONTE_MICRO, COR_PERIGO,
)

# Paleta pericial — cores mais usadas em croqui de transito
PALETA = [
    "#FF1A1A", "#D32F2F", "#B71C1C", "#FF6F00",  # vermelhos/laranja
    "#F0B429", "#FBC02D", "#FFEB3B", "#FFF59D",  # amarelos
    "#2E7D32", "#43A047", "#66BB6A", "#A5D6A7",  # verdes
    "#0A3D8F", "#1565C0", "#1E88E5", "#64B5F6",  # azuis
    "#4A148C", "#6A1B9A", "#8E24AA", "#BA68C8",  # roxos
    "#3E2723", "#5D4037", "#795548", "#A1887F",  # marrons
    "#000000", "#424242", "#757575", "#BDBDBD",  # cinzas
    "#FFFFFF", "#ECEFF1", "#90A4AE", "#546E7A",  # claros/neutros
]


class _SeletorCor(tk.Toplevel):
    def __init__(self, parent, cor_atual="#888888"):
        super().__init__(parent)
        self.resultado = None
        self._cor = cor_atual if cor_atual else "#888888"

        self.overrideredirect(True)
        self.configure(bg=FUNDO_PAINEL,
                        highlightbackground=DOURADO, highlightthickness=1)
        self.grab_set()
        self.attributes("-topmost", True)

        ww, wh = 340, 420
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")

        self._build()
        self.bind("<Escape>", lambda e: self._cancelar())
        self.bind("<Return>", lambda e: self._ok())

    def _build(self):
        tk.Frame(self, bg=DOURADO, height=3).pack(fill="x")

        # Titulo + fechar
        tbar = tk.Frame(self, bg=FUNDO_PAINEL, height=38)
        tbar.pack(fill="x"); tbar.pack_propagate(False)
        tk.Label(tbar, text="  Selecionar cor", font=FONTE_H3,
                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side="left", pady=8)
        fx = tk.Label(tbar, text="✕  ", font=("Segoe UI", 12),
                      bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO, cursor="hand2")
        fx.pack(side="right", pady=8)
        fx.bind("<Button-1>", lambda e: self._cancelar())
        fx.bind("<Enter>", lambda e: fx.config(fg="#E08080"))
        fx.bind("<Leave>", lambda e: fx.config(fg=TEXTO_SECUNDARIO))

        tk.Frame(self, bg=AZUL_BORDA, height=1).pack(fill="x")

        corpo = tk.Frame(self, bg=FUNDO_PAINEL)
        corpo.pack(fill="both", expand=True, padx=18, pady=14)

        # ── Paleta ──
        tk.Label(corpo, text="PALETA", font=FONTE_MICRO,
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(anchor="w")
        grid = tk.Frame(corpo, bg=FUNDO_PAINEL)
        grid.pack(fill="x", pady=(6, 14))
        cols = 8
        cell = 32
        for i, cor in enumerate(PALETA):
            r, c = divmod(i, cols)
            sw_ = tk.Frame(grid, bg=cor, width=cell, height=cell,
                           cursor="hand2",
                           highlightbackground=AZUL_BORDA,
                           highlightthickness=1)
            sw_.grid(row=r, column=c, padx=2, pady=2)
            sw_.pack_propagate(False)
            sw_.bind("<Button-1>", lambda e, k=cor: self._pick(k))
            def _ein(e, w=sw_):
                w.config(highlightbackground=DOURADO, highlightthickness=2)
            def _eout(e, w=sw_):
                w.config(highlightbackground=AZUL_BORDA, highlightthickness=1)
            sw_.bind("<Enter>", _ein)
            sw_.bind("<Leave>", _eout)

        # ── Campo hex ──
        tk.Label(corpo, text="CÓDIGO HEX", font=FONTE_MICRO,
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(anchor="w")
        hexrow = tk.Frame(corpo, bg=FUNDO_PAINEL)
        hexrow.pack(fill="x", pady=(6, 14))
        tk.Label(hexrow, text="#", font=FONTE_BODY_BOLD,
                 bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO).pack(side="left")
        self._hex_var = tk.StringVar(value=self._cor.lstrip("#").upper())
        self._hex_entry = tk.Entry(hexrow, textvariable=self._hex_var,
                                   font=("Consolas", 12),
                                   bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,
                                   insertbackground=DOURADO,
                                   relief="flat", bd=5, width=10,
                                   highlightthickness=1,
                                   highlightcolor=DOURADO,
                                   highlightbackground=AZUL_BORDA)
        self._hex_entry.pack(side="left", padx=(4, 10))
        self._hex_var.trace_add("write", lambda *a: self._hex_changed())

        # ── Preview ──
        tk.Label(corpo, text="PRÉVIA", font=FONTE_MICRO,
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(anchor="w")
        prev_wrap = tk.Frame(corpo, bg=AZUL_BORDA,
                             highlightthickness=0)
        prev_wrap.pack(fill="x", pady=(6, 0))
        self._preview = tk.Frame(prev_wrap, bg=self._cor, height=54)
        self._preview.pack(fill="x", padx=1, pady=1)
        self._preview.pack_propagate(False)
        self._lbl_prev = tk.Label(self._preview, text=self._cor.upper(),
                                  font=FONTE_BODY_BOLD, bg=self._cor,
                                  fg=self._contraste(self._cor))
        self._lbl_prev.pack(expand=True)

        tk.Frame(self, bg=AZUL_BORDA, height=1).pack(fill="x")

        # ── Botoes ──
        bt = tk.Frame(self, bg=FUNDO_PAINEL)
        bt.pack(fill="x", padx=18, pady=12)

        bcancel = tk.Frame(bt, bg=FUNDO_CARD, cursor="hand2")
        bcancel.pack(side="right", padx=(8, 0))
        lc = tk.Label(bcancel, text="Cancelar", font=FONTE_SMALL,
                      bg=FUNDO_CARD, fg=TEXTO_SECUNDARIO, padx=16, pady=7)
        lc.pack()
        for w in (bcancel, lc):
            w.bind("<Button-1>", lambda e: self._cancelar())
            w.bind("<Enter>", lambda e: (bcancel.config(bg=FUNDO_HOVER),
                                          lc.config(bg=FUNDO_HOVER)))
            w.bind("<Leave>", lambda e: (bcancel.config(bg=FUNDO_CARD),
                                          lc.config(bg=FUNDO_CARD)))

        bok = tk.Frame(bt, bg=AZUL_MEDIO, cursor="hand2")
        bok.pack(side="right")
        lo = tk.Label(bok, text="Aplicar", font=FONTE_BODY_BOLD,
                      bg=AZUL_MEDIO, fg=TEXTO_PRIMARIO, padx=20, pady=7)
        lo.pack()
        for w in (bok, lo):
            w.bind("<Button-1>", lambda e: self._ok())
            w.bind("<Enter>", lambda e: (bok.config(bg=AZUL_CLARO),
                                          lo.config(bg=AZUL_CLARO)))
            w.bind("<Leave>", lambda e: (bok.config(bg=AZUL_MEDIO),
                                          lo.config(bg=AZUL_MEDIO)))

        tk.Frame(self, bg=DOURADO, height=3).pack(fill="x", side="bottom")

    # ── helpers ──
    def _contraste(self, hexcor):
        """Texto preto ou branco conforme luminancia do fundo."""
        try:
            h = hexcor.lstrip("#")
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            lum = (0.299*r + 0.587*g + 0.114*b)
            return "#000000" if lum > 140 else "#FFFFFF"
        except Exception:
            return "#FFFFFF"

    def _valida_hex(self, s):
        s = s.strip().lstrip("#")
        if len(s) != 6:
            return None
        try:
            int(s, 16)
            return "#" + s.upper()
        except ValueError:
            return None

    def _pick(self, cor):
        self._cor = cor
        self._hex_var.set(cor.lstrip("#").upper())
        self._aplicar_preview(cor)

    def _hex_changed(self):
        cor = self._valida_hex(self._hex_var.get())
        if cor:
            self._cor = cor
            self._aplicar_preview(cor)
            self._hex_entry.config(highlightbackground=AZUL_BORDA)
        else:
            self._hex_entry.config(highlightbackground=COR_PERIGO)

    def _aplicar_preview(self, cor):
        try:
            self._preview.config(bg=cor)
            self._lbl_prev.config(bg=cor, text=cor.upper(),
                                  fg=self._contraste(cor))
        except Exception:
            pass

    def _ok(self):
        cor = self._valida_hex(self._hex_var.get())
        if cor:
            self.resultado = cor
            self.destroy()
        else:
            self._hex_entry.config(highlightbackground=COR_PERIGO)

    def _cancelar(self):
        self.resultado = None
        self.destroy()


def escolher_cor(parent, cor_atual="#888888"):
    """Abre o seletor e retorna '#RRGGBB' ou None se cancelado."""
    dlg = _SeletorCor(parent, cor_atual)
    parent.wait_window(dlg)
    return dlg.resultado
