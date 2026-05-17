from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))
src=(Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("Desenho de R1/R2 (eixos) — trecho exato")
P("="*60)
m=re.search(r'if tipo in \("r1","r2"\):.*?(?=\n        # ──|\n        if tipo|\n        elif tipo|\n    def )', src, re.DOTALL)
if not m:
    m=re.search(r'tipo==?"r1".*?(?=\n        # ──|\n        if tipo|\n        elif tipo|\n    def )', src, re.DOTALL)
if m:
    linha=src[:m.start()].count("\n")+1
    P(f"  (inicia L{linha})")
    for i,l in enumerate(m.group(0).split("\n")[:30]):
        P(f"  {i:3}: {l}")
else:
    P("  padrao r1/r2 nao casou — busca ampla:")
    for mm in re.finditer(r'cor_eixo|COR_R1|COR_R2|nome_eixo', src):
        ln=src[:mm.start()].count("\n")+1
        P(f"  L{ln}: {src[mm.start():mm.start()+90].splitlines()[0]}")

P("\n"+"="*60)
P("Desenho de COTA — trecho exato")
P("="*60)
m=re.search(r'tipo==?"cota":.*?(?=\n        # ──|\n        if tipo|\n        elif tipo|\n    def )', src, re.DOTALL)
if m:
    linha=src[:m.start()].count("\n")+1
    P(f"  (inicia L{linha})")
    for i,l in enumerate(m.group(0).split("\n")[:15]):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("COR_R1/COR_R2/COR_COTA importados no editor?")
P("="*60)
for c in ["COR_R1","COR_R2","COR_COTA"]:
    for m in re.finditer(re.escape(c), src):
        ln=src[:m.start()].count("\n")+1
        P(f"  L{ln}: {src[m.start():m.start()+70].splitlines()[0]}")
        break

Path("diag_desenho_linha.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_desenho_linha.txt")
