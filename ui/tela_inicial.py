import tkinter as tk
import datetime
import json
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import (
    COR_FUNDO, COR_PAINEL, COR_CARD, COR_BORDA,
    COR_TEXTO, COR_TEXTO_SEC,
    AMARELO, BRANCO, CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO,
    AZUL_MEDIO, AZUL_CLARO,
    FONTE_SUB, FONTE_NORMAL, FONTE_PEQ,
    DIR_CROQUIS,
)
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False


class TelaInicial(tk.Frame):
    """
    Tela inicial do SICRO PCI/AP.
    Exibe botoes para criar novo croqui e a biblioteca de croquis salvos.

    Callbacks:
      on_novo(modo)     — chamado ao clicar em novo croqui ('zero' ou 'drone')
      on_abrir(caminho) — chamado ao abrir um croqui da biblioteca
    """

    def __init__(self, master, on_novo, on_abrir, img_brasao=None):
        super().__init__(master, bg=COR_FUNDO)
        self.on_novo    = on_novo
        self.on_abrir   = on_abrir
        self.img_brasao = img_brasao
        self._build()

    def _build(self):
        # Cabecalho
        cab = tk.Frame(self, bg=COR_PAINEL)
        cab.pack(fill='x')
        tk.Frame(cab, bg=AMARELO, height=4).pack(fill='x')
        inner = tk.Frame(cab, bg=COR_PAINEL)
        inner.pack(fill='x', padx=20, pady=10)
        if self.img_brasao and PIL_OK:
            img = self.img_brasao.resize((40, 40), Image.LANCZOS)
            self._hdr_tk = ImageTk.PhotoImage(img)
            tk.Label(inner, image=self._hdr_tk,
                     bg=COR_PAINEL).pack(side='left', padx=(0,10))
        tk.Label(inner, text='SICRO PCI/AP', font=('Segoe UI',14,'bold'),
                 bg=COR_PAINEL, fg=BRANCO).pack(side='left')
        tk.Label(inner, text='Policia Cientifica do Amapa',
                 font=FONTE_PEQ, bg=COR_PAINEL, fg=AMARELO).pack(side='left', padx=10)
        tk.Label(inner, text=datetime.date.today().strftime('%d/%m/%Y'),
                 font=FONTE_PEQ, bg=COR_PAINEL, fg=CINZA_MEDIO).pack(side='right')

        # Corpo
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill='both', expand=True, padx=24, pady=18)

        # Coluna esquerda: novo croqui
        esq = tk.Frame(corpo, bg=COR_FUNDO)
        esq.pack(side='left', fill='y', padx=(0,16))
        tk.Label(esq, text='Novo croqui', font=FONTE_SUB,
                 bg=COR_FUNDO, fg=AMARELO).pack(anchor='w', pady=(0,8))
        self._card(esq, 'Croqui do zero',
                   'Sem imagem de fundo\ndesenho vetorial completo',
                   AZUL_MEDIO, lambda: self.on_novo('zero'))
        self._card(esq, 'Croqui sobre drone',
                   'Carrega foto aerea\ncalibra escala pela lona',
                   CINZA_ESCURO, lambda: self.on_novo('drone'))

        tk.Frame(corpo, bg=COR_BORDA, width=1).pack(side='left', fill='y', padx=4)

        # Coluna direita: biblioteca
        dir_ = tk.Frame(corpo, bg=COR_FUNDO)
        dir_.pack(side='left', fill='both', expand=True)
        topo = tk.Frame(dir_, bg=COR_FUNDO)
        topo.pack(fill='x')
        tk.Label(topo, text='Biblioteca de croquis', font=FONTE_SUB,
                 bg=COR_FUNDO, fg=AMARELO).pack(side='left')
        tk.Button(topo, text='Atualizar', font=FONTE_PEQ, cursor='hand2',
                  bg=COR_CARD, fg=COR_TEXTO_SEC, activebackground=COR_BORDA,
                  relief='flat', command=self._carregar).pack(side='right')
        flb = tk.Frame(dir_, bg=COR_CARD)
        flb.pack(fill='both', expand=True, pady=6)
        scrl = tk.Scrollbar(flb)
        scrl.pack(side='right', fill='y')
        self.lb = tk.Listbox(flb, yscrollcommand=scrl.set,
                             bg=COR_CARD, fg=COR_TEXTO,
                             selectbackground=AZUL_MEDIO,
                             selectforeground=BRANCO,
                             font=FONTE_NORMAL, relief='flat', bd=0,
                             activestyle='none', highlightthickness=0)
        self.lb.pack(fill='both', expand=True, padx=2)
        scrl.config(command=self.lb.yview)
        self.lb.bind('<Double-Button-1>', self._abrir_sel)
        tk.Button(dir_, text='Abrir croqui selecionado ->',
                  font=FONTE_NORMAL, cursor='hand2',
                  bg=AZUL_MEDIO, fg=BRANCO,
                  activebackground=AZUL_CLARO,
                  relief='flat', pady=7,
                  command=self._abrir_sel).pack(fill='x')
        self._carregar()

    def _card(self, parent, titulo, desc, cor, cmd):
        f = tk.Frame(parent, bg=COR_CARD, cursor='hand2')
        f.pack(fill='x', pady=4, ipadx=12, ipady=10)
        tk.Frame(f, bg=cor, width=4).pack(side='left', fill='y')
        inner = tk.Frame(f, bg=COR_CARD)
        inner.pack(side='left', padx=10)
        tk.Label(inner, text=titulo, font=('Segoe UI',11,'bold'),
                 bg=COR_CARD, fg=BRANCO).pack(anchor='w')
        tk.Label(inner, text=desc, font=FONTE_PEQ,
                 bg=COR_CARD, fg=CINZA_CLARO, justify='left').pack(anchor='w')
        for w in [f, inner] + list(inner.winfo_children()):
            w.bind('<Button-1>', lambda e, c=cmd: c())
        f.bind('<Enter>', lambda e: f.config(bg='#1E2A60'))
        f.bind('<Leave>', lambda e: f.config(bg=COR_CARD))

    def _carregar(self):
        self.lb.delete(0, tk.END)
        self._arqs = sorted(DIR_CROQUIS.glob('*.sicro'), reverse=True)
        if not self._arqs:
            self.lb.insert(tk.END, '  (nenhum croqui salvo)')
            return
        for a in self._arqs:
            try:
                with open(a) as f:
                    d = json.load(f)
                self.lb.insert(tk.END,
                    f"  BO {d.get('bo','?')}  .  {d.get('data','')}  .  "
                    f"{d.get('local', a.stem)[:40]}")
            except Exception:
                self.lb.insert(tk.END, f'  {a.name}')

    def _abrir_sel(self, event=None):
        idx = self.lb.curselection()
        if not idx or not hasattr(self, '_arqs'): return
        if idx[0] < len(self._arqs):
            self.on_abrir(self._arqs[idx[0]])
