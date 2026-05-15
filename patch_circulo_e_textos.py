"""
patch_circulo_e_textos.py
1. Remove TODOS os 4 circulos de selecao (handles ja indicam)
2. Corrige textos R1/R2 (tira vertical/horizontal)
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# Remove circulos via regex flexivel (qualquer indentacao)
# ══════════════════════════════════════════════

# Circulo 1+2: r1/r2/cota com pontos (L2392/2394) — dois ovals juntos
pat1 = re.compile(
    r'( *)if sel:\n'
    r' *r=10\*self\.zoom\n'
    r' *c\.create_oval\(ax1-r,ay1-r,ax1\+r,ay1\+r,\n'
    r' *outline=AMARELO,width=2,dash=\(4,3\)\)\n'
    r' *c\.create_oval\(ax2-r,ay2-r,ax2\+r,ay2\+r,\n'
    r' *outline=AMARELO,width=2,dash=\(4,3\)\)'
)
def rep1(m):
    ind = m.group(1)
    return f"{ind}if sel:\n{ind}    pass  # circulo removido — handles indicam selecao"
src, n1 = pat1.subn(rep1, src)
print(f"Circulo r1/r2/cota: {n1} removido(s)")

# Circulo 3: veiculo (L2476) — r=16
pat2 = re.compile(
    r'( *)if sel:\n'
    r' *r=16\*self\.zoom\n'
    r' *c\.create_oval\(tx-r,ty-r,tx\+r,ty\+r,\n'
    r' *outline=AMARELO,width=2,dash=\(4,3\)\)'
)
def rep2(m):
    ind = m.group(1)
    return f"{ind}if sel:\n{ind}    pass  # circulo removido — handles indicam selecao"
src, n2 = pat2.subn(rep2, src)
print(f"Circulo veiculo (r=16): {n2} removido(s)")

# Circulo 4: L3338 — r2=18, com possivel x2
pat3 = re.compile(
    r'( *)if sel:\n'
    r' *r2=18\*self\.zoom\n'
    r' *c\.create_oval\(tx-r2,ty-r2,tx\+r2,ty\+r2,\n'
    r' *outline=AMARELO,width=2,dash=\(4,3\)\)'
)
def rep3(m):
    ind = m.group(1)
    return f"{ind}if sel:\n{ind}    pass  # circulo removido"
src, n3 = pat3.subn(rep3, src)
print(f"Circulo r2=18: {n3} removido(s)")

# ══════════════════════════════════════════════
# Corrige textos R1/R2
# ══════════════════════════════════════════════
src2 = src.replace(
    '"Traçar eixo R1 (vertical)"',
    '"Traçar eixo R1"'
).replace(
    '"Traçar eixo R2 (horizontal)"',
    '"Traçar eixo R2"'
)
if src2 != src:
    src = src2
    print("Textos R1/R2 corrigidos")
else:
    print("Textos R1/R2: nao encontrados (ja corrigidos?)")

editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO linha {e.lineno}: {e.msg}")
    linhas=src.split("\n")
    for i in range(max(0,e.lineno-4),min(len(linhas),e.lineno+3)):
        print(f"  {i+1:4}: {linhas[i]}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print(f"\nTotal circulos removidos: {n1+n2+n3}")
print("Rode: python main.py")
