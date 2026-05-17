from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

# popup_veiculo.py COMPLETO (vamos reescrever)
pv=Path("popups/popup_veiculo.py").read_text(encoding="utf-8")
P("="*60)
P("popup_veiculo.py COMPLETO ("+str(len(pv.splitlines()))+" linhas)")
P("="*60)
for i,l in enumerate(pv.split("\n")):
    P(f"{i+1:3}: {l}")

src=Path("ui/editor_croqui.py").read_text(encoding="utf-8")

P("\n"+"="*60)
P("FERRAMENTAS atual (ordem dos botoes)")
P("="*60)
m=re.search(r"FERRAMENTAS\s*=\s*\[.*?\]", src, re.DOTALL)
if m:
    linha=src[:m.start()].count("\n")+1
    P(f"(L{linha})")
    for l in m.group(0).split("\n"): P("  "+l)

P("\n"+"="*60)
P("Como _click trata as ferramentas (onde chama _inserir)")
P("="*60)
m=re.search(r"    def _click\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("_inserir COMPLETO (vamos refatorar para desacoplar)")
P("="*60)
m=re.search(r"    def _inserir\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("_set_ferr (como ferramenta vira acao) - inicio")
P("="*60)
m=re.search(r"    def _set_ferr\(self, c\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")[:30]):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("Como o botao de ferramenta chama a acao (bind/lambda)")
P("="*60)
for m in re.finditer(r'_set_ferr|_inserir|btns_ferr|FERRAMENTAS', src):
    linha=src[:m.start()].count("\n")+1
    ctx=src[m.start():m.start()+90].split("\n")[0]
    P(f"  L{linha}: {ctx}")
    if len([x for x in out if x.startswith("  L")])>25: break

P("\n"+"="*60)
P("catalogo_veiculos importado no editor? CATEGORIAS disponivel?")
P("="*60)
P(f"  'catalogo_veiculos' no editor: {'catalogo_veiculos' in src}")
cv=Path("desenho/catalogo_veiculos.py")
if cv.exists():
    s=cv.read_text(encoding="utf-8")
    P(f"  catalogo tem CATEGORIAS: {'CATEGORIAS' in s}")
    P(f"  catalogo tem por_categoria: {'def por_categoria' in s}")
    P(f"  catalogo tem get(): {'def get(' in s}")

Path("diag_etapa4.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_etapa4.txt - "+str(len(out))+" linhas")
