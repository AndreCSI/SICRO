"""
criar_popup_veiculo.py — Cria popups/popup_veiculo.py
Execute com: python criar_popup_veiculo.py
"""
from pathlib import Path

linhas = [
    "import tkinter as tk\n",
    "import sys\n",
    "from pathlib import Path\n",
    "_raiz = Path(__file__).parent.parent\n",
    "if str(_raiz) not in sys.path:\n",
    "    sys.path.insert(0, str(_raiz))\n",
    "from config import (\n",
    "    COR_FUNDO, COR_PAINEL, COR_CARD, AMARELO, BRANCO, CINZA_CLARO,\n",
    "    FONTE_SUB, FONTE_PEQ, AZUL_CLARO, COR_PERIGO,\n",
    ")\n",
    "from desenho.veiculos_arte import (\n",
    "    arte_sedan, arte_suv, arte_hatch,\n",
    "    arte_moto_esportiva, arte_moto_urbana, arte_moto_carga,\n",
    "    arte_caminhao_leve, arte_caminhao_truck, arte_caminhao_carreta,\n",
    ")\n",
    "\n",
    "\n",
    "# Catalogo de modelos de veiculos\n",
    "MODELOS_VEICULOS = {\n",
    "    'carro': [\n",
    "        {'chave':'sedan',  'nome':'Sedan',       'desc':'4 portas',        'arte':arte_sedan,          'png':'sedan.png', 'larg':28,'alt':14,'cor':AZUL_CLARO},\n",
    "        {'chave':'suv',    'nome':'SUV / Picape', 'desc':'4x4, utilitario', 'arte':arte_suv,            'png':'suv.png',   'larg':30,'alt':16,'cor':'#3A8A3A'},\n",
    "        {'chave':'hatch',  'nome':'Hatchback',    'desc':'Compacto',        'arte':arte_hatch,          'png':'hatch.png', 'larg':24,'alt':13,'cor':'#A04040'},\n",
    "    ],\n",
    "    'moto': [\n",
    "        {'chave':'esportiva','nome':'Esportiva',      'desc':'Moto baixa',    'arte':arte_moto_esportiva,'larg':20,'alt':7,'cor':'#9B3030'},\n",
    "        {'chave':'urbana',   'nome':'Urbana / Naked', 'desc':'Guidad alto',   'arte':arte_moto_urbana,  'larg':18,'alt':8,'cor':'#9B6BDF'},\n",
    "        {'chave':'carga',    'nome':'Motoboy / Carga','desc':'Com bau',       'arte':arte_moto_carga,   'larg':22,'alt':9,'cor':'#3A6A3A'},\n",
    "    ],\n",
    "    'caminhao': [\n",
    "        {'chave':'leve',   'nome':'Caminhao leve', 'desc':'VUC / 3/4',           'arte':arte_caminhao_leve,   'larg':36,'alt':16,'cor':COR_PERIGO},\n",
    "        {'chave':'truck',  'nome':'Caminhao truck','desc':'Toco / truck',         'arte':arte_caminhao_truck,  'larg':48,'alt':18,'cor':'#C06020'},\n",
    "        {'chave':'carreta','nome':'Carreta',        'desc':'Bitrem / semirreboque','arte':arte_caminhao_carreta,'larg':56,'alt':17,'cor':'#606060'},\n",
    "    ],\n",
    "}\n",
    "\n",
    "\n",
    "class PopupModeloVeiculo(tk.Toplevel):\n",
    "    def __init__(self, parent, tipo_base):\n",
    "        super().__init__(parent)\n",
    "        self.title(f'Escolha o modelo - {tipo_base.capitalize()}')\n",
    "        self.configure(bg=COR_FUNDO)\n",
    "        self.resizable(False, False)\n",
    "        self.resultado = None\n",
    "        modelos = MODELOS_VEICULOS.get(tipo_base, [])\n",
    "        n = len(modelos)\n",
    "        card_w, card_h = 210, 175\n",
    "        pad = 12\n",
    "        w = n * card_w + (n + 1) * pad\n",
    "        h = 310\n",
    "        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()\n",
    "        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')\n",
    "        self.lift()\n",
    "        self.focus_force()\n",
    "        self.grab_set()\n",
    "        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x')\n",
    "        cab = tk.Frame(self, bg=COR_PAINEL)\n",
    "        cab.pack(fill='x')\n",
    "        icone_cat = {'carro':'🚗','moto':'🏍','caminhao':'🚚'}.get(tipo_base,'🚗')\n",
    "        tk.Label(cab, text=f'{icone_cat}  Escolha o modelo de {tipo_base}',\n",
    "                 font=FONTE_SUB, bg=COR_PAINEL, fg=AMARELO).pack(\n",
    "                     side='left', padx=16, pady=10)\n",
    "        grid_frame = tk.Frame(self, bg=COR_FUNDO)\n",
    "        grid_frame.pack(fill='both', expand=True, padx=pad, pady=pad)\n",
    "        for col, modelo in enumerate(modelos):\n",
    "            self._card(grid_frame, modelo, col, card_w, card_h)\n",
    "        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x', side='bottom')\n",
    "\n",
    "    def _card(self, parent, modelo, col, cw, ch):\n",
    "        card = tk.Frame(parent, bg=COR_CARD, cursor='hand2', width=cw, height=ch)\n",
    "        card.grid(row=0, column=col, padx=8, pady=4, sticky='nsew')\n",
    "        card.grid_propagate(False)\n",
    "        parent.grid_columnconfigure(col, weight=1)\n",
    "        prev = tk.Canvas(card, width=cw-16, height=105, bg='#0D1830', highlightthickness=0)\n",
    "        prev.pack(padx=8, pady=(10,4))\n",
    "        self._desenhar_preview(prev, modelo, cw-16, 105)\n",
    "        lbl_nome = tk.Label(card, text=modelo['nome'],\n",
    "                            font=('Segoe UI',10,'bold'), bg=COR_CARD, fg=BRANCO)\n",
    "        lbl_nome.pack()\n",
    "        lbl_desc = tk.Label(card, text=modelo['desc'],\n",
    "                            font=FONTE_PEQ, bg=COR_CARD, fg=CINZA_CLARO)\n",
    "        lbl_desc.pack()\n",
    "        def sel(m=modelo):\n",
    "            self.resultado = m\n",
    "            self.destroy()\n",
    "        def hover_in(e, f=card):\n",
    "            f.config(bg='#2A3060')\n",
    "            for w in f.winfo_children():\n",
    "                try: w.config(bg='#2A3060')\n",
    "                except Exception: pass\n",
    "        def hover_out(e, f=card):\n",
    "            f.config(bg=COR_CARD)\n",
    "            for w in f.winfo_children():\n",
    "                try: w.config(bg=COR_CARD)\n",
    "                except Exception: pass\n",
    "        for widget in [card, prev, lbl_nome, lbl_desc]:\n",
    "            widget.bind('<Button-1>', lambda e, m=modelo: sel(m))\n",
    "        card.bind('<Enter>', hover_in)\n",
    "        card.bind('<Leave>', hover_out)\n",
    "\n",
    "    def _desenhar_preview(self, c, modelo, pw, ph):\n",
    "        cx, cy = pw // 2, ph // 2\n",
    "        larg_ref = modelo['larg']\n",
    "        sc = min((pw - 24) / (larg_ref * 2.2), 1.6)\n",
    "        sc = max(sc, 0.5)\n",
    "        modelo['arte'](c, cx, cy, sc, modelo['cor'])\n",
]

dest = Path("popups") / "popup_veiculo.py"
dest.write_text("".join(linhas), encoding="utf-8")
print(f"OK — {dest} criado com {len(linhas)} linhas")

# Verifica sintaxe
import ast
code = dest.read_text(encoding="utf-8")
try:
    ast.parse(code)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO sintaxe: {e}")

# Verifica imports (sem tkinter display)
import importlib.util
spec = importlib.util.spec_from_file_location("popup_veiculo", dest)
mod  = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    print(f"MODELOS_VEICULOS: {list(mod.MODELOS_VEICULOS.keys())}")
    print(f"PopupModeloVeiculo: {'OK' if hasattr(mod,'PopupModeloVeiculo') else 'FALTANDO'}")
except Exception as e:
    # tkinter pode falhar sem display — verifica só a sintaxe
    if "display" in str(e).lower() or "TclError" in str(e):
        print("Import OK (sem display grafico no teste)")
    else:
        print(f"ERRO import: {e}")

print("Rode: python main.py")