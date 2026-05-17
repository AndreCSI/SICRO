from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

# Resto do dialogo_caso.py (L114 ate fim)
src = (Path("ui")/"dialogo_caso.py").read_text(encoding="utf-8")
P("="*60)
P("dialogo_caso.py — L114 ate fim (DialogoDadosCaso)")
P("="*60)
linhas = src.split("\n")
for i in range(113, len(linhas)):
    P(f"{i+1:3}: {linhas[i]}")

# Onde esta a pergunta "Como deseja iniciar" / modelo vs branco
P("\n"+"="*60)
P("BUSCA da pergunta modelo/branco em TODOS os arquivos")
P("="*60)
for arq in ["main.py","ui/dialogo_caso.py","ui/tela_inicial.py",
            "ui/editor_croqui.py","popups/popup_modelo_via.py"]:
    p=Path(arq)
    if not p.exists(): 
        P(f"\n{arq}: NAO EXISTE")
        continue
    s=p.read_text(encoding="utf-8")
    achou=False
    for kw in ["Como deseja","Usar modelo de via","Desenhar do zero",
               "Modelo de via","askyesno","GridModelos","PopupModeloVia",
               "modelo_via","_escolher_inicio","Como deseja iniciar"]:
        for m in re.finditer(re.escape(kw), s):
            linha=s[:m.start()].count("\n")+1
            ctx=s[max(0,m.start()-50):m.start()+100].replace("\n"," | ")
            P(f"\n{arq} L{linha} [{kw}]:")
            P(f"  ...{ctx}...")
            achou=True
            break
    if not achou:
        P(f"\n{arq}: nada encontrado")

Path("diag_dialogo2.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_dialogo2.txt")
