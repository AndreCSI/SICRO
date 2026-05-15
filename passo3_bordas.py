"""
passo3_bordas.py — Handles de BORDA (resize em um eixo)
4 quadradinhos no meio de cada lado.
Borda L/R = so largura. Borda T/B = so altura.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: Helper _draw_handles_borda
# ══════════════════════════════════════════════
helper = '''    def _draw_handles_borda(self, el, tx, ty):
        """Desenha 4 handles de borda (meio dos lados) para resize 1 eixo."""
        import math
        tipo = el.get("tipo")
        larg_padrao={"carro":28,"moto":20,"caminhao":36,"bicicleta":16,"pedestre":14,"sc":20}
        alt_padrao= {"carro":14,"moto":8, "caminhao":16,"bicicleta":5, "pedestre":14,"sc":20}
        if tipo not in larg_padrao:
            self._borda_handles = []
            return
        larg = el.get("larg", larg_padrao[tipo]) * self.zoom
        alt  = el.get("alt",  alt_padrao[tipo]) * self.zoom
        ang  = math.radians(el.get("angulo", 0))
        ca, sa = math.cos(ang), math.sin(ang)
        hw, hh = larg/2, alt/2
        # Meio de cada lado: n(topo) s(baixo) e(direita) w(esquerda)
        lados = {
            "n": (0, -hh), "s": (0, hh),
            "e": (hw, 0),  "w": (-hw, 0),
        }
        c = self.canvas
        self._borda_handles = []
        r = 5
        for nome, (dx, dy) in lados.items():
            hx = tx + dx*ca - dy*sa
            hy = ty + dx*sa + dy*ca
            # Quadradinho levemente diferente (sem preenchimento solido)
            c.create_rectangle(hx-r, hy-r, hx+r, hy+r,
                               fill=FUNDO_PAINEL, outline=DOURADO, width=2)
            self._borda_handles.append((hx, hy, r+4, nome))

'''

idx = src.find("    def _draw_handles_canto(self, el, tx, ty):")
if idx < 0:
    print("ERRO: _draw_handles_canto nao encontrado")
    raise SystemExit
src = src[:idx] + helper + src[idx:]
print("PATCH 1 OK — helper _draw_handles_borda")

# ══════════════════════════════════════════════
# PATCH 2: chamar no wrapper
# ══════════════════════════════════════════════
old_wrap = '''            tx, ty = self._mt(el.get("x",0), el.get("y",0))
            self._draw_handles_canto(el, tx, ty)
            self._draw_handle_rot(el, tx, ty)'''
new_wrap = '''            tx, ty = self._mt(el.get("x",0), el.get("y",0))
            self._draw_handles_canto(el, tx, ty)
            self._draw_handles_borda(el, tx, ty)
            self._draw_handle_rot(el, tx, ty)'''

if old_wrap in src:
    src = src.replace(old_wrap, new_wrap, 1)
    print("PATCH 2 OK — wrapper chama bordas")
else:
    print("PATCH 2 ERRO")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 3: _click detecta borda (ANTES dos cantos)
# ══════════════════════════════════════════════
old_click = '''        # Detecta clique em handle de CANTO (resize)
        if f=="sel" and self.sel_idx is not None:
            for hx, hy, hr, nome in getattr(self, "_canto_handles", []):'''

new_click = '''        # Detecta clique em handle de BORDA (resize 1 eixo)
        if f=="sel" and self.sel_idx is not None:
            for hx, hy, hr, nome in getattr(self, "_borda_handles", []):
                if (e.x-hx)**2 + (e.y-hy)**2 <= (hr+4)**2:
                    self._resize_borda = nome
                    self._salvar_historico()
                    el = self.elementos[self.sel_idx]
                    import math
                    larg_p={"carro":28,"moto":20,"caminhao":36,
                            "bicicleta":16,"pedestre":14,"sc":20}
                    alt_p= {"carro":14,"moto":8,"caminhao":16,
                            "bicicleta":5,"pedestre":14,"sc":20}
                    t = el.get("tipo")
                    self._rb_larg0 = el.get("larg", larg_p.get(t,28))
                    self._rb_alt0  = el.get("alt",  alt_p.get(t,14))
                    self._rb_mouse0 = (e.x, e.y)
                    self._rb_cx, self._rb_cy = self._mt(
                        el.get("x",0), el.get("y",0))
                    self._rb_ang = el.get("angulo", 0)
                    return
        # Detecta clique em handle de CANTO (resize)
        if f=="sel" and self.sel_idx is not None:
            for hx, hy, hr, nome in getattr(self, "_canto_handles", []):'''

if old_click in src:
    src = src.replace(old_click, new_click, 1)
    print("PATCH 3 OK — _click detecta borda")
else:
    print("PATCH 3 ERRO")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 4: _drag — resize por borda (projeta movimento no eixo)
# ANTES do bloco de resize por canto
# ══════════════════════════════════════════════
old_drag = '''        # Modo redimensionar ativo (proporcional pelos cantos)
        if getattr(self, "_redimensionando", None) and self.sel_idx is not None:'''

new_drag = '''        # Modo resize por BORDA (um eixo so)
        if getattr(self, "_resize_borda", None) and self.sel_idx is not None:
            import math
            el = self.elementos[self.sel_idx]
            nome = self._resize_borda
            mx0, my0 = self._rb_mouse0
            # Vetor de movimento do mouse (em tela)
            dxm = e.x - mx0
            dym = e.y - my0
            # Projeta no eixo local do objeto (considera rotacao)
            ang = math.radians(self._rb_ang)
            ca, sa = math.cos(ang), math.sin(ang)
            # eixo X local (largura) e Y local (altura) em tela
            # desfaz rotacao para achar delta no eixo do objeto
            dlocal_x =  dxm*ca + dym*sa
            dlocal_y = -dxm*sa + dym*ca
            z = self.zoom if self.zoom else 1.0
            if nome in ("e", "w"):
                # Largura. Borda 'e' cresce com +x local, 'w' com -x
                sinal = 1 if nome == "e" else -1
                nova_larg = self._rb_larg0 + sinal * (dlocal_x / z) * 2
                el["larg"] = max(3, round(nova_larg, 1))
            else:
                # Altura. Borda 's' cresce com +y local, 'n' com -y
                sinal = 1 if nome == "s" else -1
                nova_alt = self._rb_alt0 + sinal * (dlocal_y / z) * 2
                el["alt"] = max(2, round(nova_alt, 1))
            self._redesenhar()
            k = self.k if (self.calibrado and self.k) else 1.0
            ft = k if self.calibrado else 1.0
            lv = getattr(self, "_larg_var", None)
            av = getattr(self, "_alt_var", None)
            try:
                if lv is not None: lv.set(f"{el.get('larg',0)*ft:.2f}")
                if av is not None: av.set(f"{el.get('alt',0)*ft:.2f}")
            except Exception:
                pass
            return
        # Modo redimensionar ativo (proporcional pelos cantos)
        if getattr(self, "_redimensionando", None) and self.sel_idx is not None:'''

if old_drag in src:
    src = src.replace(old_drag, new_drag, 1)
    print("PATCH 4 OK — _drag resize borda")
else:
    print("PATCH 4 ERRO")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 5: _release limpa _resize_borda
# ══════════════════════════════════════════════
old_rel = '''        if getattr(self, "_redimensionando", None):
            self._redimensionando = None
            self._redesenhar()
            return'''
new_rel = '''        if getattr(self, "_resize_borda", None):
            self._resize_borda = None
            self._redesenhar()
            return
        if getattr(self, "_redimensionando", None):
            self._redimensionando = None
            self._redesenhar()
            return'''

if old_rel in src:
    src = src.replace(old_rel, new_rel, 1)
    print("PATCH 5 OK — _release limpa borda")
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
print("  1. Insira carro, selecione")
print("  2. Agora tem 4 cantos + 4 bordas + bolinha rotacao")
print("  3. Arraste borda DIREITA/ESQUERDA — so largura muda")
print("  4. Arraste borda TOPO/BAIXO — so altura muda")
print("  5. Cantos ainda fazem proporcional, rotacao ainda gira")
