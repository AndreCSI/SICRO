from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

src = (Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("1. _salvar — o que o .sicro guarda hoje")
P("="*60)
m=re.search(r"    def _salvar\(self\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("2. _exportar_pdf — geracao atual do PDF")
P("="*60)
m=re.search(r"    def _exportar_pdf\(self\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")
else:
    P("  _exportar_pdf NAO encontrado, procurando variantes...")
    for mm in re.finditer(r"    def (_?\w*pdf\w*|_?\w*export\w*)\(self", src):
        linha=src[:mm.start()].count("\n")+1
        P(f"  L{linha}: {mm.group(0)}")

P("\n"+"="*60)
P("3. dados_caso — estrutura (o que tem em metadata)")
P("="*60)
for kw in ["self.dados_caso","dados_caso.get","dados_caso\\[","self.modo","self.k","self.calibrado","self.elementos","img_drone","self.u_k"]:
    for m in re.finditer(kw, src):
        linha=src[:m.start()].count("\n")+1
        ctx=src[m.start():m.start()+90].split("\n")[0]
        P(f"  L{linha}: {ctx}")
        break

P("\n"+"="*60)
P("4. Onde guarda elementos no JSON do .sicro")
P("="*60)
for m in re.finditer(r'(json\.dump|"elementos"|"modo"|"k"|"calibrado"|"u_k"|"norte"|"escala")', src):
    linha=src[:m.start()].count("\n")+1
    ctx=src[max(0,m.start()-40):m.start()+100].replace("\n"," | ")
    P(f"  L{linha}: ...{ctx}...")

# arquivo/salvar.py existe?
P("\n"+"="*60)
P("5. arquivo/salvar.py")
P("="*60)
sp=Path("arquivo/salvar.py")
if sp.exists():
    s2=sp.read_text(encoding="utf-8")
    P(f"  {len(s2.splitlines())} linhas")
    for i,l in enumerate(s2.split("\n")[:80]):
        P(f"  {i+1:3}: {l}")
else:
    P("  NAO existe")

Path("diag_export.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_export.txt")
