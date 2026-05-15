import tkinter as tk
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False
from tema import (
    FUNDO_BASE, DOURADO, AZUL_BORDA,
    TEXTO_TERCIARIO,
    SPLASH_W, SPLASH_H, SPLASH_DURACAO, SPLASH_MSGS,
)


class SplashScreen(tk.Toplevel):
    def __init__(self, parent, img_brasao=None):
        super().__init__(parent)
        self.overrideredirect(True)
        parent.withdraw()
        parent.wm_attributes('-alpha', 0)
        W, H = SPLASH_W, SPLASH_H
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f'{W}x{H}+{(sw-W)//2}+{(sh-H)//2}')
        self.configure(bg=FUNDO_BASE)
        self.lift()
        self.attributes('-topmost', True)
        self._W = W; self._H = H
        self._p = 0.0
        self._build()
        self._anim()

    def _build(self):
        W, H = self._W, self._H
        self.cv = tk.Canvas(self, width=W, height=H,
                            bg=FUNDO_BASE, highlightthickness=0)
        self.cv.place(x=0, y=0, width=W, height=H)

        # Carrega splash_bg.png — ela tem todo o visual
        bg_path = Path(__file__).parent.parent / 'assets' / 'splash_bg.png'
        self._bg_tk = None
        if PIL_OK and bg_path.exists():
            try:
                bg = Image.open(bg_path).resize((W, H), Image.LANCZOS)
                self._bg_tk = ImageTk.PhotoImage(bg)
                self.cv.create_image(0, 0, anchor='nw', image=self._bg_tk)
            except Exception:
                self.cv.create_rectangle(0, 0, W, H, fill=FUNDO_BASE, outline='')
        else:
            # Fallback minimo se nao houver imagem
            self.cv.create_rectangle(0, 0, W, H, fill=FUNDO_BASE, outline='')
            self.cv.create_text(W//2, H//2, text='SICRO',
                                font=('Segoe UI', 44, 'bold'),
                                fill='#E8EDF5', anchor='center')

        # Barra de progresso — unico elemento programatico
        # Posicao: 77.5% da altura, 20% de margem lateral
        bx = int(W * 0.12)
        bw = W - bx * 2
        by = int(H * 0.775)
        bh = 4

        # Trilho
        self.cv.create_rectangle(bx, by, bx+bw, by+bh,
                                 fill='#1A2A4A', outline='')
        # Preenchimento
        self._barra = self.cv.create_rectangle(
            bx, by, bx, by+bh,
            fill=DOURADO, outline='')

        self._bx = bx; self._bw = bw
        self._by = by; self._bh = bh

        # Texto de status — unico texto programatico
        self._status = self.cv.create_text(
            W//2, int(H * 0.838),
            text='Inicializando...',
            font=('Segoe UI', 9),
            fill=TEXTO_TERCIARIO,
            anchor='center')

    def _anim(self):
        if self._p >= 100: return
        self._p = min(100.0, self._p + 100 / (SPLASH_DURACAO / 50))
        larg = int(self._bw * self._p / 100)
        self.cv.coords(self._barra,
                       self._bx, self._by,
                       self._bx + larg, self._by + self._bh)
        msg = SPLASH_MSGS[0][1]
        for pct, txt in SPLASH_MSGS:
            if self._p >= pct: msg = txt
        self.cv.itemconfig(self._status, text=msg)
        self.after(50, self._anim)

    def fechar(self):
        try:
            self.master.wm_attributes('-alpha', 1)
        except Exception:
            pass
        self.destroy()
