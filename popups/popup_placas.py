import tkinter as tk
from tkinter import simpledialog
import math
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import (
    COR_FUNDO, COR_PAINEL, COR_CARD, AMARELO, BRANCO,
    CINZA_CLARO, MODELOS_PLACA,
)


class PopupPlacas(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Escolha a placa')
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)
        self.resultado = None
        self.lift(); self.focus_force(); self.grab_set()
        n = len(MODELOS_PLACA)
        cols = 3; rows = (n + cols - 1) // cols
        cw, ch = 130, 120
        pad = 10
        w = cols*cw + (cols+1)*pad
        h = rows*ch + (rows+1)*pad + 80
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x')
        tk.Label(self, text='Escolha o modelo de placa',
                 font=('Segoe UI',11,'bold'),
                 bg=COR_FUNDO, fg=AMARELO).pack(pady=(10,6))
        grid = tk.Frame(self, bg=COR_FUNDO)
        grid.pack(padx=pad, pady=4)
        for idx, m in enumerate(MODELOS_PLACA):
            row, col = idx//cols, idx%cols
            self._card(grid, m, row, col, cw, ch)
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x', side='bottom')

    def _card(self, parent, m, row, col, cw, ch):
        card = tk.Frame(parent, bg=COR_CARD, cursor='hand2', width=cw, height=ch)
        card.grid(row=row, column=col, padx=6, pady=6)
        card.grid_propagate(False)
        prev = tk.Canvas(card, width=cw-16, height=70,
                         bg='#0D1830', highlightthickness=0)
        prev.pack(padx=8, pady=(8,2))
        self._preview(prev, m, (cw-16)//2, 35)
        tk.Label(card, text=m['desc'], font=('Segoe UI',8),
                 bg=COR_CARD, fg=CINZA_CLARO, wraplength=cw-16).pack()
        def sel(modelo=m):
            if modelo['chave'] == 'custom':
                txt = simpledialog.askstring(
                    'Placa personalizada', 'Texto da placa:',
                    parent=self.master) or '?'
                modelo = dict(modelo); modelo['label'] = txt
            self.resultado = modelo
            self.destroy()
        for w in [card, prev] + list(card.winfo_children()):
            w.bind('<Button-1>', lambda e, m=m: sel(m))
        card.bind('<Enter>', lambda e, f=card: f.config(bg='#2A3060'))
        card.bind('<Leave>', lambda e, f=card: f.config(bg=COR_CARD))

    def _preview(self, c, m, cx, cy):
        r = 22
        cor = m['cor']
        label = m['label']
        if m['chave'] == 'pare':
            pts = []
            for i in range(8):
                ang = math.radians(i*45 + 22.5)
                pts.extend([cx+math.cos(ang)*r, cy+math.sin(ang)*r])
            c.create_polygon(pts, fill=cor, outline=BRANCO, width=2)
            c.create_text(cx, cy, text='PARE', fill=BRANCO,
                          font=('Segoe UI',9,'bold'))
        elif m['chave'] in ('vel_30','vel_40','vel_60','vel_80'):
            c.create_oval(cx-r,cy-r,cx+r,cy+r, fill=BRANCO, outline='#CC0000', width=3)
            c.create_text(cx, cy, text=label, fill='#CC0000',
                          font=('Segoe UI',11,'bold'))
        elif m['chave'] == 'atencao':
            pts = [cx,cy-r, cx+r*0.87,cy+r*0.5, cx-r*0.87,cy+r*0.5]
            c.create_polygon(pts, fill='#CC8800', outline=BRANCO, width=2)
            c.create_text(cx, cy+6, text='!', fill=BRANCO,
                          font=('Segoe UI',14,'bold'))
        elif m['chave'] == 'proib':
            c.create_oval(cx-r,cy-r,cx+r,cy+r, fill=BRANCO, outline='#CC0000', width=3)
            c.create_line(cx-r*.7,cy-r*.7,cx+r*.7,cy+r*.7, fill='#CC0000', width=4)
        else:
            c.create_rectangle(cx-r,cy-r,cx+r,cy+r, fill=cor, outline=BRANCO, width=2)
            c.create_text(cx, cy, text=label, fill=BRANCO,
                          font=('Segoe UI',12,'bold'))
