"""diag_camadas.py — Investiga o painel de Camadas. Nao modifica nada."""
from pathlib import Path
import re

src = (Path("ui") / "editor_croqui.py").read_text(encoding="utf-8")
out = []
def P(s=""): out.append(str(s))

P("="*60)
P("DIAGNOSTICO PAINEL CAMADAS")
P("="*60)

# Procura "Camadas" no codigo
P("\n1. Ocorrencias de 'Camadas':")
for m in re.finditer(r'["\']Camadas["\']', src):
    linha = src[:m.start()].count("\n")+1
    ctx = src[max(0,m.start()-80):m.start()+120].replace("\n"," | ")
    P(f"  L{linha}: ...{ctx}...")

# Metodo _atualizar_camadas
P("\n2. _atualizar_camadas COMPLETO:")
m = re.search(r"    def _atualizar_camadas\(self\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")
else:
    P("  NAO encontrado")

# Listbox / Treeview / Frame de camadas
P("\n3. Widget de camadas (listbox/tree/canvas):")
for kw in ["self.lst_camadas", "self.tree_camadas", "self.camadas_frame",
           "Listbox", "self.lb_camadas", "_camadas_box", "self.painel_camadas"]:
    cnt = src.count(kw)
    if cnt:
        m = re.search(re.escape(kw), src)
        linha = src[:m.start()].count("\n")+1
        P(f"  '{kw}': {cnt}x — primeira L{linha}")

# Onde o painel direito e construido
P("\n4. Construcao do painel direito (pd):")
m = re.search(r"        pd\s*=\s*tk\.Frame.*?(?=\n        self\._set_ferr|\n        # Ctrl)", src, re.DOTALL)
if m:
    txt = m.group(0)
    # Mostra so as primeiras 60 linhas
    for i,l in enumerate(txt.split("\n")[:60]):
        P(f"  {i:3}: {l}")
else:
    P("  Padrao 'pd = tk.Frame' nao encontrado")
    # tenta achar onde Camadas label e criado
    m = re.search(r'text="Camadas".*?\n', src)
    if m:
        idx = m.start()
        P("  Contexto do label Camadas (800 chars antes ate 400 depois):")
        for l in src[max(0,idx-800):idx+400].split("\n"):
            P(f"    {l}")

Path("diag_camadas.txt").write_text("\n".join(out), encoding="utf-8")
print("OK - diag_camadas.txt criado")
