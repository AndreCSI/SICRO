from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

# Fluxo de _novo no main.py (onde escolhe a foto do drone)
mm=Path("main.py").read_text(encoding="utf-8")
P("="*60)
P("main.py _novo COMPLETO (fluxo da foto drone)")
P("="*60)
m=re.search(r"    def _novo\(self.*?(?=\n    def )", mm, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n--- imports do main.py (PIL, Image, filedialog) ---")
for i,l in enumerate(mm.split("\n")[:40]):
    if any(k in l for k in ["import","from ","PIL_OK"]):
        P(f"  {i+1:3}: {l}")

P("\n--- classes Toplevel existentes no main.py (padrao de janela) ---")
for m in re.finditer(r"^class (\w+)", mm, re.M):
    linha=mm[:m.start()].count("\n")+1
    P(f"  L{linha}: class {m.group(1)}")

# Como SplashScreen/dialogos fazem janela sem moldura (padrao a seguir)
P("\n--- TitleBar / overrideredirect no main.py (padrao visual) ---")
for m in re.finditer(r'overrideredirect|class TitleBar|FUNDO_|DOURADO|from tema', mm):
    linha=mm[:m.start()].count("\n")+1
    P(f"  L{linha}: {mm[m.start():m.start()+70].splitlines()[0]}")
    if len([x for x in out if 'L' in x])>30: break

# config — tema disponivel?
P("\n--- config.py exporta tema? ---")
cfg=Path("config.py").read_text(encoding="utf-8")
for m in re.finditer(r'(FUNDO_BASE|DOURADO|from tema|TEXTO_PRIMARIO)', cfg):
    linha=cfg[:m.start()].count("\n")+1
    P(f"  config L{linha}: {cfg[m.start():m.start()+60].splitlines()[0]}")

# tema.py existe e o que exporta
P("\n--- tema.py existe? quais nomes? ---")
tp=Path("tema.py")
if tp.exists():
    t=tp.read_text(encoding="utf-8")
    nomes=re.findall(r'^([A-Z_]+)\s*=', t, re.M)
    P(f"  {len(nomes)} constantes: {', '.join(nomes[:40])}")
    fontes=re.findall(r'^(FONTE_[A-Z_0-9]+)\s*=', t, re.M)
    P(f"  Fontes: {', '.join(fontes)}")

Path("diag_crop.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_crop.txt")
