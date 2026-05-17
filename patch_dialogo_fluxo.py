"""
patch_dialogo_fluxo.py
1. Moderniza DialogoDadosCaso (remove moldura Windows + tema)
2. Remove pergunta redundante: Manual->editor direto, Modelo->GridModelos direto
"""
from pathlib import Path
import ast, re

# ══════════════════════════════════════════════
# PARTE A: main.py — reescreve _novo sem PopupModeloVia
# ══════════════════════════════════════════════
main_path = Path("main.py")
main = main_path.read_text(encoding="utf-8")
main_orig = main

old_novo = '''    def _novo(self, modo):
        dlg = DialogoDadosCaso(self, modo=modo)
        self.wait_window(dlg)
        if not dlg.resultado:
            return

        img_drone = None
        if modo == "drone":
            if not PIL_OK:
                messagebox.showerror("Pillow", "pip install Pillow")
                return
            cam = filedialog.askopenfilename(
                title="Foto do drone (ja retificada)",
                filetypes=[("Imagens", "*.jpg *.jpeg *.png *.tif")])
            if not cam:
                return
            img_drone = Image.open(cam)

        popup = PopupModeloVia(self)
        self.wait_window(popup)
        res = popup.resultado or {"icone": "branco"}

        els = []
        if res.get("icone", "branco") != "branco":
            W = max(self.winfo_width(), 800)
            H = max(self.winfo_height(), 600)
            els = gerar_elementos_modelo(res["icone"], W, H)

        editor = EditorCroqui(self, dlg.resultado, modo=modo,
                              img_drone=img_drone, elementos_iniciais=els)
        self._trocar(editor)'''

new_novo = '''    def _novo(self, modo):
        # modo: "zero" (manual), "drone", "modelo"
        usar_modelo = (modo == "modelo")
        modo_editor = "drone" if modo == "drone" else "zero"

        dlg = DialogoDadosCaso(self, modo=modo_editor)
        self.wait_window(dlg)
        if not dlg.resultado:
            return

        img_drone = None
        if modo == "drone":
            if not PIL_OK:
                messagebox.showerror("Pillow", "pip install Pillow")
                return
            cam = filedialog.askopenfilename(
                title="Foto do drone (ja retificada)",
                filetypes=[("Imagens", "*.jpg *.jpeg *.png *.tif")])
            if not cam:
                return
            img_drone = Image.open(cam)

        els = []
        if usar_modelo:
            # Vai DIRETO para a grade de modelos (sem pergunta redundante)
            from popups.popup_modelo_via import GridModelos
            grid = GridModelos(self)
            self.wait_window(grid)
            if not grid.resultado:
                return
            icone = grid.resultado.get("icone", "branco")
            if icone != "branco":
                W = max(self.winfo_width(), 800)
                H = max(self.winfo_height(), 600)
                els = gerar_elementos_modelo(icone, W, H)

        editor = EditorCroqui(self, dlg.resultado, modo=modo_editor,
                              img_drone=img_drone, elementos_iniciais=els)
        self._trocar(editor)'''

if old_novo in main:
    main = main.replace(old_novo, new_novo, 1)
    main_path.write_text(main, encoding="utf-8")
    try:
        ast.parse(main)
        print("PARTE A OK — main.py _novo sem PopupModeloVia")
    except SyntaxError as e:
        print(f"PARTE A ERRO sintaxe: {e}")
        main_path.write_text(main_orig, encoding="utf-8")
        raise SystemExit
else:
    print("PARTE A ERRO — _novo nao bate")
    raise SystemExit

# ══════════════════════════════════════════════
# PARTE B: dialogo_caso.py — moderniza DialogoDadosCaso
# Remove moldura Windows, aplica tema novo
# ══════════════════════════════════════════════
dlg_path = Path("ui") / "dialogo_caso.py"
dlg = dlg_path.read_text(encoding="utf-8")
dlg_orig = dlg

# B1: importa tema
old_imp = '''from config import (
    COR_FUNDO, COR_PAINEL, COR_CARD, COR_BORDA,
    COR_TEXTO_SEC, AMARELO, BRANCO, CINZA_CLARO, CINZA_MEDIO,
    AZUL_MEDIO, AZUL_CLARO, PRETO_SOFT,
    FONTE_SUB, FONTE_NORMAL, FONTE_PEQ,
    MUNICIPIOS_AP,
)'''
new_imp = '''from config import (
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
)'''
if old_imp in dlg:
    dlg = dlg.replace(old_imp, new_imp, 1)
    print("PARTE B1 OK — tema importado")

# B2: reescreve __init__ do DialogoDadosCaso para sem moldura
old_init = '''    def __init__(self, parent, modo='zero'):
        super().__init__(parent)
        self.title('Dados do caso')
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)
        self.grab_set()
        self.resultado = None
        w, h = 480, 400
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x')
        corpo = tk.Frame(self, bg=COR_FUNDO)
        corpo.pack(fill='both', expand=True, padx=24, pady=16)
        titulo = 'Croqui do zero' if modo=='zero' else 'Croqui sobre drone'
        tk.Label(corpo, text=f'  {titulo}',
                 font=FONTE_SUB, bg=COR_FUNDO, fg=AMARELO).pack(anchor='w', pady=(0,12))'''

new_init = '''    def __init__(self, parent, modo='zero'):
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
                 font=FONTE_H2, bg=FUNDO_PAINEL, fg=DOURADO).pack(anchor='w', pady=(0,16))'''

if old_init in dlg:
    dlg = dlg.replace(old_init, new_init, 1)
    print("PARTE B2 OK — __init__ modernizado")
else:
    print("PARTE B2 ERRO — __init__ nao bate")
    main_path.write_text(main_orig, encoding="utf-8")
    raise SystemExit

# B3: atualiza cores dos campos e botoes
dlg = dlg.replace(
    "tk.Label(row, text=label, font=FONTE_PEQ, width=20,\n"
    "                     anchor='w', bg=COR_FUNDO, fg=COR_TEXTO_SEC).pack(side='left')",
    "tk.Label(row, text=label, font=FONTE_SMALL, width=18,\n"
    "                     anchor='w', bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO).pack(side='left')"
)
dlg = dlg.replace("row = tk.Frame(corpo, bg=COR_FUNDO)",
                  "row = tk.Frame(corpo, bg=FUNDO_PAINEL)")
dlg = dlg.replace(
    "e = tk.Entry(row, font=FONTE_NORMAL,\n"
    "                             bg=COR_CARD, fg=BRANCO,\n"
    "                             insertbackground=BRANCO, relief='flat', bd=4)",
    "e = tk.Entry(row, font=FONTE_BODY,\n"
    "                             bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,\n"
    "                             insertbackground=DOURADO, relief='flat', bd=5,\n"
    "                             highlightthickness=1, highlightcolor=DOURADO,\n"
    "                             highlightbackground=AZUL_BORDA)"
)
dlg = dlg.replace("tk.Frame(corpo, bg=COR_BORDA, height=1).pack(fill='x', pady=10)",
                  "tk.Frame(corpo, bg=AZUL_BORDA, height=1).pack(fill='x', pady=14)")
dlg = dlg.replace("btns = tk.Frame(corpo, bg=COR_FUNDO)",
                  "btns = tk.Frame(corpo, bg=FUNDO_PAINEL)")
dlg = dlg.replace(
    "tk.Button(btns, text='Cancelar', font=FONTE_NORMAL, cursor='hand2',\n"
    "                  bg=COR_CARD, fg=COR_TEXTO_SEC, activebackground=COR_BORDA,\n"
    "                  relief='flat', padx=14, pady=5,\n"
    "                  command=self.destroy).pack(side='right', padx=(6,0))",
    "tk.Button(btns, text='Cancelar', font=FONTE_SMALL, cursor='hand2',\n"
    "                  bg=FUNDO_CARD, fg=TEXTO_SECUNDARIO, activebackground=FUNDO_HOVER,\n"
    "                  relief='flat', padx=16, pady=6,\n"
    "                  command=self.destroy).pack(side='right', padx=(6,0))"
)
dlg = dlg.replace(
    "tk.Button(btns, text='Criar croqui ->',\n"
    "                  font=('Segoe UI',10,'bold'), cursor='hand2',\n"
    "                  bg=AZUL_MEDIO, fg=BRANCO, activebackground=AZUL_CLARO,\n"
    "                  relief='flat', padx=14, pady=5,\n"
    "                  command=self._ok).pack(side='right')",
    "tk.Button(btns, text='Criar croqui  →',\n"
    "                  font=FONTE_BODY_BOLD, cursor='hand2',\n"
    "                  bg=AZUL_MEDIO, fg=TEXTO_PRIMARIO, activebackground=AZUL_CLARO,\n"
    "                  relief='flat', padx=18, pady=6,\n"
    "                  command=self._ok).pack(side='right')"
)
dlg = dlg.replace(
    "tk.Frame(self, bg=AMARELO, height=4).pack(fill='x', side='bottom')",
    "tk.Frame(self, bg=DOURADO, height=3).pack(fill='x', side='bottom')"
)
print("PARTE B3 OK — cores dos campos atualizadas")

dlg_path.write_text(dlg, encoding="utf-8")
try:
    ast.parse(dlg)
    print("Sintaxe dialogo_caso.py OK")
except SyntaxError as e:
    print(f"ERRO dialogo_caso linha {e.lineno}: {e.msg}")
    dlg_path.write_text(dlg_orig, encoding="utf-8")
    main_path.write_text(main_orig, encoding="utf-8")
    print("TUDO REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste:")
print("  1. Novo Croqui Manual -> dialogo SEM moldura Windows -> Criar -> editor direto")
print("  2. Usar Modelo Pronto -> dialogo -> Criar -> grade de modelos direto")
print("  3. SEM a pergunta 'Como deseja iniciar'")
