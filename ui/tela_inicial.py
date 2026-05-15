import tkinter as tk
import datetime, json, sys
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
    FUNDO_BASE, FUNDO_PAINEL, FUNDO_CARD, FUNDO_HOVER,
    FUNDO_ATIVO, AZUL_BORDA, AZUL_MEDIO,
    DOURADO, TEXTO_PRIMARIO, TEXTO_SECUNDARIO, TEXTO_TERCIARIO,
    TEXTO_INVERTIDO, COR_SUCESSO,
    FONTE_H1, FONTE_H2, FONTE_H3, FONTE_BODY, FONTE_BODY_BOLD,
    FONTE_SMALL, FONTE_SMALL_BOLD, FONTE_MICRO,
    LARGURA_SIDEBAR_INICIO, ALTURA_HEADER, ALTURA_BARRA_TOP,
    SIDEBAR_ITENS,
)
from config import DIR_CROQUIS

# Assets dos cards
_CARD_IMGS = {
    'zero':   'card_manual.png',
    'drone':  'card_drone.png',
    'modelo': 'card_modelo.png',
}
_card_tk_cache = {}

def _carregar_card_img(chave, w, h):
    if not PIL_OK: return None
    key = (chave, w, h)
    if key in _card_tk_cache: return _card_tk_cache[key]
    path = Path(__file__).parent.parent / 'assets' / _CARD_IMGS[chave]
    if not path.exists(): return None
    try:
        img = Image.open(path).convert('RGBA').resize((w, h), Image.LANCZOS)
        # Escurece levemente para o texto ficar legivel
        from PIL import ImageEnhance
        img = ImageEnhance.Brightness(img).enhance(0.55)
        tk_img = ImageTk.PhotoImage(img)
        _card_tk_cache[key] = tk_img
        return tk_img
    except Exception:
        return None


class TelaInicial(tk.Frame):
    def __init__(self, master, on_novo, on_abrir, img_brasao=None):
        super().__init__(master, bg=FUNDO_BASE)
        self.on_novo    = on_novo
        self.on_abrir   = on_abrir
        self.img_brasao = img_brasao
        self._aba_ativa = 'inicio'
        self._build()

    def _build(self):
        # Header gerenciado pela TitleBar do main.py
        corpo = tk.Frame(self, bg=FUNDO_BASE)
        corpo.pack(fill='both', expand=True)
        self._build_sidebar(corpo)
        self._area = tk.Frame(corpo, bg=FUNDO_BASE)
        self._area.pack(side='left', fill='both', expand=True)
        self._mostrar_inicio()

    def _build_header(self):
        h = tk.Frame(self, bg=FUNDO_PAINEL, height=ALTURA_HEADER)
        h.pack(fill='x'); h.pack_propagate(False)
        esq = tk.Frame(h, bg=FUNDO_PAINEL)
        esq.pack(side='left', padx=16, pady=0, fill='y')
        if self.img_brasao and PIL_OK:
            try:
                img = self.img_brasao.resize((28, 28), Image.LANCZOS)
                self._hdr_tk = ImageTk.PhotoImage(img)
                tk.Label(esq, image=self._hdr_tk,
                         bg=FUNDO_PAINEL).pack(side='left', padx=(0,8))
            except Exception: pass
        tk.Label(esq, text='SICRO', font=FONTE_H2,
                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side='left')
        tk.Label(esq, text='  Sistema de Croquis Periciais',
                 font=FONTE_SMALL, bg=FUNDO_PAINEL,
                 fg=TEXTO_TERCIARIO).pack(side='left')
        dir_ = tk.Frame(h, bg=FUNDO_PAINEL)
        dir_.pack(side='right', padx=16, fill='y')
        tk.Label(dir_,
                 text=f'Policia Cientifica do Amapa  |  '
                      f'{datetime.date.today().strftime("%d/%m/%Y")}',
                 font=FONTE_MICRO, bg=FUNDO_PAINEL,
                 fg=TEXTO_TERCIARIO).pack(expand=True)

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=FUNDO_PAINEL,
                      width=LARGURA_SIDEBAR_INICIO)
        sb.pack(side='left', fill='y')
        sb.pack_propagate(False)
        # Borda direita
        tk.Frame(sb, bg=AZUL_BORDA, width=1).pack(side='right', fill='y')
        inner = tk.Frame(sb, bg=FUNDO_PAINEL)
        inner.pack(fill='both', expand=True)
        tk.Frame(inner, bg=FUNDO_PAINEL, height=16).pack()
        self._sb_btns = {}
        for chave, icone, label in SIDEBAR_ITENS:
            if chave == 'sep':
                tk.Frame(inner, bg=AZUL_BORDA, height=1).pack(
                    fill='x', padx=16, pady=8)
                continue
            ativo = (chave == self._aba_ativa)
            self._sb_btns[chave] = self._sb_btn(
                inner, icone, label, chave, ativo)
        # Rodape
        rod = tk.Frame(sb, bg=FUNDO_PAINEL)
        rod.pack(side='bottom', pady=14)
        tk.Label(rod, text='PCI/AP', font=FONTE_SMALL_BOLD,
                 bg=FUNDO_PAINEL, fg=DOURADO).pack()
        tk.Label(rod, text='v1.0.0-alpha', font=FONTE_MICRO,
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack()

    def _sb_btn(self, parent, icone, label, chave, ativo=False):
        bg_n  = FUNDO_ATIVO if ativo else FUNDO_PAINEL
        f = tk.Frame(parent, bg=bg_n, cursor='hand2')
        f.pack(fill='x', pady=1)
        ind = tk.Frame(f, bg=DOURADO if ativo else bg_n, width=3)
        ind.pack(side='left', fill='y')
        tk.Label(f, text=icone, font=('Segoe UI', 13),
                 bg=bg_n,
                 fg=DOURADO if ativo else TEXTO_SECUNDARIO,
                 width=2).pack(side='left', padx=(10,4), pady=10)
        tk.Label(f, text=label,
                 font=FONTE_SMALL_BOLD if ativo else FONTE_SMALL,
                 bg=bg_n,
                 fg=TEXTO_PRIMARIO if ativo else TEXTO_SECUNDARIO,
                 anchor='w').pack(side='left', fill='x', expand=True)
        def _hin(e, fr=f, at=ativo):
            if not at:
                fr.config(bg=FUNDO_HOVER)
                for w in fr.winfo_children(): w.config(bg=FUNDO_HOVER)
        def _hout(e, fr=f, at=ativo):
            if not at:
                fr.config(bg=FUNDO_PAINEL)
                for w in fr.winfo_children(): w.config(bg=FUNDO_PAINEL)
        def _click(e, ch=chave): self._navegar(ch)
        for w in [f] + list(f.winfo_children()):
            w.bind('<Enter>', _hin)
            w.bind('<Leave>', _hout)
            w.bind('<Button-1>', _click)
        return f

    def _navegar(self, chave):
        self._aba_ativa = chave
        for w in self._area.winfo_children(): w.destroy()
        if chave == 'inicio':   self._mostrar_inicio()
        elif chave == 'recentes': self._mostrar_recentes()
        else:
            tk.Label(self._area,
                     text=f'Em construcao: {chave}',
                     font=FONTE_H2, bg=FUNDO_BASE,
                     fg=TEXTO_TERCIARIO).pack(expand=True)

    def _mostrar_inicio(self):
        a = self._area
        tk.Frame(a, bg=FUNDO_BASE, height=28).pack()
        tk.Label(a, text='Bem-vindo ao SICRO',
                 font=FONTE_H1, bg=FUNDO_BASE,
                 fg=TEXTO_PRIMARIO).pack(anchor='w', padx=32)
        tk.Label(a, text='Escolha como deseja iniciar o seu croqui.',
                 font=FONTE_SMALL, bg=FUNDO_BASE,
                 fg=TEXTO_SECUNDARIO).pack(anchor='w', padx=32)
        tk.Frame(a, bg=FUNDO_BASE, height=20).pack()
        # Cards
        cf = tk.Frame(a, bg=FUNDO_BASE)
        cf.pack(fill='x', padx=32)
        acoes = [
            ('Novo Croqui Manual',
             'Comece um croqui do zero\nem uma tela vazia.',
             AZUL_MEDIO, 'zero',
             lambda: self.on_novo('zero')),
            ('Croqui com Drone',
             'Importe imagens aereas\ne crie seu croqui.',
             '#1A5A3A', 'drone',
             lambda: self.on_novo('drone')),
            ('Usar Modelo Pronto',
             'Escolha um modelo de via\ne comece rapidamente.',
             DOURADO, 'modelo',
             lambda: self.on_novo('modelo')),
        ]
        for titulo, desc, cor, img_chave, cmd in acoes:
            self._card_acao(cf, titulo, desc, cor, img_chave, cmd)
        tk.Frame(a, bg=FUNDO_BASE, height=28).pack()
        # Recentes
        rh = tk.Frame(a, bg=FUNDO_BASE)
        rh.pack(fill='x', padx=32)
        tk.Label(rh, text='Croquis recentes',
                 font=FONTE_H3, bg=FUNDO_BASE,
                 fg=TEXTO_PRIMARIO).pack(side='left')
        tk.Button(rh, text='Ver todos >',
                  font=FONTE_MICRO, cursor='hand2',
                  bg=FUNDO_BASE, fg=DOURADO,
                  activebackground=FUNDO_BASE,
                  relief='flat', bd=0,
                  command=lambda: self._navegar('recentes')).pack(side='right')
        tk.Frame(a, bg=FUNDO_BASE, height=10).pack()
        self._lista_recentes(a, limite=5)
        # Rodape
        rod = tk.Frame(a, bg=FUNDO_BASE)
        rod.pack(fill='x', padx=32, pady=16, side='bottom')
        tk.Button(rod, text='  Abrir croqui existente...',
                  font=FONTE_SMALL_BOLD, cursor='hand2',
                  bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,
                  activebackground=FUNDO_HOVER,
                  relief='flat', bd=0, padx=16, pady=8,
                  command=self._abrir_sel).pack(side='left')

    def _card_acao(self, parent, titulo, desc, cor_acento, img_chave, cmd):
        IMG_H = 140
        card = tk.Frame(parent, bg=FUNDO_CARD, cursor='hand2')
        card.pack(side='left', fill='x', expand=True, padx=(0,12))
        # Imagem de fundo — Canvas com altura fixa
        img_canvas = tk.Canvas(card, height=IMG_H, bg=FUNDO_CARD,
                              highlightthickness=0)
        img_canvas.pack(fill='x')
        def _draw_img(event, ic=img_canvas, ck=img_chave, ih=IMG_H, ca=cor_acento):
            w = ic.winfo_width()
            if w < 2: return
            tk_img = _carregar_card_img(ck, w, ih)
            ic.delete('all')
            if tk_img:
                ic._img = tk_img
                ic.create_image(0, 0, anchor='nw', image=tk_img)
            else:
                ic.create_rectangle(0, 0, w, ih, fill=ca, outline='')
        img_canvas.bind('<Configure>', _draw_img)
        # Faixa colorida separadora
        tk.Frame(card, bg=cor_acento, height=2).pack(fill='x')
        # Conteudo
        inner = tk.Frame(card, bg=FUNDO_CARD)
        inner.pack(fill='both', expand=True, padx=14, pady=12)
        tk.Label(inner, text=titulo, font=FONTE_BODY_BOLD,
                 bg=FUNDO_CARD, fg=TEXTO_PRIMARIO, anchor='w').pack(fill='x')
        tk.Label(inner, text=desc, font=FONTE_SMALL,
                 bg=FUNDO_CARD, fg=TEXTO_SECUNDARIO,
                 justify='left', anchor='w').pack(fill='x', pady=(4,10))
        btn_fg = TEXTO_INVERTIDO if cor_acento == DOURADO else TEXTO_PRIMARIO
        tk.Button(inner, text='Iniciar  >',
                  font=FONTE_SMALL_BOLD, cursor='hand2',
                  bg=cor_acento, fg=btn_fg,
                  activebackground=FUNDO_HOVER,
                  relief='flat', bd=0, padx=12, pady=5,
                  command=cmd).pack(anchor='w')
        # Hover
        def _hin(e):
            card.config(bg=FUNDO_HOVER); inner.config(bg=FUNDO_HOVER)
            for w in inner.winfo_children():
                try: w.config(bg=FUNDO_HOVER)
                except Exception: pass
        def _hout(e):
            card.config(bg=FUNDO_CARD); inner.config(bg=FUNDO_CARD)
            for w in inner.winfo_children():
                try: w.config(bg=FUNDO_CARD)
                except Exception: pass
        card.bind('<Enter>', _hin); card.bind('<Leave>', _hout)
        inner.bind('<Enter>', _hin); inner.bind('<Leave>', _hout)

    def _mostrar_recentes(self):
        a = self._area
        tk.Frame(a, bg=FUNDO_BASE, height=28).pack()
        tk.Label(a, text='Croquis recentes',
                 font=FONTE_H1, bg=FUNDO_BASE,
                 fg=TEXTO_PRIMARIO).pack(anchor='w', padx=32)
        tk.Frame(a, bg=FUNDO_BASE, height=14).pack()
        self._lista_recentes(a, limite=50)

    def _lista_recentes(self, parent, limite=5):
        arqs = sorted(DIR_CROQUIS.glob('*.sicro'), reverse=True)[:limite]
        self._arqs_recentes = list(arqs)
        if not arqs:
            tk.Label(parent,
                     text='Nenhum croqui salvo ainda.',
                     font=FONTE_SMALL, bg=FUNDO_BASE,
                     fg=TEXTO_TERCIARIO).pack(padx=32, anchor='w')
            return
        for i, arq in enumerate(arqs):
            self._item_recente(parent, arq)

    def _item_recente(self, parent, arq):
        try:
            with open(arq) as f: d = json.load(f)
        except Exception: d = {}
        bo    = d.get('bo', '?')
        local = d.get('local', arq.stem)[:50]
        data  = d.get('data', '')
        modo  = d.get('modo', 'zero')
        tag_cor = AZUL_MEDIO if modo == 'zero' else '#1A5A3A'
        tag_txt = 'Manual' if modo == 'zero' else 'Drone'
        row = tk.Frame(parent, bg=FUNDO_CARD, cursor='hand2')
        row.pack(fill='x', padx=32, pady=2)
        tk.Frame(row, bg=AZUL_BORDA, width=3).pack(side='left', fill='y')
        info = tk.Frame(row, bg=FUNDO_CARD)
        info.pack(side='left', fill='both', expand=True, padx=12, pady=8)
        top = tk.Frame(info, bg=FUNDO_CARD)
        top.pack(fill='x')
        tk.Label(top, text=f'BO {bo}', font=FONTE_BODY_BOLD,
                 bg=FUNDO_CARD, fg=TEXTO_PRIMARIO).pack(side='left')
        tk.Label(top, text=f'  {tag_txt}', font=FONTE_MICRO,
                 bg=tag_cor, fg=TEXTO_PRIMARIO,
                 padx=6).pack(side='left', padx=8)
        tk.Label(top, text=data, font=FONTE_MICRO,
                 bg=FUNDO_CARD, fg=TEXTO_TERCIARIO).pack(side='right')
        tk.Label(info, text=local, font=FONTE_SMALL,
                 bg=FUNDO_CARD, fg=TEXTO_SECUNDARIO, anchor='w').pack(fill='x')
        def _bg_rec(w, cor):
            try: w.config(bg=cor)
            except Exception: pass
            for ch in w.winfo_children(): _bg_rec(ch, cor)
        def _hin(e): _bg_rec(row, FUNDO_HOVER)
        def _hout(e): _bg_rec(row, FUNDO_CARD)
        def _abrir(e): self.on_abrir(arq)
        row.bind('<Enter>', _hin); row.bind('<Leave>', _hout)
        row.bind('<Double-Button-1>', _abrir)
        for w in row.winfo_children():
            w.bind('<Double-Button-1>', _abrir)

    def _abrir_sel(self):
        from tkinter import filedialog
        cam = filedialog.askopenfilename(
            title='Abrir croqui',
            filetypes=[('Croquis SICRO', '*.sicro'), ('Todos', '*.*')],
            initialdir=DIR_CROQUIS)
        if cam:
            self.on_abrir(Path(cam))
