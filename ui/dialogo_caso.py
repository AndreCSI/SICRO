import tkinter as tk
import datetime
import calendar
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import (
    COR_FUNDO, COR_PAINEL, COR_CARD, COR_BORDA,
    COR_TEXTO_SEC, AMARELO, BRANCO, CINZA_CLARO, CINZA_MEDIO,
    AZUL_MEDIO, AZUL_CLARO, PRETO_SOFT,
    FONTE_SUB, FONTE_NORMAL, FONTE_PEQ,
    MUNICIPIOS_AP,
)
from tema import (
    FUNDO_BASE, FUNDO_PAINEL, FUNDO_CARD, FUNDO_HOVER,
    DOURADO, AZUL_BORDA, TEXTO_PRIMARIO, TEXTO_SECUNDARIO,
    TEXTO_TERCIARIO, FONTE_H2, FONTE_H3, FONTE_BODY,
    FONTE_BODY_BOLD, FONTE_SMALL,
)


class CalendarioPopup(tk.Toplevel):
    """Calendario nativo em Tkinter puro, sem dependencias externas."""

    def __init__(self, parent, entry_destino):
        super().__init__(parent)
        self.entry = entry_destino
        self.overrideredirect(True)
        self.configure(bg=COR_PAINEL)
        self.attributes('-topmost', True)
        try:
            d, m, y = entry_destino.get().strip().split('/')
            self._data = datetime.date(int(y), int(m), int(d))
        except Exception:
            self._data = datetime.date.today()
        self._ano = self._data.year
        self._mes = self._data.month
        self.update_idletasks()
        ex = entry_destino.winfo_rootx()
        ey = entry_destino.winfo_rooty() + entry_destino.winfo_height()
        self.geometry(f'260x240+{ex}+{ey}')
        self.lift()
        self._build()
        self.bind('<FocusOut>', lambda e: self.after(100, self._fechar_se_fora))
        self.focus_force()

    def _fechar_se_fora(self):
        try:
            if not self.focus_get():
                self.destroy()
        except Exception:
            self.destroy()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        tk.Frame(self, bg=AMARELO, height=3).pack(fill='x')
        nav = tk.Frame(self, bg=COR_PAINEL)
        nav.pack(fill='x', padx=4, pady=4)
        tk.Button(nav, text='<', font=('Segoe UI',10), width=2,
                  bg=COR_PAINEL, fg=BRANCO, relief='flat', cursor='hand2',
                  command=self._mes_anterior).pack(side='left')
        tk.Button(nav, text='>', font=('Segoe UI',10), width=2,
                  bg=COR_PAINEL, fg=BRANCO, relief='flat', cursor='hand2',
                  command=self._mes_seguinte).pack(side='right')
        MESES = ['Janeiro','Fevereiro','Marco','Abril','Maio','Junho',
                 'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
        tk.Label(nav, text=f'{MESES[self._mes-1]} {self._ano}',
                 font=('Segoe UI',10,'bold'),
                 bg=COR_PAINEL, fg=AMARELO).pack(expand=True)
        dias_sem = tk.Frame(self, bg=COR_PAINEL)
        dias_sem.pack(fill='x', padx=4)
        for ds in ['Dom','Seg','Ter','Qua','Qui','Sex','Sab']:
            tk.Label(dias_sem, text=ds, font=('Segoe UI',8),
                     bg=COR_PAINEL, fg=CINZA_MEDIO, width=3).pack(side='left')
        tk.Frame(self, bg=COR_BORDA, height=1).pack(fill='x', padx=4, pady=2)
        grid = tk.Frame(self, bg=COR_PAINEL)
        grid.pack(fill='both', expand=True, padx=4, pady=2)
        cal = calendar.monthcalendar(self._ano, self._mes)
        hoje = datetime.date.today()
        for semana in cal:
            row_f = tk.Frame(grid, bg=COR_PAINEL)
            row_f.pack(fill='x')
            for dia in semana:
                if dia == 0:
                    tk.Label(row_f, text='', width=3, bg=COR_PAINEL).pack(side='left')
                else:
                    d = datetime.date(self._ano, self._mes, dia)
                    is_hoje = (d == hoje)
                    is_sel  = (d == self._data)
                    bg = AMARELO if is_sel else AZUL_MEDIO if is_hoje else COR_PAINEL
                    fg = PRETO_SOFT if is_sel else BRANCO
                    tk.Button(row_f, text=str(dia), width=3,
                              font=('Segoe UI',9,'bold' if is_hoje or is_sel else 'normal'),
                              bg=bg, fg=fg,
                              activebackground=AZUL_CLARO,
                              relief='flat', cursor='hand2',
                              command=lambda d=d: self._selecionar(d)).pack(side='left')
        tk.Frame(self, bg=AMARELO, height=3).pack(fill='x', side='bottom')

    def _mes_anterior(self):
        if self._mes == 1: self._mes=12; self._ano-=1
        else: self._mes -= 1
        self._build()

    def _mes_seguinte(self):
        if self._mes == 12: self._mes=1; self._ano+=1
        else: self._mes += 1
        self._build()

    def _selecionar(self, data):
        self._data = data
        self.entry.delete(0, tk.END)
        self.entry.insert(0, data.strftime('%d/%m/%Y'))
        self.destroy()


class DialogoDadosCaso(tk.Toplevel):
    """Formulario de dados do caso: BO, requisicao, local, municipio, perito, data."""

    def __init__(self, parent, modo='zero'):
        super().__init__(parent)
        self.overrideredirect(True)  # sem moldura Windows
        self.configure(bg=FUNDO_PAINEL)
        self.grab_set()
        self.resultado = None
        w, h = 460, 420
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        self.attributes('-topmost', True)
        # Borda externa sutil
        self.configure(highlightbackground=DOURADO, highlightthickness=1)
        # Faixa dourada topo
        tk.Frame(self, bg=DOURADO, height=3).pack(fill='x')
        # Barra de titulo customizada (arrastavel)
        tbar = tk.Frame(self, bg=FUNDO_PAINEL, height=36)
        tbar.pack(fill='x'); tbar.pack_propagate(False)
        tk.Label(tbar, text='  Dados do caso', font=FONTE_H3,
                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side='left', pady=8)
        _fechar = tk.Label(tbar, text='✕  ', font=('Segoe UI',11),
                           bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO,
                           cursor='hand2')
        _fechar.pack(side='right', pady=8)
        _fechar.bind('<Button-1>', lambda e: self.destroy())
        _fechar.bind('<Enter>', lambda e: _fechar.config(fg='#E08080'))
        _fechar.bind('<Leave>', lambda e: _fechar.config(fg=TEXTO_SECUNDARIO))
        # Arrastar pela barra
        def _ds(e): self._dx, self._dy = e.x_root-self.winfo_x(), e.y_root-self.winfo_y()
        def _dm(e): self.geometry(f'+{e.x_root-self._dx}+{e.y_root-self._dy}')
        for _w in (tbar,):
            _w.bind('<ButtonPress-1>', _ds)
            _w.bind('<B1-Motion>', _dm)
        tk.Frame(self, bg=AZUL_BORDA, height=1).pack(fill='x')
        corpo = tk.Frame(self, bg=FUNDO_PAINEL)
        corpo.pack(fill='both', expand=True, padx=28, pady=20)
        titulo = 'Croqui do zero' if modo=='zero' else 'Croqui sobre drone'
        tk.Label(corpo, text=titulo,
                 font=FONTE_H2, bg=FUNDO_PAINEL, fg=DOURADO).pack(anchor='w', pady=(0,16))
        campos = [
            ('No do BO',           'bo',         ''),
            ('No da Requisicao',   'requisicao',  ''),
            ('Local (ruas/av.)',   'local',       ''),
            ('Municipio',          'municipio',   'Porto Grande'),
            ('Perito responsavel', 'perito',      'Andre Ricardo Barroso'),
            ('Data do exame',      'data',        datetime.date.today().strftime('%d/%m/%Y')),
        ]
        self.entradas = {}
        self._dd_win  = None
        for label, chave, ph in campos:
            row = tk.Frame(corpo, bg=FUNDO_PAINEL)
            row.pack(fill='x', pady=3)
            tk.Label(row, text=label, font=FONTE_SMALL, width=18,
                     anchor='w', bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO).pack(side='left')
            if chave == 'municipio':
                e = self._campo_municipio(row, ph)
            elif chave == 'data':
                e = self._campo_data(row, ph)
            else:
                e = tk.Entry(row, font=FONTE_BODY,
                             bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,
                             insertbackground=DOURADO, relief='flat', bd=5,
                             highlightthickness=1, highlightcolor=DOURADO,
                             highlightbackground=AZUL_BORDA)
                e.insert(0, ph)
                e.pack(side='left', fill='x', expand=True)
            self.entradas[chave] = e
        tk.Frame(corpo, bg=AZUL_BORDA, height=1).pack(fill='x', pady=14)
        btns = tk.Frame(corpo, bg=FUNDO_PAINEL)
        btns.pack(fill='x')
        tk.Button(btns, text='Cancelar', font=FONTE_SMALL, cursor='hand2',
                  bg=FUNDO_CARD, fg=TEXTO_SECUNDARIO, activebackground=FUNDO_HOVER,
                  relief='flat', padx=16, pady=6,
                  command=self.destroy).pack(side='right', padx=(6,0))
        tk.Button(btns, text='Criar croqui  →',
                  font=FONTE_BODY_BOLD, cursor='hand2',
                  bg=AZUL_MEDIO, fg=TEXTO_PRIMARIO, activebackground=AZUL_CLARO,
                  relief='flat', padx=18, pady=6,
                  command=self._ok).pack(side='right')
        tk.Frame(self, bg=DOURADO, height=3).pack(fill='x', side='bottom')

    def _campo_municipio(self, row, ph):
        mframe = tk.Frame(row, bg=COR_CARD)
        mframe.pack(side='left', fill='x', expand=True)
        e = tk.Entry(mframe, font=FONTE_NORMAL,
                     bg=COR_CARD, fg=BRANCO,
                     insertbackground=BRANCO, relief='flat', bd=4)
        e.insert(0, ph)
        e.pack(side='left', fill='x', expand=True)
        btn_dd = tk.Button(mframe, text='v', font=('Segoe UI',10),
                           bg=COR_CARD, fg=CINZA_CLARO,
                           activebackground=AZUL_MEDIO,
                           relief='flat', cursor='hand2', padx=4)
        btn_dd.pack(side='right')

        def _fechar_dd():
            if self._dd_win and self._dd_win.winfo_exists():
                self._dd_win.destroy()
            self._dd_win = None

        def _mostrar_dd(lista, entry=e):
            _fechar_dd()
            self.update_idletasks()
            ex = mframe.winfo_rootx()
            ey = mframe.winfo_rooty() + mframe.winfo_height()
            ew = mframe.winfo_width()
            altura = min(len(lista), 10) * 24
            win = tk.Toplevel(self)
            win.overrideredirect(True)
            win.geometry(f'{ew}x{altura}+{ex}+{ey}')
            win.configure(bg=COR_CARD)
            win.attributes('-topmost', True)
            win.lift()
            self._dd_win = win
            lb2 = tk.Listbox(win, bg='#1A2A5A', fg=BRANCO,
                             selectbackground=AZUL_MEDIO,
                             selectforeground=BRANCO,
                             font=FONTE_NORMAL, relief='flat', bd=0,
                             activestyle='dotbox',
                             highlightthickness=1,
                             highlightcolor=AZUL_MEDIO)
            lb2.pack(fill='both', expand=True)
            for m in lista:
                lb2.insert(tk.END, f'  {m}')
            def _sel_dd(event, entry=entry):
                idx = lb2.nearest(event.y)
                if idx >= 0:
                    lb2.selection_clear(0, tk.END)
                    lb2.selection_set(idx)
                    val = lb2.get(idx).strip()
                    entry.delete(0, tk.END)
                    entry.insert(0, val)
                win.after(200, _fechar_dd)
            lb2.bind('<Button-1>', _sel_dd)

        def _ao_digitar(event, entry=e):
            txt = entry.get().lower()
            filtrados = [m for m in MUNICIPIOS_AP if txt in m.lower()]
            if filtrados and txt:
                _mostrar_dd(filtrados, entry)
            else:
                _fechar_dd()

        def _toggle_dd(entry=e):
            if self._dd_win and self._dd_win.winfo_exists():
                _fechar_dd()
            else:
                _mostrar_dd(MUNICIPIOS_AP, entry)

        e.bind('<KeyRelease>', _ao_digitar)
        e.bind('<Escape>', lambda ev: _fechar_dd())
        btn_dd.config(command=_toggle_dd)
        return e

    def _campo_data(self, row, ph):
        dframe = tk.Frame(row, bg=COR_CARD)
        dframe.pack(side='left', fill='x', expand=True)
        e = tk.Entry(dframe, font=FONTE_NORMAL,
                     bg=COR_CARD, fg=BRANCO,
                     insertbackground=BRANCO, relief='flat', bd=4)
        e.insert(0, datetime.date.today().strftime('%d/%m/%Y'))
        e.pack(side='left', fill='x', expand=True)
        btn_cal = tk.Button(dframe, text='Cal', font=('Segoe UI',10),
                            bg=COR_CARD, fg=AMARELO,
                            activebackground=AZUL_MEDIO,
                            relief='flat', cursor='hand2', padx=4)
        btn_cal.pack(side='right')
        btn_cal.config(command=lambda: CalendarioPopup(self, e))
        e.bind('<Button-1>', lambda ev: CalendarioPopup(self, e))
        return e

    def _ok(self):
        self.resultado = {k: v.get().strip() for k,v in self.entradas.items()}
        self.destroy()
