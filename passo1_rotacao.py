"""
passo1_rotacao.py — Handle de rotacao nos objetos
Adiciona bolinha dourada acima do objeto selecionado.
Arrastar ela gira o objeto.
NAO altera fluxo de mover/inserir existente.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: Desenhar handle de rotacao no _desenhar_el
# Achar o bloco dos veiculos (tipo in larg_padrao) e adicionar
# a bolinha de rotacao quando sel=True
# ══════════════════════════════════════════════
# Procura onde desenha o objeto veiculo selecionado.
# Pelo diagnostico, veiculos usam larg_padrao. Vou achar onde
# termina o desenho do veiculo e adicionar handle de rotacao.
# Estrategia: inserir um metodo helper _desenhar_handle_rotacao
# e chama-lo no final de _desenhar_el quando sel=True para tipos giraveis.

# Adiciona metodo helper antes de _desenhar_el
helper = '''    def _draw_handle_rot(self, el, tx, ty):
        """Desenha a bolinha de rotacao acima do objeto e guarda sua posicao."""
        tipo = el.get("tipo")
        if tipo not in ("carro","moto","caminhao","bicicleta","pedestre","sc"):
            self._rot_handle_pos = None
            return
        # Calcula posicao acima do objeto, considerando o angulo
        import math
        larg_padrao={"carro":28,"moto":20,"caminhao":36,"bicicleta":16,"pedestre":14,"sc":20}
        alt_padrao= {"carro":14,"moto":8, "caminhao":16,"bicicleta":5, "pedestre":14,"sc":20}
        alt = el.get("alt", alt_padrao.get(tipo, 14))
        ang = math.radians(el.get("angulo", 0))
        # Distancia acima do objeto (em tela)
        dist = (alt/2 + 22) * self.zoom
        # Direcao "para cima" do objeto rotacionada
        hx = tx + dist * math.sin(ang)
        hy = ty - dist * math.cos(ang)
        c = self.canvas
        # Linha conectora
        c.create_line(tx, ty, hx, hy, fill=DOURADO,
                      width=max(1,int(self.zoom)), dash=(3,2))
        # Bolinha
        r = 7
        c.create_oval(hx-r, hy-r, hx+r, hy+r,
                      fill=FUNDO_PAINEL, outline=DOURADO, width=2)
        # Icone de rotacao (arco)
        c.create_arc(hx-4, hy-4, hx+4, hy+4,
                     start=30, extent=240, style="arc",
                     outline=DOURADO, width=2)
        # Guarda posicao para hit-test (em coordenadas de tela)
        self._rot_handle_pos = (hx, hy, r + 4)

'''

# Insere helper antes de "    def _desenhar_el"
idx = src.find("    def _desenhar_el(self,el,sel=False):")
if idx < 0:
    print("ERRO: _desenhar_el nao encontrado")
    raise SystemExit
src = src[:idx] + helper + src[idx:]
print("PATCH 1 OK — helper _draw_handle_rot adicionado")

# ══════════════════════════════════════════════
# PATCH 2: Chamar _draw_handle_rot quando sel=True
# No _desenhar_el, no bloco dos veiculos selecionados
# Procuramos onde desenha veiculo e adicionamos no final
# ══════════════════════════════════════════════
# O jeito mais seguro: no inicio do _desenhar_el, apos calcular tx,ty,
# guardamos. Depois adicionamos chamada quando sel.
# Vamos achar "if tipo in larg_padrao:" e dentro dele, o "if sel"
# Pelo diagnostico, ha um padrao de desenho. Vamos inserir a chamada
# logo apos a definicao de tx,ty no inicio, condicionada a sel.

# Estrategia mais robusta: adicionar no FIM do _desenhar_el uma chamada
# que desenha o handle se sel e tipo for giravel.
# Acha o fim do metodo _desenhar_el (proximo "    def ")
m = re.search(r"(    def _desenhar_el\(self,el,sel=False\):.*?)(\n    def )", src, re.DOTALL)
if not m:
    print("ERRO: corpo _desenhar_el nao localizado")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

corpo = m.group(1)
# Adiciona no inicio do corpo: se sel e giravel, agenda desenho do handle
# Melhor: inserir logo apos "tx,ty=self._mt(...)" a marcacao, e desenhar
# o handle no final. Como ha muitos 'return' no meio, a abordagem segura
# e desenhar o handle ANTES dos returns dos veiculos.
# Solucao pragmatica: cria wrapper. Renomeia _desenhar_el original e
# cria novo que chama original e depois desenha handle.

# Renomeia metodo original
src = src.replace(
    "    def _desenhar_el(self,el,sel=False):",
    "    def _desenhar_el_orig(self,el,sel=False):",
    1
)
# Cria wrapper logo antes do _desenhar_el_orig
wrapper = '''    def _desenhar_el(self, el, sel=False):
        self._desenhar_el_orig(el, sel)
        if sel and el.get("tipo") in ("carro","moto","caminhao",
                                       "bicicleta","pedestre","sc"):
            tx, ty = self._mt(el.get("x",0), el.get("y",0))
            self._draw_handle_rot(el, tx, ty)

'''
idx = src.find("    def _desenhar_el_orig(self,el,sel=False):")
src = src[:idx] + wrapper + src[idx:]
print("PATCH 2 OK — wrapper _desenhar_el criado")

# ══════════════════════════════════════════════
# PATCH 3: Detectar clique no handle de rotacao no _click
# Intercepta ANTES de _selecionar
# ══════════════════════════════════════════════
old_click = '''    def _click(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._click_via(e, x, y)
            return
        f=self.ferramenta
        if f=="sel":         self._selecionar(x,y)'''

new_click = '''    def _click(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._click_via(e, x, y)
            return
        f=self.ferramenta
        # Detecta clique no handle de rotacao
        if f=="sel" and self.sel_idx is not None:
            hp = getattr(self, "_rot_handle_pos", None)
            if hp is not None:
                hx, hy, hr = hp
                if (e.x-hx)**2 + (e.y-hy)**2 <= (hr+4)**2:
                    self._rotacionando = True
                    self._salvar_historico()
                    return
        if f=="sel":         self._selecionar(x,y)'''

if old_click in src:
    src = src.replace(old_click, new_click, 1)
    print("PATCH 3 OK — _click detecta handle de rotacao")
else:
    print("PATCH 3 ERRO — _click nao bate")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 4: No _drag, se rotacionando, calcular angulo
# ══════════════════════════════════════════════
old_drag = '''    def _drag(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._drag_via(e, x, y)
            return
        if self.ferramenta=="sel" and self.sel_idx is not None and self.drag_start:'''

new_drag = '''    def _drag(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._drag_via(e, x, y)
            return
        # Modo rotacao ativo
        if getattr(self, "_rotacionando", False) and self.sel_idx is not None:
            import math
            el = self.elementos[self.sel_idx]
            cx, cy = el.get("x",0), el.get("y",0)
            # Angulo entre centro do objeto e o mouse (em metros)
            dx = x - cx
            dy = y - cy
            # atan2 com Y invertido (tela cresce pra baixo)
            ang = math.degrees(math.atan2(dx, -dy))
            el["angulo"] = round(ang, 1)
            self._redesenhar()
            if self.sel_idx is not None:
                self._mostrar_props(self.sel_idx)
            return
        if self.ferramenta=="sel" and self.sel_idx is not None and self.drag_start:'''

if old_drag in src:
    src = src.replace(old_drag, new_drag, 1)
    print("PATCH 4 OK — _drag calcula rotacao")
else:
    print("PATCH 4 ERRO — _drag nao bate")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 5: No _release, limpar _rotacionando
# ══════════════════════════════════════════════
old_release = '''    def _release(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._release_via(e, x, y)
            return'''

new_release = '''    def _release(self,e):
        x,y=self._tm(e.x,e.y)
        if self._modo_via:
            self._release_via(e, x, y)
            return
        if getattr(self, "_rotacionando", False):
            self._rotacionando = False
            self._redesenhar()
            return'''

if old_release in src:
    src = src.replace(old_release, new_release, 1)
    print("PATCH 5 OK — _release limpa rotacao")
else:
    print("PATCH 5 ERRO — _release nao bate")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

# Salva e valida
editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO linha {e.lineno}: {e.msg}")
    linhas = src.split("\n")
    for i in range(max(0,e.lineno-4), min(len(linhas),e.lineno+3)):
        print(f"  {i+1:4}: {linhas[i]}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste:")
print("  1. Insira um carro")
print("  2. Clique nele (ferramenta Selecionar)")
print("  3. Aparece bolinha dourada acima do carro com icone de giro")
print("  4. Arraste a bolinha — carro gira")
print("  5. Campo Rotacao no painel atualiza junto")
