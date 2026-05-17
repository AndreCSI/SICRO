from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))
src=(Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("img_drone — todas as referencias")
P("="*60)
for m in re.finditer(r'img_drone|self\.img_base|self\._img_drone|self\.drone_img|imagem_base|self\.norte_ang|norte_angulo', src):
    linha=src[:m.start()].count("\n")+1
    ctx=src[max(0,m.start()-50):m.start()+110].replace("\n"," | ")
    P(f"  L{linha}: ...{ctx}...")

P("\n--- __init__ do EditorCroqui (assinatura + onde guarda img_drone) ---")
m=re.search(r"    def __init__\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")[:60]):
        P(f"  {i:3}: {l}")

P("\n--- _salvar atual (exato) ---")
m=re.search(r"    def _salvar\(self\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n--- main.py _abrir (como carrega) ---")
mm=Path("main.py").read_text(encoding="utf-8")
m=re.search(r"    def _abrir\(self.*?(?=\n    def )", mm, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n--- como img_drone vira self.algo no __init__ ---")
for m in re.finditer(r'self\.\w*\s*=\s*img_drone|img_drone\s*=|Image\.open', src):
    linha=src[:m.start()].count("\n")+1
    ctx=src[m.start():m.start()+80].split("\n")[0]
    P(f"  L{linha}: {ctx}")

Path("diag_imgdrone.txt").write_text("\n".join(out),encoding="utf-8")
print("OK")
