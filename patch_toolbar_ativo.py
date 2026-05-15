"""
patch_toolbar_ativo.py — Corrige bug de todos botoes acenderem
O codigo antigo de _set_ferr ainda esta no arquivo, pintando todos os Frames.
Solucao: remover as linhas antigas que usam btn.config diretamente.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# Remove o codigo antigo de _set_ferr que pintava com btn.config
# Padrao antigo:
#   for k, btn in self.btns_ferr.items():
#       btn.config(bg=AZUL_MEDIO if k==c else COR_PAINEL)
old1 = re.compile(
    r'\n        for k, btn in self\.btns_ferr\.items\(\):\n'
    r'\s+btn\.config\(bg=AZUL_MEDIO if k==[a-z]+ else COR_PAINEL\)\n'
)
n1 = len(old1.findall(src))
src = old1.sub('\n', src)
print(f"PATCH 1: removeu {n1} blocos antigos de btns_ferr")

old2 = re.compile(
    r'\n        for k, btn in self\.btns_via\.items\(\):\n'
    r'\s+btn\.config\(bg=AZUL_MEDIO if k==[a-z]+ else COR_PAINEL\)\n'
)
n2 = len(old2.findall(src))
src = old2.sub('\n', src)
print(f"PATCH 2: removeu {n2} blocos antigos de btns_via")

# Remove tambem o reset que pintava todos com COR_PAINEL ao trocar modo
old3 = re.compile(
    r'\n            for btn in self\.btns_via\.values\(\):\n'
    r'\s+btn\.config\(bg=COR_PAINEL\)\n'
)
n3 = len(old3.findall(src))
src = old3.sub('\n', src)
print(f"PATCH 3: removeu {n3} reset de btns_via")

old4 = re.compile(
    r'\n            for btn in self\.btns_ferr\.values\(\):\n'
    r'\s+btn\.config\(bg=COR_PAINEL\)\n'
)
n4 = len(old4.findall(src))
src = old4.sub('\n', src)
print(f"PATCH 4: removeu {n4} reset de btns_ferr")

# Salva
editor_path.write_text(src, encoding="utf-8")

try:
    ast.parse(src)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO linha {e.lineno}: {e.msg}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("Revertido")
    raise SystemExit

print(f"\nTotal de blocos removidos: {n1+n2+n3+n4}")
print("Rode: python main.py")
