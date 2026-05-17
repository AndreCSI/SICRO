from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))
src=Path("ui/editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("1. _veiculo_arte ATUAL (exato, para reescrever)")
P("="*60)
m=re.search(r"    def _veiculo_arte\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    linha=src[:m.start()].count("\n")+1
    P(f"  (inicia L{linha})")
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("2. Onde _veiculo_arte e CHAMADO (contexto da chamada)")
P("="*60)
for m in re.finditer(r'self\._veiculo_arte\([^\n]*\)', src):
    linha=src[:m.start()].count("\n")+1
    ini=src.rfind("\n",0,m.start()-400)
    P(f"--- chamada L{linha} ---")
    for l in src[ini:m.end()+50].split("\n"):
        P(f"  {l}")
    P("")

P("="*60)
P("3. Bloco que decide arte_fn/png (antes da chamada)")
P("="*60)
# o trecho 'if tipo in larg_padrao' que monta arte_fn e png
m=re.search(r'if tipo in larg_padrao:.*?self\._veiculo_arte\([^\n]*\)', src, re.DOTALL)
if m:
    linha=src[:m.start()].count("\n")+1
    P(f"  (inicia L{linha})")
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("4. _inserir — como guarda modelo/cor (estado atual)")
P("="*60)
m=re.search(r"    def _inserir\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

P("\n"+"="*60)
P("5. Imports no topo do editor (render_svg ja importado?)")
P("="*60)
for m in re.finditer(r'^(from |import )[^\n]*', src[:3000], re.M):
    P("  "+m.group(0))
P("  ...")
P(f"  'render_svg' aparece: {'render_svg' in src}")
P(f"  'catalogo_veiculos' aparece: {'catalogo_veiculos' in src}")

P("\n"+"="*60)
P("6. MODELOS_VEICULOS — chaves de cada modelo (tem 'svg'?)")
P("="*60)
pv=Path("popups/popup_veiculo.py").read_text(encoding="utf-8")
m=re.search(r"MODELOS_VEICULOS\s*=\s*\{.*?\n\}", pv, re.DOTALL)
if m:
    # pega so as keys de um item exemplo
    primeiro=re.search(r"\{'chave'.*?\}", m.group(0))
    if primeiro:
        P("  Exemplo de item atual:")
        P("  "+primeiro.group(0))
P(f"  campo 'svg' ja existe nos modelos: {'svg' in (m.group(0) if m else '')}")

Path("diag_integra.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_integra.txt")
