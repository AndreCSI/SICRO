from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))

# carregar_imagem_veiculo — como funciona hoje a tinturizacao
src=Path("ui/editor_croqui.py").read_text(encoding="utf-8")
P("="*60)
P("carregar_imagem_veiculo — onde e definida e como tinge")
P("="*60)
for m in re.finditer(r'carregar_imagem_veiculo|def carregar_imagem', src):
    linha=src[:m.start()].count("\n")+1
    P(f"  L{linha}: {src[m.start():m.start()+80].splitlines()[0]}")
m=re.search(r"def carregar_imagem_veiculo.*?(?=\ndef |\nclass |\n    def )", src, re.DOTALL)
if not m:
    # procura em outros modulos
    for arq in ["desenho/veiculos_arte.py","config.py","main.py"]:
        s=Path(arq).read_text(encoding="utf-8")
        mm=re.search(r"def carregar_imagem_veiculo.*?(?=\ndef |\nclass |\Z)", s, re.DOTALL)
        if mm:
            P(f"\n  Definida em {arq}:")
            for i,l in enumerate(mm.group(0).split("\n")[:35]):
                P(f"  {i:3}: {l}")
            break
else:
    for i,l in enumerate(m.group(0).split("\n")[:35]):
        P(f"  {i:3}: {l}")

# import do veiculos_arte no editor (o que e importado)
P("\n"+"="*60)
P("Import de veiculos_arte no editor (L35)")
P("="*60)
m=re.search(r"from desenho\.veiculos_arte import \(.*?\)", src, re.DOTALL)
if m:
    for l in m.group(0).split("\n"):
        P(f"  {l}")

# popup_veiculo _card e _desenhar_preview (como mostra modelo)
P("\n"+"="*60)
P("popup_veiculo.py — _card + _desenhar_preview + __init__")
P("="*60)
pv=Path("popups/popup_veiculo.py").read_text(encoding="utf-8")
for nome in ["__init__","_card","_desenhar_preview"]:
    m=re.search(rf"    def {nome}\(self.*?(?=\n    def |\nclass |\Z)", pv, re.DOTALL)
    if m:
        P(f"\n  def {nome}:")
        for i,l in enumerate(m.group(0).split("\n")[:30]):
            P(f"  {i:3}: {l}")

# resource_path (para assets no .exe)
P("\n"+"="*60)
P("resource_path em config.py (assets no .exe)")
P("="*60)
cfg=Path("config.py").read_text(encoding="utf-8")
m=re.search(r"def resource_path.*?(?=\ndef |\n[A-Z_]+ =|\Z)", cfg, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")[:20]):
        P(f"  {i:3}: {l}")
for m in re.finditer(r'DIR_ASSETS|DIR_VEICULOS|resource_path', cfg):
    linha=cfg[:m.start()].count("\n")+1
    P(f"  L{linha}: {cfg[m.start():m.start()+70].splitlines()[0]}")

Path("diag_svgspec.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_svgspec.txt")
