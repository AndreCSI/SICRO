"""diag3.py — Investiga N duplicado e fluxo de ativacao da toolbar."""
from pathlib import Path
import re

src = (Path("ui") / "editor_croqui.py").read_text(encoding="utf-8")
out = []
def P(s=""): out.append(str(s))

P("="*60)
P("INVESTIGACAO N DUPLICADO + TOOLBAR")
P("="*60)

# 1. Procura TODOS os create_text com "N" no arquivo
P("\n1. TODOS os create_text contendo N isolado:")
for m in re.finditer(r'create_text\([^)]*text\s*=\s*["\']N["\'][^)]*\)', src):
    linha = src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0)[:80]}")

# 2. Procura desenho de bussola/norte em outros lugares
P("\n2. Referencias a bussola/norte/compass:")
for m in re.finditer(r'(bussola|norte|compass|"N"|seta_n)', src, re.I):
    linha = src[:m.start()].count("\n")+1
    ctx = src[m.start()-30:m.start()+50].replace("\n"," ")
    P(f"  L{linha}: ...{ctx}...")

# 3. Quem chama _bussola e _rodape
P("\n3. Chamadas de _bussola e _rodape:")
for m in re.finditer(r'self\._(bussola|rodape)\([^)]*\)', src):
    linha = src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0)}")

# 4. _set_ferr_via conteudo (a 1a, da EditorCroqui, L1418)
P("\n4. _set_ferr_via (EditorCroqui):")
m = re.search(r"^    def _set_ferr_via\(self,?\s*\w+\):.*?(?=^    def )", src, re.M|re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

# 5. Como _criar_btn_ferr completo funciona
P("\n5. _criar_btn_ferr COMPLETO:")
m = re.search(r"        def _criar_btn_ferr.*?return f", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

# 6. Onde self.btns_ferr e populado e como _set_ferr e chamado inicialmente
P("\n6. Chamadas _set_ferr / _set_ferr_via (todas):")
for m in re.finditer(r'self\._set_ferr\w*\([^)]*\)', src):
    linha = src[:m.start()].count("\n")+1
    P(f"  L{linha}: {m.group(0)}")

# 7. Verifica se ha "_aplicar_estilo" ou funcao que pinta ativo
P("\n7. Funcoes de estilo/ativo na toolbar:")
for kw in ["_aplicar_estilo", "_marcar_ativo", "_ativo", "FUNDO_ATIVO"]:
    cnt = src.count(kw)
    P(f"  '{kw}': {cnt} ocorrencias")

# 8. Trecho que cria os botoes (loop FERRAMENTAS)
P("\n8. Loop que cria botoes de ferramenta:")
m = re.search(r"for .{0,40}FERRAMENTAS.*?(?=\n        [a-z_]+\s*=|\n        #|\n        self\.)", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")[:30]):
        P(f"  {i:3}: {l}")

Path("diag3.txt").write_text("\n".join(out), encoding="utf-8")
print("OK - diag3.txt criado")
