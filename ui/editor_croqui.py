import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json, math, datetime
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

from config import (
    COR_FUNDO, COR_PAINEL, COR_CARD, COR_BORDA,
    COR_TEXTO, COR_TEXTO_SEC,
    COR_SUCESSO, COR_PERIGO, COR_AVISO,
    COR_R1, COR_R2, COR_COTA,
    AMARELO, BRANCO, CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_SOFT,
    AZUL_MEDIO, AZUL_CLARO,
    FONTE_SUB, FONTE_NORMAL, FONTE_PEQ, FONTE_MONO,
    DIR_CROQUIS, TIPO_INFO, FERRAMENTAS_VIA, MODELOS_PLACA, MODELOS_VIA,
    gerar_elementos_modelo,
)
from desenho.veiculos_arte import (
    arte_sedan, arte_suv, arte_hatch,
    arte_moto_esportiva, arte_moto_urbana, arte_moto_carga,
    arte_caminhao_leve, arte_caminhao_truck, arte_caminhao_carreta,
    arte_bicicleta, arte_pedestre, escurecer,
)
from popups.popup_veiculo import PopupModeloVeiculo, MODELOS_VEICULOS
from popups.popup_placas import PopupPlacas
from popups.popup_modelo_via import PopupModeloVia
from widgets.editor_texto import EditorTextoInline

# Aliases para compatibilidade com codigo interno do EditorCroqui
_arte_bicicleta = arte_bicicleta
_arte_pedestre  = arte_pedestre

# Cache de imagens PNG dos veiculos
_IMG_CACHE: dict = {}

def carregar_imagem_veiculo(nome_arquivo, cor_hex):
    if not PIL_OK: return None
    chave = (nome_arquivo, cor_hex)
    if chave in _IMG_CACHE: return _IMG_CACHE[chave]
    try:
        import numpy as np
        from collections import deque
        from config import DIR_ASSETS
        caminho = DIR_ASSETS / nome_arquivo
        if not caminho.exists(): return None
        img = Image.open(caminho).convert('RGBA')
        arr = np.array(img)
        alpha = arr[:,:,3]
        brightness = arr[:,:,0].astype(int)+arr[:,:,1].astype(int)+arr[:,:,2].astype(int)
        if alpha.min()==255:
            gray=(brightness//3).clip(0,255).astype('uint8')
            visited=np.zeros(gray.shape,dtype=bool)
            mask=np.ones(gray.shape,dtype=bool)
            h_,w_=gray.shape; threshold=20
            starts=([(0,x) for x in range(0,w_,4)]+[(h_-1,x) for x in range(0,w_,4)]+
                    [(y,0) for y in range(0,h_,4)]+[(y,w_-1) for y in range(0,h_,4)])
            queue=deque()
            for sy,sx in starts:
                if not visited[sy,sx] and gray[sy,sx]<threshold:
                    visited[sy,sx]=True; mask[sy,sx]=False; queue.append((sy,sx))
            while queue:
                y,x=queue.popleft()
                for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                    ny,nx=y+dy,x+dx
                    if 0<=ny<h_ and 0<=nx<w_ and not visited[ny,nx] and gray[ny,nx]<threshold:
                        visited[ny,nx]=True; mask[ny,nx]=False; queue.append((ny,nx))
            arr[~mask,3]=0
        try: cr=int(cor_hex[1:3],16); cg=int(cor_hex[3:5],16); cb_=int(cor_hex[5:7],16)
        except: cr,cg,cb_=79,114,224
        opaque=arr[:,:,3]>30
        escuro=(arr[:,:,0].astype(int)+arr[:,:,1].astype(int)+arr[:,:,2].astype(int))<300
        alvo=opaque&escuro
        arr[alvo,0]=cr; arr[alvo,1]=cg; arr[alvo,2]=cb_
        resultado=Image.fromarray(arr); _IMG_CACHE[chave]=resultado; return resultado
    except Exception as e:
        print(f'[carregar_imagem_veiculo] erro: {e}'); return None

# ─── DialogoRedimensionar ───
class DialogoRedimensionar(tk.Toplevel):
    """
    Abre após inserir qualquer elemento.
    Mostra sliders de largura, altura e ângulo.
    Atualiza o elemento em tempo real.
    """
    def __init__(self, parent, elemento, redesenhar_cb):
        super().__init__(parent)
        self.title("Ajustar elemento")
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)
        self.grab_set()
        self.el = elemento
        self.cb = redesenhar_cb

        w, h = 440, 380
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        tk.Frame(self, bg=AMARELO, height=4).pack(fill="x")
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=20, pady=14)

        icone, nome = TIPO_INFO.get(elemento["tipo"], ("?", elemento["tipo"]))
        tk.Label(corpo, text=f"{icone}  Ajustar: {nome}",
                 font=FONTE_SUB, bg=COR_FUNDO, fg=AMARELO).pack(anchor="w", pady=(0,8))

        tipo = elemento["tipo"]
        self.vars = {}

        # ── Campo de rótulo (sempre visível quando elemento tem label) ──
        if "label" in elemento:
            row_lbl = tk.Frame(corpo, bg=COR_FUNDO)
            row_lbl.pack(fill="x", pady=4)
            tk.Label(row_lbl, text="Identificação", font=FONTE_PEQ,
                     width=18, anchor="w",
                     bg=COR_FUNDO, fg=COR_TEXTO_SEC).pack(side="left")
            self._entry_label = tk.Entry(row_lbl, font=FONTE_NORMAL,
                                         bg=COR_CARD, fg=BRANCO,
                                         insertbackground=BRANCO,
                                         relief="flat", bd=4)
            self._entry_label.insert(0, elemento.get("label", ""))
            self._entry_label.pack(side="left", fill="x", expand=True)
            self._entry_label.bind("<KeyRelease>", self._ao_digitar_label)
        else:
            self._entry_label = None

        # ── Sliders ──
        tem_escala    = tipo in ("carro","moto","caminhao","bicicleta","pedestre")
        tem_angulo    = tipo in ("carro","moto","caminhao","bicicleta","pedestre","sc")
        tem_espessura = tipo in ("r1","r2")
        tem_tamanho   = tipo == "sc"

        if tem_escala:
            self._slider(corpo, "Largura  (px)", "larg",
                         elemento.get("larg", self._larg_padrao(tipo)), 5, 120)
            self._slider(corpo, "Altura    (px)", "alt",
                         elemento.get("alt",  self._alt_padrao(tipo)), 3, 60)

        if tem_angulo:
            self._slider(corpo, "Ângulo   (°)", "angulo",
                         elemento.get("angulo", 0), 0, 359)

        if tem_espessura:
            self._slider(corpo, "Espessura da linha (px)", "espessura",
                         elemento.get("espessura", 2), 1, 16)

        if tem_tamanho:
            self._slider(corpo, "Tamanho  (px)", "tamanho_sc",
                         elemento.get("tamanho_sc", 10), 4, 50)
            self._slider(corpo, "Ângulo   (°)", "angulo",
                         elemento.get("angulo", 0), 0, 359)

        tk.Frame(corpo, bg=COR_BORDA, height=1).pack(fill="x", pady=10)

        btns = tk.Frame(corpo, bg=COR_FUNDO)
        btns.pack(fill="x")
        tk.Button(btns, text="OK  ✓",
                  font=("Segoe UI",10,"bold"), cursor="hand2",
                  bg=AZUL_MEDIO, fg=BRANCO,
                  activebackground=AZUL_CLARO,
                  relief="flat", padx=16, pady=5,
                  command=self._confirmar).pack(side="right")

        tk.Frame(self, bg=AMARELO, height=4).pack(fill="x", side="bottom")

    def _ao_digitar_label(self, event=None):
        """Atualiza o label do elemento em tempo real enquanto digita."""
        if self._entry_label:
            self.el["label"] = self._entry_label.get()
            self.cb()

    def _confirmar(self):
        """Salva o label e fecha."""
        if self._entry_label:
            self.el["label"] = self._entry_label.get()
        self.destroy()

    def _larg_padrao(self, tipo):
        return {"carro":26,"moto":18,"caminhao":36,"bicicleta":15,"pedestre":14}.get(tipo,20)

    def _alt_padrao(self, tipo):
        return {"carro":13,"moto":7,"caminhao":15,"bicicleta":5,"pedestre":14}.get(tipo,10)

    def _slider(self, parent, label, chave, valor_ini, minv, maxv):
        row = tk.Frame(parent, bg=COR_FUNDO)
        row.pack(fill="x", pady=4)

        tk.Label(row, text=label, font=FONTE_PEQ, width=18,
                 anchor="w", bg=COR_FUNDO, fg=COR_TEXTO_SEC).pack(side="left")

        var = tk.IntVar(value=int(valor_ini))
        self.vars[chave] = var

        lbl_val = tk.Label(row, text=str(int(valor_ini)),
                           font=FONTE_MONO, width=4,
                           bg=COR_FUNDO, fg=AMARELO)
        lbl_val.pack(side="right")

        sty = ttk.Style()
        sty.configure("Amarelo.Horizontal.TScale",
                       background=COR_FUNDO, troughcolor=COR_CARD,
                       sliderthickness=14)

        def ao_mover(val, c=chave, lv=lbl_val):
            v = int(float(val))
            lv.config(text=str(v))
            self.el[c] = v
            self.cb()

        sc = ttk.Scale(row, from_=minv, to=maxv, orient="horizontal",
                       variable=var, command=ao_mover,
                       style="Amarelo.Horizontal.TScale",
                       length=170)
        sc.pack(side="left", padx=6)
        self.el.setdefault(chave, int(valor_ini))


# ─────────────────────────────────────────────
#  TELA INICIAL
# ─────────────────────────────────────────────
class TelaInicial(tk.Frame):
    def __init__(self, master, on_novo, on_abrir, img_brasao=None):
        super().__init__(master, bg=COR_FUNDO)
        self.on_novo = on_novo
        self.on_abrir = on_abrir
        self.img_brasao = img_brasao
        self._build()

    def _build(self):
        cab = tk.Frame(self, bg=COR_PAINEL)
        cab.pack(fill="x")
        tk.Frame(cab, bg=AMARELO, height=4).pack(fill="x")
        inner = tk.Frame(cab, bg=COR_PAINEL)
        inner.pack(fill="x", padx=20, pady=10)

        if self.img_brasao and PIL_OK:
            img = self.img_brasao.resize((40,40), Image.LANCZOS)
            self._hdr_tk = ImageTk.PhotoImage(img)
            tk.Label(inner, image=self._hdr_tk, bg=COR_PAINEL).pack(side="left", padx=(0,10))

        tk.Label(inner, text="SICRO PCI/AP", font=("Segoe UI",14,"bold"),
                 bg=COR_PAINEL, fg=BRANCO).pack(side="left")
        tk.Label(inner, text="Polícia Científica do Amapá",
                 font=FONTE_PEQ, bg=COR_PAINEL, fg=AMARELO).pack(side="left", padx=10)
        tk.Label(inner, text=datetime.date.today().strftime("%d/%m/%Y"),
                 font=FONTE_PEQ, bg=COR_PAINEL, fg=CINZA_MEDIO).pack(side="right")

        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=24, pady=18)

        esq = tk.Frame(corpo, bg=COR_FUNDO)
        esq.pack(side="left", fill="y", padx=(0,16))
        tk.Label(esq, text="Novo croqui", font=FONTE_SUB,
                 bg=COR_FUNDO, fg=AMARELO).pack(anchor="w", pady=(0,8))
        self._card(esq,"🗺","Croqui do zero",
                   "Sem imagem de fundo\ndesenho vetorial completo",
                   AZUL_MEDIO, lambda: self.on_novo("zero"))
        self._card(esq,"🚁","Croqui sobre drone",
                   "Carrega foto aérea\ncalibra escala pela lona",
                   CINZA_ESCURO, lambda: self.on_novo("drone"))

        tk.Frame(corpo, bg=COR_BORDA, width=1).pack(side="left", fill="y", padx=4)

        dir_ = tk.Frame(corpo, bg=COR_FUNDO)
        dir_.pack(side="left", fill="both", expand=True)
        topo = tk.Frame(dir_, bg=COR_FUNDO)
        topo.pack(fill="x")
        tk.Label(topo, text="Biblioteca de croquis", font=FONTE_SUB,
                 bg=COR_FUNDO, fg=AMARELO).pack(side="left")
        tk.Button(topo, text="↺ Atualizar", font=FONTE_PEQ, cursor="hand2",
                  bg=COR_CARD, fg=COR_TEXTO_SEC, activebackground=COR_BORDA,
                  relief="flat", command=self._carregar).pack(side="right")

        flb = tk.Frame(dir_, bg=COR_CARD)
        flb.pack(fill="both", expand=True, pady=6)
        scrl = tk.Scrollbar(flb)
        scrl.pack(side="right", fill="y")
        self.lb = tk.Listbox(flb, yscrollcommand=scrl.set,
                             bg=COR_CARD, fg=COR_TEXTO,
                             selectbackground=AZUL_MEDIO,
                             selectforeground=BRANCO,
                             font=FONTE_NORMAL, relief="flat", bd=0,
                             activestyle="none", highlightthickness=0)
        self.lb.pack(fill="both", expand=True, padx=2)
        scrl.config(command=self.lb.yview)
        self.lb.bind("<Double-Button-1>", self._abrir_sel)

        tk.Button(dir_, text="Abrir croqui selecionado →",
                  font=FONTE_NORMAL, cursor="hand2",
                  bg=AZUL_MEDIO, fg=BRANCO,
                  activebackground=AZUL_CLARO,
                  relief="flat", pady=7,
                  command=self._abrir_sel).pack(fill="x")
        self._carregar()

    def _card(self, parent, icone, titulo, desc, cor, cmd):
        f = tk.Frame(parent, bg=COR_CARD, cursor="hand2")
        f.pack(fill="x", pady=4, ipadx=12, ipady=10)
        tk.Frame(f, bg=cor, width=4).pack(side="left", fill="y")
        inner = tk.Frame(f, bg=COR_CARD)
        inner.pack(side="left", padx=10)
        tk.Label(inner, text=f"{icone}  {titulo}", font=("Segoe UI",11,"bold"),
                 bg=COR_CARD, fg=BRANCO).pack(anchor="w")
        tk.Label(inner, text=desc, font=FONTE_PEQ,
                 bg=COR_CARD, fg=CINZA_CLARO, justify="left").pack(anchor="w")
        for w in [f,inner]+list(inner.winfo_children()):
            w.bind("<Button-1>", lambda e,c=cmd: c())
        f.bind("<Enter>", lambda e: f.config(bg="#1E2A60"))
        f.bind("<Leave>", lambda e: f.config(bg=COR_CARD))

    def _carregar(self):
        self.lb.delete(0, tk.END)
        self._arqs = sorted(DIR_CROQUIS.glob("*.sicro"), reverse=True)
        if not self._arqs:
            self.lb.insert(tk.END, "  (nenhum croqui salvo)")
            return
        for a in self._arqs:
            try:
                with open(a) as f:
                    d = json.load(f)
                self.lb.insert(tk.END,
                    f"  BO {d.get('bo','?')}  ·  {d.get('data','')}  ·  {d.get('local',a.stem)[:40]}")
            except Exception:
                self.lb.insert(tk.END, f"  {a.name}")

    def _abrir_sel(self, event=None):
        idx = self.lb.curselection()
        if not idx or not hasattr(self,"_arqs"): return
        if idx[0] < len(self._arqs):
            self.on_abrir(self._arqs[idx[0]])


# ─────────────────────────────────────────────
#  CALENDÁRIO POPUP (seleção de data nativa Tkinter)
# ─────────────────────────────────────────────
class CalendarioPopup(tk.Toplevel):
    """Calendário nativo em Tkinter puro — sem dependências externas."""
    def __init__(self, parent, entry_destino):
        super().__init__(parent)
        self.entry = entry_destino
        self.overrideredirect(True)
        self.configure(bg=COR_PAINEL)
        self.attributes("-topmost", True)

        # Data atual
        try:
            d, m, y = entry_destino.get().strip().split("/")
            self._data = datetime.date(int(y), int(m), int(d))
        except Exception:
            self._data = datetime.date.today()
        self._ano  = self._data.year
        self._mes  = self._data.month

        # Posiciona abaixo do entry
        self.update_idletasks()
        ex = entry_destino.winfo_rootx()
        ey = entry_destino.winfo_rooty() + entry_destino.winfo_height()
        self.geometry(f"260x240+{ex}+{ey}")
        self.lift()

        self._build()
        self.bind("<FocusOut>", lambda e: self.after(100, self._fechar_se_fora))
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

        tk.Frame(self, bg=AMARELO, height=3).pack(fill="x")

        # Cabeçalho: mês/ano com navegação
        nav = tk.Frame(self, bg=COR_PAINEL)
        nav.pack(fill="x", padx=4, pady=4)

        tk.Button(nav, text="◀", font=("Segoe UI",10), width=2,
                  bg=COR_PAINEL, fg=BRANCO, relief="flat", cursor="hand2",
                  command=self._mes_anterior).pack(side="left")
        tk.Button(nav, text="▶", font=("Segoe UI",10), width=2,
                  bg=COR_PAINEL, fg=BRANCO, relief="flat", cursor="hand2",
                  command=self._mes_seguinte).pack(side="right")

        MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                 "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        tk.Label(nav, text=f"{MESES[self._mes-1]} {self._ano}",
                 font=("Segoe UI",10,"bold"),
                 bg=COR_PAINEL, fg=AMARELO).pack(expand=True)

        # Dias da semana
        dias_sem = tk.Frame(self, bg=COR_PAINEL)
        dias_sem.pack(fill="x", padx=4)
        for ds in ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"]:
            tk.Label(dias_sem, text=ds, font=("Segoe UI",8),
                     bg=COR_PAINEL, fg=CINZA_MEDIO, width=3).pack(side="left")

        tk.Frame(self, bg=COR_BORDA, height=1).pack(fill="x", padx=4, pady=2)

        # Grid de dias
        import calendar
        grid = tk.Frame(self, bg=COR_PAINEL)
        grid.pack(fill="both", expand=True, padx=4, pady=2)

        cal = calendar.monthcalendar(self._ano, self._mes)
        hoje = datetime.date.today()

        for semana in cal:
            row_f = tk.Frame(grid, bg=COR_PAINEL)
            row_f.pack(fill="x")
            for dia in semana:
                if dia == 0:
                    tk.Label(row_f, text="", width=3, bg=COR_PAINEL).pack(side="left")
                else:
                    d = datetime.date(self._ano, self._mes, dia)
                    is_hoje  = (d == hoje)
                    is_sel   = (d == self._data)
                    bg = AMARELO if is_sel else AZUL_MEDIO if is_hoje else COR_PAINEL
                    fg = PRETO_SOFT if is_sel else BRANCO
                    btn = tk.Button(row_f, text=str(dia),
                                    font=("Segoe UI",9,"bold" if is_hoje or is_sel else "normal"),
                                    width=3, bg=bg, fg=fg,
                                    activebackground=AZUL_CLARO,
                                    relief="flat", cursor="hand2",
                                    command=lambda d=d: self._selecionar(d))
                    btn.pack(side="left")

        tk.Frame(self, bg=AMARELO, height=3).pack(fill="x", side="bottom")

    def _mes_anterior(self):
        if self._mes == 1:
            self._mes = 12; self._ano -= 1
        else:
            self._mes -= 1
        self._build()

    def _mes_seguinte(self):
        if self._mes == 12:
            self._mes = 1; self._ano += 1
        else:
            self._mes += 1
        self._build()

    def _selecionar(self, data):
        self._data = data
        self.entry.delete(0, tk.END)
        self.entry.insert(0, data.strftime("%d/%m/%Y"))
        self.destroy()


# ─────────────────────────────────────────────
#  DIÁLOGO DADOS DO CASO
# ─────────────────────────────────────────────
class DialogoDadosCaso(tk.Toplevel):
    def __init__(self, parent, modo="zero"):
        super().__init__(parent)
        self.title("Dados do caso")
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)
        self.grab_set()
        self.resultado = None
        w, h = 480, 400
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        tk.Frame(self, bg=AMARELO, height=4).pack(fill="x")
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True, padx=24, pady=16)
        tk.Label(corpo, text=f"📋  {'Croqui do zero' if modo=='zero' else 'Croqui sobre drone'}",
                 font=FONTE_SUB, bg=COR_FUNDO, fg=AMARELO).pack(anchor="w", pady=(0,12))

        campos = [
            ("Nº do BO",           "bo",         ""),
            ("Nº da Requisição",   "requisicao",  ""),
            ("Local (ruas/av.)",   "local",       ""),
            ("Município",          "municipio",   "Porto Grande"),
            ("Perito responsável", "perito",      "André Ricardo Barroso"),
            ("Data do exame",      "data",        datetime.date.today().strftime("%d/%m/%Y")),
        ]
        MUNICIPIOS_AP = [
            "Macapá","Santana","Laranjal do Jari","Oiapoque","Tartarugalzinho",
            "Mazagão","Porto Grande","Calçoene","Pedra Branca do Amapari",
            "Vitória do Jari","Serra do Navio","Amapá","Ferreira Gomes",
            "Itaubal","Cutias","Pracuúba"
        ]

        self.entradas = {}
        for label, chave, ph in campos:
            row = tk.Frame(corpo, bg=COR_FUNDO)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=FONTE_PEQ, width=20,
                     anchor="w", bg=COR_FUNDO, fg=COR_TEXTO_SEC).pack(side="left")

            if chave == "municipio":
                # Frame especial com Entry + botão dropdown
                mframe = tk.Frame(row, bg=COR_CARD)
                mframe.pack(side="left", fill="x", expand=True)
                e = tk.Entry(mframe, font=FONTE_NORMAL,
                             bg=COR_CARD, fg=BRANCO,
                             insertbackground=BRANCO, relief="flat", bd=4)
                e.insert(0, ph)
                e.pack(side="left", fill="x", expand=True)
                # Botão dropdown
                btn_dd = tk.Button(mframe, text="▾", font=("Segoe UI",10),
                                   bg=COR_CARD, fg=CINZA_CLARO,
                                   activebackground=AZUL_MEDIO,
                                   relief="flat", cursor="hand2", padx=4)
                btn_dd.pack(side="right")

                # Lista de sugestões (autocomplete)
                # Dropdown flutuante (Toplevel) posicionado sobre o Entry
                self._dd_win = None

                def _fechar_dd():
                    if self._dd_win and self._dd_win.winfo_exists():
                        self._dd_win.destroy()
                    self._dd_win = None

                def _mostrar_dd(lista, entry=e):
                    _fechar_dd()
                    self.update_idletasks()
                    # Posiciona abaixo do mframe (Entry+botão)
                    ex = mframe.winfo_rootx()
                    ey = mframe.winfo_rooty() + mframe.winfo_height()
                    ew = mframe.winfo_width()
                    altura = min(len(lista), 10) * 24
                    win = tk.Toplevel(self)
                    win.overrideredirect(True)
                    win.geometry(f"{ew}x{altura}+{ex}+{ey}")
                    win.configure(bg=COR_CARD)
                    win.attributes("-topmost", True)
                    win.lift()
                    self._dd_win = win
                    lb2 = tk.Listbox(win,
                                     bg="#1A2A5A", fg=BRANCO,
                                     selectbackground=AZUL_MEDIO,
                                     selectforeground=BRANCO,
                                     font=FONTE_NORMAL,
                                     relief="flat", bd=0,
                                     activestyle="dotbox",
                                     highlightthickness=1,
                                     highlightcolor=AZUL_MEDIO)
                    lb2.pack(fill="both", expand=True)
                    for m in lista:
                        lb2.insert(tk.END, f"  {m}")

                    def _sel_dd(event, entry=entry):
                        idx = lb2.nearest(event.y)
                        if idx >= 0:
                            lb2.selection_clear(0, tk.END)
                            lb2.selection_set(idx)
                            val = lb2.get(idx).strip()
                            entry.delete(0, tk.END)
                            entry.insert(0, val)
                        # Delay maior para garantir que o Entry recebeu o valor
                        win.after(200, _fechar_dd)

                    lb2.bind("<Button-1>", _sel_dd)
                    # Sem FocusOut — fecha apenas ao selecionar

                def _ao_digitar(event, entry=e, lista=MUNICIPIOS_AP):
                    txt = entry.get().lower()
                    filtrados = [m for m in lista if txt in m.lower()]
                    if filtrados and txt:
                        _mostrar_dd(filtrados, entry)
                    else:
                        _fechar_dd()

                e.bind("<KeyRelease>", _ao_digitar)
                e.bind("<Escape>", lambda ev: _fechar_dd())
                # Fecha só com Escape ou selecionando — sem outros fechamentos automáticos
                # O botão alterna: se já aberto fecha, se fechado abre
                def _toggle_dd(lista=MUNICIPIOS_AP, entry=e):
                    if self._dd_win and self._dd_win.winfo_exists():
                        _fechar_dd()
                    else:
                        _mostrar_dd(lista, entry)
                btn_dd.config(command=_toggle_dd)
            elif chave == "data":
                # Frame com Entry de data + botão calendário
                dframe = tk.Frame(row, bg=COR_CARD)
                dframe.pack(side="left", fill="x", expand=True)
                e = tk.Entry(dframe, font=FONTE_NORMAL,
                             bg=COR_CARD, fg=BRANCO,
                             insertbackground=BRANCO, relief="flat", bd=4)
                e.insert(0, datetime.date.today().strftime("%d/%m/%Y"))
                e.pack(side="left", fill="x", expand=True)
                btn_cal = tk.Button(dframe, text="📅", font=("Segoe UI",10),
                                    bg=COR_CARD, fg=AMARELO,
                                    activebackground=AZUL_MEDIO,
                                    relief="flat", cursor="hand2", padx=4)
                btn_cal.pack(side="right")

                def _abrir_calendario(entry=e):
                    CalendarioPopup(self, entry)

                btn_cal.config(command=_abrir_calendario)
                e.bind("<Button-1>", lambda ev, en=e: _abrir_calendario(en))
            else:
                e = tk.Entry(row, font=FONTE_NORMAL,
                             bg=COR_CARD, fg=BRANCO,
                             insertbackground=BRANCO, relief="flat", bd=4)
                e.insert(0, ph)
                e.pack(side="left", fill="x", expand=True)

            self.entradas[chave] = e

        tk.Frame(corpo, bg=COR_BORDA, height=1).pack(fill="x", pady=10)
        btns = tk.Frame(corpo, bg=COR_FUNDO)
        btns.pack(fill="x")
        tk.Button(btns, text="Cancelar", font=FONTE_NORMAL, cursor="hand2",
                  bg=COR_CARD, fg=COR_TEXTO_SEC, activebackground=COR_BORDA,
                  relief="flat", padx=14, pady=5,
                  command=self.destroy).pack(side="right", padx=(6,0))
        tk.Button(btns, text="Criar croqui →",
                  font=("Segoe UI",10,"bold"), cursor="hand2",
                  bg=AZUL_MEDIO, fg=BRANCO, activebackground=AZUL_CLARO,
                  relief="flat", padx=14, pady=5,
                  command=self._ok).pack(side="right")
        tk.Frame(self, bg=AMARELO, height=4).pack(fill="x", side="bottom")

    def _ok(self):
        self.resultado = {k: v.get().strip() for k,v in self.entradas.items()}
        self.destroy()


# ─────────────────────────────────────────────
#  EDITOR DE CROQUI  ── NÚCLEO
# ─────────────────────────────────────────────

# ─── EditorCroqui ───
class EditorCroqui(tk.Frame):

    FERRAMENTAS = [
        ("sel",       "↖",  "Selecionar / mover"),
        ("r1",        "R1", "Traçar eixo R1 (vertical)"),
        ("r2",        "R2", "Traçar eixo R2 (horizontal)"),
        ("carro",     "🚗", "Veículo — carro"),
        ("moto",      "🏍", "Veículo — moto"),
        ("caminhao",  "🚚", "Veículo — caminhão"),
        ("bicicleta", "🚲", "Veículo — bicicleta"),
        ("pedestre",  "🚶", "Pedestre"),
        ("sc",        "✕",  "Sítio de colisão (SC)"),
        ("cota",      "↔",  "Cota / medida"),
        ("calibrar",  "📐", "Calibrar escala (drone)"),
        ("texto",     "T",  "Texto / anotação"),
        ("apagar",    "⌫",  "Apagar elemento"),
    ]

    def __init__(self, master, dados_caso, modo="zero",
                 img_drone=None, elementos_iniciais=None):
        super().__init__(master, bg=COR_FUNDO)
        self.dados_caso   = dados_caso
        self.modo         = modo
        self.img_drone    = img_drone
        self.img_drone_tk = None

        self.elementos  = list(elementos_iniciais or [])
        self._historico = []
        self._MAX_UNDO  = 50
        self.ferramenta = "sel"
        self.sel_idx    = None
        self.drag_start = None
        self.tmp_linha  = None
        # Modo via: False = modo normal, True = modo arte/via
        self._modo_via  = False

        self.calibrado  = False
        self.k          = None
        self.calib_pts  = []
        self.u_k        = None

        self.zoom  = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._pan_start = None

        self._build_ui()
        self._atualizar_camadas()
        # Aguarda o canvas ter tamanho real antes do primeiro redesenho
        self.after(50, self._redesenhar)

    # ──────────────────────────────────────────
    #  HISTÓRICO / UNDO (Ctrl+Z)
    # ──────────────────────────────────────────
    def _salvar_historico(self):
        """Salva snapshot dos elementos antes de qualquer mutação."""
        import copy
        snap = copy.deepcopy(self.elementos)
        self._historico.append(snap)
        if len(self._historico) > self._MAX_UNDO:
            self._historico.pop(0)

    def _desfazer(self, event=None):
        """Ctrl+Z — restaura o último snapshot."""
        if not self._historico:
            self.status.config(text="Nada para desfazer")
            return
        import copy
        self.elementos = copy.deepcopy(self._historico.pop())
        self.sel_idx = None
        self._atualizar_camadas()
        self._redesenhar()
        self.status.config(text=f"Desfeito  ({len(self._historico)} passos disponíveis)")

    # ──────────────────────────────────────────
    #  UI
    # ──────────────────────────────────────────
    def _build_ui(self):
        # Barra superior
        barra = tk.Frame(self, bg=COR_PAINEL)
        barra.pack(fill="x")
        tk.Frame(barra, bg=AMARELO, height=3).pack(fill="x")
        info = tk.Frame(barra, bg=COR_PAINEL)
        info.pack(fill="x", padx=12, pady=6)
        bo = self.dados_caso.get("bo","—")
        local = self.dados_caso.get("local","—")
        tk.Label(info, text=f"BO {bo}  ·  {local}",
                 font=("Segoe UI",10,"bold"), bg=COR_PAINEL, fg=BRANCO).pack(side="left")
        self.label_escala = tk.Label(info,
            text="📐 Não calibrado" if self.modo=="drone" else "Modo vetorial",
            font=FONTE_PEQ, bg=COR_PAINEL,
            fg=COR_AVISO if self.modo=="drone" else COR_SUCESSO)
        self.label_escala.pack(side="right", padx=8)
        for txt, cmd in [("💾 Salvar",self._salvar),
                          ("📄 PDF",self._exportar_pdf),
                          ("🏠 Início",self._voltar)]:
            tk.Button(info, text=txt, font=FONTE_PEQ, cursor="hand2",
                      bg=COR_CARD, fg=BRANCO, activebackground=AZUL_MEDIO,
                      relief="flat", padx=10, pady=3,
                      command=cmd).pack(side="right", padx=2)

        # Corpo
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True)

        # ── Toolbar esquerda ──
        self._tb = tk.Frame(corpo, bg=COR_PAINEL, width=56)
        self._tb.pack(side="left", fill="y")
        self._tb.pack_propagate(False)
        tb = self._tb

        # Faixa topo
        tk.Frame(tb, bg=AMARELO, height=2).pack(fill="x")

        # Botões de ferramentas normais
        self.btns_ferr = {}
        for chave, icone, dica in self.FERRAMENTAS:
            btn = tk.Button(tb, text=icone, font=("Segoe UI",12),
                            width=3, cursor="hand2",
                            bg=COR_PAINEL, fg=BRANCO,
                            activebackground=AZUL_MEDIO, relief="flat",
                            command=lambda c=chave: self._set_ferr(c))
            btn.pack(pady=1, padx=3)
            btn.bind("<Enter>", lambda e,d=dica: self.status.config(text=d))
            self.btns_ferr[chave] = btn

        # Botões de ferramentas de via (ocultos inicialmente)
        self.btns_via = {}
        for chave, icone, dica in FERRAMENTAS_VIA:
            btn = tk.Button(tb, text=icone, font=("Segoe UI",12),
                            width=3, cursor="hand2",
                            bg=COR_PAINEL, fg=BRANCO,
                            activebackground=AZUL_MEDIO, relief="flat",
                            command=lambda c=chave: self._set_ferr_via(c))
            btn.bind("<Enter>", lambda e,d=dica: self.status.config(text=d))
            self.btns_via[chave] = btn
            # NÃO faz pack ainda — serão mostrados ao entrar no modo via

        # Botões de zoom (sempre visíveis)
        self._sep_zoom = tk.Frame(tb, bg=COR_BORDA, height=1)
        self._sep_zoom.pack(fill="x", pady=3)
        self._btns_zoom = []
        for txt, cmd in [("+",lambda: self._zoom_d(1.2)),
                          ("−",lambda: self._zoom_d(1/1.2)),
                          ("⌂",self._reset_view)]:
            b = tk.Button(tb, text=txt, font=("Segoe UI",13), width=3,
                          bg=COR_PAINEL, fg=BRANCO, relief="flat", cursor="hand2",
                          command=cmd)
            b.pack(pady=1, padx=3)
            self._btns_zoom.append(b)

        # Botão 🛣 — base da toolbar, sempre visível
        tk.Frame(tb, height=1, bg=COR_FUNDO).pack(fill="x", expand=True)
        tk.Frame(tb, height=2, bg=AMARELO).pack(fill="x")
        self._btn_modo_via = tk.Button(tb, text="🛣",
                                       font=("Segoe UI",18),
                                       width=3, cursor="hand2",
                                       bg="#162810", fg=AMARELO,
                                       activebackground="#2A4A1A",
                                       relief="flat", pady=4,
                                       command=self._toggle_modo_via)
        self._btn_modo_via.pack(fill="x", padx=2, pady=2)
        self._btn_modo_via.bind("<Enter>", lambda e: self.status.config(
            text="Editor de Via  —  alterna modo arte"))
        tk.Frame(tb, height=2, bg=AMARELO).pack(fill="x")

        # ── Canvas central ──
        cf = tk.Frame(corpo, bg=COR_FUNDO)
        cf.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(cf, bg="#0A1020",
                                cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>",        self._click)
        self.canvas.bind("<Double-Button-1>", self._dblclick)
        self.canvas.bind("<B1-Motion>",       self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<Button-3>",        self._click_dir)
        self.canvas.bind("<MouseWheel>",      self._scroll_zoom)
        self.canvas.bind("<Button-2>",        self._pan_ini)
        self.canvas.bind("<B2-Motion>",       self._pan_mov)
        self.canvas.bind("<Configure>",       lambda e: self._redesenhar())
        # Ctrl+Z — bind no canvas e na toplevel para capturar em qualquer foco
        self.canvas.bind("<Control-z>",       self._desfazer)
        self.canvas.bind("<Control-Z>",       self._desfazer)
        self.bind("<Control-z>",              self._desfazer)
        self.bind("<Control-Z>",              self._desfazer)

        # ── Painel direito: CAMADAS + PROPRIEDADES ──
        pd = tk.Frame(corpo, bg=COR_PAINEL, width=220)
        pd.pack(side="right", fill="y")
        pd.pack_propagate(False)
        tk.Frame(pd, bg=AMARELO, height=2).pack(fill="x")

        # --- Seção Camadas ---
        cab_cam = tk.Frame(pd, bg=COR_PAINEL)
        cab_cam.pack(fill="x", padx=6, pady=(8,2))
        tk.Label(cab_cam, text="Camadas", font=FONTE_SUB,
                 bg=COR_PAINEL, fg=AMARELO).pack(side="left")

        # Botões mover camada
        for sym, tip, cmd in [("▲","Subir camada",self._camada_subir),
                                ("▼","Descer camada",self._camada_descer)]:
            b = tk.Button(cab_cam, text=sym, font=("Segoe UI",9),
                          width=2, cursor="hand2",
                          bg=COR_CARD, fg=BRANCO,
                          activebackground=AZUL_MEDIO,
                          relief="flat", pady=1,
                          command=cmd)
            b.pack(side="right", padx=1)
            b.bind("<Enter>", lambda e,t=tip: self.status.config(text=t))

        # Listbox de camadas
        flb = tk.Frame(pd, bg=COR_CARD)
        flb.pack(fill="both", expand=True, padx=4, pady=2)
        scrl_cam = tk.Scrollbar(flb)
        scrl_cam.pack(side="right", fill="y")
        self.lb_camadas = tk.Listbox(
            flb,
            yscrollcommand=scrl_cam.set,
            bg=COR_CARD, fg=BRANCO,
            selectbackground=AZUL_MEDIO,
            selectforeground=BRANCO,
            font=("Segoe UI",9),
            relief="flat", bd=0,
            activestyle="none",
            highlightthickness=0,
        )
        self.lb_camadas.pack(fill="both", expand=True)
        scrl_cam.config(command=self.lb_camadas.yview)
        self.lb_camadas.bind("<<ListboxSelect>>", self._camada_selecionada)

        # Botão apagar da camada
        tk.Button(pd, text="⌫  Apagar selecionado",
                  font=FONTE_PEQ, cursor="hand2",
                  bg="#3A1010", fg="#FF8080",
                  activebackground="#5A1A1A",
                  relief="flat", pady=4,
                  command=self._camada_apagar).pack(fill="x", padx=4, pady=(0,4))

        # --- Separador ---
        tk.Frame(pd, bg=AMARELO, height=1).pack(fill="x", padx=4)

        # --- Seção Propriedades ---
        tk.Label(pd, text="Propriedades", font=FONTE_SUB,
                 bg=COR_PAINEL, fg=AMARELO).pack(pady=(6,2))
        self.label_prop = tk.Label(pd,
                                   text="Selecione um\nelemento",
                                   font=FONTE_PEQ,
                                   bg=COR_PAINEL, fg=CINZA_CLARO,
                                   justify="left", wraplength=200)
        self.label_prop.pack(padx=10, anchor="w")

        # Botão redimensionar
        self.btn_redim = tk.Button(pd, text="⇲  Redimensionar",
                                   font=FONTE_PEQ, cursor="hand2",
                                   bg=COR_CARD, fg=CINZA_CLARO,
                                   activebackground=AZUL_MEDIO,
                                   relief="flat", pady=4, state="disabled",
                                   command=self._abrir_redimensionar)
        self.btn_redim.pack(fill="x", padx=4, pady=(6,2))

        # Status bar
        self.status = tk.Label(self, text="Pronto",
                               font=FONTE_MONO, bg=COR_PAINEL,
                               fg=CINZA_MEDIO, anchor="w")
        self.status.pack(fill="x", side="bottom", padx=8, pady=2)

        self._set_ferr("sel")
        # Ctrl+Z e Delete na janela raiz
        self.after(100, lambda: self.winfo_toplevel().bind("<Control-z>", self._desfazer))
        self.after(100, lambda: self.winfo_toplevel().bind("<Control-Z>", self._desfazer))
        self.after(100, lambda: self.winfo_toplevel().bind("<Delete>",    self._del_key))
        self.after(100, lambda: self.winfo_toplevel().bind("<BackSpace>", self._del_key))
        self.canvas.bind("<Delete>",   self._del_key)
        self.canvas.bind("<BackSpace>",self._del_key)

    # ──────────────────────────────────────────
    #  SISTEMA DE CAMADAS
    # ──────────────────────────────────────────
    def _atualizar_camadas(self):
        """Sincroniza o Listbox com self.elementos (ordem invertida = topo primeiro)."""
        sel_atual = self.sel_idx
        self.lb_camadas.delete(0, tk.END)

        for i, el in reversed(list(enumerate(self.elementos))):
            icone, nome = TIPO_INFO.get(el["tipo"], ("?", el["tipo"]))
            label_el = el.get("label","")
            txt = f" {icone}  {nome}"
            if label_el:
                txt += f"  [{label_el}]"
            self.lb_camadas.insert(tk.END, txt)
            # Colorir elementos de infra levemente
            if el["tipo"].startswith("_"):
                self.lb_camadas.itemconfig(tk.END, fg=CINZA_MEDIO)
            else:
                self.lb_camadas.itemconfig(tk.END, fg=BRANCO)

        # Restaura seleção visual
        if sel_atual is not None:
            # índice no listbox está invertido
            lb_idx = len(self.elementos) - 1 - sel_atual
            if 0 <= lb_idx < self.lb_camadas.size():
                self.lb_camadas.selection_set(lb_idx)
                self.lb_camadas.see(lb_idx)

    def _camada_selecionada(self, event=None):
        sel = self.lb_camadas.curselection()
        if not sel:
            return
        lb_idx = sel[0]
        # Converte índice invertido → índice real
        el_idx = len(self.elementos) - 1 - lb_idx
        if 0 <= el_idx < len(self.elementos):
            self.sel_idx = el_idx
            self._mostrar_props(el_idx)
            self._redesenhar()

    def _camada_subir(self):
        """Move o elemento selecionado uma posição acima (para a frente)."""
        if self.sel_idx is None: return
        i = self.sel_idx
        if i < len(self.elementos) - 1:
            self._salvar_historico()
            self.elementos[i], self.elementos[i+1] = \
                self.elementos[i+1], self.elementos[i]
            self.sel_idx = i + 1
        self._atualizar_camadas()
        self._redesenhar()

    def _camada_descer(self):
        """Move o elemento selecionado uma posição abaixo (para trás)."""
        if self.sel_idx is None: return
        i = self.sel_idx
        if i > 0:
            self.elementos[i], self.elementos[i-1] = \
                self.elementos[i-1], self.elementos[i]
            self.sel_idx = i - 1
        self._atualizar_camadas()
        self._redesenhar()

    def _del_key(self, event=None):
        """Delete/Backspace apaga o elemento selecionado."""
        if self.sel_idx is not None:
            self._salvar_historico()
            self.elementos.pop(self.sel_idx)
            self.sel_idx = None
            self.label_prop.config(text="Selecione um\nelemento")
            self.btn_redim.config(state="disabled", fg=CINZA_CLARO)
            self._atualizar_camadas()
            self._redesenhar()
            self.status.config(text="Elemento apagado (Delete)")

    def _camada_apagar(self):
        if self.sel_idx is None: return
        self._salvar_historico()
        self.elementos.pop(self.sel_idx)
        self.sel_idx = None
        self.label_prop.config(text="Selecione um\nelemento")
        self.btn_redim.config(state="disabled")
        self._atualizar_camadas()
        self._redesenhar()

    def _mostrar_props(self, idx):
        el = self.elementos[idx]
        linhas = []
        icone, nome = TIPO_INFO.get(el["tipo"],("?",el["tipo"]))
        linhas.append(f"{icone}  {nome}")
        if el.get("label"):      linhas.append(f"Rótulo: {el['label']}")
        if el.get("angulo") is not None and el["tipo"] != "_rotatoria":
            linhas.append(f"Ângulo: {el.get('angulo',0):.0f}°")
        if el.get("larg"):       linhas.append(f"Largura: {el['larg']} px")
        if el.get("alt"):        linhas.append(f"Altura: {el['alt']} px")
        self.label_prop.config(text="\n".join(linhas))

        # Habilita botão redimensionar apenas para tipos redimensionáveis
        tipos_redim = ("carro","moto","caminhao","bicicleta",
                       "pedestre","sc","via_h","via_v","r1","r2")
        if el["tipo"] in tipos_redim:
            self.btn_redim.config(state="normal", fg=AMARELO)
        else:
            self.btn_redim.config(state="disabled", fg=CINZA_CLARO)

    def _abrir_redimensionar(self):
        if self.sel_idx is None: return
        el = self.elementos[self.sel_idx]
        dlg = DialogoRedimensionar(self.winfo_toplevel(), el, self._redesenhar)
        self.winfo_toplevel().wait_window(dlg)
        self._atualizar_camadas()
        self._redesenhar()

    # ──────────────────────────────────────────
    #  FERRAMENTAS
    # ──────────────────────────────────────────
    def _toggle_modo_via(self):
        """Alterna entre modo normal e modo arte/via no mesmo canvas."""
        self._modo_via = not self._modo_via
        if self._modo_via:
            # Entra no modo via
            self._btn_modo_via.config(bg="#2A5A1A", fg=BRANCO)
            self.status.config(text="🛣 Modo Via ativo — ferramentas de infraestrutura")
            # Oculta botões normais, mostra botões de via
            for btn in self.btns_ferr.values():
                btn.pack_forget()
            self._sep_zoom.pack_forget()
            for b in self._btns_zoom:
                b.pack_forget()
            # Repack zoom depois dos botões de via
            self._sep_zoom.pack(fill="x", pady=2)
            for chave, icone, dica in FERRAMENTAS_VIA:
                self.btns_via[chave].pack(pady=1, padx=3)
            for b in self._btns_zoom:
                b.pack(pady=1, padx=3)
            self._ferr_via = "asfalto"
            self._set_ferr_via("asfalto")
        else:
            # Sai do modo via
            self._btn_modo_via.config(bg="#162810", fg=AMARELO)
            self.status.config(text="Modo Normal")
            # Oculta botões de via, mostra normais
            for btn in self.btns_via.values():
                btn.pack_forget()
            self._sep_zoom.pack_forget()
            for b in self._btns_zoom:
                b.pack_forget()
            self._sep_zoom.pack(fill="x", pady=3)
            for chave, icone, dica in self.FERRAMENTAS:
                self.btns_ferr[chave].pack(pady=1, padx=3)
            for b in self._btns_zoom:
                b.pack(pady=1, padx=3)
            self._ferr_via = None
            self._set_ferr("sel")
        self._redesenhar()

    def _set_ferr_via(self, f):
        """Define ferramenta no modo via."""
        self._ferr_via = f
        for k, btn in self.btns_via.items():
            btn.config(bg=AZUL_MEDIO if k==f else COR_PAINEL)
        dica = next((d for ch,i,d in FERRAMENTAS_VIA if ch==f), f)
        self.status.config(text=f"🛣 Via: {dica}  — clique e arraste")

    def _set_ferr(self, c):
        self.ferramenta = c
        for k, btn in self.btns_ferr.items():
            btn.config(bg=AZUL_MEDIO if k==c else COR_PAINEL)
        if c == "calibrar" and self.modo == "zero":
            messagebox.showinfo("Calibração","Disponível apenas no modo drone.")
            self._set_ferr("sel")

    # ──────────────────────────────────────────
    #  COORDENADAS / ZOOM / PAN
    # ──────────────────────────────────────────
    def _mt(self,x,y): return x*self.zoom+self.pan_x, y*self.zoom+self.pan_y
    def _tm(self,tx,ty): return (tx-self.pan_x)/self.zoom, (ty-self.pan_y)/self.zoom
    def _tx(self,x): return x*self.zoom+self.pan_x
    def _ty(self,y): return y*self.zoom+self.pan_y

    def _zoom_d(self,f,cx=None,cy=None):
        if cx is None:
            cx=self.canvas.winfo_width()/2; cy=self.canvas.winfo_height()/2
        wx,wy=self._tm(cx,cy)
        self.zoom=max(0.1,min(10.0,self.zoom*f))
        self.pan_x=cx-wx*self.zoom; self.pan_y=cy-wy*self.zoom
        self._redesenhar()

    def _reset_view(self):
        self.zoom,self.pan_x,self.pan_y=1.0,0,0; self._redesenhar()

    def _scroll_zoom(self,e):
        self._zoom_d(1.1 if e.delta>0 else 1/1.1, e.x, e.y)

    def _pan_ini(self,e): self._pan_start=(e.x-self.pan_x, e.y-self.pan_y)
    def _pan_mov(self,e):
        if self._pan_start:
            self.pan_x=e.x-self._pan_start[0]; self.pan_y=e.y-self._pan_start[1]
            self._redesenhar()

    # ──────────────────────────────────────────
    #  EVENTOS DO CANVAS
    # ──────────────────────────────────────────
    def _click(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._click_via(e, x, y)
            return
        f=self.ferramenta
        if f=="sel":         self._selecionar(x,y)
        elif f=="apagar":    self._apagar_em(x,y)
        elif f=="calibrar":  self._calib_click(x,y,e.x,e.y)
        elif f in ("r1","r2","cota"):
            self.drag_start=(x,y)
        elif f in ("carro","moto","caminhao","bicicleta",
                   "pedestre","sc","texto"):
            self._inserir(f,x,y)


    def _dblclick(self, e):
        """Duplo clique — abre editor de texto se elemento for texto."""
        x,y=self._tm(e.x,e.y)
        i=self._em(x,y)
        if i is not None and self.elementos[i]["tipo"]=="texto":
            self._abrir_editor_texto(self.elementos[i])

    def _drag(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._drag_via(e, x, y)
            return
        if self.ferramenta=="sel" and self.sel_idx is not None and self.drag_start:
            el=self.elementos[self.sel_idx]
            dx=x-self.drag_start[0]; dy=y-self.drag_start[1]
            if not getattr(self, "_drag_saved", False):
                self._salvar_historico()
                self._drag_saved = True
            dp = getattr(self, "_drag_ponto", None)
            if dp == "p1":
                # Arrasta só o ponto inicial
                el["x"] += dx; el["y"] += dy
            elif dp == "p2" and "x2" in el:
                # Arrasta só o ponto final
                el["x2"] += dx; el["y2"] += dy
            else:
                # Move o objeto todo
                el["x"]=el.get("x",0)+dx; el["y"]=el.get("y",0)+dy
                if "x2" in el: el["x2"]+=dx; el["y2"]+=dy
            self.drag_start=(x,y)
            self._redesenhar()
        elif self.ferramenta in ("r1","r2","cota") and self.drag_start:
            if self.tmp_linha: self.canvas.delete(self.tmp_linha)
            tx1,ty1=self._mt(*self.drag_start)
            tx2,ty2=self._mt(x,y)
            cor={"r1":COR_R1,"r2":COR_R2,"cota":COR_COTA}.get(self.ferramenta,"#888")
            self.tmp_linha=self.canvas.create_line(tx1,ty1,tx2,ty2,fill=cor,width=2)

    def _release(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._release_via(e, x, y)
            return
        if self.ferramenta in ("r1","r2","cota") and self.drag_start:
            self._finalizar_linha(x,y)
        elif self.ferramenta=="sel" and self.sel_idx is not None:
            # Salva histórico após mover/editar elemento
            pass  # historico salvo no início do drag não necessário aqui
        self.drag_start=None
        self._drag_ponto=None
        self._drag_saved=False
        if self.tmp_linha:
            self.canvas.delete(self.tmp_linha); self.tmp_linha=None

    def _click_dir(self,e):
        x,y=self._tm(e.x,e.y)
        i=self._em(x,y)
        if i is not None: self._editar(i)

    # ──────────────────────────────────────────
    #  LINHAS / EIXOS
    # ──────────────────────────────────────────
    def _finalizar_linha(self,x2,y2):
        x1,y1=self.drag_start; f=self.ferramenta
        if f=="r1":
            self._salvar_historico()
            self.elementos.append({"tipo":"r1","x":x1,"y":y1,"x2":x2,"y2":y2})
        elif f=="r2":
            self._salvar_historico()
            self.elementos.append({"tipo":"r2","x":x1,"y":y1,"x2":x2,"y2":y2})
        elif f=="cota":
            dp=math.hypot(x2-x1,y2-y1)
            if self.calibrado and self.k:
                dm=dp*self.k
                lb=f"{dm:.2f} m"
                u=self._incert(dp)
                if u: lb+=f"\n±{u:.3f} m"
            else:
                val=simpledialog.askstring("Cota","Valor (ex: 3.6):",
                                           parent=self.winfo_toplevel())
                lb=(val or "?").replace(",",".")+"m"
            self._salvar_historico()
            self.elementos.append({"tipo":"cota","x":x1,"y":y1,
                                   "x2":x2,"y2":y2,"label":lb})

        self._atualizar_camadas()
        self._redesenhar()

    # ──────────────────────────────────────────
    #  CALIBRAÇÃO
    # ──────────────────────────────────────────
    def _calib_click(self,x,y,tx,ty):
        self.calib_pts.append((x,y))
        self.canvas.create_oval(tx-5,ty-5,tx+5,ty+5,
                                fill=AMARELO,outline=BRANCO,tags="calib")
        if len(self.calib_pts)==1:
            self.status.config(text="📐 Clique no 2º extremo da lona (2,00 m)")
        elif len(self.calib_pts)>=2:
            p1,p2=self.calib_pts[:2]
            dp=math.hypot(p2[0]-p1[0],p2[1]-p1[1])
            if dp<1: self.calib_pts.clear(); self.canvas.delete("calib"); return
            L,uL=2.000,0.005
            self.k=L/dp
            uP=math.sqrt(2)
            self.u_k=self.k*math.sqrt((uL/L)**2+(uP/dp)**2)
            self.calibrado=True
            self.calib_pts.clear(); self.canvas.delete("calib")
            self.label_escala.config(
                text=f"📐 k={self.k*1000:.3f}mm/px  u={self.u_k*1000:.3f}mm/px",
                fg=COR_SUCESSO)
            self.status.config(text=f"Calibrado! k={self.k:.5f} m/px")
            self._set_ferr("cota")

    def _incert(self,dp):
        if not self.calibrado or not self.k: return None
        L,uL=2.000,0.005; P=L/self.k; uP=uM=math.sqrt(2)
        D=self.k*dp
        return D*math.sqrt((uL/L)**2+(uP/P)**2+(uM/dp)**2)

    # ──────────────────────────────────────────
    #  INSERÇÃO DE ELEMENTOS
    # ──────────────────────────────────────────
    def _inserir(self,tipo,x,y):
        label=""
        modelo_chave = None
        modelo_larg  = None
        modelo_alt   = None
        modelo_cor   = None

        # ── Popup de seleção de modelo para veículos ──
        if tipo in ("carro", "moto", "caminhao"):
            popup = PopupModeloVeiculo(self.winfo_toplevel(), tipo)
            self.winfo_toplevel().wait_window(popup)
            if popup.resultado is None:
                return   # cancelou / fechou sem escolher
            m = popup.resultado
            modelo_chave = m["chave"]
            modelo_larg  = m["larg"]
            modelo_alt   = m["alt"]
            modelo_cor   = m["cor"]

        if tipo in ("carro","moto","caminhao","bicicleta","pedestre"):
            n=sum(1 for e in self.elementos if e["tipo"]==tipo)+1
            sig={"carro":"V","moto":"V","caminhao":"V","bicicleta":"B","pedestre":"P"}
            label=simpledialog.askstring(
                "Identificação","Identificação (ex: V1 — FIORINO):",
                initialvalue=f"{sig[tipo]}{n}",
                parent=self.winfo_toplevel()) or f"{sig[tipo]}{n}"
        elif tipo=="texto":
            label = ""  # será preenchido pelo EditorTexto
        elif tipo=="sc":
            label="SC"

        el={"tipo":tipo,"x":x,"y":y,"label":label,"angulo":0}
        if modelo_chave: el["modelo"] = modelo_chave
        if modelo_larg:  el["larg"]   = modelo_larg
        if modelo_alt:   el["alt"]    = modelo_alt
        if modelo_cor:   el["cor"]    = modelo_cor

        self._salvar_historico()
        self.elementos.append(el)
        self.sel_idx=len(self.elementos)-1

        self._atualizar_camadas()
        self._redesenhar()

        # Abre automaticamente o diálogo de ajuste
        if tipo in ("carro","moto","caminhao","bicicleta","pedestre","sc"):
            dlg=DialogoRedimensionar(self.winfo_toplevel(),el,self._redesenhar)
            self.winfo_toplevel().wait_window(dlg)
            self._atualizar_camadas()
            self._redesenhar()
        elif tipo == "texto":
            # Abre editor de texto inline
            self._abrir_editor_texto(el)

    # ──────────────────────────────────────────
    #  MODO CRIAÇÃO DE VIA
    # ──────────────────────────────────────────
    def _abrir_editor_via(self):
        """Legado — agora usa _toggle_modo_via."""
        self._toggle_modo_via()

    # ──────────────────────────────────────────
    #  SELEÇÃO / EDIÇÃO
    # ──────────────────────────────────────────
    def _em(self,x,y,r=20):
        rz = r / self.zoom
        for i,el in reversed(list(enumerate(self.elementos))):
            # Verifica ponto inicial
            if math.hypot(x-el.get("x",0), y-el.get("y",0)) < rz:
                return i
            # Para R1/R2/cota: verifica também ponto final e meio da linha
            if el["tipo"] in ("r1","r2","cota") and "x2" in el:
                if math.hypot(x-el["x2"], y-el["y2"]) < rz:
                    return i
                mx = (el["x"]+el["x2"])/2; my = (el["y"]+el["y2"])/2
                if math.hypot(x-mx, y-my) < rz*1.5:
                    return i
        return None

    def _selecionar(self,x,y):
        i=self._em(x,y)
        self.sel_idx=i
        self.drag_start=(x,y) if i is not None else None
        self._drag_ponto = None
        if i is not None:
            el = self.elementos[i]
            if el["tipo"] in ("r1","r2","cota") and "x2" in el:
                rz = 20/self.zoom
                if math.hypot(x-el["x2"],y-el["y2"]) < rz:
                    self._drag_ponto = "p2"
                elif math.hypot(x-el["x"],y-el["y"]) < rz:
                    self._drag_ponto = "p1"
                else:
                    self._drag_ponto = "move"
            self._mostrar_props(i)
        else:
            self.label_prop.config(text="Selecione um\nelemento")
            self.btn_redim.config(state="disabled",fg=CINZA_CLARO)
        self._atualizar_camadas()
        self._redesenhar()


    def _apagar_em(self,x,y):
        i=self._em(x,y)
        if i is not None:
            self._salvar_historico()
            self.elementos.pop(i)
            self.sel_idx=None
            self._atualizar_camadas()
            self._redesenhar()

    def _editar(self, i):
        el = self.elementos[i]
        if el["tipo"] == "texto":
            self._abrir_editor_texto(el)
            return
        tipos_redim = ("carro","moto","caminhao","bicicleta",
                       "pedestre","sc","r1","r2","cota")
        if el["tipo"] in tipos_redim:
            dlg = DialogoRedimensionar(self.winfo_toplevel(), el, self._redesenhar)
            self.winfo_toplevel().wait_window(dlg)
        elif "label" in el:
            novo = simpledialog.askstring("Editar", "Rótulo:",
                initialvalue=el["label"], parent=self.winfo_toplevel())
            if novo is not None:
                el["label"] = novo
        self._atualizar_camadas()
        self._redesenhar()

    def _abrir_editor_texto(self, el):
        """Abre o editor de texto inline com painel de formatação flutuante."""
        EditorTextoInline(self.winfo_toplevel(), self.canvas, el,
                          self._mt, self._redesenhar, self._atualizar_camadas)

    # ──────────────────────────────────────────
    #  REDESENHO
    # ──────────────────────────────────────────
    # ──────────────────────────────────────────
    #  MODO VIA — handlers de evento no canvas principal
    # ──────────────────────────────────────────
    def _click_via(self, e, x, y):
        f = getattr(self, "_ferr_via", "asfalto")
        if f == "_sel":
            self._sel_via(x, y)
        else:
            self.drag_start = (x, y)
            self.status.config(text="Arraste para definir o tamanho...")

    def _drag_via(self, e, x, y):
        f = getattr(self, "_ferr_via", "asfalto")
        if f == "_sel" and self.sel_idx is not None and self.drag_start:
            el = self.elementos[self.sel_idx]
            if not getattr(self,"_drag_saved",False):
                self._salvar_historico(); self._drag_saved=True
            dx=x-self.drag_start[0]; dy=y-self.drag_start[1]
            el["x"]+=dx; el["y"]+=dy
            if "x2" in el: el["x2"]+=dx; el["y2"]+=dy
            self.drag_start=(x,y); self._redesenhar()
        elif f != "_sel" and self.drag_start:
            self._preview_via(e.x, e.y)

    def _release_via(self, e, x, y):
        f = getattr(self, "_ferr_via", "asfalto")
        if f != "_sel" and self.drag_start:
            for tid in getattr(self,"_tmp_via_ids",[]): self.canvas.delete(tid)
            self._tmp_via_ids = []
            self._criar_el_via(f, x, y)
        self.drag_start = None; self._drag_saved = False

    def _sel_via(self, x, y):
        """Seleciona elemento de via (tipos v_ e _)."""
        rz = 22/self.zoom
        for i, el in reversed(list(enumerate(self.elementos))):
            t = el["tipo"]
            if not (t.startswith("v_") or t.startswith("_")): continue
            ex,ey = el.get("x",0),el.get("y",0)
            if math.hypot(x-ex,y-ey) < rz:
                self.sel_idx=i; self._redesenhar(); return
            if "x2" in el:
                mx=(ex+el["x2"])/2; my=(ey+el["y2"])/2
                if math.hypot(x-mx,y-my)<rz:
                    self.sel_idx=i; self._redesenhar(); return
        self.sel_idx=None; self._redesenhar()

    def _preview_via(self, tx2, ty2):
        """Preview dos elementos de via durante o drag."""
        for tid in getattr(self,"_tmp_via_ids",[]): self.canvas.delete(tid)
        self._tmp_via_ids = []
        if not self.drag_start: return
        tx1,ty1 = self._mt(*self.drag_start)
        f = getattr(self,"_ferr_via","asfalto")
        c = self.canvas
        if f in ("asfalto","calcada","conflito","faixa_ped"):
            cor={"asfalto":"#606060","calcada":"#A0A0A0",
                 "conflito":COR_PERIGO,"faixa_ped":"#DDDDDD"}.get(f,"#666")
            self._tmp_via_ids.append(
                c.create_rectangle(tx1,ty1,tx2,ty2,fill=cor,outline=BRANCO,width=1))
        elif f in ("faixa_am","faixa_br"):
            cor=AMARELO if f=="faixa_am" else BRANCO
            self._tmp_via_ids.append(
                c.create_line(tx1,ty1,tx2,ty2,fill=cor,width=3,dash=(14,8)))
        elif f=="rotatoria":
            r=max(8,int(math.hypot(tx2-tx1,ty2-ty1)/2))
            mx,my=(tx1+tx2)/2,(ty1+ty2)/2
            self._tmp_via_ids.append(
                c.create_oval(mx-r,my-r,mx+r,my+r,fill="#606060",outline=AMARELO,width=2))
        elif f in ("semaforo","placa","arvore","poste"):
            r=10
            cor={"semaforo":"#222","placa":"#CC0000","arvore":"#1A6A1A","poste":"#888"}.get(f,"#444")
            self._tmp_via_ids.append(
                c.create_oval(tx2-r,ty2-r,tx2+r,ty2+r,fill=cor,outline=BRANCO,width=1))

    def _criar_el_via(self, f, x2, y2):
        """Cria elemento de via no canvas principal."""
        if not self.drag_start: return
        x1,y1=self.drag_start
        if f in ("asfalto","calcada","conflito","faixa_ped"):
            if abs(x2-x1)<5 and abs(y2-y1)<5: return
        self._salvar_historico()
        if f=="asfalto":
            el={"tipo":"v_asfalto","x":min(x1,x2),"y":min(y1,y2),"x2":max(x1,x2),"y2":max(y1,y2)}
        elif f=="calcada":
            el={"tipo":"v_calcada","x":min(x1,x2),"y":min(y1,y2),"x2":max(x1,x2),"y2":max(y1,y2)}
        elif f=="conflito":
            el={"tipo":"v_conflito","x":min(x1,x2),"y":min(y1,y2),"x2":max(x1,x2),"y2":max(y1,y2)}
        elif f=="faixa_am":
            el={"tipo":"v_faixa_am","x":x1,"y":y1,"x2":x2,"y2":y2}
        elif f=="faixa_br":
            el={"tipo":"v_faixa_br","x":x1,"y":y1,"x2":x2,"y2":y2}
        elif f=="faixa_ped":
            el={"tipo":"v_faixa_ped","x":min(x1,x2),"y":min(y1,y2),"x2":max(x1,x2),"y2":max(y1,y2)}
        elif f=="rotatoria":
            cx,cy=(x1+x2)/2,(y1+y2)/2; r=max(10,math.hypot(x2-x1,y2-y1)/2)
            el={"tipo":"v_rotatoria","x":cx,"y":cy,"r":r}
        elif f=="semaforo":
            el={"tipo":"v_semaforo","x":x2,"y":y2}
        elif f=="placa":
            popup_placa=PopupPlacas(self.winfo_toplevel())
            self.winfo_toplevel().wait_window(popup_placa)
            if popup_placa.resultado is None: return
            m=popup_placa.resultado
            el={"tipo":"v_placa","x":x2,"y":y2,"label":m["label"],
                "cor_placa":m["cor"],"chave_placa":m["chave"]}
        elif f=="arvore":
            el={"tipo":"v_arvore","x":x2,"y":y2}
        elif f=="poste":
            el={"tipo":"v_poste","x":x2,"y":y2}
        else:
            return
        # Insere no início (camada de baixo)
        self.elementos.insert(0, el)
        self.sel_idx = 0
        self._atualizar_camadas(); self._redesenhar()

    # ──────────────────────────────────────────
    #  REDESENHO
    # ──────────────────────────────────────────
    def _redesenhar(self):
        c=self.canvas; c.delete("all")
        self._tk_imgs = []
        W=c.winfo_width(); H=c.winfo_height()
        if W<2 or H<2: return

        if self.img_drone and PIL_OK:
            nw=int(self.img_drone.width*self.zoom)
            nh=int(self.img_drone.height*self.zoom)
            if nw>0 and nh>0:
                img_r=self.img_drone.resize((nw,nh),Image.LANCZOS)
                self.img_drone_tk=ImageTk.PhotoImage(img_r)
                c.create_image(self.pan_x,self.pan_y,anchor="nw",image=self.img_drone_tk)
        else:
            passo=max(1,int(50*self.zoom))
            ox=int(self.pan_x)%passo; oy=int(self.pan_y)%passo
            for xi in range(-passo,W+passo,passo):
                c.create_line(xi+ox,0,xi+ox,H,fill="#14183A",width=1)
            for yi in range(-passo,H+passo,passo):
                c.create_line(0,yi+oy,W,yi+oy,fill="#14183A",width=1)

        if self._modo_via:
            # Modo via: elementos normais fantasma (stipple), via em destaque
            for i,el in enumerate(self.elementos):
                t = el["tipo"]
                if t.startswith("v_") or t.startswith("_"):
                    # Elementos de via: destaque total
                    self._desenhar_el(el, i==self.sel_idx)
                else:
                    # Elementos normais: salva canvas ref, desenha e sobrepõe stipple
                    self._desenhar_el(el, False)
            # Overlay semitransparente sobre elementos normais
            # Desenhamos o overlay SOMENTE sobre os elementos não-via
            # usando um retângulo stipple que cobre tudo e deixa ver via por baixo
            # Estratégia: desenhar via primeiro (já feito acima), depois overlay
            # Redesenho em duas passadas:
            c.delete("all")
            self._tk_imgs = []
            # Passada 1: grade
            if self.img_drone and PIL_OK:
                nw=int(self.img_drone.width*self.zoom)
                nh=int(self.img_drone.height*self.zoom)
                if nw>0 and nh>0:
                    img_r=self.img_drone.resize((nw,nh),Image.LANCZOS)
                    self.img_drone_tk=ImageTk.PhotoImage(img_r)
                    c.create_image(self.pan_x,self.pan_y,anchor="nw",image=self.img_drone_tk)
            else:
                passo=max(1,int(50*self.zoom))
                ox=int(self.pan_x)%passo; oy=int(self.pan_y)%passo
                for xi in range(-passo,W+passo,passo):
                    c.create_line(xi+ox,0,xi+ox,H,fill="#14183A",width=1)
                for yi in range(-passo,H+passo,passo):
                    c.create_line(0,yi+oy,W,yi+oy,fill="#14183A",width=1)
            # Passada 2: elementos normais com overlay
            for i,el in enumerate(self.elementos):
                t=el["tipo"]
                if not (t.startswith("v_") or t.startswith("_")):
                    self._desenhar_el(el, False)
            # Overlay: retângulo semitransparente sobre tudo
            c.create_rectangle(0,0,W,H, fill="#0A1020", outline="", stipple="gray50")
            # Passada 3: elementos de via por cima (sem stipple)
            for i,el in enumerate(self.elementos):
                t=el["tipo"]
                if t.startswith("v_") or t.startswith("_"):
                    self._desenhar_el(el, i==self.sel_idx)
            # Label do modo
            c.create_text(W//2, 18, text="🛣  MODO VIA — clique em 🛣 para sair",
                          fill=AMARELO, font=("Segoe UI",9,"bold"))
        else:
            # Modo normal: desenha tudo normalmente
            for i,el in enumerate(self.elementos):
                self._desenhar_el(el, i==self.sel_idx)

        self._norte(W-40,40)
        self._rodape(W,H)

    def _desenhar_el(self,el,sel=False):
        c=self.canvas; tipo=el["tipo"]
        tx,ty=self._mt(el.get("x",0),el.get("y",0))
        label=el.get("label","")

        # ── Infraestrutura de via ──
        if tipo=="_asfalto":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#606060",outline=""); return
        if tipo=="_asfalto_terra":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#5A4A2A",outline=""); return
        if tipo=="_calcada":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#909090",outline=""); return
        if tipo=="_canteiro":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#1A3A1A",outline=""); return
        if tipo=="_faixa_h":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            # Linha tracejada amarela no centro da via
            c.create_line(ax1,ay1,ax2,ay2,
                          fill=AMARELO,
                          width=max(2,int(2*self.zoom)),
                          dash=(max(8,int(14*self.zoom)), max(6,int(10*self.zoom))))
            return
        if tipo=="_faixa_v":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_line(ax1,ay1,ax2,ay2,
                          fill=AMARELO,
                          width=max(2,int(2*self.zoom)),
                          dash=(max(8,int(14*self.zoom)), max(6,int(10*self.zoom))))
            return
        if tipo=="_rotatoria":
            r=el.get("r",80)*self.zoom; ri=r*0.45
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="#606060",outline="")
            c.create_oval(tx-ri,ty-ri,tx+ri,ty+ri,fill="#1A3A1A",outline="")
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="",outline=AMARELO,
                          width=max(1,int(self.zoom)),dash=(6,4)); return

        # ── Elementos de via (EditorVia) ──
        if tipo == "v_asfalto":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#606060",outline="#808080",width=1); return
        if tipo == "v_calcada":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#A0A0A0",outline="#C0C0C0",width=1)
            p=max(4,int(10*self.zoom))
            for xi in range(int(ax1),int(ax2),p):
                c.create_line(xi,int(ay1),xi,int(ay2),fill="#888",width=1)
            return
        if tipo == "v_conflito":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="",outline=COR_PERIGO,width=2,dash=(8,4))
            c.create_text((ax1+ax2)/2,(ay1+ay2)/2,text="CONFLITO",
                          fill=COR_PERIGO,font=("Segoe UI",max(8,int(9*self.zoom)),"bold")); return
        if tipo == "v_faixa_am":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_line(ax1,ay1,ax2,ay2,fill=AMARELO,
                          width=max(2,int(3*self.zoom)),
                          dash=(max(10,int(14*self.zoom)),max(6,int(8*self.zoom)))); return
        if tipo == "v_faixa_br":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_line(ax1,ay1,ax2,ay2,fill=BRANCO,
                          width=max(2,int(2*self.zoom))); return
        if tipo == "v_faixa_ped":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            larg=max(1,ax2-ax1); n=max(3,int(larg/max(1,8*self.zoom)))
            passo=larg/n
            for i in range(n):
                lx=ax1+i*passo
                c.create_rectangle(lx,ay1,lx+passo*0.55,ay2,fill=BRANCO,outline="")
            return
        if tipo == "v_rotatoria":
            r=el.get("r",60)*self.zoom; ri=r*0.38
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="#606060",outline="#808080",width=1)
            c.create_oval(tx-ri,ty-ri,tx+ri,ty+ri,fill="#1A3A1A",outline="#2A5A2A",width=1)
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="",outline=AMARELO,
                          width=max(1,int(1.5*self.zoom)),dash=(8,5)); return
        if tipo == "v_semaforo":
            r=max(5,int(8*self.zoom)); bw=r*1.6; bh=r*5
            c.create_rectangle(tx-bw/2,ty-bh/2,tx+bw/2,ty+bh/2,fill="#111",outline="#444",width=1)
            for oy_,cor_ in [(-r*1.6,"#CC2200"),(0,"#CCAA00"),(r*1.6,"#00AA00")]:
                c.create_oval(tx-r*0.6,ty+oy_-r*0.6,tx+r*0.6,ty+oy_+r*0.6,
                             fill=cor_,outline="#222",width=1)
            c.create_line(tx,ty+bh/2,tx,ty+bh/2+r*2,fill="#666",
                          width=max(2,int(2*self.zoom))); return
        if tipo == "v_placa":
            lb=el.get("label","PARE"); r=max(6,int(10*self.zoom))
            cor_p=el.get("cor_placa","#CC0000"); chave_p=el.get("chave_placa","pare")
            c.create_line(tx,ty+r,tx,ty+r*2.5,fill="#666",width=max(1,int(1.5*self.zoom)))
            if chave_p=="pare":
                pts=[]
                for i in range(8):
                    ang=math.radians(i*45+22.5)
                    pts.extend([tx+math.cos(ang)*r, ty+math.sin(ang)*r])
                c.create_polygon(pts,fill=cor_p,outline=BRANCO,width=max(1,int(1.5*self.zoom)))
                c.create_text(tx,ty,text="PARE",fill=BRANCO,font=("Segoe UI",max(5,int(6*self.zoom)),"bold"))
            elif chave_p in ("vel_30","vel_40","vel_60","vel_80"):
                c.create_oval(tx-r,ty-r,tx+r,ty+r,fill=BRANCO,outline="#CC0000",width=max(2,int(2*self.zoom)))
                c.create_text(tx,ty,text=lb,fill="#CC0000",font=("Segoe UI",max(5,int(6*self.zoom)),"bold"))
            elif chave_p=="atencao":
                pts=[tx,ty-r, tx+r*0.87,ty+r*0.5, tx-r*0.87,ty+r*0.5]
                c.create_polygon(pts,fill=cor_p,outline=BRANCO,width=max(1,int(1.5*self.zoom)))
                c.create_text(tx,ty+3,text="!",fill=BRANCO,font=("Segoe UI",max(6,int(8*self.zoom)),"bold"))
            elif chave_p=="proib":
                c.create_oval(tx-r,ty-r,tx+r,ty+r,fill=BRANCO,outline="#CC0000",width=max(2,int(2*self.zoom)))
                c.create_line(tx-r*.7,ty-r*.7,tx+r*.7,ty+r*.7,fill="#CC0000",width=max(2,int(2.5*self.zoom)))
            else:
                c.create_rectangle(tx-r,ty-r,tx+r,ty+r,fill=cor_p,outline=BRANCO,width=max(1,int(1.5*self.zoom)))
                c.create_text(tx,ty,text=lb[:6],fill=BRANCO,font=("Segoe UI",max(5,int(6*self.zoom)),"bold"))
            return
        if tipo == "v_arvore":
            r=max(8,int(12*self.zoom))
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="#1A6A1A",outline="#2A8A2A",width=1)
            c.create_oval(tx-r*.5,ty-r*.5,tx+r*.5,ty+r*.5,fill="#2A8A2A",outline=""); return
        if tipo == "v_poste":
            r=max(3,int(5*self.zoom))
            c.create_line(tx,ty-r*3,tx,ty+r*1.5,fill="#888",width=max(2,int(2*self.zoom)))
            c.create_oval(tx-r,ty-r*4,tx+r,ty-r*2,fill="#FFEE88",outline="#CCCC44",width=1)
            c.create_line(tx-r*2,ty-r*3,tx,ty-r*3,fill="#888",width=max(1,int(1.5*self.zoom))); return

        # ── Eixos R1/R2 — linha livre em qualquer ângulo ──
        if tipo in ("r1","r2"):
            cor_eixo  = COR_R1 if tipo=="r1" else COR_R2
            nome_eixo = "R1"   if tipo=="r1" else "R2"
            esp = el.get("espessura", 2)
            if "x2" in el:
                ax1,ay1 = self._mt(el["x"],  el["y"])
                ax2,ay2 = self._mt(el["x2"], el["y2"])
            else:
                ax1 = self._tx(el["x"]); ay1 = self._ty(el["y"])
                ax2 = ax1;               ay2 = self._ty(el.get("y2", el["y"]+100))
            # Linha contínua
            c.create_line(ax1,ay1,ax2,ay2, fill=cor_eixo,
                          width=max(1,int(esp*self.zoom)))
            # Rótulo perpendicular à linha, afastado para não ser cortado
            dx = ax2 - ax1; dy = ay2 - ay1
            length = math.hypot(dx, dy)
            if length > 0:
                # Vetor perpendicular normalizado
                px = -dy / length; py = dx / length
                # Ponto a 60% do comprimento, deslocado 14px para o lado
                mx = ax1 + dx*0.15 + px*14
                my = ay1 + dy*0.15 + py*14
                # Ângulo do texto alinhado com a linha
                ang_deg = math.degrees(math.atan2(dy, dx))
                # Mantém texto legível (sem ficar de cabeça para baixo)
                if ang_deg > 90 or ang_deg < -90:
                    ang_deg += 180
                # Fundo pequeno para legibilidade
                c.create_text(mx, my, text=nome_eixo,
                              fill=cor_eixo,
                              font=("Segoe UI", 9, "bold"),
                              angle=-ang_deg)
            # Marcador de seleção
            if sel:
                r=10*self.zoom
                c.create_oval(ax1-r,ay1-r,ax1+r,ay1+r,
                              outline=AMARELO,width=2,dash=(4,3))
                c.create_oval(ax2-r,ay2-r,ax2+r,ay2+r,
                              outline=AMARELO,width=2,dash=(4,3))
            return

        # ── Cota ──
        if tipo=="cota":
            tx2,ty2=self._mt(el["x2"],el["y2"])
            c.create_line(tx,ty,tx2,ty2,fill=COR_COTA,width=1,
                          arrow="both",arrowshape=(6,8,3))
            c.create_text((tx+tx2)/2,(ty+ty2)/2-8,text=label,
                          fill=COR_COTA,font=FONTE_MONO,anchor="s"); return

        # ── Vias manuais ──
        if tipo in ("via_h","via_v"):
            tx2,ty2=self._mt(el["x2"],el["y2"])
            larg=max(2,int(el.get("espessura",40)*self.zoom))
            c.create_line(tx,ty,tx2,ty2,fill="#606060",width=larg,capstyle="butt")
            c.create_line(tx,ty,tx2,ty2,fill="#707070",
                          width=max(1,larg-2),capstyle="butt"); return

        # ── Veículos ──
        larg_padrao={"carro":28,"moto":20,"caminhao":36,"bicicleta":16,"pedestre":14}
        alt_padrao= {"carro":14,"moto":8, "caminhao":16,"bicicleta":5, "pedestre":14}
        cores_padrao={"carro":AZUL_CLARO,"moto":"#9B6BDF",
                      "caminhao":COR_PERIGO,"bicicleta":COR_SUCESSO,"pedestre":AMARELO}

        if tipo in larg_padrao:
            larg = el.get("larg", larg_padrao[tipo])
            alt  = el.get("alt",  alt_padrao[tipo])
            ang  = el.get("angulo", 0)
            cor  = el.get("cor", cores_padrao[tipo])

            # Busca função de arte e PNG do modelo
            arte_fn = None
            png_file = None
            modelo_chave = el.get("modelo")
            if modelo_chave and tipo in MODELOS_VEICULOS:
                for m in MODELOS_VEICULOS[tipo]:
                    if m["chave"] == modelo_chave:
                        arte_fn = m["arte"]
                        png_file = m.get("png")
                        break
            if tipo == "bicicleta": arte_fn = _arte_bicicleta
            if tipo == "pedestre":  arte_fn = _arte_pedestre

            if arte_fn:
                self._veiculo_arte(tx, ty, ang, larg, alt, cor, label, arte_fn, png=png_file)
            else:
                self._veiculo(tx, ty, ang, larg, alt, cor, label)

        elif tipo=="sc":
            r=el.get("tamanho_sc",10)*self.zoom
            ang=el.get("angulo",0)
            rad=math.radians(ang)
            ca,sa=math.cos(rad),math.sin(rad)
            def rot(dx,dy): return tx+dx*ca-dy*sa, ty+dx*sa+dy*ca
            p1=rot(-r,-r); p2=rot(r,r); p3=rot(r,-r); p4=rot(-r,r)
            c.create_line(*p1,*p2,fill=COR_PERIGO,width=2)
            c.create_line(*p3,*p4,fill=COR_PERIGO,width=2)
            c.create_text(tx+r+4,ty-r,text="SC",fill=COR_PERIGO,
                          font=("Segoe UI",9,"bold"),anchor="w")

        elif tipo=="texto":
            fonte_nome = el.get("fonte","Segoe UI")
            fonte_tam  = el.get("tamanho", 12)
            fonte_bold = "bold" if el.get("negrito",False) else "normal"
            fonte_itl  = "italic" if el.get("italico",False) else ""
            fonte_spec = (fonte_nome, fonte_tam,
                          (fonte_bold+" "+fonte_itl).strip() or "normal")
            cor_txt    = el.get("cor_texto", BRANCO)
            c.create_text(tx, ty, text=label, fill=cor_txt,
                          font=fonte_spec, anchor="nw")
            # Borda de seleção ao redor do texto
            if sel:
                try:
                    bbox = c.bbox(c.find_withtag("current"))
                except Exception:
                    bbox = None

        # Marcador seleção
        if sel:
            r=16*self.zoom
            c.create_oval(tx-r,ty-r,tx+r,ty+r,
                          outline=AMARELO,width=2,dash=(4,3))

    def _veiculo_arte(self, tx, ty, angulo, larg, alt, cor, label, arte_fn, png=None):
        """
        Desenha veículo com PNG (se disponível) ou arte vetorial.
        Rotação via PIL para PNG, via polígonos rotacionados para vetorial.
        """
        c = self.canvas
        sc = self.zoom
        desenhado = False

        # ── Tenta renderizar via PNG ──
        if PIL_OK and png:
            img_base = carregar_imagem_veiculo(png, cor)
            if img_base:
                try:
                    # Redimensiona para tamanho atual no zoom
                    tw = max(4, int(larg * sc * 1.6))
                    th = max(4, int(alt  * sc * 2.8))
                    img_res = img_base.resize((tw, th), Image.LANCZOS)
                    # Rotaciona
                    ang = angulo % 360
                    if ang > 1:
                        img_res = img_res.rotate(-ang, expand=True,
                                                  resample=Image.BILINEAR)
                    tk_img = ImageTk.PhotoImage(img_res)
                    if not hasattr(self, "_tk_imgs"):
                        self._tk_imgs = []
                    self._tk_imgs.append(tk_img)
                    c.create_image(tx, ty, image=tk_img, anchor="center")
                    desenhado = True
                except Exception as e:
                    print(f"[PNG render] {e}")

        # ── Fallback: arte vetorial ──
        if not desenhado:
            arte_fn(c, tx, ty, sc, cor)

        # ── Rótulo abaixo do veículo (rotacionado junto) ──
        if label:
            rad = math.radians(angulo)
            off = (alt * sc / 2 + 10)
            lx = tx + math.sin(rad) * off
            ly = ty + math.cos(rad) * off
            c.create_text(lx, ly, text=label,
                          fill=BRANCO, font=("Segoe UI", 8, "bold"))

    def _veiculo(self, tx, ty, angulo, larg, alt, cor, label):
        """Fallback retangular simples (usado quando não há arte nem PNG)."""
        c = self.canvas
        hw = larg*self.zoom/2; hh = alt*self.zoom/2
        rad = math.radians(angulo); ca, sa = math.cos(rad), math.sin(rad)
        def rot(dx, dy): return tx+dx*ca-dy*sa, ty+dx*sa+dy*ca
        pts = [rot(-hw,-hh), rot(hw,-hh), rot(hw,hh), rot(-hw,hh)]
        c.create_polygon([v for p in pts for v in p],
                         fill=cor, outline=BRANCO, width=1)
        pw, ph = hw*0.6, hh*0.4
        pts2 = [rot(-pw,-hh+ph), rot(pw,-hh+ph),
                rot(pw*0.8,-hh), rot(-pw*0.8,-hh)]
        c.create_polygon([v for p in pts2 for v in p],
                         fill="#A0C0F0", outline="")
        if label:
            lx, ly = rot(0, hh+9)
            c.create_text(lx, ly, text=label,
                          fill=BRANCO, font=("Segoe UI", 8, "bold"))

    def _norte(self,cx,cy):
        c=self.canvas; r=16
        c.create_line(cx,cy-r,cx,cy+r,fill="#334",width=1)
        c.create_line(cx-r,cy,cx+r,cy,fill="#334",width=1)
        c.create_polygon(cx,cy-r,cx+5,cy,cx-5,cy,fill=AMARELO,outline="")
        c.create_text(cx,cy-r-8,text="N",fill=AMARELO,font=("Segoe UI",9,"bold"))

    def _rodape(self,W,H):
        c=self.canvas
        perito=self.dados_caso.get("perito","")
        bo=self.dados_caso.get("bo","")
        data=self.dados_caso.get("data","")
        c.create_rectangle(0,H-22,W,H,fill=COR_PAINEL,outline="")
        c.create_line(0,H-22,W,H-22,fill=AMARELO,width=1)
        c.create_text(W//2,H-11,
                      text=f"BO {bo}  ·  {data}  ·  Perito: {perito}",
                      fill=CINZA_CLARO,font=FONTE_PEQ)

    # ──────────────────────────────────────────
    #  SALVAR / PDF
    # ──────────────────────────────────────────
    def _salvar(self):
        dados={**self.dados_caso,"modo":self.modo,"k":self.k,
               "u_k":self.u_k,"calibrado":self.calibrado,
               "elementos":self.elementos}
        bo=self.dados_caso.get("bo","").replace("/","-")
        nome=f"BO_{bo}_{datetime.date.today()}.sicro"
        cam=DIR_CROQUIS/nome
        with open(cam,"w",encoding="utf-8") as f:
            json.dump(dados,f,ensure_ascii=False,indent=2)
        messagebox.showinfo("Salvo",f"Croqui salvo:\n{cam}")

    def _exportar_pdf(self):
        try:
            from reportlab.pdfgen import canvas as rl
            from reportlab.lib.pagesizes import A4,landscape
            from reportlab.lib.units import mm
        except ImportError:
            messagebox.showerror("ReportLab","pip install reportlab"); return
        path=filedialog.asksaveasfilename(
            defaultextension=".pdf",filetypes=[("PDF","*.pdf")],
            initialfile=f"Croqui_BO_{self.dados_caso.get('bo','').replace('/','_')}.pdf")
        if not path: return
        W_pt,H_pt=landscape(A4)
        cv=rl.Canvas(path,pagesize=(W_pt,H_pt))
        cv.setFont("Helvetica-Bold",14)
        cv.drawCentredString(W_pt/2,H_pt-20*mm,"SICRO PCI/AP — CROQUI DE AMARRAÇÃO")
        cv.setFont("Helvetica",10)
        cv.drawCentredString(W_pt/2,H_pt-27*mm,
            f"BO Nº {self.dados_caso.get('bo','')}  ·  "
            f"{self.dados_caso.get('local','')}  ·  "
            f"{self.dados_caso.get('data','')}")
        if PIL_OK:
            try:
                from PIL import ImageGrab
                x0=self.canvas.winfo_rootx(); y0=self.canvas.winfo_rooty()
                x1=x0+self.canvas.winfo_width(); y1=y0+self.canvas.winfo_height()
                img=ImageGrab.grab(bbox=(x0,y0,x1,y1))
                tmp=Path.home()/"SicroPCIAP"/"_tmp.png"
                img.save(tmp)
                cv.drawImage(str(tmp),15*mm,15*mm,
                             width=W_pt-30*mm,height=H_pt-50*mm,
                             preserveAspectRatio=True)
                tmp.unlink(missing_ok=True)
            except Exception: pass
        cv.setFont("Helvetica",8)
        cv.drawString(15*mm,8*mm,
            f"Perito: {self.dados_caso.get('perito','')}  ·  "
            f"SICRO PCI/AP  ·  {datetime.date.today()}")
        if self.calibrado and self.k:
            cv.drawRightString(W_pt-15*mm,8*mm,
                f"k={self.k:.5f} m/px  |  ±{self.u_k*1000:.3f}mm/px")
        cv.save()
        messagebox.showinfo("PDF exportado",f"Salvo:\n{path}")

    def _voltar(self):
        if messagebox.askyesno("Voltar",
                "Voltar ao início?\nAlterações não salvas serão perdidas."):
            self.winfo_toplevel().mostrar_inicio()


# ─────────────────────────────────────────────
#  POPUP SELEÇÃO DE PLACA
# ─────────────────────────────────────────────
MODELOS_PLACA = [
    {"chave":"pare",    "label":"PARE",   "cor":"#CC0000","desc":"Parada obrigatória"},
    {"chave":"vel_30",  "label":"30",     "cor":"#CC6600","desc":"Velocidade máx. 30km/h"},
    {"chave":"vel_40",  "label":"40",     "cor":"#CC6600","desc":"Velocidade máx. 40km/h"},
    {"chave":"vel_60",  "label":"60",     "cor":"#CC6600","desc":"Velocidade máx. 60km/h"},
    {"chave":"vel_80",  "label":"80",     "cor":"#CC6600","desc":"Velocidade máx. 80km/h"},
    {"chave":"proib",   "label":"🚫",     "cor":"#CC0000","desc":"Proibido"},
    {"chave":"atencao", "label":"⚠",      "cor":"#CC8800","desc":"Atenção / perigo"},
    {"chave":"ped",     "label":"🚶",     "cor":"#005500","desc":"Passagem de pedestre"},
    {"chave":"custom",  "label":"...",    "cor":"#003388","desc":"Personalizada"},
]


# ─── EditorVia ───
class EditorVia(tk.Toplevel):
    def __init__(self, parent, editor_principal):
        super().__init__(parent)
        self.title("Editor de Via  —  SICRO PCI/AP")
        self.configure(bg=COR_FUNDO)
        self.ep   = editor_principal   # referência ao editor principal
        self.state("zoomed")
        self.lift()
        self.focus_force()
        # grab_set após zoomed resolver — senão bloqueia eventos do canvas
        self.after(200, self._grab_seguro)

        # Copia camada de via + elementos de modelo (via pronta) já existentes
        import copy
        TIPOS_VIA = ("v_","_asfalto","_calcada","_canteiro","_faixa","_rotatoria","_asfalto_terra")
        self.elementos_via = [copy.deepcopy(e)
                              for e in editor_principal.elementos
                              if any(e["tipo"].startswith(p) for p in TIPOS_VIA)]

        self.ferramenta = "asfalto"
        self.sel_idx    = None
        self.drag_start = None
        self.tmp_ids    = []          # ids canvas do preview
        self._drag_saved = False

        # Herda visão do editor principal
        self.zoom  = editor_principal.zoom
        self.pan_x = editor_principal.pan_x
        self.pan_y = editor_principal.pan_y
        self._pan_start = None

        self._historico = []
        self._MAX_UNDO  = 50

        self._build_ui()
        # Aguarda o canvas ter tamanho real antes de redesenhar
        self.after(150, self._redesenhar)

    def _grab_seguro(self):
        """Aplica grab após window estar totalmente renderizada."""
        try:
            if self.winfo_exists():
                self.grab_set()
        except Exception:
            pass

    # ── UI ─────────────────────────────────────
    def _build_ui(self):
        tk.Frame(self, bg=AMARELO, height=4).pack(fill="x")

        # Cabeçalho
        cab = tk.Frame(self, bg=COR_PAINEL)
        cab.pack(fill="x")
        tk.Label(cab, text="🛣  Editor de Via",
                 font=("Segoe UI",12,"bold"),
                 bg=COR_PAINEL, fg=AMARELO).pack(side="left", padx=14, pady=7)
        tk.Label(cab,
                 text="Veículos e cotas aparecem como referência  —  "
                      "edições aqui ficam numa camada separada de via",
                 font=FONTE_PEQ, bg=COR_PAINEL, fg=CINZA_CLARO).pack(side="left")
        tk.Button(cab, text="✓  Aplicar e fechar",
                  font=("Segoe UI",10,"bold"), cursor="hand2",
                  bg=COR_SUCESSO, fg=PRETO_SOFT,
                  activebackground="#3AB870",
                  relief="flat", padx=14, pady=5,
                  command=self._aplicar_fechar).pack(side="right", padx=8, pady=5)
        tk.Button(cab, text="✕  Cancelar",
                  font=FONTE_PEQ, cursor="hand2",
                  bg=COR_CARD, fg=CINZA_CLARO,
                  activebackground=COR_BORDA,
                  relief="flat", padx=10, pady=5,
                  command=self.destroy).pack(side="right", pady=5)

        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill="both", expand=True)

        # Toolbar
        tb = tk.Frame(corpo, bg=COR_PAINEL, width=62)
        tb.pack(side="left", fill="y")
        tb.pack_propagate(False)
        tk.Frame(tb, bg=AMARELO, height=2).pack(fill="x")
        tk.Label(tb, text="Via", font=("Segoe UI",8,"bold"),
                 bg=COR_PAINEL, fg=AMARELO).pack(pady=(6,2))

        self.btns_via = {}
        for chave, icone, dica in FERRAMENTAS_VIA:
            btn = tk.Button(tb, text=icone, font=("Segoe UI",12),
                            width=3, cursor="hand2",
                            bg=COR_PAINEL, fg=BRANCO,
                            activebackground=AZUL_MEDIO, relief="flat",
                            command=lambda c=chave: self._set_ferr(c))
            btn.pack(pady=1, padx=3)
            btn.bind("<Enter>", lambda e,d=dica: self.status.config(text=d))
            self.btns_via[chave] = btn

        tk.Frame(tb, bg=COR_BORDA, height=1).pack(fill="x", pady=4)
        tk.Label(tb, text="Editar", font=("Segoe UI",8),
                 bg=COR_PAINEL, fg=CINZA_MEDIO).pack(pady=(2,2))

        for txt, cmd, dica in [
            ("↖", self._modo_sel,   "Selecionar / mover"),
            ("⌫", self._apagar_sel, "Apagar selecionado"),
            ("↺", self._desfazer,   "Desfazer (Ctrl+Z)"),
        ]:
            b = tk.Button(tb, text=txt, font=("Segoe UI",13), width=3,
                          cursor="hand2", bg=COR_PAINEL, fg=BRANCO,
                          activebackground=AZUL_MEDIO, relief="flat",
                          command=cmd)
            b.pack(pady=1, padx=3)
            b.bind("<Enter>", lambda e,d=dica: self.status.config(text=d))

        tk.Frame(tb, bg=COR_BORDA, height=1).pack(fill="x", pady=4)
        for txt, cmd in [("+",lambda: self._zoom_d(1.2)),
                          ("−",lambda: self._zoom_d(1/1.2)),
                          ("⌂",self._reset_view)]:
            tk.Button(tb, text=txt, font=("Segoe UI",13), width=3,
                      bg=COR_PAINEL, fg=BRANCO, relief="flat", cursor="hand2",
                      command=cmd).pack(pady=1, padx=3)

        # Canvas
        cf = tk.Frame(corpo, bg=COR_FUNDO)
        cf.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(cf, bg="#0A1020",
                                cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>",        self._click)
        self.canvas.bind("<B1-Motion>",       self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<Button-3>",        self._click_dir)
        self.canvas.bind("<MouseWheel>",      self._scroll_zoom)
        self.canvas.bind("<Button-2>",        self._pan_ini)
        self.canvas.bind("<B2-Motion>",       self._pan_mov)
        self.canvas.bind("<Configure>",       lambda e: self._redesenhar())
        self.canvas.bind("<Motion>",           self._motion_preview)
        self.canvas.bind("<Control-z>",       self._desfazer)
        self.bind("<Control-z>",              self._desfazer)
        self.canvas.bind("<Delete>",           self._apagar_sel)
        self.bind("<Delete>",                  self._apagar_sel)

        # Painel direito: camadas de via
        pd = tk.Frame(corpo, bg=COR_PAINEL, width=200)
        pd.pack(side="right", fill="y")
        pd.pack_propagate(False)
        tk.Frame(pd, bg=AMARELO, height=2).pack(fill="x")
        tk.Label(pd, text="Camadas de via",
                 font=("Segoe UI",11,"bold"),
                 bg=COR_PAINEL, fg=AMARELO).pack(pady=(8,4))
        flb = tk.Frame(pd, bg=COR_CARD)
        flb.pack(fill="both", expand=True, padx=4)
        scrl = tk.Scrollbar(flb)
        scrl.pack(side="right", fill="y")
        self.lb = tk.Listbox(flb, yscrollcommand=scrl.set,
                             bg=COR_CARD, fg=BRANCO,
                             selectbackground=AZUL_MEDIO,
                             font=("Segoe UI",9), relief="flat", bd=0,
                             activestyle="none", highlightthickness=0)
        self.lb.pack(fill="both", expand=True)
        scrl.config(command=self.lb.yview)
        self.lb.bind("<<ListboxSelect>>", self._camada_sel)
        tk.Button(pd, text="⌫  Apagar selecionado",
                  font=FONTE_PEQ, cursor="hand2",
                  bg="#3A1010", fg="#FF8080",
                  activebackground="#5A1A1A",
                  relief="flat", pady=4,
                  command=self._apagar_sel).pack(fill="x", padx=4, pady=4)

        self.status = tk.Label(self, text="Pronto",
                               font=FONTE_MONO, bg=COR_PAINEL,
                               fg=CINZA_MEDIO, anchor="w")
        self.status.pack(fill="x", side="bottom", padx=8, pady=2)
        tk.Frame(self, bg=AMARELO, height=2).pack(fill="x", side="bottom")

        self._set_ferr("asfalto")

    # ── Ferramentas ──────────────────────────
    def _set_ferr(self, f):
        self.ferramenta = f
        # Limpa preview de motion anterior
        for tid in getattr(self,"_motion_ids",[]):
            try: self.canvas.delete(tid)
            except: pass
        self._motion_ids=[]
        for k, btn in self.btns_via.items():
            btn.config(bg=AZUL_MEDIO if k==f else COR_PAINEL)
        dica = next((d for c,i,d in FERRAMENTAS_VIA if c==f), f)
        self.status.config(text=f"Ferramenta: {dica}  —  clique e arraste")
        self.canvas.config(cursor="crosshair")

    def _modo_sel(self):
        self.ferramenta = "_sel"
        for btn in self.btns_via.values():
            btn.config(bg=COR_PAINEL)
        self.status.config(text="Selecionar / mover  —  clique no elemento")
        self.canvas.config(cursor="arrow")

    # ── Coordenadas / zoom / pan ──────────────
    def _mt(self,x,y): return x*self.zoom+self.pan_x, y*self.zoom+self.pan_y
    def _tm(self,tx,ty): return (tx-self.pan_x)/self.zoom,(ty-self.pan_y)/self.zoom
    def _tx(self,x): return x*self.zoom+self.pan_x
    def _ty(self,y): return y*self.zoom+self.pan_y

    def _zoom_d(self,f,cx=None,cy=None):
        if cx is None:
            cx=self.canvas.winfo_width()/2; cy=self.canvas.winfo_height()/2
        wx,wy=self._tm(cx,cy)
        self.zoom=max(0.1,min(10.0,self.zoom*f))
        self.pan_x=cx-wx*self.zoom; self.pan_y=cy-wy*self.zoom
        self._redesenhar()

    def _reset_view(self):
        self.zoom=self.ep.zoom; self.pan_x=self.ep.pan_x; self.pan_y=self.ep.pan_y
        self._redesenhar()

    def _scroll_zoom(self,e):
        self._zoom_d(1.1 if e.delta>0 else 1/1.1, e.x, e.y)

    def _pan_ini(self,e): self._pan_start=(e.x-self.pan_x, e.y-self.pan_y)
    def _pan_mov(self,e):
        if self._pan_start:
            self.pan_x=e.x-self._pan_start[0]; self.pan_y=e.y-self._pan_start[1]
            self._redesenhar()

    # ── Undo ─────────────────────────────────
    def _salvar_hist(self):
        import copy
        self._historico.append(copy.deepcopy(self.elementos_via))
        if len(self._historico)>self._MAX_UNDO: self._historico.pop(0)

    def _desfazer(self,event=None):
        if not self._historico:
            self.status.config(text="Nada para desfazer"); return
        import copy
        self.elementos_via=copy.deepcopy(self._historico.pop())
        self.sel_idx=None
        self._atualizar_camadas(); self._redesenhar()
        self.status.config(text=f"Desfeito  ({len(self._historico)} passos)")

    # ── Eventos ──────────────────────────────
    def _click(self,e):
        x,y=self._tm(e.x,e.y)
        if self.ferramenta=="_sel":
            self._selecionar(x,y)
        else:
            self.drag_start=(x,y)
            self.status.config(text="Arraste para definir o tamanho...")

    def _drag(self,e):
        x,y=self._tm(e.x,e.y)
        if self.ferramenta=="_sel" and self.sel_idx is not None and self.drag_start:
            el=self.elementos_via[self.sel_idx]
            if not self._drag_saved:
                self._salvar_hist(); self._drag_saved=True
            dx=x-self.drag_start[0]; dy=y-self.drag_start[1]
            el["x"]+=dx; el["y"]+=dy
            if "x2" in el: el["x2"]+=dx; el["y2"]+=dy
            self.drag_start=(x,y); self._redesenhar()
        elif self.ferramenta!="_sel" and self.drag_start:
            self._preview(e.x,e.y)

    def _release(self,e):
        x,y=self._tm(e.x,e.y)
        if self.ferramenta!="_sel" and self.drag_start:
            # Limpa preview
            for tid in self.tmp_ids: self.canvas.delete(tid)
            self.tmp_ids=[]
            self._criar_elemento(x,y)
        self.drag_start=None; self._drag_saved=False

    def _click_dir(self,e):
        x,y=self._tm(e.x,e.y); i=self._em(x,y)
        if i is not None:
            self.sel_idx=i; self._redesenhar()

    # ── Preview durante drag ──────────────────
    def _motion_preview(self,e):
        """Mostra preview semitransparente de semaforo/placa/arvore/poste
        enquanto o cursor se move, antes de clicar."""
        f=self.ferramenta
        if f not in ("semaforo","placa","arvore","poste","rotatoria"): return
        if self.drag_start: return  # já está arrastando, _preview cuida disso
        # Limpa preview anterior de motion
        for tid in getattr(self,"_motion_ids",[]):
            try: self.canvas.delete(tid)
            except: pass
        self._motion_ids=[]
        c=self.canvas; tx,ty=e.x,e.y
        if f=="semaforo":
            r=max(5,int(8*self.zoom))
            bw,bh=r*1.6,r*5
            self._motion_ids.append(
                c.create_rectangle(tx-bw/2,ty-bh/2,tx+bw/2,ty+bh/2,
                                   fill="#222222",outline="#CCCCCC",
                                   width=1,stipple="gray25"))
            for oy_,cor_ in [(-r*1.6,"#CC2200"),(0,"#CCAA00"),(r*1.6,"#00AA00")]:
                self._motion_ids.append(
                    c.create_oval(tx-r*.6,ty+oy_-r*.6,tx+r*.6,ty+oy_+r*.6,
                                 fill=cor_,outline=""))
        elif f=="placa":
            r=max(6,int(10*self.zoom))
            self._motion_ids.append(
                c.create_rectangle(tx-r,ty-r,tx+r,ty+r,
                                   fill="#CC0000",outline="#CCCCCC",
                                   width=1,stipple="gray25"))
            self._motion_ids.append(
                c.create_text(tx,ty,text="?",fill="#CCCCCC",
                              font=("Segoe UI",max(5,int(6*self.zoom)),"bold")))
        elif f=="arvore":
            r=max(8,int(12*self.zoom))
            self._motion_ids.append(
                c.create_oval(tx-r,ty-r,tx+r,ty+r,
                              fill="#1A6A1A",outline="#2A8A2A",
                              width=1,stipple="gray25"))
        elif f=="poste":
            r=max(3,int(5*self.zoom))
            self._motion_ids.append(
                c.create_line(tx,ty-r*3,tx,ty+r*1.5,
                              fill="#888888",width=max(2,int(2*self.zoom))))
            self._motion_ids.append(
                c.create_oval(tx-r,ty-r*4,tx+r,ty-r*2,
                             fill="#FFEE88",outline=""))
        elif f=="rotatoria":
            r=40*self.zoom
            self._motion_ids.append(
                c.create_oval(tx-r,ty-r,tx+r,ty+r,
                              fill="#606060",outline="#FFCC00",
                              width=2,stipple="gray25"))

    def _preview(self,tx2,ty2):
        for tid in self.tmp_ids: self.canvas.delete(tid)
        self.tmp_ids=[]
        if not self.drag_start: return
        tx1,ty1=self._mt(*self.drag_start)
        f=self.ferramenta
        c=self.canvas

        if f in ("asfalto","calcada","conflito","faixa_ped"):
            cor={"asfalto":"#606060","calcada":"#909090",
                 "conflito":"#E05555","faixa_ped":"#DDDDDD"}.get(f,"#666")
            dash=(6,4) if f=="conflito" else ()
            self.tmp_ids.append(
                c.create_rectangle(tx1,ty1,tx2,ty2,
                                   fill=cor,outline=BRANCO,
                                   width=1,stipple="gray50" if f=="conflito" else ""))
        elif f in ("faixa_am","faixa_br"):
            cor=AMARELO if f=="faixa_am" else BRANCO
            self.tmp_ids.append(
                c.create_line(tx1,ty1,tx2,ty2,fill=cor,width=3,
                              dash=(14,8)))
        elif f=="rotatoria":
            r=max(8,int(math.hypot(tx2-tx1,ty2-ty1)/2))
            mx,my=(tx1+tx2)/2,(ty1+ty2)/2
            self.tmp_ids.append(
                c.create_oval(mx-r,my-r,mx+r,my+r,
                              fill="#606060",outline=AMARELO,width=2))
            self.tmp_ids.append(
                c.create_oval(mx-r*0.4,my-r*0.4,mx+r*0.4,my+r*0.4,
                              fill="#1A3A1A",outline=""))
        elif f in ("semaforo","placa","arvore","poste"):
            cor={"semaforo":"#111","placa":"#005500",
                 "arvore":"#1A4A1A","poste":"#888"}.get(f,"#444")
            r=10
            self.tmp_ids.append(
                c.create_oval(tx2-r,ty2-r,tx2+r,ty2+r,
                              fill=cor,outline=BRANCO,width=1))

    # ── Criação do elemento ───────────────────
    def _criar_elemento(self,x2,y2):
        x1,y1=self.drag_start; f=self.ferramenta
        # Ignora clicks sem arraste mínimo para áreas
        if f in ("asfalto","calcada","conflito","faixa_ped"):
            if abs(x2-x1)<5 and abs(y2-y1)<5: return
        self._salvar_hist()

        if f=="asfalto":
            el={"tipo":"v_asfalto",
                "x":min(x1,x2),"y":min(y1,y2),"x2":max(x1,x2),"y2":max(y1,y2)}
        elif f=="calcada":
            el={"tipo":"v_calcada",
                "x":min(x1,x2),"y":min(y1,y2),"x2":max(x1,x2),"y2":max(y1,y2)}
        elif f=="conflito":
            el={"tipo":"v_conflito",
                "x":min(x1,x2),"y":min(y1,y2),"x2":max(x1,x2),"y2":max(y1,y2)}
        elif f=="faixa_am":
            el={"tipo":"v_faixa_am","x":x1,"y":y1,"x2":x2,"y2":y2}
        elif f=="faixa_br":
            el={"tipo":"v_faixa_br","x":x1,"y":y1,"x2":x2,"y2":y2}
        elif f=="faixa_ped":
            el={"tipo":"v_faixa_ped",
                "x":min(x1,x2),"y":min(y1,y2),"x2":max(x1,x2),"y2":max(y1,y2)}
        elif f=="rotatoria":
            cx,cy=(x1+x2)/2,(y1+y2)/2
            r=max(10,math.hypot(x2-x1,y2-y1)/2)
            el={"tipo":"v_rotatoria","x":cx,"y":cy,"r":r}
        elif f=="semaforo":
            el={"tipo":"v_semaforo","x":x2,"y":y2}
        elif f=="placa":
            popup_placa = PopupPlacas(self)
            self.wait_window(popup_placa)
            if popup_placa.resultado is None: return
            m_placa = popup_placa.resultado
            el={"tipo":"v_placa","x":x2,"y":y2,
                "label":m_placa["label"],"cor_placa":m_placa["cor"],
                "chave_placa":m_placa["chave"]}
        elif f=="arvore":
            el={"tipo":"v_arvore","x":x2,"y":y2}
        elif f=="poste":
            el={"tipo":"v_poste","x":x2,"y":y2}
        else:
            return

        self.elementos_via.append(el)
        self.sel_idx=len(self.elementos_via)-1
        self._atualizar_camadas(); self._redesenhar()

    # ── Seleção e camadas ─────────────────────
    def _em(self,x,y,r=22):
        rz=r/self.zoom
        for i,el in reversed(list(enumerate(self.elementos_via))):
            ex,ey=el.get("x",0),el.get("y",0)
            if math.hypot(x-ex,y-ey)<rz: return i
            if "x2" in el:
                mx=(ex+el["x2"])/2; my=(ey+el["y2"])/2
                if math.hypot(x-mx,y-my)<rz: return i
        return None

    def _selecionar(self,x,y):
        i=self._em(x,y); self.sel_idx=i
        self.drag_start=(x,y) if i is not None else None
        self._redesenhar()

    def _apagar_sel(self):
        if self.sel_idx is None: return
        self._salvar_hist()
        self.elementos_via.pop(self.sel_idx)
        self.sel_idx=None
        self._atualizar_camadas(); self._redesenhar()

    def _camada_sel(self,event=None):
        sel=self.lb.curselection()
        if not sel: return
        el_idx=len(self.elementos_via)-1-sel[0]
        if 0<=el_idx<len(self.elementos_via):
            self.sel_idx=el_idx; self._redesenhar()

    def _atualizar_camadas(self):
        self.lb.delete(0,tk.END)
        for el in reversed(self.elementos_via):
            ic,nm=TIPO_INFO_VIA.get(el["tipo"],("?",el["tipo"]))
            self.lb.insert(tk.END,f"  {ic}  {nm}")

    # ── Redesenho ────────────────────────────
    def _redesenhar(self):
        c=self.canvas; c.delete("all")
        self._motion_ids = []  # reseta previews de motion
        W=c.winfo_width(); H=c.winfo_height()
        if W<2 or H<2: return

        # Grade de fundo
        passo=max(1,int(50*self.zoom))
        ox=int(self.pan_x)%passo; oy=int(self.pan_y)%passo
        for xi in range(-passo,W+passo,passo):
            c.create_line(xi+ox,0,xi+ox,H,fill="#14183A",width=1)
        for yi in range(-passo,H+passo,passo):
            c.create_line(0,yi+oy,W,yi+oy,fill="#14183A",width=1)

        # ── Referências do croqui principal (fantasma 40% opacidade) ──
        self._desenhar_ref_direto(c)

        # ── Elementos de via (v_ e modelo _) ──
        for i,el in enumerate(self.elementos_via):
            self._desenhar_via(el, i==self.sel_idx)

        # Atualiza status
        n=len(self.elementos_via)
        self.status.config(
            text=f"Via: {n} elemento(s)  |  Ferramenta: {self.ferramenta}  |  Ctrl+Z desfaz")

    def _desenhar_ref_direto(self, c):
        """
        Desenha os elementos do croqui principal diretamente no canvas do EditorVia,
        redirecionando temporariamente ep.canvas e usando zoom/pan do editor de via.
        Efeito fantasma: stipple='gray50' simula ~50% de transparência.
        Veículos PNG: desenhados normalmente pois _veiculo_arte usa self.ep.canvas.
        """
        # Salva estado do editor principal
        old_canvas = self.ep.canvas
        old_zoom   = self.ep.zoom
        old_pan_x  = self.ep.pan_x
        old_pan_y  = self.ep.pan_y
        old_tk_imgs = getattr(self.ep, "_tk_imgs", [])

        # Redireciona para o canvas do EditorVia
        self.ep.canvas  = c
        self.ep.zoom    = self.zoom
        self.ep.pan_x   = self.pan_x
        self.ep.pan_y   = self.pan_y
        self.ep._tk_imgs = []   # cache fresco para este frame

        for el in self.ep.elementos:
            t = el["tipo"]
            if t.startswith("v_") or t.startswith("_"):
                continue  # vias: não mostrar (já estão em elementos_via)
            try:
                self.ep._desenhar_el(el, False)
            except Exception:
                pass

        # Aplica stipple sobre tudo que foi desenhado acima
        # Sobrepõe um retângulo semitransparente para atenuar
        W = c.winfo_width(); H = c.winfo_height()
        if W > 2 and H > 2:
            c.create_rectangle(0, 0, W, H,
                               fill="#0A1020", outline="",
                               stipple="gray50")

        # Restaura estado original
        self.ep.canvas  = old_canvas
        self.ep.zoom    = old_zoom
        self.ep.pan_x   = old_pan_x
        self.ep.pan_y   = old_pan_y
        self.ep._tk_imgs = old_tk_imgs

    def _desenhar_via(self,el,sel=False):
        c=self.canvas; t=el["tipo"]
        tx,ty=self._mt(el.get("x",0),el.get("y",0))

        # ── Elementos de modelo (via pronta selecionada na tela inicial) ──
        if t=="_asfalto" or t=="_asfalto_terra":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            cor="#5A4A2A" if t=="_asfalto_terra" else "#606060"
            c.create_rectangle(ax1,ay1,ax2,ay2,fill=cor,outline="#808080",width=1)
            return
        if t=="_calcada":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#A0A0A0",outline="#C0C0C0",width=1)
            return
        if t=="_canteiro":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#1A3A1A",outline="")
            return
        if t=="_faixa_h" or t=="_faixa_v":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_line(ax1,ay1,ax2,ay2,fill=AMARELO,
                          width=max(2,int(2*self.zoom)),
                          dash=(max(8,int(14*self.zoom)),max(6,int(10*self.zoom))))
            return
        if t=="_rotatoria":
            r=el.get("r",80)*self.zoom; ri=r*0.4
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="#606060",outline="")
            c.create_oval(tx-ri,ty-ri,tx+ri,ty+ri,fill="#1A3A1A",outline="")
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="",outline=AMARELO,
                          width=max(1,int(1.5*self.zoom)),dash=(8,5))
            return

        if t=="v_asfalto":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#606060",outline="#808080",width=1)

        elif t=="v_calcada":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,fill="#A0A0A0",outline="#C0C0C0",width=1)
            # Hachura
            p=max(4,int(10*self.zoom))
            for xi in range(int(ax1),int(ax2),p):
                c.create_line(xi,int(ay1),xi,int(ay2),fill="#888",width=1)

        elif t=="v_conflito":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_rectangle(ax1,ay1,ax2,ay2,
                               fill="",outline=COR_PERIGO,width=2,dash=(8,4))
            c.create_text((ax1+ax2)/2,(ay1+ay2)/2,
                          text="CONFLITO",fill=COR_PERIGO,
                          font=("Segoe UI",max(8,int(9*self.zoom)),"bold"))

        elif t=="v_faixa_am":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_line(ax1,ay1,ax2,ay2,fill=AMARELO,
                          width=max(2,int(3*self.zoom)),
                          dash=(max(10,int(14*self.zoom)),max(6,int(8*self.zoom))))

        elif t=="v_faixa_br":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            c.create_line(ax1,ay1,ax2,ay2,fill=BRANCO,
                          width=max(2,int(2*self.zoom)))

        elif t=="v_faixa_ped":
            ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
            larg=max(1,ax2-ax1); n=max(3,int(larg/max(1,8*self.zoom)))
            passo=larg/n
            for i in range(n):
                lx=ax1+i*passo
                c.create_rectangle(lx,ay1,lx+passo*0.55,ay2,
                                   fill=BRANCO,outline="")

        elif t=="v_rotatoria":
            r=el.get("r",60)*self.zoom; ri=r*0.38
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="#606060",outline="#808080",width=1)
            c.create_oval(tx-ri,ty-ri,tx+ri,ty+ri,fill="#1A3A1A",outline="#2A5A2A",width=1)
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="",outline=AMARELO,
                          width=max(1,int(1.5*self.zoom)),dash=(8,5))

        elif t=="v_semaforo":
            r=max(5,int(8*self.zoom))
            bw=r*1.6; bh=r*5
            c.create_rectangle(tx-bw/2,ty-bh/2,tx+bw/2,ty+bh/2,
                               fill="#111",outline="#444",width=1)
            for oy_,cor_ in [(-r*1.6,"#CC2200"),
                              (0,     "#CCAA00"),
                              (r*1.6, "#00AA00")]:
                c.create_oval(tx-r*0.6,ty+oy_-r*0.6,
                             tx+r*0.6,ty+oy_+r*0.6,
                             fill=cor_,outline="#222",width=1)
            c.create_line(tx,ty+bh/2,tx,ty+bh/2+r*2,
                          fill="#666",width=max(2,int(2*self.zoom)))

        elif t=="v_placa":
            lb=el.get("label","PARE"); r=max(6,int(10*self.zoom))
            cor_p=el.get("cor_placa","#CC0000")
            chave_p=el.get("chave_placa","pare")
            # Poste
            c.create_line(tx,ty+r,tx,ty+r*2.5,
                          fill="#666",width=max(1,int(1.5*self.zoom)))
            if chave_p=="pare":
                pts=[]
                for i in range(8):
                    ang=math.radians(i*45+22.5)
                    pts.extend([tx+math.cos(ang)*r, ty+math.sin(ang)*r])
                c.create_polygon(pts,fill=cor_p,outline=BRANCO,
                                 width=max(1,int(1.5*self.zoom)))
            elif chave_p in ("vel_30","vel_40","vel_60","vel_80"):
                c.create_oval(tx-r,ty-r,tx+r,ty+r,fill=BRANCO,
                              outline="#CC0000",width=max(2,int(2*self.zoom)))
                c.create_text(tx,ty,text=lb,fill="#CC0000",
                              font=("Segoe UI",max(5,int(6*self.zoom)),"bold"))
                return  # sem poste redraw
            elif chave_p=="atencao":
                pts=[tx,ty-r, tx+r*0.87,ty+r*0.5, tx-r*0.87,ty+r*0.5]
                c.create_polygon(pts,fill=cor_p,outline=BRANCO,
                                 width=max(1,int(1.5*self.zoom)))
                c.create_text(tx,ty+3,text="!",fill=BRANCO,
                              font=("Segoe UI",max(6,int(8*self.zoom)),"bold"))
            elif chave_p=="proib":
                c.create_oval(tx-r,ty-r,tx+r,ty+r,fill=BRANCO,
                              outline="#CC0000",width=max(2,int(2*self.zoom)))
                c.create_line(tx-r*.7,ty-r*.7,tx+r*.7,ty+r*.7,
                              fill="#CC0000",width=max(2,int(2.5*self.zoom)))
            else:
                c.create_rectangle(tx-r,ty-r,tx+r,ty+r,
                                   fill=cor_p,outline=BRANCO,
                                   width=max(1,int(1.5*self.zoom)))
                c.create_text(tx,ty,text=lb[:6],fill=BRANCO,
                              font=("Segoe UI",max(5,int(6*self.zoom)),"bold"))

        elif t=="v_arvore":
            r=max(8,int(12*self.zoom))
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill="#1A6A1A",outline="#2A8A2A",width=1)
            c.create_oval(tx-r*.5,ty-r*.5,tx+r*.5,ty+r*.5,fill="#2A8A2A",outline="")

        elif t=="v_poste":
            r=max(3,int(5*self.zoom))
            c.create_line(tx,ty-r*3,tx,ty+r*1.5,
                          fill="#888",width=max(2,int(2*self.zoom)))
            c.create_oval(tx-r,ty-r*4,tx+r,ty-r*2,
                         fill="#FFEE88",outline="#CCCC44",width=1)
            c.create_line(tx-r*2,ty-r*3,tx,ty-r*3,
                          fill="#888",width=max(1,int(1.5*self.zoom)))

        # Marcador de seleção
        if sel:
            r2=18*self.zoom
            c.create_oval(tx-r2,ty-r2,tx+r2,ty+r2,
                         outline=AMARELO,width=2,dash=(4,3))
            if "x2" in el:
                ax1,ay1=self._mt(el["x"],el["y"]); ax2,ay2=self._mt(el["x2"],el["y2"])
                c.create_oval(ax1-6,ay1-6,ax1+6,ay1+6,fill=AMARELO,outline="")
                c.create_oval(ax2-6,ay2-6,ax2+6,ay2+6,fill=AMARELO,outline="")

    # ── Aplicar ao croqui principal ───────────
    def _aplicar_fechar(self):
        import copy
        TIPOS_VIA = ("v_","_asfalto","_calcada","_canteiro","_faixa","_rotatoria","_asfalto_terra")
        # Remove elementos de via e modelo antigos do croqui principal
        self.ep.elementos = [e for e in self.ep.elementos
                             if not any(e["tipo"].startswith(p) for p in TIPOS_VIA)]
        # Insere nova camada de via na base (desenhada primeiro = fica atrás)
        self.ep.elementos = copy.deepcopy(self.elementos_via) + self.ep.elementos
        self.destroy()


# ─────────────────────────────────────────────
#  EDITOR DE TEXTO INLINE
# ─────────────────────────────────────────────

# ─── EditorTextoInline ───
FONTES_DISPONIVEIS = [
    "Segoe UI", "Arial", "Calibri", "Times New Roman",
    "Courier New", "Verdana", "Tahoma", "Georgia",
]

class EditorTextoInline:
    """
    Editor de texto inline: cria um Entry diretamente sobre o canvas
    na posição do elemento, com um painel flutuante de formatação.
    O texto aparece no canvas em tempo real conforme o usuário digita.
    """
    def __init__(self, janela, canvas, elemento, fn_mt, fn_redesenhar, fn_camadas):
        self.janela      = janela
        self.canvas      = canvas
        self.el          = elemento
        self._mt         = fn_mt
        self._redesenhar = fn_redesenhar
        self._camadas    = fn_camadas
        self._ativo      = True

        # Posição no canvas
        tx, ty = self._mt(elemento.get("x", 0), elemento.get("y", 0))

        # ── Entry inline sobre o canvas ──
        fonte_nome = elemento.get("fonte", "Segoe UI")
        fonte_tam  = elemento.get("tamanho", 12)
        bold_opt   = "bold" if elemento.get("negrito", False) else "normal"
        self._entry_font = (fonte_nome, fonte_tam, bold_opt)

        self._entry = tk.Entry(canvas,
                               font=self._entry_font,
                               bg="#1A2A4A",
                               fg=elemento.get("cor_texto", BRANCO),
                               insertbackground=AMARELO,
                               relief="flat", bd=2,
                               highlightthickness=1,
                               highlightcolor=AMARELO,
                               highlightbackground=AZUL_MEDIO,
                               width=30)
        if elemento.get("label"):
            self._entry.insert(0, elemento["label"])
            self._entry.select_range(0, tk.END)

        # Janela do Entry sobre o canvas
        self._entry_id = canvas.create_window(
            tx, ty, window=self._entry, anchor="nw")

        self._entry.focus_set()
        self._entry.bind("<KeyRelease>",  self._ao_digitar)
        self._entry.bind("<Return>",      self._confirmar)
        self._entry.bind("<KP_Enter>",    self._confirmar)
        self._entry.bind("<Escape>",      self._cancelar)
        self._entry.bind("<FocusOut>",    self._ao_perder_foco)

        # ── Painel flutuante de formatação ──
        self._painel = tk.Toplevel(janela)
        self._painel.overrideredirect(True)
        self._painel.attributes("-topmost", True)
        self._painel.configure(bg=COR_PAINEL)
        self._painel_build()

        # Posiciona o painel acima do Entry
        canvas.update_idletasks()
        px = canvas.winfo_rootx() + tx
        py = canvas.winfo_rooty() + ty - 90
        if py < 0: py = canvas.winfo_rooty() + ty + 30
        self._painel.geometry(f"420x80+{int(px)}+{int(py)}")

    def _painel_build(self):
        p = self._painel
        for w in p.winfo_children(): w.destroy()

        tk.Frame(p, bg=AMARELO, height=2).pack(fill="x")
        corpo = tk.Frame(p, bg=COR_PAINEL)
        corpo.pack(fill="both", expand=True, padx=6, pady=4)

        # ── Fonte ──
        tk.Label(corpo, text="Fonte", font=FONTE_PEQ,
                 bg=COR_PAINEL, fg=CINZA_CLARO).grid(row=0, column=0, padx=(0,2))

        self._var_fonte = tk.StringVar(value=self.el.get("fonte","Segoe UI"))
        cb_fonte = ttk.Combobox(corpo, textvariable=self._var_fonte,
                                values=FONTES_DISPONIVEIS,
                                width=14, state="readonly",
                                font=FONTE_PEQ)
        cb_fonte.grid(row=0, column=1, padx=2)
        cb_fonte.bind("<<ComboboxSelected>>", self._aplicar_formato)

        # ── Tamanho ──
        tk.Label(corpo, text="Tam", font=FONTE_PEQ,
                 bg=COR_PAINEL, fg=CINZA_CLARO).grid(row=0, column=2, padx=(6,2))

        self._var_tam = tk.IntVar(value=self.el.get("tamanho", 12))
        spin = tk.Spinbox(corpo, textvariable=self._var_tam,
                          from_=6, to=72, width=4,
                          font=FONTE_PEQ,
                          bg=COR_CARD, fg=BRANCO,
                          buttonbackground=COR_CARD,
                          relief="flat",
                          command=self._aplicar_formato)
        spin.grid(row=0, column=3, padx=2)
        spin.bind("<KeyRelease>", self._aplicar_formato)

        # ── Cor ──
        tk.Label(corpo, text="Cor", font=FONTE_PEQ,
                 bg=COR_PAINEL, fg=CINZA_CLARO).grid(row=0, column=4, padx=(6,2))

        CORES_TEXTO = [BRANCO, AMARELO, COR_R1, AZUL_CLARO,
                       COR_SUCESSO, "#FF8800", "#FF00FF", PRETO_SOFT]
        self._var_cor = tk.StringVar(value=self.el.get("cor_texto", BRANCO))

        frame_cores = tk.Frame(corpo, bg=COR_PAINEL)
        frame_cores.grid(row=0, column=5, padx=2)
        for cor in CORES_TEXTO:
            b = tk.Button(frame_cores, bg=cor, width=1, height=1,
                          relief="solid", bd=1, cursor="hand2",
                          command=lambda c=cor: self._set_cor(c))
            b.pack(side="left", padx=1)

        # ── Negrito / Itálico ──
        self._var_bold = tk.BooleanVar(value=self.el.get("negrito", False))
        self._var_ital = tk.BooleanVar(value=self.el.get("italico", False))

        tk.Checkbutton(corpo, text="B", font=("Segoe UI",10,"bold"),
                       variable=self._var_bold,
                       bg=COR_PAINEL, fg=BRANCO,
                       selectcolor=AZUL_MEDIO,
                       activebackground=COR_PAINEL,
                       relief="flat",
                       command=self._aplicar_formato).grid(row=0, column=6, padx=2)

        tk.Checkbutton(corpo, text="i", font=("Segoe UI",10,"italic"),
                       variable=self._var_ital,
                       bg=COR_PAINEL, fg=BRANCO,
                       selectcolor=AZUL_MEDIO,
                       activebackground=COR_PAINEL,
                       relief="flat",
                       command=self._aplicar_formato).grid(row=0, column=7, padx=2)

        # ── OK / Cancelar ──
        tk.Button(corpo, text="✓", font=("Segoe UI",10,"bold"),
                  bg=COR_SUCESSO, fg=PRETO_SOFT,
                  relief="flat", cursor="hand2", padx=4,
                  command=self._confirmar).grid(row=0, column=8, padx=(8,2))
        tk.Button(corpo, text="✕", font=("Segoe UI",10),
                  bg=COR_PERIGO, fg=BRANCO,
                  relief="flat", cursor="hand2", padx=4,
                  command=self._cancelar).grid(row=0, column=9, padx=2)

        tk.Frame(p, bg=AMARELO, height=2).pack(fill="x", side="bottom")

    def _ao_digitar(self, event=None):
        self.el["label"] = self._entry.get()
        self._redesenhar()

    def _set_cor(self, cor):
        self._var_cor.set(cor)
        self.el["cor_texto"] = cor
        self._entry.config(fg=cor)
        self._redesenhar()

    def _aplicar_formato(self, event=None):
        self.el["fonte"]    = self._var_fonte.get()
        self.el["negrito"]  = self._var_bold.get()
        self.el["italico"]  = self._var_ital.get()
        try:
            self.el["tamanho"] = max(6, min(72, int(self._var_tam.get())))
        except Exception:
            pass
        # Atualiza a fonte do Entry inline
        bold_opt = "bold" if self.el["negrito"] else "normal"
        ital_opt = "italic" if self.el["italico"] else ""
        spec = (self.el["fonte"], self.el["tamanho"],
                (bold_opt+" "+ital_opt).strip() or "normal")
        self._entry.config(font=spec)
        self._redesenhar()

    def _confirmar(self, event=None):
        if not self._ativo: return
        self._ativo = False
        self.el["label"] = self._entry.get()
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
        # Só confirma se o painel não recebeu o foco
        if self._ativo:
            self.janela.after(150, self._verificar_foco)

    def _verificar_foco(self):
        if not self._ativo: return
        try:
            foco = self.janela.focus_get()
            # Se o foco foi para o painel ou filhos, não fecha
            if self._painel.winfo_exists():
                pw = str(self._painel)
                if foco and str(foco).startswith(pw):
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


# ─────────────────────────────────────────────
#  JANELA PRINCIPAL
# ─────────────────────────────────────────────
