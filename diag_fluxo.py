from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

# Fluxo de criacao no main.py
src = Path("main.py").read_text(encoding="utf-8")
P("="*60)
P("main.py — fluxo de novo croqui")
P("="*60)
for kw in ["DialogoDadosCaso","PopupModeloVia","novo_croqui","_novo","on_novo",
           "abrir_editor","def _criar","modo=","_iniciar_croqui","TelaInicial"]:
    for m in re.finditer(re.escape(kw), src):
        linha=src[:m.start()].count("\n")+1
        ctx=src[max(0,m.start()-40):m.start()+120].replace("\n"," | ")
        P(f"L{linha} [{kw}]: ...{ctx}...")
        break

# Acha o metodo que cria o croqui (onde DialogoDadosCaso e usado)
P("\n--- Metodo(s) que usam DialogoDadosCaso / PopupModeloVia ---")
for m in re.finditer(r"    def (\w+)\(self[^)]*\):", src):
    nome=m.group(1)
    ini=m.start()
    fim=src.find("\n    def ", ini+10)
    if fim<0: fim=len(src)
    corpo=src[ini:fim]
    if "DialogoDadosCaso" in corpo or "PopupModeloVia" in corpo or "EditorCroqui" in corpo:
        linha=src[:ini].count("\n")+1
        P(f"\n--- def {nome} (L{linha}) ---")
        for i,l in enumerate(corpo.split("\n")):
            P(f"  {i:3}: {l}")

# popup_modelo_via.py completo
P("\n"+"="*60)
P("popup_modelo_via.py COMPLETO")
P("="*60)
s2=Path("popups/popup_modelo_via.py").read_text(encoding="utf-8")
for i,l in enumerate(s2.split("\n")):
    P(f"{i+1:3}: {l}")

Path("diag_fluxo.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_fluxo.txt")
