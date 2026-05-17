from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))
src=(Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("1. Botao PDF/Exportar no header")
P("="*60)
for m in re.finditer(r'"PDF"|text="PDF"|_exportar_pdf|"Exportar"', src):
    linha=src[:m.start()].count("\n")+1
    ctx=src[max(0,m.start()-80):m.start()+100].replace("\n"," | ")
    P(f"  L{linha}: ...{ctx}...")

P("\n"+"="*60)
P("2. _mostrar_props COMPLETO (como monta os campos por tipo)")
P("="*60)
m=re.search(r"    def _mostrar_props\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("3. funcao _campo (helper de campo editavel)")
P("="*60)
m=re.search(r"        def _campo\(.*?(?=\n        [a-zA-Z_]+ =|\n        # |\n        if |\n        for |\n        tk\.|\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

Path("diag_props.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_props.txt")
