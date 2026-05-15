"""
patch_main_e_cards.py — Corrige barra Windows + cards esticados
Execute: python patch_main_e_cards.py
"""
from pathlib import Path

# ══════════════════════════════════════════════
# PATCH 1: main.py — remove barra de título Windows
# ══════════════════════════════════════════════
main_path = Path("main.py")
main = main_path.read_text(encoding="utf-8")

old_init = (
    "        self.withdraw()\n"
    "        self.title(\"SICRO PCI/AP — Policia Cientifica do Amapa\")\n"
    "        self.configure(bg=COR_FUNDO)\n"
    "        self.state(\"zoomed\")\n"
    "        ttk.Style(self).theme_use(\"clam\")\n"
)
new_init = (
    "        self.withdraw()\n"
    "        self.title(\"SICRO PCI/AP — Policia Cientifica do Amapa\")\n"
    "        self.configure(bg=COR_FUNDO)\n"
    "        self.state(\"zoomed\")\n"
    "        ttk.Style(self).theme_use(\"clam\")\n"
    "        # Remove barra de titulo padrao do Windows\n"
    "        self.overrideredirect(True)\n"
    "        # Restaura maximize/minimize via bind de teclado\n"
    "        self.bind('<Escape>', lambda e: self.state('normal'))\n"
)

if old_init in main:
    main = main.replace(old_init, new_init, 1)
    main_path.write_text(main, encoding="utf-8")
    print("PATCH 1 OK — barra Windows removida do main.py")
else:
    print("PATCH 1 SKIP — main.py ja atualizado ou diferente")

# ══════════════════════════════════════════════
# PATCH 2: ui/tela_inicial.py — limita altura dos cards
# ══════════════════════════════════════════════
tela_path = Path("ui") / "tela_inicial.py"
tela = tela_path.read_text(encoding="utf-8")

old_cf = (
    "        cf = tk.Frame(a, bg=FUNDO_BASE)\n"
    "        cf.pack(fill='x', padx=32)\n"
)
new_cf = (
    "        # Frame dos cards com altura máxima fixa\n"
    "        cf = tk.Frame(a, bg=FUNDO_BASE)\n"
    "        cf.pack(fill='x', padx=32)\n"
    "        cf.pack_propagate(False)\n"
)

old_card_pack = (
    "        card = tk.Frame(parent, bg=FUNDO_CARD, cursor='hand2')\n"
    "        card.pack(side='left', fill='both', expand=True, padx=(0,12))\n"
    "        # Imagem de fundo — usa Canvas para controlar altura\n"
    "        img_canvas = tk.Canvas(card, height=IMG_H, bg=FUNDO_CARD,\n"
    "                              highlightthickness=0)\n"
    "        img_canvas.pack(fill='x')\n"
)
new_card_pack = (
    "        card = tk.Frame(parent, bg=FUNDO_CARD, cursor='hand2')\n"
    "        card.pack(side='left', fill='x', expand=True, padx=(0,12))\n"
    "        # Imagem de fundo — Canvas com altura fixa\n"
    "        img_canvas = tk.Canvas(card, height=IMG_H, bg=FUNDO_CARD,\n"
    "                              highlightthickness=0)\n"
    "        img_canvas.pack(fill='x')\n"
)

changed = False
if old_cf in tela:
    tela = tela.replace(old_cf, new_cf, 1)
    changed = True
    print("PATCH 2a OK — cf pack_propagate")

if old_card_pack in tela:
    tela = tela.replace(old_card_pack, new_card_pack, 1)
    changed = True
    print("PATCH 2b OK — card fill='x'")

if changed:
    tela_path.write_text(tela, encoding="utf-8")
else:
    print("PATCH 2 SKIP — nada encontrado")

import ast
try:
    ast.parse(tela_path.read_text(encoding="utf-8"))
    print("Sintaxe tela_inicial.py OK")
except SyntaxError as e:
    print(f"ERRO: {e}")

print("\nRode: python main.py")