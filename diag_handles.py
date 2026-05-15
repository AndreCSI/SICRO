"""diag_handles.py — Investiga seleção, handles e arraste. Nao modifica nada."""
from pathlib import Path
import re

src = (Path("ui") / "editor_croqui.py").read_text(encoding="utf-8")
out = []
def P(s=""): out.append(str(s))

P("="*60)
P("DIAGNOSTICO HANDLES / SELECAO / ARRASTE")
P("="*60)

# 1. _desenhar_el — como desenha o objeto e os handles
P("\n1. _desenhar_el (assinatura e inicio):")
m = re.search(r"    def _desenhar_el\(self[^)]*\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    linhas = m.group(0).split("\n")
    P(f"  Total: {len(linhas)} linhas")
    for i,l in enumerate(linhas[:50]):
        P(f"  {i:3}: {l}")
    P("  ...")
    # Procura handles dentro
    if "handle" in m.group(0).lower():
        P("  >> Contem 'handle'")
    for kw in ["create_rectangle","create_oval","sel=","_sel","alça","alca","quadrad"]:
        c = m.group(0).count(kw)
        if c: P(f"  contem '{kw}': {c}x")

# 2. Eventos de mouse: click, drag, release
P("\n2. Binds de mouse no canvas:")
for m in re.finditer(r'self\.canvas\.bind\(["\']<([^>]+)>["\'],\s*(self\.\w+)', src):
    linha = src[:m.start()].count("\n")+1
    P(f"  L{linha}: <{m.group(1)}> -> {m.group(2)}")

# 3. Metodos de arraste/movimento
P("\n3. Metodos de drag/move/click:")
for nome in ["_click","_drag","_arrastar","_release","_mouse","_b1","_motion","_press"]:
    for m in re.finditer(rf"    def ({nome}\w*)\(self", src):
        linha = src[:m.start()].count("\n")+1
        P(f"  L{linha}: def {m.group(1)}")

# 4. Como detecta clique em elemento (hit test)
P("\n4. Hit-test / deteccao de elemento sob mouse:")
for kw in ["_elem_em","_hit","_pegar_elem","_elemento_em","sel_idx","_em_handle","_handle_em"]:
    for m in re.finditer(rf"def ({re.escape(kw)}\w*)\(", src):
        linha = src[:m.start()].count("\n")+1
        P(f"  L{linha}: def {m.group(1)}")
    c = src.count(kw)
    if c and not any(kw in l for l in out[-6:]):
        P(f"  '{kw}': {c} ocorrencias")

# 5. DialogoRedimensionar — ja existe um jeito de redimensionar
P("\n5. _abrir_redimensionar / DialogoRedimensionar:")
m = re.search(r"    def _abrir_redimensionar\(self\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")[:20]):
        P(f"  {i:3}: {l}")

# 6. Estrutura de um elemento (dict keys)
P("\n6. Chaves de um elemento (x,y,larg,alt,angulo...):")
m = re.search(r"def _inserir\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    txt = m.group(0)
    keys = set(re.findall(r'["\'](\w+)["\']\s*:', txt))
    P(f"  Keys encontradas em _inserir: {sorted(keys)}")

# 7. Procura onde desenha os quadradinhos amarelos de selecao
P("\n7. Desenho de selecao (handles amarelos da imagem):")
for m in re.finditer(r'create_(rectangle|oval)\([^)]*(?:AMARELO|DOURADO|amarelo)[^)]*\)', src):
    linha = src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0)[:90]}")

Path("diag_handles.txt").write_text("\n".join(out), encoding="utf-8")
print("OK - diag_handles.txt criado")
