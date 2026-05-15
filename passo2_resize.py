"""
passo2_resize.py — Handles de canto para redimensionar (proporcional)
4 quadradinhos dourados nos cantos. Arrastar = redimensiona mantendo proporcao.
Mesma tecnica do handle de rotacao.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: Helper _draw_handles_canto
# Desenha 4 quadradinhos nos cantos do objeto (considerando angulo)
# Guarda posicoes em self._canto_handles = [(hx,hy,raio,nome),...]
# ══════════════════════════════════════════════
helper = '''    def _draw_handles_canto(self, el, tx, ty):
        """Desenha 4 handles de canto e guarda posicoes para hit-test."""
        import math
        tipo = el.get("tipo")
        larg_padrao={"carro":28,"moto":20,"caminhao":36,"bicicleta":16,"pedestre":14,"sc":20}
        alt_padrao= {"carro":14,"moto":8, "caminhao":16,"bicicleta":5, "pedestre":14,"sc":20}
        if tipo not in larg_padrao:
            self._canto_handles = []
            return
        larg = el.get("larg", larg_padrao[tipo]) * self.zoom
        alt  = el.get("alt",  alt_padrao[tipo]) * self.zoom
        ang  = math.radians(el.get("angulo", 0))
        ca, sa = math.cos(ang), math.sin(ang)
        hw, hh = larg/2, alt/2
        # 4 cantos relativos ao centro (antes de rotacionar)
        cantos = {
            "nw": (-hw, -hh), "ne": (hw, -hh),
            "se": (hw, hh),   "sw": (-hw, hh),
        }
        c = self.canvas
        self._canto_handles = []
        r = 5
        for nome, (dx, dy) in cantos.items():
            # Rotaciona o offset
            hx = tx + dx*ca - dy*sa
            hy = ty + dx*sa + dy*ca
            c.create_rectangle(hx-r, hy-r, hx+r, hy+r,
                               fill=FUNDO_PAINEL, outline=DOURADO, width=2)
            self._canto_handles.append((hx, hy, r+4, nome))

'''

idx = src.find("    def _draw_handle_rot(self, el, tx, ty):")
if idx < 0:
    print("ERRO: _draw_handle_rot nao encontrado")
    raise SystemExit
src = src[:idx] + helper + src[idx:]
print("PATCH 1 OK — helper _draw_handles_canto adicionado")

# ══════════════════════════════════════════════
# PATCH 2: Chamar no wrapper _desenhar_el
# ══════════════════════════════════════════════
old_wrapper = '''    def _desenhar_el(self, el, sel=False):
        self._desenhar_el_orig(el, sel)
        if sel and el.get("tipo") in ("carro","moto","caminhao",
                                       "bicicleta","pedestre","sc"):
            tx, ty = self._mt(el.get("x",0), el.get("y",0))
            self._draw_handle_rot(el, tx, ty)'''

new_wrapper = '''    def _desenhar_el(self, el, sel=False):
        self._desenhar_el_orig(el, sel)
        if sel and el.get("tipo") in ("carro","moto","caminhao",
                                       "bicicleta","pedestre","sc"):
            tx, ty = self._mt(el.get("x",0), el.get("y",0))
            self._draw_handles_canto(el, tx, ty)
            self._draw_handle_rot(el, tx, ty)'''

if old_wrapper in src:
    src = src.replace(old_wrapper, new_wrapper, 1)
    print("PATCH 2 OK — wrapper chama handles de canto")
else:
    print("PATCH 2 ERRO — wrapper nao bate")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 3: _click detecta clique em handle de canto
# Inserir ANTES da deteccao de rotacao
# ══════════════════════════════════════════════
old_click = '''        # Detecta clique no handle de rotacao
        if f=="sel" and self.sel_idx is not None:
            hp = getattr(self, "_rot_handle_pos", None)
            if hp is not None:
                hx, hy, hr = hp
                if (e.x-hx)**2 + (e.y-hy)**2 <= (hr+4)**2:
                    self._rotacionando = True
                    self._salvar_historico()
                    return'''

new_click = '''        # Detecta clique em handle de CANTO (resize)
        if f=="sel" and self.sel_idx is not None:
            for hx, hy, hr, nome in getattr(self, "_canto_handles", []):
                if (e.x-hx)**2 + (e.y-hy)**2 <= (hr+4)**2:
                    self._redimensionando = nome
                    self._salvar_historico()
                    el = self.elementos[self.sel_idx]
                    # Guarda larg/alt inicial e ponto inicial do mouse
                    import math
                    larg_p={"carro":28,"moto":20,"caminhao":36,
                            "bicicleta":16,"pedestre":14,"sc":20}
                    alt_p= {"carro":14,"moto":8,"caminhao":16,
                            "bicicleta":5,"pedestre":14,"sc":20}
                    t = el.get("tipo")
                    self._resize_larg0 = el.get("larg", larg_p.get(t,28))
                    self._resize_alt0  = el.get("alt",  alt_p.get(t,14))
                    self._resize_mouse0 = (e.x, e.y)
                    self._resize_cx, self._resize_cy = self._mt(
                        el.get("x",0), el.get("y",0))
                    return
        # Detecta clique no handle de rotacao
        if f=="sel" and self.sel_idx is not None:
            hp = getattr(self, "_rot_handle_pos", None)
            if hp is not None:
                hx, hy, hr = hp
                if (e.x-hx)**2 + (e.y-hy)**2 <= (hr+4)**2:
                    self._rotacionando = True
                    self._salvar_historico()
                    return'''

if old_click in src:
    src = src.replace(old_click, new_click, 1)
    print("PATCH 3 OK — _click detecta canto")
else:
    print("PATCH 3 ERRO — _click rotacao nao bate")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 4: _drag — se redimensionando, calcula nova escala
# Inserir ANTES do bloco de rotacao
# ══════════════════════════════════════════════
old_drag = '''        # Modo rotacao ativo
        if getattr(self, "_rotacionando", False) and self.sel_idx is not None:'''

new_drag = '''        # Modo redimensionar ativo (proporcional pelos cantos)
        if getattr(self, "_redimensionando", None) and self.sel_idx is not None:
            import math
            el = self.elementos[self.sel_idx]
            mx0, my0 = self._resize_mouse0
            cx, cy = self._resize_cx, self._resize_cy
            # Distancia do centro ao mouse inicial e atual
            d0 = math.hypot(mx0 - cx, my0 - cy)
            d1 = math.hypot(e.x - cx, e.y - cy)
            if d0 > 1:
                fator = d1 / d0
                fator = max(0.2, min(5.0, fator))  # limites sensatos
                el["larg"] = max(3, round(self._resize_larg0 * fator, 1))
                el["alt"]  = max(2, round(self._resize_alt0  * fator, 1))
                self._redesenhar()
                if self.sel_idx is not None:
                    self._mostrar_props(self.sel_idx)
            return
        # Modo rotacao ativo
        if getattr(self, "_rotacionando", False) and self.sel_idx is not None:'''

if old_drag in src:
    src = src.replace(old_drag, new_drag, 1)
    print("PATCH 4 OK — _drag redimensiona")
else:
    print("PATCH 4 ERRO")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 5: _release limpa _redimensionando
# ══════════════════════════════════════════════
old_rel = '''        if getattr(self, "_rotacionando", False):
            self._rotacionando = False
            self._redesenhar()
            if self.sel_idx is not None:
                self._mostrar_props(self.sel_idx)
            return'''

new_rel = '''        if getattr(self, "_redimensionando", None):
            self._redimensionando = None
            self._redesenhar()
            if self.sel_idx is not None:
                self._mostrar_props(self.sel_idx)
            return
        if getattr(self, "_rotacionando", False):
            self._rotacionando = False
            self._redesenhar()
            if self.sel_idx is not None:
                self._mostrar_props(self.sel_idx)
            return'''

if old_rel in src:
    src = src.replace(old_rel, new_rel, 1)
    print("PATCH 5 OK — _release limpa resize")
else:
    print("PATCH 5 ERRO")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO linha {e.lineno}: {e.msg}")
    linhas=src.split("\n")
    for i in range(max(0,e.lineno-4),min(len(linhas),e.lineno+3)):
        print(f"  {i+1:4}: {linhas[i]}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste:")
print("  1. Insira um carro, selecione")
print("  2. 4 quadradinhos dourados nos cantos + bolinha rotacao no topo")
print("  3. Arraste um canto — carro aumenta/diminui proporcional")
print("  4. Largura e Altura no painel atualizam")
print("  5. Rotacao ainda funciona (bolinha do topo)")
