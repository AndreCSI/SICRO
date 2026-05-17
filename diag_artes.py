from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

P("="*60)
P("ARQUIVOS DE ARTE / ASSETS")
P("="*60)
# Estrutura desenho/
for d in ["desenho","assets","assets/veiculos","popups"]:
    p=Path(d)
    if p.exists():
        P(f"\n{d}/:")
        for f in sorted(p.iterdir()):
            tam=f.stat().st_size if f.is_file() else 0
            P(f"  {f.name}  ({tam} bytes)" if f.is_file() else f"  {f.name}/ (dir)")

# veiculos_arte.py
P("\n"+"="*60)
P("desenho/veiculos_arte.py — funcoes de arte")
P("="*60)
va=Path("desenho/veiculos_arte.py")
if va.exists():
    s=va.read_text(encoding="utf-8")
    P(f"  {len(s.splitlines())} linhas")
    for m in re.finditer(r"^def (\w+)", s, re.M):
        linha=s[:m.start()].count("\n")+1
        P(f"  L{linha}: def {m.group(1)}")
    # primeira funcao completa como exemplo
    m=re.search(r"^def _arte_\w+.*?(?=\n^def |\Z)", s, re.M|re.DOTALL)
    if m:
        P("\n  --- exemplo de funcao de arte (primeira) ---")
        for i,l in enumerate(m.group(0).split("\n")[:40]):
            P(f"  {i:3}: {l}")

# MODELOS_VEICULOS no config
P("\n"+"="*60)
P("MODELOS_VEICULOS (config.py)")
P("="*60)
cfg=Path("config.py").read_text(encoding="utf-8")
m=re.search(r"MODELOS_VEICULOS\s*=\s*\{.*?\n\}", cfg, re.DOTALL)
if m:
    txt=m.group(0)
    P(f"  ({len(txt.splitlines())} linhas)")
    for l in txt.split("\n")[:50]:
        P(f"  {l}")
else:
    P("  nao encontrado em config.py — buscando em outros arquivos")
    for arq in ["desenho/veiculos_arte.py","popups/popup_veiculo.py","ui/editor_croqui.py"]:
        s=Path(arq).read_text(encoding="utf-8")
        mm=re.search(r"MODELOS_VEICULOS\s*=\s*\{.*?\n\}", s, re.DOTALL)
        if mm:
            P(f"  Encontrado em {arq}:")
            for l in mm.group(0).split("\n")[:40]:
                P(f"  {l}")
            break

# Como o editor chama a arte
P("\n"+"="*60)
P("Como editor_croqui chama arte (_veiculo_arte / arte_fn)")
P("="*60)
src=Path("ui/editor_croqui.py").read_text(encoding="utf-8")
for kw in ["_veiculo_arte","arte_fn","MODELOS_VEICULOS","_arte_","def _veiculo","import.*veiculos_arte","from desenho"]:
    for m in re.finditer(kw, src):
        linha=src[:m.start()].count("\n")+1
        P(f"  L{linha}: {src[m.start():m.start()+90].splitlines()[0]}")
        break

# _veiculo_arte completo
m=re.search(r"    def _veiculo_arte\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    P("\n  --- _veiculo_arte completo ---")
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

# popup_veiculo (escolha de modelo)
P("\n"+"="*60)
P("popups/popup_veiculo.py — estrutura")
P("="*60)
pv=Path("popups/popup_veiculo.py")
if pv.exists():
    s=pv.read_text(encoding="utf-8")
    P(f"  {len(s.splitlines())} linhas")
    for m in re.finditer(r"^(class |    def )(\w+)", s, re.M):
        linha=s[:m.start()].count("\n")+1
        P(f"  L{linha}: {m.group(0).strip()}")

Path("diag_artes.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_artes.txt")
