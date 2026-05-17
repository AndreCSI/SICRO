from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

src = (Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("1. messagebox de Voltar e Salvo")
P("="*60)
for m in re.finditer(r'messagebox\.\w+\([^)]*\)', src, re.DOTALL):
    linha=src[:m.start()].count("\n")+1
    txt=m.group(0).replace("\n"," ")[:140]
    P(f"  L{linha}: {txt}")

P("\n"+"="*60)
P("2. Popup de Identificacao (V1) ao inserir veiculo")
P("="*60)
for kw in ["Identificacao","Identificação","ex: V1","simpledialog","askstring","FIORINO","_inserir"]:
    for m in re.finditer(re.escape(kw), src):
        linha=src[:m.start()].count("\n")+1
        ctx=src[max(0,m.start()-60):m.start()+120].replace("\n"," | ")
        P(f"  L{linha} [{kw}]: ...{ctx}...")
        break

P("\n--- _inserir COMPLETO ---")
m=re.search(r"    def _inserir\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("3. FERRAMENTAS — nomes Veiculo")
P("="*60)
m=re.search(r"FERRAMENTAS\s*=\s*\[.*?\]", src, re.DOTALL)
if m:
    for l in m.group(0).split("\n"):
        P(f"  {l}")

P("\n"+"="*60)
P("4. Como _criar_btn_ferr monta o label (split)")
P("="*60)
m=re.search(r"lbl_txt = tk\.Label\(f, text=dica[^\n]*", src)
if m:
    linha=src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0)}")

Path("diag_ajustes.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_ajustes.txt")
