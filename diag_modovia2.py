from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))
src=(Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("--- Criacao do _btn_modo_via (L949 +- contexto) ---")
i=src.find("self._btn_modo_via = tk.Frame")
if i>=0:
    ini=src.rfind("\n",0,i-50)
    fim=src.find("\n\n",i+400)
    if fim<0: fim=i+900
    for l in src[ini:fim].split("\n"):
        P(f"  {l}")

P("\n--- Linha 1398 (toggle _modo_via) com contexto ---")
m=re.search(r'self\._modo_via = not self\._modo_via', src)
if m:
    ini=src.rfind("\n",0,m.start()-400)
    fim=src.find("\n\n",m.end())
    if fim<0 or fim-m.end()>600: fim=m.end()+500
    for l in src[ini:fim].split("\n"):
        P(f"  {l}")

P("\n--- metodo que contem o toggle (def ...) ---")
# acha a def antes da L1398
idx=src.find("self._modo_via = not self._modo_via")
defs=[mm for mm in re.finditer(r"    def (\w+)\(self", src) if mm.start()<idx]
if defs:
    ultima=defs[-1]
    nome=ultima.group(1)
    fim=src.find("\n    def ", idx)
    P(f"  def {nome} (contem o toggle):")
    for i,l in enumerate(src[ultima.start():fim].split("\n")):
        P(f"  {i:3}: {l}")

Path("diag_modovia2.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_modovia2.txt")
