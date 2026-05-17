"""
ui/cropador.py — Ferramenta de recorte da foto do drone
Aparece apos escolher a foto, antes de entrar no editor.
Permite selecionar uma regiao retangular e limitar a resolucao final.
"""
import tkinter as tk
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    PIL_OK = False

from tema import (
    FUNDO_BASE, FUNDO_PAINEL, FUNDO_CARD, FUNDO_HOVER,
    DOURADO, AZUL_BORDA, AZUL_MEDIO, AZUL_CLARO,
    TEXTO_PRIMARIO, TEXTO_SECUNDARIO, TEXTO_TERCIARIO,
    FONTE_H2, FONTE_H3, FONTE_BODY, FONTE_BODY_BOLD,
    FONTE_SMALL, COR_SUCESSO,
)


class CropadorImagem(tk.Toplevel):
    """
    Janela de recorte. Uso:
        c = CropadorImagem(parent, img_pil)
        parent.wait_window(c)
        if c.resultado is not None:
            img_final = c.resultado   # PIL.Image recortada/otimizada
        # se c.resultado for None => usuario cancelou
    """

    # Resolucoes maximas oferecidas (lado maior)
    OPCOES_RES = [
        ("Alta — 2500 px (nitida, recomendado)", 2500),
        ("Media — 1800 px (mais leve)", 1800),
        ("Original (sem reduzir)", 0),
    ]

    def __init__(self, parent, img_pil):
        super().__init__(parent)
        self.img_full = img_pil
        self.resultado = None
        self._res_max = 2500

        self.overrideredirect(True)
        self.configure(bg=FUNDO_PAINEL)
        self.grab_set()
        self.attributes("-topmost", True)
        self.configure(highlightbackground=DOURADO, highlightthickness=1)

        # Dimensoes da janela: grande, mas cabe na tela
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        win_w = min(1100, sw - 80)
        win_h = min(760, sh - 80)
        self.geometry(f"{win_w}x{win_h}+{(sw-win_w)//2}+{(sh-win_h)//2}")

        self._build(win_w, win_h)
        self.bind("<Escape>", lambda e: self._cancelar())

    # ──────────────────────────────────────────
    def _build(self, win_w, win_h):
        tk.Frame(self, bg=DOURADO, height=3).pack(fill="x")

        # Barra de titulo
        tbar = tk.Frame(self, bg=FUNDO_PAINEL, height=40)
        tbar.pack(fill="x"); tbar.pack_propagate(False)
        tk.Label(tbar, text="  ✂  Recortar imagem do drone",
                 font=FONTE_H3, bg=FUNDO_PAINEL,
                 fg=TEXTO_PRIMARIO).pack(side="left", pady=9)
        fx = tk.Label(tbar, text="✕  ", font=("Segoe UI", 12),
                      bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO, cursor="hand2")
        fx.pack(side="right", pady=9)
        fx.bind("<Button-1>", lambda e: self._cancelar())
        fx.bind("<Enter>", lambda e: fx.config(fg="#E08080"))
        fx.bind("<Leave>", lambda e: fx.config(fg=TEXTO_SECUNDARIO))

        tk.Frame(self, bg=AZUL_BORDA, height=1).pack(fill="x")

        # Instrucao
        inst = tk.Frame(self, bg=FUNDO_PAINEL)
        inst.pack(fill="x", padx=16, pady=(10, 4))
        tk.Label(inst,
                 text="Arraste sobre a área do acidente para selecionar. "
                      "Só a região recortada será usada — deixa o trabalho mais rápido.",
                 font=FONTE_SMALL, bg=FUNDO_PAINEL,
                 fg=TEXTO_SECUNDARIO).pack(side="left")

        # Area da imagem (canvas)
        area = tk.Frame(self, bg=FUNDO_BASE)
        area.pack(fill="both", expand=True, padx=16, pady=8)

        # Espaco disponivel para o preview
        prev_w = win_w - 32
        prev_h = win_h - 200

        # Calcula escala para caber
        iw, ih = self.img_full.width, self.img_full.height
        escala = min(prev_w / iw, prev_h / ih, 1.0)
        self._escala = escala
        disp_w = max(1, int(iw * escala))
        disp_h = max(1, int(ih * escala))

        self._canvas = tk.Canvas(area, width=disp_w, height=disp_h,
                                 bg=FUNDO_BASE, highlightthickness=0,
                                 cursor="cross")
        self._canvas.pack(expand=True)

        # Renderiza preview
        img_prev = self.img_full.resize((disp_w, disp_h), Image.LANCZOS)
        self._tk_prev = ImageTk.PhotoImage(img_prev)
        self._canvas.create_image(0, 0, anchor="nw", image=self._tk_prev)
        self._disp_w, self._disp_h = disp_w, disp_h

        # Estado da selecao (em coords do canvas)
        self._sel = None      # (x0,y0,x1,y1)
        self._rect_id = None
        self._drag_ini = None
        self._canvas.bind("<ButtonPress-1>", self._sel_ini)
        self._canvas.bind("<B1-Motion>", self._sel_mov)
        self._canvas.bind("<ButtonRelease-1>", self._sel_fim)

        # Rodape: resolucao + info + botoes
        tk.Frame(self, bg=AZUL_BORDA, height=1).pack(fill="x")
        rod = tk.Frame(self, bg=FUNDO_PAINEL)
        rod.pack(fill="x", padx=16, pady=10)

        tk.Label(rod, text="Resolução final:", font=FONTE_SMALL,
                 bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO).pack(side="left")

        self._res_var = tk.StringVar(value=self.OPCOES_RES[0][0])
        om = tk.OptionMenu(rod, self._res_var,
                           *[o[0] for o in self.OPCOES_RES],
                           command=self._mudar_res)
        om.config(font=FONTE_SMALL, bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,
                  activebackground=FUNDO_HOVER, relief="flat",
                  highlightthickness=0, bd=0, cursor="hand2")
        om["menu"].config(bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,
                          activebackground=AZUL_MEDIO,
                          font=FONTE_SMALL)
        om.pack(side="left", padx=(8, 16))

        self._lbl_info = tk.Label(rod,
                 text=f"Imagem: {iw} × {ih} px", font=FONTE_SMALL,
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO)
        self._lbl_info.pack(side="left")

        # Botoes
        btn_crop = tk.Frame(rod, bg=AZUL_MEDIO, cursor="hand2")
        btn_crop.pack(side="right")
        _lc = tk.Label(btn_crop, text="Recortar  →", font=FONTE_BODY_BOLD,
                       bg=AZUL_MEDIO, fg=TEXTO_PRIMARIO, padx=18, pady=7)
        _lc.pack()
        for w in (btn_crop, _lc):
            w.bind("<Button-1>", lambda e: self._recortar())
            w.bind("<Enter>", lambda e: (btn_crop.config(bg=AZUL_CLARO),
                                          _lc.config(bg=AZUL_CLARO)))
            w.bind("<Leave>", lambda e: (btn_crop.config(bg=AZUL_MEDIO),
                                          _lc.config(bg=AZUL_MEDIO)))

        btn_full = tk.Frame(rod, bg=FUNDO_CARD, cursor="hand2")
        btn_full.pack(side="right", padx=(0, 10))
        _lf = tk.Label(btn_full, text="Usar imagem inteira",
                       font=FONTE_SMALL, bg=FUNDO_CARD,
                       fg=TEXTO_SECUNDARIO, padx=14, pady=7)
        _lf.pack()
        for w in (btn_full, _lf):
            w.bind("<Button-1>", lambda e: self._usar_inteira())
            w.bind("<Enter>", lambda e: (btn_full.config(bg=FUNDO_HOVER),
                                          _lf.config(bg=FUNDO_HOVER)))
            w.bind("<Leave>", lambda e: (btn_full.config(bg=FUNDO_CARD),
                                          _lf.config(bg=FUNDO_CARD)))

        tk.Frame(self, bg=DOURADO, height=3).pack(fill="x", side="bottom")

    # ──────────────────────────────────────────
    #  Selecao retangular
    # ──────────────────────────────────────────
    def _sel_ini(self, e):
        self._drag_ini = (e.x, e.y)
        if self._rect_id:
            self._canvas.delete(self._rect_id)
            self._rect_id = None

    def _sel_mov(self, e):
        if not self._drag_ini:
            return
        x0, y0 = self._drag_ini
        x1 = max(0, min(e.x, self._disp_w))
        y1 = max(0, min(e.y, self._disp_h))
        if self._rect_id:
            self._canvas.delete(self._rect_id)
        # Sombreado fora + retangulo
        self._rect_id = self._canvas.create_rectangle(
            x0, y0, x1, y1, outline=DOURADO, width=2, dash=(5, 3))
        self._sel = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        self._atualizar_info()

    def _sel_fim(self, e):
        self._drag_ini = None

    def _atualizar_info(self):
        if not self._sel:
            return
        sx0, sy0, sx1, sy1 = self._sel
        # Converte para px da imagem original
        rw = int((sx1 - sx0) / self._escala)
        rh = int((sy1 - sy0) / self._escala)
        fw, fh = self._dim_final(rw, rh)
        self._lbl_info.config(
            text=f"Seleção: {rw} × {rh} px  →  saída: {fw} × {fh} px")

    def _dim_final(self, w, h):
        """Aplica limite de resolucao mantendo proporcao."""
        if self._res_max <= 0 or max(w, h) <= self._res_max:
            return w, h
        if w >= h:
            return self._res_max, max(1, int(h * self._res_max / w))
        return max(1, int(w * self._res_max / h)), self._res_max

    def _mudar_res(self, _=None):
        txt = self._res_var.get()
        for label, val in self.OPCOES_RES:
            if label == txt:
                self._res_max = val
                break
        self._atualizar_info()

    # ──────────────────────────────────────────
    #  Acoes
    # ──────────────────────────────────────────
    def _recortar(self):
        if not self._sel:
            # Sem selecao = trata como imagem inteira
            self._usar_inteira()
            return
        sx0, sy0, sx1, sy1 = self._sel
        # Converte coords do canvas -> imagem original
        ix0 = int(sx0 / self._escala)
        iy0 = int(sy0 / self._escala)
        ix1 = int(sx1 / self._escala)
        iy1 = int(sy1 / self._escala)
        ix0 = max(0, min(ix0, self.img_full.width))
        iy0 = max(0, min(iy0, self.img_full.height))
        ix1 = max(0, min(ix1, self.img_full.width))
        iy1 = max(0, min(iy1, self.img_full.height))
        if ix1 - ix0 < 10 or iy1 - iy0 < 10:
            self._usar_inteira()
            return
        rec = self.img_full.crop((ix0, iy0, ix1, iy1))
        fw, fh = self._dim_final(rec.width, rec.height)
        if (fw, fh) != (rec.width, rec.height):
            rec = rec.resize((fw, fh), Image.LANCZOS)
        self.resultado = rec.convert("RGBA")
        self.destroy()

    def _usar_inteira(self):
        img = self.img_full
        fw, fh = self._dim_final(img.width, img.height)
        if (fw, fh) != (img.width, img.height):
            img = img.resize((fw, fh), Image.LANCZOS)
        self.resultado = img.convert("RGBA")
        self.destroy()

    def _cancelar(self):
        self.resultado = None
        self.destroy()
