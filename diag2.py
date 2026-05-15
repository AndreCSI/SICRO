"""diag2.py — Escreve diag2.txt em UTF-8. Nao modifica o codigo."""
from pathlib import Path
import re

src = (Path("ui") / "editor_croqui.py").read_text(encoding="utf-8")
out = []
def P(s=""): out.append(str(s))

P("="*60)
P("ASSINATURAS REAIS")
P("="*60)
P(f"Total linhas: {len(src.splitlines())}")

for m in re.finditer(r"^    def (_set_ferr\w*)\(self,?\s*(\w+)?\):", src, re.M):
    linha = src[:m.start()].count("\n")+1
    P(f"  L{linha}: def {m.group(1)}(self, {m.group(2)})")

for m in re.finditer(r"^    def (_bussola|_rodape)\b[^\n]*:", src, re.M):
    linha = src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0).strip()}")

P("\nCLASSES:")
for m in re.finditer(r"^class (\w+)", src, re.M):
    linha = src[:m.start()].count("\n")+1
    P(f"  L{linha}: class {m.group(1)}")

P("\n_criar_btn_ferr:")
m = re.search(r"def _criar_btn_ferr.*?return f", src, re.DOTALL)
if m:
    b = m.group(0)
    P("  ENCONTRADO (fase 4 aplicada)")
    P(f"  _ind: {'_ind' in b} | _ico: {'_ico' in b} | _txt: {'_txt' in b}")
else:
    P("  NAO encontrado - toolbar fase 4 ausente")

P("\n_set_ferr (1a ocorrencia = EditorCroqui):")
m = re.search(r"^    def _set_ferr\(self,?\s*\w+\):.*?(?=^    def )", src, re.M|re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n_bussola conteudo:")
m = re.search(r"^    def _bussola\b.*?(?=^    def )", src, re.M|re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")
else:
    P("  _bussola NAO existe")

P("\n_brasao contexto:")
i = src.find("_brasao_tk")
if i > 0:
    for l in src[max(0,i-400):i+200].split("\n"):
        P(f"  {l}")
else:
    P("  sem _brasao_tk")

# Escreve em UTF-8 explicito
Path("diag2.txt").write_text("\n".join(out), encoding="utf-8")
print("OK - diag2.txt criado. Abra com: notepad diag2.txt")
