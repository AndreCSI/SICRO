from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

P("="*60)
P("ESTADO ATUAL — SISTEMA DE VEICULOS (pre-SVG)")
P("="*60)

# 1. Estrutura de pastas
for d in ["assets","assets/veiculos","desenho","popups"]:
    p=Path(d)
    if p.exists():
        P(f"\n{d}/:")
        for f in sorted(p.iterdir()):
            if f.is_file():
                P(f"  {f.name} ({f.stat().st_size}b)")
            else:
                P(f"  {f.name}/")

# 2. FERRAMENTAS (ordem dos botoes atual)
src=Path("ui/editor_croqui.py").read_text(encoding="utf-8")
P("\n"+"="*60)
P("FERRAMENTAS (ordem atual dos botoes)")
P("="*60)
m=re.search(r"FERRAMENTAS\s*=\s*\[.*?\]", src, re.DOTALL)
if m:
    for l in m.group(0).split("\n"): P("  "+l)

# 3. MODELOS_VEICULOS atual
P("\n"+"="*60)
P("MODELOS_VEICULOS (onde esta + conteudo)")
P("="*60)
for arq in ["popups/popup_veiculo.py","config.py","ui/editor_croqui.py"]:
    s=Path(arq).read_text(encoding="utf-8")
    mm=re.search(r"MODELOS_VEICULOS\s*=\s*\{.*?\n\}", s, re.DOTALL)
    if mm:
        P(f"  [em {arq}]")
        for l in mm.group(0).split("\n"): P("  "+l)
        break

# 4. _inserir atual (como cria veiculo, popup de modelo)
P("\n"+"="*60)
P("_inserir (fluxo de criacao de veiculo)")
P("="*60)
m=re.search(r"    def _inserir\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")): P(f"  {i:3}: {l}")

# 5. _veiculo_arte atual + carregar_imagem_veiculo
P("\n"+"="*60)
P("_veiculo_arte (renderizacao atual)")
P("="*60)
m=re.search(r"    def _veiculo_arte\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")): P(f"  {i:3}: {l}")

P("\n--- carregar_imagem_veiculo (def + assinatura) ---")
for arq in ["ui/editor_croqui.py","desenho/veiculos_arte.py"]:
    s=Path(arq).read_text(encoding="utf-8")
    mm=re.search(r"def carregar_imagem_veiculo.*?(?=\ndef |\nclass |\n    def )", s, re.DOTALL)
    if mm:
        P(f"  [em {arq}]")
        for i,l in enumerate(mm.group(0).split("\n")[:30]): P(f"  {i:3}: {l}")
        break

# 6. imports do veiculos_arte no editor
P("\n"+"="*60)
P("import veiculos_arte no editor + TIPO_INFO")
P("="*60)
m=re.search(r"from desenho\.veiculos_arte import \(.*?\)", src, re.DOTALL)
if m:
    for l in m.group(0).split("\n"): P("  "+l)
cfg=Path("config.py").read_text(encoding="utf-8")
m=re.search(r"TIPO_INFO\s*=\s*\{.*?\n\}", cfg, re.DOTALL)
if m:
    P("\n  TIPO_INFO (config.py):")
    for l in m.group(0).split("\n"): P("  "+l)

# 7. _mostrar_props - campos atuais (para planejar novos)
P("\n"+"="*60)
P("_mostrar_props (campos atuais por tipo) - so estrutura")
P("="*60)
m=re.search(r"    def _mostrar_props\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    linhas=m.group(0).split("\n")
    P(f"  ({len(linhas)} linhas no metodo)")
    for i,l in enumerate(linhas):
        if any(k in l for k in ['_campo(','el.get("tipo"','tipo ==','tipo in','"cor"','"larg"','"alt"','def _campo','if el','Espessura','Rotacao']):
            P(f"  {i:3}: {l}")

# 8. popup_veiculo estrutura
P("\n"+"="*60)
P("popup_veiculo.py (estrutura completa)")
P("="*60)
pv=Path("popups/popup_veiculo.py").read_text(encoding="utf-8")
P(f"  ({len(pv.splitlines())} linhas)")
for m in re.finditer(r"^(class |    def )(\w+)", pv, re.M):
    linha=pv[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0).strip()}")

# 9. config.py - resource_path e DIR
P("\n"+"="*60)
P("config.py - paths de assets")
P("="*60)
for m in re.finditer(r'(def resource_path|DIR_ASSETS|DIR_VEICULOS|DIR_CROQUIS)\b.*', cfg):
    linha=cfg[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0)[:80]}")

Path("diag_artes2.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_artes2.txt - "+str(len(out))+" linhas")
