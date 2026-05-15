import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import (
    AZUL_ESCURO, AZUL_MEDIO, AMARELO, BRANCO,
    CINZA_CLARO, CINZA_MEDIO, FONTE_PEQ,
)
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False


class SplashScreen(tk.Toplevel):
    """
    Tela de splash exibida na inicializacao do SICRO PCI/AP.
    Mostra brasao, nome do sistema e barra de progresso animada.
    Fecha automaticamente apos completar a animacao.
    """

    def __init__(self, parent, img_brasao=None):
        super().__init__(parent)
        self.overrideredirect(True)
        w, h = 560, 420
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        self.configure(bg=AZUL_ESCURO)
        self.lift()
        self.attributes('-topmost', True)

        tk.Frame(self, bg=AMARELO, height=6).pack(fill='x')
        corpo = tk.Frame(self, bg=AZUL_ESCURO)
        corpo.pack(fill='both', expand=True, padx=48, pady=16)

        if img_brasao and PIL_OK:
            img = img_brasao.resize((110, 110), Image.LANCZOS)
            self._tk = ImageTk.PhotoImage(img)
            tk.Label(corpo, image=self._tk, bg=AZUL_ESCURO).pack(pady=(4, 0))
        else:
            tk.Label(corpo, text='Brasao', font=('Segoe UI', 52),
                     bg=AZUL_ESCURO, fg=AMARELO).pack(pady=(4, 0))

        tk.Label(corpo, text='POLICIA CIENTIFICA DO AMAPA',
                 font=('Segoe UI', 10, 'bold'),
                 bg=AZUL_ESCURO, fg=AMARELO).pack(pady=(4, 0))
        tk.Label(corpo, text='SICRO PCI/AP',
                 font=('Segoe UI', 26, 'bold'),
                 bg=AZUL_ESCURO, fg=BRANCO).pack(pady=(6, 0))
        tk.Label(corpo, text='Sistema de Croquis Periciais de Transito',
                 font=('Segoe UI', 10),
                 bg=AZUL_ESCURO, fg=CINZA_CLARO).pack(pady=(2, 0))
        tk.Frame(corpo, bg=AZUL_MEDIO, height=1).pack(fill='x', pady=12)
        tk.Label(corpo, text='Departamento de Criminalistica - DC',
                 font=('Segoe UI', 9),
                 bg=AZUL_ESCURO, fg=CINZA_CLARO).pack()
        tk.Label(corpo,
                 text='Desenvolvido por Andre Ricardo Barroso - Perito Criminal',
                 font=('Segoe UI', 9, 'italic'),
                 bg=AZUL_ESCURO, fg=CINZA_MEDIO).pack(pady=(3, 12))

        sty = ttk.Style()
        sty.configure('Sp.Horizontal.TProgressbar',
                       troughcolor=AZUL_ESCURO, background=AMARELO,
                       borderwidth=0, thickness=6)
        self.barra = ttk.Progressbar(corpo, length=380,
                                     style='Sp.Horizontal.TProgressbar',
                                     maximum=100, value=0)
        self.barra.pack()
        self.lbl = tk.Label(corpo, text='Inicializando...',
                            font=FONTE_PEQ, bg=AZUL_ESCURO, fg=CINZA_MEDIO)
        self.lbl.pack(pady=6)
        tk.Label(self, text='v16.0.0', font=('Segoe UI', 8),
                 bg=AZUL_ESCURO, fg=CINZA_MEDIO).pack(side='right', padx=10)
        tk.Frame(self, bg=AMARELO, height=6).pack(fill='x', side='bottom')

        self._p = 0
        self._anim()

    def _anim(self):
        if self._p < 100:
            self._p += 1.25
            self.barra['value'] = self._p
            msgs = {
                10: 'Carregando interface...',
                35: 'Carregando biblioteca...',
                60: 'Preparando ferramentas...',
                85: 'Quase pronto...',
            }
            for lim, m in msgs.items():
                if int(self._p) == lim:
                    self.lbl.config(text=m)
            self.after(50, self._anim)

    def fechar(self):
        self.destroy()
