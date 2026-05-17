from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))
src=(Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("1. TIPO_INFO / nomes de tipo (legenda automatica)")
P("="*60)
# Procura no editor e no config
for arq in ["ui/editor_croqui.py","config.py"]:
    s=Path(arq).read_text(encoding="utf-8")
    m=re.search(r"TIPO_INFO\s*=\s*\{.*?\n\}", s, re.DOTALL)
    if m:
        P(f"--- {arq} ---")
        for l in m.group(0).split("\n"):
            P(f"  {l}")
    # nomes alternativos
    for kw in ["sig=","TIPO_NOME","NOMES_TIPO","_nome_tipo"]:
        mm=re.search(re.escape(kw)+r".*", s)
        if mm:
            linha=s[:mm.start()].count("\n")+1
            P(f"  {arq} L{linha}: {mm.group(0)[:100]}")

P("\n"+"="*60)
P("2. Como elemento cota guarda a medida (quadro distancias)")
P("="*60)
m=re.search(r'tipo==?"cota".*?(?=\n        # ──|\n        if tipo|\n        elif tipo)', src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")[:20]):
        P(f"  {i:3}: {l}")
# Onde cota recebe valor
for m in re.finditer(r'"cota".*?(valor|medida|texto|label|dist)', src):
    linha=src[:m.start()].count("\n")+1
    P(f"  L{linha}: {src[m.start():m.start()+90].splitlines()[0]}")

P("\n"+"="*60)
P("3. _zoom_d e como ajustar zoom para captura total")
P("="*60)
m=re.search(r"    def _zoom_d\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")[:20]):
        P(f"  {i:3}: {l}")
# zoom total / fit
for kw in ["_zoom_total","_fit","_ajustar_zoom","_enquadrar","Zoom total","zoom_tot"]:
    for m in re.finditer(re.escape(kw), src):
        linha=src[:m.start()].count("\n")+1
        P(f"  L{linha} [{kw}]: {src[m.start():m.start()+80].splitlines()[0]}")
        break

P("\n"+"="*60)
P("4. self.canvas / pan / zoom / _redesenhar (estado p/ captura)")
P("="*60)
for kw in ["self.zoom","self.pan_x","self.pan_y","def _redesenhar","self.canvas ="]:
    m=re.search(re.escape(kw), src)
    if m:
        linha=src[:m.start()].count("\n")+1
        P(f"  L{linha}: {src[m.start():m.start()+70].splitlines()[0]}")

P("\n"+"="*60)
P("5. dados_caso chaves disponiveis")
P("="*60)
for m in re.finditer(r"dados_caso\.get\(['\"](\w+)['\"]", src):
    P(f"  {m.group(1)}")

P("\n6. Brasao acessivel do editor? (winfo_toplevel._brasao)")
for m in re.finditer(r'_brasao|winfo_toplevel\(\)', src):
    linha=src[:m.start()].count("\n")+1
    P(f"  L{linha}: {src[m.start():m.start()+70].splitlines()[0]}")
    break

Path("diag_prancha.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_prancha.txt")
