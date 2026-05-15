"""
fase1_aplicar_tema.py — Aplica o novo tema visual no editor de croqui
SEM alterar funcionalidade — apenas troca cores e fontes.
Execute: python fase1_aplicar_tema.py
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
if not editor_path.exists():
    print("ERRO: ui/editor_croqui.py nao encontrado")
    raise SystemExit

src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: garante que importa do tema.py
# ══════════════════════════════════════════════
old_import = "from config import ("
new_import = (
    "# Imports do novo tema visual\n"
    "from tema import (\n"
    "    FUNDO_BASE, FUNDO_PAINEL, FUNDO_CARD, FUNDO_HOVER, FUNDO_ATIVO,\n"
    "    DOURADO, AZUL_BORDA, AZUL_MEDIO,\n"
    "    TEXTO_PRIMARIO, TEXTO_SECUNDARIO, TEXTO_TERCIARIO,\n"
    "    FONTE_BODY, FONTE_BODY_BOLD, FONTE_SMALL, FONTE_SMALL_BOLD,\n"
    "    FONTE_H2, FONTE_H3, FONTE_MICRO,\n"
    ")\n"
    "from config import ("
)

if old_import in src and "from tema import" not in src:
    src = src.replace(old_import, new_import, 1)
    print("PATCH 1 OK — imports do tema adicionados")
else:
    print("PATCH 1 SKIP — tema ja importado")

# ══════════════════════════════════════════════
# PATCH 2: substitui cores antigas pelos aliases novos do tema
# COR_FUNDO -> FUNDO_BASE, COR_PAINEL -> FUNDO_PAINEL etc.
# Como config.py ja tem aliases que apontam para tema.py, isso so funciona
# se config.py estiver atualizado. Vamos garantir isso.
# ══════════════════════════════════════════════

# Garante que config.py importa de tema.py
config_path = Path("config.py")
config = config_path.read_text(encoding="utf-8")

if "from tema import" not in config:
    # Adiciona imports do tema no inicio do config.py
    config_novo = (
        "# Importa cores e fontes do tema centralizado\n"
        "try:\n"
        "    from tema import (\n"
        "        FUNDO_BASE, FUNDO_PAINEL, FUNDO_CARD, FUNDO_HOVER,\n"
        "        DOURADO, DOURADO_CLARO, AZUL_BORDA, AZUL_MEDIO, AZUL_CLARO,\n"
        "        TEXTO_PRIMARIO, TEXTO_SECUNDARIO, TEXTO_TERCIARIO,\n"
        "    )\n"
        "    # Substitui aliases antigos pelos novos\n"
        "    AZUL_ESCURO   = FUNDO_PAINEL\n"
        "    BRANCO        = TEXTO_PRIMARIO\n"
        "    CINZA_CLARO   = TEXTO_SECUNDARIO\n"
        "    CINZA_MEDIO   = TEXTO_TERCIARIO\n"
        "    PRETO_SOFT    = FUNDO_BASE\n"
        "    AMARELO       = DOURADO\n"
        "    COR_FUNDO     = FUNDO_BASE\n"
        "    COR_PAINEL    = FUNDO_PAINEL\n"
        "    COR_CARD      = FUNDO_CARD\n"
        "    COR_BORDA     = AZUL_BORDA\n"
        "    COR_TEXTO     = TEXTO_PRIMARIO\n"
        "    COR_TEXTO_SEC = TEXTO_SECUNDARIO\n"
        "    _TEMA_OK = True\n"
        "except ImportError:\n"
        "    _TEMA_OK = False\n"
        "\n"
        + config
    )
    config_path.write_text(config_novo, encoding="utf-8")
    print("PATCH 2 OK — config.py agora importa do tema")
else:
    print("PATCH 2 SKIP — config ja importa do tema")

# ══════════════════════════════════════════════
# PATCH 3: ajusta o EditorCroqui para usar cores mais consistentes
# Procura por valores hardcoded no editor que deveriam usar variaveis
# ══════════════════════════════════════════════
trocas = [
    # Substituicoes de cores hardcoded antigas pelas novas variaveis
    ('"#0E1932"', "FUNDO_PAINEL"),
    ('"#0F1830"', "FUNDO_PAINEL"),
    ('"#15265A"', "FUNDO_CARD"),
    ('"#162a5a"', "FUNDO_CARD"),
    ('"#1E3460"', "FUNDO_HOVER"),
    ('"#152244"', "FUNDO_CARD"),
    ('"#A0A8C0"', "TEXTO_SECUNDARIO"),
    ('"#8890B0"', "TEXTO_TERCIARIO"),
]

n_trocas = 0
for antigo, novo in trocas:
    if antigo in src:
        count = src.count(antigo)
        src = src.replace(antigo, novo)
        n_trocas += count

print(f"PATCH 3 OK — {n_trocas} cores hardcoded substituidas")

# ══════════════════════════════════════════════
# Salva e valida
# ══════════════════════════════════════════════
editor_path.write_text(src, encoding="utf-8")

try:
    ast.parse(src)
    print("Sintaxe editor_croqui.py OK")
except SyntaxError as e:
    print(f"ERRO SINTAXE: linha {e.lineno}: {e.msg}")
    print("Revertendo...")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

try:
    ast.parse(config_path.read_text(encoding="utf-8"))
    print("Sintaxe config.py OK")
except SyntaxError as e:
    print(f"ERRO config.py: {e}")

print("\nRode: python main.py")
print("Teste: criar um novo croqui e verificar se as cores ficaram coerentes")
