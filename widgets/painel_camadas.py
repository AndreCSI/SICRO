import tkinter as tk
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import (
    COR_PAINEL, COR_CARD, AMARELO, BRANCO,
    CINZA_MEDIO, CINZA_CLARO, AZUL_MEDIO,
    FONTE_SUB, FONTE_PEQ,
    TIPO_INFO,
)


class PainelCamadas:
    """
    Painel lateral de camadas.
    Construido dentro de um frame pai (pd).
    Recebe callbacks do EditorCroqui via construtor.

    Callbacks esperados:
      on_selecionar(el_idx)  — chamado ao clicar numa camada
      on_subir()             — move elemento selecionado para cima
      on_descer()            — move elemento selecionado para baixo
      on_apagar()            — apaga elemento selecionado
      get_elementos()        — retorna lista atual de elementos
      get_sel_idx()          — retorna indice selecionado atual
    """

    def __init__(self, pd, status_bar,
                 on_selecionar, on_subir, on_descer, on_apagar,
                 get_elementos, get_sel_idx):
        self.status      = status_bar
        self.on_sel      = on_selecionar
        self.on_subir    = on_subir
        self.on_descer   = on_descer
        self.on_apagar   = on_apagar
        self.get_els     = get_elementos
        self.get_sel_idx = get_sel_idx

        tk.Frame(pd, bg=AMARELO, height=2).pack(fill='x')

        # Cabecalho com botoes de ordem
        cab = tk.Frame(pd, bg=COR_PAINEL)
        cab.pack(fill='x', padx=6, pady=(8,2))
        tk.Label(cab, text='Camadas', font=FONTE_SUB,
                 bg=COR_PAINEL, fg=AMARELO).pack(side='left')
        for sym, tip, cmd in [
            ('▲', 'Subir camada',  self._subir),
            ('▼', 'Descer camada', self._descer),
        ]:
            b = tk.Button(cab, text=sym, font=('Segoe UI',9),
                          width=2, cursor='hand2',
                          bg=COR_CARD, fg=BRANCO,
                          activebackground=AZUL_MEDIO,
                          relief='flat', pady=1,
                          command=cmd)
            b.pack(side='right', padx=1)
            b.bind('<Enter>', lambda e, t=tip: self.status.config(text=t))

        # Listbox
        flb = tk.Frame(pd, bg=COR_CARD)
        flb.pack(fill='both', expand=True, padx=4, pady=2)
        scrl = tk.Scrollbar(flb)
        scrl.pack(side='right', fill='y')
        self.lb = tk.Listbox(
            flb,
            yscrollcommand=scrl.set,
            bg=COR_CARD, fg=BRANCO,
            selectbackground=AZUL_MEDIO,
            selectforeground=BRANCO,
            font=('Segoe UI', 9),
            relief='flat', bd=0,
            activestyle='none',
            highlightthickness=0,
        )
        self.lb.pack(fill='both', expand=True)
        scrl.config(command=self.lb.yview)
        self.lb.bind('<<ListboxSelect>>', self._selecionada)

        # Botao apagar
        tk.Button(pd, text='Apagar selecionado',
                  font=FONTE_PEQ, cursor='hand2',
                  bg='#3A1010', fg='#FF8080',
                  activebackground='#5A1A1A',
                  relief='flat', pady=4,
                  command=self._apagar).pack(fill='x', padx=4, pady=(0,4))

    def atualizar(self):
        """Sincroniza o Listbox com a lista de elementos atual."""
        elementos = self.get_els()
        sel_atual = self.get_sel_idx()
        self.lb.delete(0, tk.END)
        for i, el in reversed(list(enumerate(elementos))):
            icone, nome = TIPO_INFO.get(el['tipo'], ('?', el['tipo']))
            label_el = el.get('label', '')
            txt = f' {icone}  {nome}'
            if label_el:
                txt += f'  [{label_el}]'
            self.lb.insert(tk.END, txt)
            if el['tipo'].startswith('_'):
                self.lb.itemconfig(tk.END, fg=CINZA_MEDIO)
            else:
                self.lb.itemconfig(tk.END, fg=BRANCO)
        if sel_atual is not None:
            lb_idx = len(elementos) - 1 - sel_atual
            if 0 <= lb_idx < self.lb.size():
                self.lb.selection_set(lb_idx)
                self.lb.see(lb_idx)

    def _selecionada(self, event=None):
        sel = self.lb.curselection()
        if not sel: return
        lb_idx = sel[0]
        elementos = self.get_els()
        el_idx = len(elementos) - 1 - lb_idx
        if 0 <= el_idx < len(elementos):
            self.on_sel(el_idx)

    def _subir(self):   self.on_subir()
    def _descer(self):  self.on_descer()
    def _apagar(self):  self.on_apagar()
