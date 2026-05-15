from pathlib import Path
import re
src = (Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")
out=[]
def P(s=""): out.append(str(s))

P("="*60)
P("BUSCA AMPLA DO CIRCULO DE SELECAO")
P("="*60)

# Todos os create_oval do arquivo
P("\n1. TODOS os create_oval:")
for m in re.finditer(r'create_oval\([^\n]{0,140}', src):
    linha=src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0)}")

# Procura por 'raio' / 'rsel' / 'r_sel' / area selecionavel
P("\n2. Referencias a raio de selecao:")
for kw in ["raio_sel","r_sel","rsel","raio_clique","_raio","RAIO_SEL","sel_raio"]:
    for m in re.finditer(re.escape(kw), src):
        linha=src[:m.start()].count("\n")+1
        ctx=src[max(0,m.start()-40):m.start()+60].replace("\n"," ")
        P(f"  L{linha} [{kw}]: ...{ctx}...")

# Como _selecionar acha o elemento (raio de toque)
P("\n3. _selecionar (EditorCroqui real):")
# Acha todas as defs _selecionar
for m in re.finditer(r"    def _selecionar\(self[^)]*\):", src):
    linha=src[:m.start()].count("\n")+1
    P(f"  Encontrado L{linha}: {m.group(0)}")
# Pega a que esta dentro de EditorCroqui (apos linha 652)
ms = list(re.finditer(r"    def _selecionar\(self[^)]*\):.*?(?=\n    def )", src, re.DOTALL))
for mm in ms:
    linha=src[:mm.start()].count("\n")+1
    if linha > 600:  # dentro do EditorCroqui
        P(f"\n  --- _selecionar L{linha} (corpo) ---")
        for i,l in enumerate(mm.group(0).split("\n")[:30]):
            P(f"  {i:3}: {l}")
        break

# Procura desenho condicional a 'sel' que faca circulo/oval/arco
P("\n4. Trechos com 'sel' que desenham algo circular:")
for m in re.finditer(r'if sel.*?(?=\n            return|\n        #|\n    def )', src, re.DOTALL):
    if 'oval' in m.group(0) or 'arc' in m.group(0):
        linha=src[:m.start()].count("\n")+1
        P(f"  --- L{linha} ---")
        for l in m.group(0).split("\n")[:15]:
            P(f"    {l}")

Path("diag_circulo2.txt").write_text("\n".join(out),encoding="utf-8")
print("OK - diag_circulo2.txt")
