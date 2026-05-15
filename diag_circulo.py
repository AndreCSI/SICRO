from pathlib import Path
import re
src = (Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")
out=[]
def P(s=""): out.append(str(s))
P("Procurando circulo amarelo de selecao...")
# Procura create_oval com dash e AMARELO/DOURADO perto de 'sel'
for m in re.finditer(r'c\.create_oval\([^\n]*dash[^\n]*\)', src):
    linha=src[:m.start()].count("\n")+1
    P(f"L{linha}: {m.group(0)[:120]}")
P("")
P("Contexto de cada um (5 linhas antes):")
for m in re.finditer(r'c\.create_oval\([^\n]*dash[^\n]*\)', src):
    linha=src[:m.start()].count("\n")+1
    ini=src.rfind("\n",0,m.start()-200)
    P(f"--- L{linha} ---")
    for l in src[ini:m.end()+50].split("\n"):
        P(f"  {l}")
    P("")
Path("diag_circulo.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_circulo.txt")
