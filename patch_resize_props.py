"""
patch_resize_props.py — Resize nao reconstroi painel inteiro
Guarda ref dos campos Largura/Altura e atualiza so eles.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: _campo guarda ref de Largura e Altura
# Ja guarda _rot_var para "Rotacao". Adicionar Largura/Altura.
# ══════════════════════════════════════════════
old = '''            # Guarda ref do campo Rotacao para update rapido
            if label == "Rotacao":
                self._rot_var = var'''

new = '''            # Guarda refs para update rapido sem reconstruir painel
            if label == "Rotacao":
                self._rot_var = var
            elif label.startswith("Largura"):
                self._larg_var = var
            elif label.startswith("Altura"):
                self._alt_var = var'''

if old in src:
    src = src.replace(old, new, 1)
    print("PATCH 1 OK — refs Largura/Altura guardadas")
else:
    print("PATCH 1 ERRO — bloco _rot_var nao bate")
    m = re.search(r'if label == "Rotacao":.*?self\._rot_var = var', src, re.DOTALL)
    if m:
        print("Atual:")
        for l in m.group(0).split("\n"): print(f"  |{l}")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 2: _drag resize — atualiza so os campos, nao reconstroi
# ══════════════════════════════════════════════
old_drag = '''                el["larg"] = max(3, round(self._resize_larg0 * fator, 1))
                el["alt"]  = max(2, round(self._resize_alt0  * fator, 1))
                self._redesenhar()
                if self.sel_idx is not None:
                    self._mostrar_props(self.sel_idx)
            return'''

new_drag = '''                el["larg"] = max(3, round(self._resize_larg0 * fator, 1))
                el["alt"]  = max(2, round(self._resize_alt0  * fator, 1))
                self._redesenhar()
                # Atualiza SO os campos largura/altura (nao reconstroi)
                k = self.k if (self.calibrado and self.k) else 1.0
                ft = k if self.calibrado else 1.0
                lv = getattr(self, "_larg_var", None)
                av = getattr(self, "_alt_var", None)
                try:
                    if lv is not None: lv.set(f"{el['larg']*ft:.2f}")
                    if av is not None: av.set(f"{el['alt']*ft:.2f}")
                except Exception:
                    pass
            return'''

if old_drag in src:
    src = src.replace(old_drag, new_drag, 1)
    print("PATCH 2 OK — _drag resize atualiza so campos")
else:
    print("PATCH 2 ERRO — bloco _drag resize nao bate")
    m = re.search(r'el\["larg"\] = max\(3.*?return', src, re.DOTALL)
    if m:
        print("Atual:")
        for l in m.group(0).split("\n"): print(f"  |{l}")
    raise SystemExit

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
print("Teste: redimensionar — painel NAO pisca, so Largura/Altura mudam")
