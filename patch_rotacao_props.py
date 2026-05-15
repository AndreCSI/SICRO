"""
patch_rotacao_props.py — Nao reconstruir painel inteiro durante rotacao
Guarda referencia ao campo de rotacao e atualiza so ele.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: No _mostrar_props, guardar ref do campo Rotacao
# Procura a criacao do campo "Rotacao" e guarda a StringVar
# ══════════════════════════════════════════════
# No fase5_v2, o campo rotacao e criado com:
#   _campo("Rotacao", f"{el.get('angulo', 0):.1f}", set_ang)
# A funcao _campo cria uma StringVar local. Vamos fazer ela
# guardar a var em self._rot_var quando o label for "Rotacao"

# Acha a funcao _campo dentro de _mostrar_props
old_campo = '''        def _campo(label, valor_str, on_change):
            """Cria um campo Entry editavel."""
            f = tk.Frame(self._props, bg=FUNDO_PAINEL)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                     width=11, anchor="w").pack(side="left")
            var = tk.StringVar(value=valor_str)'''

new_campo = '''        def _campo(label, valor_str, on_change):
            """Cria um campo Entry editavel."""
            f = tk.Frame(self._props, bg=FUNDO_PAINEL)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                     width=11, anchor="w").pack(side="left")
            var = tk.StringVar(value=valor_str)
            # Guarda ref do campo Rotacao para update rapido
            if label == "Rotacao":
                self._rot_var = var'''

if old_campo in src:
    src = src.replace(old_campo, new_campo, 1)
    print("PATCH 1 OK — _rot_var guardado")
else:
    print("PATCH 1 ERRO — funcao _campo nao bate")
    # Debug
    m = re.search(r"        def _campo\(label.*?var = tk\.StringVar\([^)]*\)", src, re.DOTALL)
    if m:
        print("Conteudo atual:")
        for l in m.group(0).split("\n"):
            print(f"  |{l}")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 2: No _drag (modo rotacao), em vez de _mostrar_props,
# atualizar so o self._rot_var
# ══════════════════════════════════════════════
old_drag_rot = '''            el["angulo"] = round(ang, 1)
            self._redesenhar()
            if self.sel_idx is not None:
                self._mostrar_props(self.sel_idx)
            return'''

new_drag_rot = '''            el["angulo"] = round(ang, 1)
            self._redesenhar()
            # Atualiza SO o campo de rotacao (nao reconstroi painel)
            rv = getattr(self, "_rot_var", None)
            if rv is not None:
                try:
                    rv.set(f"{el['angulo']:.1f}")
                except Exception:
                    pass
            return'''

if old_drag_rot in src:
    src = src.replace(old_drag_rot, new_drag_rot, 1)
    print("PATCH 2 OK — _drag atualiza so o campo rotacao")
else:
    print("PATCH 2 ERRO — bloco do _drag nao bate")
    m = re.search(r'el\["angulo"\] = round\(ang, 1\).*?return', src, re.DOTALL)
    if m:
        print("Conteudo atual:")
        for l in m.group(0).split("\n"):
            print(f"  |{l}")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 3: Ao soltar (_release rotacao), reconstroi painel
# uma vez so para garantir consistencia
# ══════════════════════════════════════════════
old_rel_rot = '''        if getattr(self, "_rotacionando", False):
            self._rotacionando = False
            self._redesenhar()
            return'''

new_rel_rot = '''        if getattr(self, "_rotacionando", False):
            self._rotacionando = False
            self._redesenhar()
            if self.sel_idx is not None:
                self._mostrar_props(self.sel_idx)
            return'''

if old_rel_rot in src:
    src = src.replace(old_rel_rot, new_rel_rot, 1)
    print("PATCH 3 OK — _release reconstroi painel uma vez")
else:
    print("PATCH 3 SKIP")

editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO linha {e.lineno}: {e.msg}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste: girar o veiculo — painel NAO pisca, so o numero muda")
