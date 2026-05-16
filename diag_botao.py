from pathlib import Path
import re
src = (Path("ui")/"tela_inicial.py").read_text(encoding="utf-8")
out=[]
def P(s=""): out.append(str(s))
P("_card_acao COMPLETO:")
m=re.search(r"    def _card_acao\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"{i:3}: {l}")
Path("diag_botao.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_botao.txt")
