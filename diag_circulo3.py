from pathlib import Path
import re
src = (Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")
out=[]
def P(s=""): out.append(str(s))

P("CIRCULOS dash=(4,3) ou pontilhados restantes:")
# Procura TODOS create_oval com dash e AMARELO/DOURADO
for m in re.finditer(r'c\.create_oval\([^)]*?(?:AMARELO|DOURADO)[^)]*?dash[^)]*?\)', src, re.DOTALL):
    linha=src[:m.start()].count("\n")+1
    P(f"\n--- L{linha} ---")
    ini=src.rfind("\n",0,m.start()-150)
    for l in src[ini:m.end()+30].split("\n"):
        P(f"  {l}")

# Tambem dash sem cor especifica
P("\n\nTODOS create_oval com dash:")
for m in re.finditer(r'create_oval\([^)]*?dash[^)]*?\)', src, re.DOTALL):
    linha=src[:m.start()].count("\n")+1
    txt=m.group(0).replace("\n"," ")[:120]
    P(f"  L{linha}: {txt}")

# FERRAMENTAS - textos R1 R2
P("\n\nFERRAMENTAS (textos R1/R2):")
m=re.search(r"FERRAMENTAS\s*=\s*\[.*?\]", src, re.DOTALL)
if m:
    for l in m.group(0).split("\n"):
        P(f"  {l}")

Path("diag_circulo3.txt").write_text("\n".join(out),encoding="utf-8")
print("OK")
