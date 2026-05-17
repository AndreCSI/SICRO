from pathlib import Path
import re
out=[]
def P(s=""): out.append(str(s))
src=(Path("ui")/"editor_croqui.py").read_text(encoding="utf-8")

P("="*60)
P("Modo Via — botao e acionamento")
P("="*60)
for kw in ["Modo Via","_modo_via","_toggle_via","_ativar_via","_set_modo_via","modo_via","_btn_modo_via","Modo arte","modo_arte"]:
    for m in re.finditer(re.escape(kw), src):
        linha=src[:m.start()].count("\n")+1
        ctx=src[max(0,m.start()-60):m.start()+100].replace("\n"," | ")
        P(f"  L{linha} [{kw}]: ...{ctx}...")
        break

P("\n--- metodo que ativa o modo via (toggle) ---")
for nome in ["_toggle_via","_modo_via_toggle","_ativar_via","_entrar_via","_set_modo_via","_alternar_via"]:
    m=re.search(rf"    def {re.escape(nome)}\(self.*?(?=\n    def )", src, re.DOTALL)
    if m:
        P(f"  def {nome}:")
        for i,l in enumerate(m.group(0).split("\n")):
            P(f"  {i:3}: {l}")
        break

P("\n--- onde o botao 'Modo Via' e criado ---")
for m in re.finditer(r'(Modo Via|🛣|Modo arte)', src):
    linha=src[:m.start()].count("\n")+1
    ini=src.rfind("\n",0,m.start()-150)
    P(f"--- L{linha} ---")
    for l in src[ini:m.end()+250].split("\n")[:12]:
        P(f"  {l}")
    P("")
    break

P("\n--- self._modo_via referencias (estado) ---")
for m in re.finditer(r'self\._modo_via', src):
    linha=src[:m.start()].count("\n")+1
    P(f"  L{linha}: {src[m.start():m.start()+80].splitlines()[0]}")
    if len([x for x in out if x.startswith('  L')])>20: break

Path("diag_modovia.txt").write_text("\n".join(out),encoding="utf-8")
print("OK diag_modovia.txt")
