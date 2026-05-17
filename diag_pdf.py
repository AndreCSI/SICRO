from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))
src=(Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("1. _exportar_pdf atual (exato, para substituir)")
P("="*60)
m=re.search(r"    def _exportar_pdf\(self\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n2. Metodos de zoom (para zoom total antes de capturar):")
for m in re.finditer(r"    def (_zoom\w*|_ajustar\w*|_fit\w*|_zoom_total\w*)\(self", src):
    linha=src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0)}")
# conteudo do zoom total / ajustar
m=re.search(r"    def _zoom_tot\w*\(self.*?(?=\n    def )", src, re.DOTALL)
if not m:
    m=re.search(r"    def _zoom_ajust\w*\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    P("  --- conteudo ---")
    for i,l in enumerate(m.group(0).split("\n")[:25]):
        P(f"  {i:3}: {l}")

P("\n3. TIPO_INFO (icones/nomes para legenda):")
m=re.search(r"TIPO_INFO\s*=\s*\{.*?\}", src, re.DOTALL)
if m:
    for l in m.group(0).split("\n"):
        P(f"  {l}")

P("\n4. Estrutura de elemento (chaves usadas):")
for kw in ['"label"','"tipo"','"x"','"y"','"larg"','"alt"','"angulo"','"x2"','"y2"','"cor"']:
    c=src.count(kw)
    P(f"  {kw}: {c}x")

P("\n5. self.k / calibrado / _mt / cota (para distancias):")
for kw in ["self.k","self.calibrado","def _mt","tipo==\"cota\"","\"cota\""]:
    m=re.search(re.escape(kw),src)
    if m:
        linha=src[:m.start()].count("\n")+1
        P(f"  L{linha}: {kw}")

P("\n6. Brasao — como main.py carrega (_brasao):")
mm=Path("main.py").read_text(encoding="utf-8")
for m in re.finditer(r'_brasao|brasao_pci|\.png', mm):
    linha=mm[:m.start()].count("\n")+1
    ctx=mm[max(0,m.start()-40):m.start()+70].replace("\n"," ")
    P(f"  main.py L{linha}: ...{ctx}...")

P("\n7. config DIR / paths:")
cfg=Path("config.py").read_text(encoding="utf-8")
for m in re.finditer(r'(DIR_\w+|BASE_DIR|RAIZ)\s*=', cfg):
    linha=cfg[:m.start()].count("\n")+1
    P(f"  config L{linha}: {cfg[m.start():m.start()+70].splitlines()[0]}")

Path("diag_pdf.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_pdf.txt")
