"""
patch_titlebar_v2.py — Corrige barra dupla
A TitleBar do main.py e o header da TelaInicial estavam se sobrepondo.
Solução: remove o _build_header da TelaInicial e deixa só a TitleBar.
Execute: python patch_titlebar_v2.py
"""
from pathlib import Path

# ══════════════════════════════════════════════
# PATCH 1: TelaInicial — remove _build_header()
# A barra de titulo agora é responsabilidade do main.py
# ══════════════════════════════════════════════
tela_path = Path("ui") / "tela_inicial.py"
tela = tela_path.read_text(encoding="utf-8")

# Remove a chamada ao _build_header no _build()
old_call = (
    "        tk.Frame(self, bg=DOURADO, height=ALTURA_BARRA_TOP).pack(fill='x')\n"
    "        self._build_header()\n"
)
new_call = (
    "        # Header gerenciado pela TitleBar do main.py\n"
)

if old_call in tela:
    tela = tela.replace(old_call, new_call, 1)
    print("PATCH 1 OK — _build_header removido da TelaInicial")
else:
    print("PATCH 1 SKIP — nao encontrado")

tela_path.write_text(tela, encoding="utf-8")

import ast
try:
    ast.parse(tela)
    print("Sintaxe tela_inicial.py OK")
except SyntaxError as e:
    print(f"ERRO: {e}")

# ══════════════════════════════════════════════
# PATCH 2: TitleBar no main.py — mostra data e PCI no centro
# Aproveita o espaço vazio do header agora que é único
# ══════════════════════════════════════════════
main_path = Path("main.py")
main = main_path.read_text(encoding="utf-8")

old_titlebar_center = (
    "        # Logo + titulo\n"
    "        esq = tk.Frame(bar, bg=FUNDO_PAINEL)\n"
    "        esq.pack(side=\"left\", padx=14, fill=\"y\")\n"
    "        tk.Label(esq, text=\"SICRO\", font=(\"Segoe UI\", 11, \"bold\"),\n"
    "                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side=\"left\")\n"
    "        tk.Label(esq, text=\"  Sistema de Croquis Periciais\",\n"
    "                 font=(\"Segoe UI\", 8),\n"
    "                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(side=\"left\")\n"
)
new_titlebar_center = (
    "        # Logo + titulo\n"
    "        esq = tk.Frame(bar, bg=FUNDO_PAINEL)\n"
    "        esq.pack(side=\"left\", padx=14, fill=\"y\")\n"
    "        tk.Label(esq, text=\"SICRO\", font=(\"Segoe UI\", 11, \"bold\"),\n"
    "                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side=\"left\")\n"
    "        tk.Label(esq, text=\"  Sistema de Croquis Periciais\",\n"
    "                 font=(\"Segoe UI\", 8),\n"
    "                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(side=\"left\")\n"
    "        # Data e instituicao no centro\n"
    "        import datetime\n"
    "        centro = tk.Frame(bar, bg=FUNDO_PAINEL)\n"
    "        centro.place(relx=0.5, rely=0.5, anchor='center')\n"
    "        tk.Label(centro,\n"
    "                 text=f'Policia Cientifica do Amapa  |  '\n"
    "                      f'{datetime.date.today().strftime(\"%d/%m/%Y\")}',\n"
    "                 font=(\"Segoe UI\", 8),\n"
    "                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack()\n"
)

if old_titlebar_center in main:
    main = main.replace(old_titlebar_center, new_titlebar_center, 1)
    main_path.write_text(main, encoding="utf-8")
    print("PATCH 2 OK — data/PCI adicionados na TitleBar")
    try:
        ast.parse(main)
        print("Sintaxe main.py OK")
    except SyntaxError as e:
        print(f"ERRO: {e}")
else:
    print("PATCH 2 SKIP — ja atualizado")

print("\nRode: python main.py")