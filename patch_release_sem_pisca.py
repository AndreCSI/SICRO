"""
patch_release_sem_pisca.py — Remove a reconstrucao do painel no _release
Os campos ja estao corretos durante o arraste (rotacao/resize),
entao reconstruir no release so causa a piscada final.
"""
from pathlib import Path
import ast

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# RESIZE release: remove _mostrar_props
old_resize = '''        if getattr(self, "_redimensionando", None):
            self._redimensionando = None
            self._redesenhar()
            if self.sel_idx is not None:
                self._mostrar_props(self.sel_idx)
            return'''
new_resize = '''        if getattr(self, "_redimensionando", None):
            self._redimensionando = None
            self._redesenhar()
            return'''

if old_resize in src:
    src = src.replace(old_resize, new_resize, 1)
    print("PATCH 1 OK — release resize sem reconstruir painel")
else:
    print("PATCH 1 SKIP")

# ROTACAO release: remove _mostrar_props
old_rot = '''        if getattr(self, "_rotacionando", False):
            self._rotacionando = False
            self._redesenhar()
            if self.sel_idx is not None:
                self._mostrar_props(self.sel_idx)
            return'''
new_rot = '''        if getattr(self, "_rotacionando", False):
            self._rotacionando = False
            self._redesenhar()
            return'''

if old_rot in src:
    src = src.replace(old_rot, new_rot, 1)
    print("PATCH 2 OK — release rotacao sem reconstruir painel")
else:
    print("PATCH 2 SKIP")

editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO: {e}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste: girar/redimensionar e soltar — SEM piscada final")
