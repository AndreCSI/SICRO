"""diag_resize.py — Ve como veiculo usa larg/alt e _selecionar. Nao modifica."""
from pathlib import Path
import re

src = (Path("ui") / "editor_croqui.py").read_text(encoding="utf-8")
out=[]
def P(s=""): out.append(str(s))

P("="*60)
P("DIAGNOSTICO RESIZE")
P("="*60)

# Bloco dos veiculos no _desenhar_el_orig
P("\n1. Bloco veiculos (larg_padrao) no _desenhar_el_orig:")
m = re.search(r"def _desenhar_el_orig.*?if tipo in larg_padrao:.*?(?=\n        # ──|\n    def )", src, re.DOTALL)
if m:
    txt = m.group(0)
    idx = txt.find("if tipo in larg_padrao:")
    for i,l in enumerate(txt[idx:idx+1800].split("\n")):
        P(f"  {i:3}: {l}")

# _selecionar — como acha o elemento
P("\n2. _selecionar:")
m = re.search(r"    def _selecionar\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

# _draw_handle_rot (ja criado) — pra ver padrao de hit-test
P("\n3. _draw_handle_rot (referencia de padrao):")
m = re.search(r"    def _draw_handle_rot\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

# Wrapper _desenhar_el atual
P("\n4. Wrapper _desenhar_el atual:")
m = re.search(r"    def _desenhar_el\(self, el, sel=False\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

Path("diag_resize.txt").write_text("\n".join(out), encoding="utf-8")
print("OK - diag_resize.txt criado")
