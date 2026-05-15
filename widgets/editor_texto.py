import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import (
    COR_PAINEL, COR_CARD, AMARELO, BRANCO,
    CINZA_CLARO, AZUL_MEDIO,
    COR_R1, COR_SUCESSO, COR_PERIGO,
    AZUL_CLARO, PRETO_SOFT,
    FONTE_PEQ, FONTES_DISPONIVEIS,
)


class EditorTextoInline:
    """
    Editor de texto inline.
    Cria um Entry sobre o canvas na posicao do elemento,
    com painel flutuante de formatacao (fonte, tamanho, cor, B/I).
    """

    def __init__(self, janela, canvas, elemento, fn_mt, fn_redesenhar, fn_camadas):
        self.janela      = janela
        self.canvas      = canvas
        self.el          = elemento
        self._mt         = fn_mt
        self._redesenhar = fn_redesenhar
        self._camadas    = fn_camadas
        self._ativo      = True

        tx, ty = self._mt(elemento.get('x', 0), elemento.get('y', 0))

        fonte_nome = elemento.get('fonte', 'Segoe UI')
        fonte_tam  = elemento.get('tamanho', 12)
        bold_opt   = 'bold' if elemento.get('negrito', False) else 'normal'

        self._entry = tk.Entry(canvas,
                               font=(fonte_nome, fonte_tam, bold_opt),
                               bg='#1A2A4A',
                               fg=elemento.get('cor_texto', BRANCO),
                               insertbackground=AMARELO,
                               relief='flat', bd=2,
                               highlightthickness=1,
                               highlightcolor=AMARELO,
                               highlightbackground=AZUL_MEDIO,
                               width=30)
        if elemento.get('label'):
            self._entry.insert(0, elemento['label'])
            self._entry.select_range(0, tk.END)

        self._entry_id = canvas.create_window(tx, ty, window=self._entry, anchor='nw')
        self._entry.focus_set()
        self._entry.bind('<KeyRelease>', self._ao_digitar)
        self._entry.bind('<Return>',    self._confirmar)
        self._entry.bind('<KP_Enter>',  self._confirmar)
        self._entry.bind('<Escape>',    self._cancelar)
        self._entry.bind('<FocusOut>',  self._ao_perder_foco)

        self._painel = tk.Toplevel(janela)
        self._painel.overrideredirect(True)
        self._painel.attributes('-topmost', True)
        self._painel.configure(bg=COR_PAINEL)
        self._painel_build()

        canvas.update_idletasks()
        px = canvas.winfo_rootx() + tx
        py = canvas.winfo_rooty() + ty - 90
        if py < 0: py = canvas.winfo_rooty() + ty + 30
        self._painel.geometry(f'420x80+{int(px)}+{int(py)}')

    def _painel_build(self):
        p = self._painel
        for w in p.winfo_children(): w.destroy()
        tk.Frame(p, bg=AMARELO, height=2).pack(fill='x')
        corpo = tk.Frame(p, bg=COR_PAINEL)
        corpo.pack(fill='both', expand=True, padx=6, pady=4)

        tk.Label(corpo, text='Fonte', font=FONTE_PEQ,
                 bg=COR_PAINEL, fg=CINZA_CLARO).grid(row=0, column=0, padx=(0,2))
        self._var_fonte = tk.StringVar(value=self.el.get('fonte', 'Segoe UI'))
        cb = ttk.Combobox(corpo, textvariable=self._var_fonte,
                          values=FONTES_DISPONIVEIS, width=14,
                          state='readonly', font=FONTE_PEQ)
        cb.grid(row=0, column=1, padx=2)
        cb.bind('<<ComboboxSelected>>', self._aplicar_formato)

        tk.Label(corpo, text='Tam', font=FONTE_PEQ,
                 bg=COR_PAINEL, fg=CINZA_CLARO).grid(row=0, column=2, padx=(6,2))
        self._var_tam = tk.IntVar(value=self.el.get('tamanho', 12))
        spin = tk.Spinbox(corpo, textvariable=self._var_tam,
                          from_=6, to=72, width=4, font=FONTE_PEQ,
                          bg=COR_CARD, fg=BRANCO, buttonbackground=COR_CARD,
                          relief='flat', command=self._aplicar_formato)
        spin.grid(row=0, column=3, padx=2)
        spin.bind('<KeyRelease>', self._aplicar_formato)

        tk.Label(corpo, text='Cor', font=FONTE_PEQ,
                 bg=COR_PAINEL, fg=CINZA_CLARO).grid(row=0, column=4, padx=(6,2))
        CORES = [BRANCO, AMARELO, COR_R1, AZUL_CLARO,
                 COR_SUCESSO, '#FF8800', '#FF00FF', PRETO_SOFT]
        fc = tk.Frame(corpo, bg=COR_PAINEL)
        fc.grid(row=0, column=5, padx=2)
        for cor in CORES:
            tk.Button(fc, bg=cor, width=1, height=1,
                      relief='solid', bd=1, cursor='hand2',
                      command=lambda c=cor: self._set_cor(c)).pack(side='left', padx=1)

        self._var_bold = tk.BooleanVar(value=self.el.get('negrito', False))
        self._var_ital = tk.BooleanVar(value=self.el.get('italico', False))
        tk.Checkbutton(corpo, text='B', font=('Segoe UI',10,'bold'),
                       variable=self._var_bold, bg=COR_PAINEL, fg=BRANCO,
                       selectcolor=AZUL_MEDIO, activebackground=COR_PAINEL,
                       relief='flat',
                       command=self._aplicar_formato).grid(row=0, column=6, padx=2)
        tk.Checkbutton(corpo, text='i', font=('Segoe UI',10,'italic'),
                       variable=self._var_ital, bg=COR_PAINEL, fg=BRANCO,
                       selectcolor=AZUL_MEDIO, activebackground=COR_PAINEL,
                       relief='flat',
                       command=self._aplicar_formato).grid(row=0, column=7, padx=2)
        tk.Button(corpo, text='V', font=('Segoe UI',10,'bold'),
                  bg=COR_SUCESSO, fg=PRETO_SOFT,
                  relief='flat', cursor='hand2', padx=4,
                  command=self._confirmar).grid(row=0, column=8, padx=(8,2))
        tk.Button(corpo, text='X', font=('Segoe UI',10),
                  bg=COR_PERIGO, fg=BRANCO,
                  relief='flat', cursor='hand2', padx=4,
                  command=self._cancelar).grid(row=0, column=9, padx=2)
        tk.Frame(p, bg=AMARELO, height=2).pack(fill='x', side='bottom')

    def _ao_digitar(self, event=None):
        self.el['label'] = self._entry.get()
        self._redesenhar()

    def _set_cor(self, cor):
        self._var_cor = cor
        self.el['cor_texto'] = cor
        self._entry.config(fg=cor)
        self._redesenhar()

    def _aplicar_formato(self, event=None):
        self.el['fonte']   = self._var_fonte.get()
        self.el['negrito'] = self._var_bold.get()
        self.el['italico'] = self._var_ital.get()
        try:
            self.el['tamanho'] = max(6, min(72, int(self._var_tam.get())))
        except Exception:
            pass
        bold_opt = 'bold' if self.el['negrito'] else 'normal'
        ital_opt = 'italic' if self.el['italico'] else ''
        spec = (self.el['fonte'], self.el['tamanho'],
                (bold_opt+' '+ital_opt).strip() or 'normal')
        self._entry.config(font=spec)
        self._redesenhar()

    def _confirmar(self, event=None):
        if not self._ativo: return
        self._ativo = False
        self.el['label'] = self._entry.get()
        self._aplicar_formato()
        self._fechar()
        self._camadas()
        self._redesenhar()

    def _cancelar(self, event=None):
        if not self._ativo: return
        self._ativo = False
        self._fechar()
        self._redesenhar()

    def _ao_perder_foco(self, event=None):
        if self._ativo:
            self.janela.after(150, self._verificar_foco)

    def _verificar_foco(self):
        if not self._ativo: return
        try:
            foco = self.janela.focus_get()
            if self._painel.winfo_exists():
                if foco and str(foco).startswith(str(self._painel)):
                    return
        except Exception:
            pass
        self._confirmar()

    def _fechar(self):
        try:
            self.canvas.delete(self._entry_id)
            self._entry.destroy()
        except Exception:
            pass
        try:
            if self._painel.winfo_exists():
                self._painel.destroy()
        except Exception:
            pass
