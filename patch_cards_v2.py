"""
patch_cards_v2.py — Corrige cards sumidos
Execute: python patch_cards_v2.py
"""
from pathlib import Path

tela_path = Path("ui") / "tela_inicial.py"
tela = tela_path.read_text(encoding="utf-8")

# Remove o pack_propagate(False) que colapsou o frame
old = (
    "        # Frame dos cards com altura máxima fixa\n"
    "        cf = tk.Frame(a, bg=FUNDO_BASE)\n"
    "        cf.pack(fill='x', padx=32)\n"
    "        cf.pack_propagate(False)\n"
)
new = (
    "        cf = tk.Frame(a, bg=FUNDO_BASE)\n"
    "        cf.pack(fill='x', padx=32)\n"
)

if old in tela:
    tela = tela.replace(old, new, 1)
    print("OK — pack_propagate removido")
else:
    print("Nao encontrado — verificando alternativa...")
    # Tenta remover só a linha do pack_propagate
    tela = tela.replace("        cf.pack_propagate(False)\n", "")
    print("OK — linha removida diretamente")

tela_path.write_text(tela, encoding="utf-8")

import ast
try:
    ast.parse(tela)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO: {e}")

print("Rode: python main.py")