import tkinter as tk
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import (
    COR_FUNDO, COR_PAINEL, COR_CARD,
    AMARELO, BRANCO, CINZA_CLARO, CINZA_MEDIO,
    AZUL_MEDIO, CINZA_ESCURO,
    COR_TEXTO, COR_TEXTO_SEC,
    FONTE_SUB, FONTE_PEQ,
    MODELOS_VIA,
)


class PopupModeloVia(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Modelo de via')
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)
        self.grab_set()
        self.resultado = None
        w, h = 460, 200
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x')
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill='both', expand=True, padx=28, pady=20)
        tk.Label(corpo, text='Como deseja iniciar o croqui?',
                 font=FONTE_SUB, bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=(0,16))
        btns = tk.Frame(corpo, bg=COR_FUNDO)
        btns.pack()
        self._btn(btns, 'Usar modelo de via',
                  'Escolha um template pronto\nde cruzamento ou rua',
                  AZUL_MEDIO, self._usar_modelo).pack(side='left', padx=10)
        self._btn(btns, 'Desenhar do zero',
                  'Canvas vazio, voce desenha\ntudo manualmente',
                  CINZA_ESCURO, self._do_zero).pack(side='left', padx=10)
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x', side='bottom')

    def _btn(self, parent, titulo, desc, cor, cmd):
        f = tk.Frame(parent, bg=cor, cursor='hand2')
        tk.Frame(f, bg=AMARELO, height=3).pack(fill='x')
        tk.Label(f, text=titulo, font=('Segoe UI',10,'bold'),
                 bg=cor, fg=BRANCO).pack(padx=16, pady=(10,2))
        tk.Label(f, text=desc, font=FONTE_PEQ, bg=cor, fg=CINZA_CLARO,
                 justify='center').pack(padx=16, pady=(0,12))
        for w in [f]+list(f.winfo_children()):
            w.bind('<Button-1>', lambda e,c=cmd: c())
        return f

    def _usar_modelo(self):
        self.withdraw()
        grid = GridModelos(self.winfo_toplevel())
        self.winfo_toplevel().wait_window(grid)
        self.resultado = grid.resultado
        self.destroy()

    def _do_zero(self):
        self.resultado = {'icone': 'branco'}
        self.destroy()


class GridModelos(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Escolha o modelo de via')
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)
        self.grab_set()
        self.resultado = None
        w, h = 680, 560
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x')
        cab = tk.Frame(self, bg=COR_PAINEL)
        cab.pack(fill='x')
        tk.Label(cab, text='Modelos de via', font=FONTE_SUB,
                 bg=COR_PAINEL, fg=COR_TEXTO).pack(side='left', padx=16, pady=10)
        tk.Label(cab, text='Clique no modelo para iniciar',
                 font=FONTE_PEQ, bg=COR_PAINEL, fg=COR_TEXTO_SEC).pack(side='right', padx=16)
        gf = tk.Frame(self, bg=COR_FUNDO)
        gf.pack(fill='both', expand=True, padx=14, pady=14)
        for idx, m in enumerate(MODELOS_VIA):
            self._card(gf, m, idx//3, idx%3)
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x', side='bottom')

    def _card(self, parent, modelo, row, col):
        card = tk.Frame(parent, bg=COR_CARD, cursor='hand2', width=190, height=140)
        card.grid(row=row, column=col, padx=6, pady=6, sticky='nsew')
        card.grid_propagate(False)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        prev = tk.Canvas(card, width=140, height=80, bg='#0D1830', highlightthickness=0)
        prev.pack(pady=(10,4))
        self._preview(prev, modelo['icone'])
        tk.Label(card, text=modelo['nome'], font=('Segoe UI',9,'bold'),
                 bg=COR_CARD, fg=COR_TEXTO).pack()
        def sel(m=modelo):
            self.resultado = m
            self.destroy()
        card.bind('<Button-1>', lambda e: sel())
        prev.bind('<Button-1>', lambda e: sel())
        for w in card.winfo_children():
            w.bind('<Button-1>', lambda e, m=modelo: self._sel(m))
        card.bind('<Enter>', lambda e, f=card: f.config(bg='#2A3060'))
        card.bind('<Leave>', lambda e, f=card: f.config(bg=COR_CARD))

    def _sel(self, m):
        self.resultado = m
        self.destroy()

    def _preview(self, c, icone):
        W, H = 140, 80
        cx, cy = W//2, H//2
        via = 18
        def asf(x1,y1,x2,y2): c.create_rectangle(x1,y1,x2,y2,fill='#606060',outline='')
        def cal(x1,y1,x2,y2): c.create_rectangle(x1,y1,x2,y2,fill='#909090',outline='')
        def fh(y):
            for x in range(0,W,14): c.create_line(x,y,x+8,y,fill=AMARELO,width=1)
        def fv(x):
            for y in range(0,H,10): c.create_line(x,y,x,y+6,fill=AMARELO,width=1)
        if icone=='cruzamento_mais':
            cal(0,0,cx-via,cy-via); cal(cx+via,0,W,cy-via)
            cal(0,cy+via,cx-via,H); cal(cx+via,cy+via,W,H)
            asf(0,cy-via,W,cy+via); asf(cx-via,0,cx+via,H)
            fh(cy); fv(cx)
        elif icone=='cruzamento_t':
            cal(0,0,cx-via,cy-via); cal(cx+via,0,W,cy-via); cal(0,cy+via,W,H)
            asf(0,cy-via,W,cy+via); asf(cx-via,0,cx+via,cy+via)
            fh(cy); fv(cx)
        elif icone=='rua_reta':
            cal(0,0,W,cy-via); cal(0,cy+via,W,H)
            asf(0,cy-via,W,cy+via); fh(cy)
        elif icone=='avenida':
            cant=6
            cal(0,0,W,cy-via-cant); cal(0,cy+via+cant,W,H)
            asf(0,cy-via-cant,W,cy-cant); asf(0,cy+cant,W,cy+via+cant)
            c.create_rectangle(0,cy-cant,W,cy+cant,fill='#2A6A2A',outline='')
            fh(cy-via//2-cant); fh(cy+via//2+cant)
        elif icone=='rotatoria':
            cal(0,0,W,H)
            r_e=min(cx,cy)-4; r_i=r_e//2
            c.create_oval(cx-r_e,cy-r_e,cx+r_e,cy+r_e,fill='#606060',outline='')
            c.create_oval(cx-r_i,cy-r_i,cx+r_i,cy+r_i,fill='#2A6A2A',outline='')
            c.create_oval(cx-r_e,cy-r_e,cx+r_e,cy+r_e,fill='',outline=AMARELO,width=1)
        elif icone=='estrada':
            c.create_rectangle(0,0,W,H,fill='#3A2A18',outline='')
            asf(0,cy-via,W,cy+via)
            c.create_line(0,cy,W,cy,fill=BRANCO,width=1,dash=(8,6))
        elif icone in ('cruzamento_y','rua_curva'):
            cal(0,0,W,H)
            asf(0,cy-via,cx+via,cy+via)
            asf(cx-via,cy-via,cx+via,H)
        else:
            c.create_rectangle(0,0,W,H,fill='#0D1830',outline='')
            c.create_text(cx,cy,text='Canvas\nlivre',fill=CINZA_MEDIO,
                          font=('Segoe UI',9),justify='center')
