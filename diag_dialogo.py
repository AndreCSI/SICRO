from pathlib import Path
import re
src = (Path("ui")/"dialogo_caso.py").read_text(encoding="utf-8")
out=[]
def P(s=""): out.append(str(s))
P("="*60)
P("DIAGNOSTICO dialogo_caso.py")
P("="*60)
P(f"Linhas: {len(src.splitlines())}")
P("\n--- Imports ---")
for l in src.split("\n")[:15]:
    P(f"  {l}")
P("\n--- Classes/defs ---")
for m in re.finditer(r"^(class |    def )(\w+)", src, re.M):
    linha=src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0).strip()}")
P("\n--- overrideredirect / title / geometry / configure ---")
for kw in ["overrideredirect","self.title","geometry","self.configure","COR_","AMARELO","FONTE_"]:
    for m in re.finditer(re.escape(kw), src):
        linha=src[:m.start()].count("\n")+1
        ctx=src[m.start():m.start()+70].split("\n")[0]
        P(f"  L{linha}: {ctx}")
        break
P("\n--- Pergunta modelo/branco (GridModelos/PopupModeloVia/messagebox) ---")
for kw in ["GridModelos","PopupModeloVia","modelo","branco","askyesno","Como deseja","Usar modelo","Desenhar do zero"]:
    for m in re.finditer(re.escape(kw), src):
        linha=src[:m.start()].count("\n")+1
        ctx=src[max(0,m.start()-30):m.start()+80].replace("\n"," ")
        P(f"  L{linha} [{kw}]: ...{ctx}...")
        break
P("\n--- Arquivo COMPLETO (primeiras 120 linhas) ---")
for i,l in enumerate(src.split("\n")[:120]):
    P(f"{i+1:3}: {l}")
Path("diag_dialogo.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_dialogo.txt")
