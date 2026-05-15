"""
criar_popup_placas.py — Cria popups/popup_placas.py
Execute com: python criar_popup_placas.py
"""
from pathlib import Path

linhas = [
    "import tkinter as tk\n",
    "from tkinter import simpledialog\n",
    "import math\n",
    "import sys\n",
    "from pathlib import Path\n",
    "_raiz = Path(__file__).parent.parent\n",
    "if str(_raiz) not in sys.path:\n",
    "    sys.path.insert(0, str(_raiz))\n",
    "from config import (\n",
    "    COR_FUNDO, COR_PAINEL, COR_CARD, AMARELO, BRANCO,\n",
    "    CINZA_CLARO, MODELOS_PLACA,\n",
    ")\n",
    "\n",
    "\n",
    "class PopupPlacas(tk.Toplevel):\n",
    "    def __init__(self, parent):\n",
    "        super().__init__(parent)\n",
    "        self.title('Escolha a placa')\n",
    "        self.configure(bg=COR_FUNDO)\n",
    "        self.resizable(False, False)\n",
    "        self.resultado = None\n",
    "        self.lift(); self.focus_force(); self.grab_set()\n",
    "        n = len(MODELOS_PLACA)\n",
    "        cols = 3; rows = (n + cols - 1) // cols\n",
    "        cw, ch = 130, 120\n",
    "        pad = 10\n",
    "        w = cols*cw + (cols+1)*pad\n",
    "        h = rows*ch + (rows+1)*pad + 80\n",
    "        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()\n",
    "        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')\n",
    "        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x')\n",
    "        tk.Label(self, text='Escolha o modelo de placa',\n",
    "                 font=('Segoe UI',11,'bold'),\n",
    "                 bg=COR_FUNDO, fg=AMARELO).pack(pady=(10,6))\n",
    "        grid = tk.Frame(self, bg=COR_FUNDO)\n",
    "        grid.pack(padx=pad, pady=4)\n",
    "        for idx, m in enumerate(MODELOS_PLACA):\n",
    "            row, col = idx//cols, idx%cols\n",
    "            self._card(grid, m, row, col, cw, ch)\n",
    "        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x', side='bottom')\n",
    "\n",
    "    def _card(self, parent, m, row, col, cw, ch):\n",
    "        card = tk.Frame(parent, bg=COR_CARD, cursor='hand2', width=cw, height=ch)\n",
    "        card.grid(row=row, column=col, padx=6, pady=6)\n",
    "        card.grid_propagate(False)\n",
    "        prev = tk.Canvas(card, width=cw-16, height=70,\n",
    "                         bg='#0D1830', highlightthickness=0)\n",
    "        prev.pack(padx=8, pady=(8,2))\n",
    "        self._preview(prev, m, (cw-16)//2, 35)\n",
    "        tk.Label(card, text=m['desc'], font=('Segoe UI',8),\n",
    "                 bg=COR_CARD, fg=CINZA_CLARO, wraplength=cw-16).pack()\n",
    "        def sel(modelo=m):\n",
    "            if modelo['chave'] == 'custom':\n",
    "                txt = simpledialog.askstring(\n",
    "                    'Placa personalizada', 'Texto da placa:',\n",
    "                    parent=self.master) or '?'\n",
    "                modelo = dict(modelo); modelo['label'] = txt\n",
    "            self.resultado = modelo\n",
    "            self.destroy()\n",
    "        for w in [card, prev] + list(card.winfo_children()):\n",
    "            w.bind('<Button-1>', lambda e, m=m: sel(m))\n",
    "        card.bind('<Enter>', lambda e, f=card: f.config(bg='#2A3060'))\n",
    "        card.bind('<Leave>', lambda e, f=card: f.config(bg=COR_CARD))\n",
    "\n",
    "    def _preview(self, c, m, cx, cy):\n",
    "        r = 22\n",
    "        cor = m['cor']\n",
    "        label = m['label']\n",
    "        if m['chave'] == 'pare':\n",
    "            pts = []\n",
    "            for i in range(8):\n",
    "                ang = math.radians(i*45 + 22.5)\n",
    "                pts.extend([cx+math.cos(ang)*r, cy+math.sin(ang)*r])\n",
    "            c.create_polygon(pts, fill=cor, outline=BRANCO, width=2)\n",
    "            c.create_text(cx, cy, text='PARE', fill=BRANCO,\n",
    "                          font=('Segoe UI',9,'bold'))\n",
    "        elif m['chave'] in ('vel_30','vel_40','vel_60','vel_80'):\n",
    "            c.create_oval(cx-r,cy-r,cx+r,cy+r, fill=BRANCO, outline='#CC0000', width=3)\n",
    "            c.create_text(cx, cy, text=label, fill='#CC0000',\n",
    "                          font=('Segoe UI',11,'bold'))\n",
    "        elif m['chave'] == 'atencao':\n",
    "            pts = [cx,cy-r, cx+r*0.87,cy+r*0.5, cx-r*0.87,cy+r*0.5]\n",
    "            c.create_polygon(pts, fill='#CC8800', outline=BRANCO, width=2)\n",
    "            c.create_text(cx, cy+6, text='!', fill=BRANCO,\n",
    "                          font=('Segoe UI',14,'bold'))\n",
    "        elif m['chave'] == 'proib':\n",
    "            c.create_oval(cx-r,cy-r,cx+r,cy+r, fill=BRANCO, outline='#CC0000', width=3)\n",
    "            c.create_line(cx-r*.7,cy-r*.7,cx+r*.7,cy+r*.7, fill='#CC0000', width=4)\n",
    "        else:\n",
    "            c.create_rectangle(cx-r,cy-r,cx+r,cy+r, fill=cor, outline=BRANCO, width=2)\n",
    "            c.create_text(cx, cy, text=label, fill=BRANCO,\n",
    "                          font=('Segoe UI',12,'bold'))\n",
]

dest = Path("popups") / "popup_placas.py"
dest.write_text("".join(linhas), encoding="utf-8")
print(f"OK — {dest} criado com {len(linhas)} linhas")

import ast
code = dest.read_text(encoding="utf-8")
try:
    ast.parse(code)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO sintaxe: {e}")

print("PopupPlacas extraido com sucesso!")
print("Rode: python main.py")