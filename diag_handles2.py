"""diag_handles2.py — Ve _click, _drag, _release e como handles sao desenhados."""
from pathlib import Path
import re

src = (Path("ui") / "editor_croqui.py").read_text(encoding="utf-8")
out = []
def P(s=""): out.append(str(s))

P("="*60)
P("DIAGNOSTICO 2 — CLICK/DRAG/RELEASE + HANDLES")
P("="*60)

# _click (L1511) da EditorCroqui
P("\n--- _click (EditorCroqui) ---")
m = re.search(r"    def _click\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

# _drag (L1534)
P("\n--- _drag (EditorCroqui) ---")
m = re.search(r"    def _drag\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

# _release (L1565)
P("\n--- _release (EditorCroqui) ---")
m = re.search(r"    def _release\(self.*?(?=\n    def )", src, re.DOTALL)
if m:
    for i,l in enumerate(m.group(0).split("\n")):
        P(f"  {i:3}: {l}")

# Como os handles dourados sao desenhados no _desenhar_el quando sel=True
P("\n--- Bloco de selecao em _desenhar_el (sel=True / handles) ---")
m = re.search(r"    def _desenhar_el\(self,el,sel=False\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    corpo = m.group(0)
    # Acha onde trata sel
    idx = corpo.find("if sel")
    if idx < 0:
        idx = corpo.find("sel:")
    if idx >= 0:
        trecho = corpo[idx:idx+1500]
        for i,l in enumerate(trecho.split("\n")):
            P(f"  {i:3}: {l}")
    else:
        P("  'if sel' nao encontrado — procurando 'alca'")
        idx = corpo.find("alca")
        if idx >= 0:
            for i,l in enumerate(corpo[max(0,idx-400):idx+800].split("\n")):
                P(f"  {i:3}: {l}")

# _mt e _tm (transformacao metro<->tela)
P("\n--- _mt / _tm (transformacao coordenadas) ---")
for nome in ["_mt","_tm","_metro_tela","_tela_metro"]:
    m = re.search(rf"    def {re.escape(nome)}\(self.*?(?=\n    def )", src, re.DOTALL)
    if m:
        for i,l in enumerate(m.group(0).split("\n")[:12]):
            P(f"  {i:3}: {l}")
        P("")

# _elem_clicado / hit test — como descobre qual elemento foi clicado
P("\n--- Como descobre elemento clicado (hit-test) ---")
for m in re.finditer(r"    def (_elem\w*|_pegar\w*|_hit\w*|_acha\w*)\(self.*?(?=\n    def )", src, re.DOTALL):
    for i,l in enumerate(m.group(0).split("\n")[:25]):
        P(f"  {i:3}: {l}")
    P("")

Path("diag_handles2.txt").write_text("\n".join(out), encoding="utf-8")
print("OK - diag_handles2.txt criado")
