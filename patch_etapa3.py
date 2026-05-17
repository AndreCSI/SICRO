"""
patch_etapa3.py — Integra o motor SVG no _veiculo_arte (Etapa 3)
Ordem de prioridade: SVG -> PNG -> vetorial.
Fallback total: sem SVG, comportamento 100% identico ao atual.
Requer: desenho/render_svg.py e desenho/catalogo_veiculos.py instalados.
"""
from pathlib import Path
import ast

for dep in ["desenho/render_svg.py", "desenho/catalogo_veiculos.py"]:
    if not Path(dep).exists():
        print(f"ATENCAO: {dep} NAO encontrado. Instale antes deste patch.")
        raise SystemExit

ep = Path("ui")/"editor_croqui.py"
src = ep.read_text(encoding="utf-8")
src_orig = src

# ── 1. Import do motor + catalogo (apos import do popup_veiculo) ──
old_imp = "from popups.popup_veiculo import PopupModeloVeiculo, MODELOS_VEICULOS"
new_imp = ("from popups.popup_veiculo import PopupModeloVeiculo, MODELOS_VEICULOS\n"
           "from desenho import render_svg\n"
           "from desenho import catalogo_veiculos")
if old_imp in src and "from desenho import render_svg" not in src:
    src = src.replace(old_imp, new_imp, 1)
    print("1 OK - imports render_svg + catalogo_veiculos")
elif "from desenho import render_svg" in src:
    print("1 SKIP - imports ja presentes")
else:
    print("1 ERRO - linha de import base nao encontrada")
    raise SystemExit

# ── 2. _veiculo_arte: adiciona parametro svg_nome e tentativa SVG ──
old_sig = '''    def _veiculo_arte(self, tx, ty, angulo, larg, alt, cor, label, arte_fn, png=None):
        """
        Desenha veículo com PNG (se disponível) ou arte vetorial.
        Rotação via PIL para PNG, via polígonos rotacionados para vetorial.
        """
        c = self.canvas
        sc = self.zoom
        desenhado = False

        # ── Tenta renderizar via PNG ──
        if PIL_OK and png:'''

new_sig = '''    def _veiculo_arte(self, tx, ty, angulo, larg, alt, cor, label, arte_fn, png=None, svg_nome=None):
        """
        Desenha veículo. Ordem de prioridade:
          1. SVG por camadas (novo motor) — se o .svg existir na pasta
          2. PNG tinturizado (legado)
          3. Arte vetorial (fallback final)
        Sem SVG presente, comporta-se exatamente como antes.
        """
        c = self.canvas
        sc = self.zoom
        desenhado = False

        # ── 1) Tenta renderizar via SVG (motor novo) ──
        if PIL_OK and svg_nome:
            try:
                # Tamanho em pixels conforme zoom (mesma proporcao do PNG)
                tw = max(4, int(larg * sc * 1.6))
                th = max(4, int(alt  * sc * 2.8))
                img_svg = render_svg.render_veiculo(
                    svg_nome, cor, tw, th, angulo % 360)
                if img_svg is not None:
                    tk_img = ImageTk.PhotoImage(img_svg)
                    if not hasattr(self, "_tk_imgs"):
                        self._tk_imgs = []
                    self._tk_imgs.append(tk_img)
                    c.create_image(tx, ty, image=tk_img, anchor="center")
                    desenhado = True
            except Exception as e:
                print(f"[SVG render] {e}")

        # ── 2) Tenta renderizar via PNG ──
        if not desenhado and PIL_OK and png:'''

if old_sig in src:
    src = src.replace(old_sig, new_sig, 1)
    print("2 OK - _veiculo_arte com tentativa SVG (prioridade 1)")
else:
    print("2 ERRO - assinatura/inicio de _veiculo_arte nao bate")
    raise SystemExit

# ── 3. Bloco que decide a arte: descobrir svg_nome pelo catalogo ──
old_blk = '''            # Busca função de arte e PNG do modelo
            arte_fn = None
            png_file = None
            modelo_chave = el.get("modelo")
            if modelo_chave and tipo in MODELOS_VEICULOS:
                for m in MODELOS_VEICULOS[tipo]:
                    if m["chave"] == modelo_chave:
                        arte_fn = m["arte"]
                        png_file = m.get("png")
                        break
            if tipo == "bicicleta": arte_fn = _arte_bicicleta
            if tipo == "pedestre":  arte_fn = _arte_pedestre

            if arte_fn:
                self._veiculo_arte(tx, ty, ang, larg, alt, cor, label, arte_fn, png=png_file)'''

new_blk = '''            # Busca função de arte e PNG do modelo
            arte_fn = None
            png_file = None
            svg_nome = None
            modelo_chave = el.get("modelo")
            if modelo_chave and tipo in MODELOS_VEICULOS:
                for m in MODELOS_VEICULOS[tipo]:
                    if m["chave"] == modelo_chave:
                        arte_fn = m["arte"]
                        png_file = m.get("png")
                        break
            if tipo == "bicicleta": arte_fn = _arte_bicicleta
            if tipo == "pedestre":  arte_fn = _arte_pedestre

            # Descobre o SVG pelo catalogo (nova arquitetura).
            # A chave do modelo pode estar no catalogo novo (32 itens);
            # se houver svg correspondente, o motor o usa.
            try:
                _citem = catalogo_veiculos.get(modelo_chave) if modelo_chave else None
                if _citem:
                    svg_nome = _citem.get("svg")
            except Exception:
                svg_nome = None

            if arte_fn or svg_nome:
                self._veiculo_arte(tx, ty, ang, larg, alt, cor, label,
                                   arte_fn, png=png_file, svg_nome=svg_nome)'''

if old_blk in src:
    src = src.replace(old_blk, new_blk, 1)
    print("3 OK - bloco de decisao busca svg_nome no catalogo")
else:
    print("3 ERRO - bloco de decisao de arte nao bate")
    raise SystemExit

ep.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO {e.lineno}: {e.msg}")
    ln=src.split("\n")
    for i in range(max(0,e.lineno-4),min(len(ln),e.lineno+3)):
        print(f"  {i+1:4}: {ln[i]}")
    ep.write_text(src_orig, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste CRITICO (garantir que nada quebrou):")
print("  1. Programa abre normalmente")
print("  2. Inserir Carro -> escolher Sedan -> desenha como ANTES")
print("     (ainda nao ha SVG, entao usa PNG/vetorial = identico)")
print("  3. Moto, Caminhao, Bicicleta, Pedestre -> todos como antes")
print("  4. Girar/redimensionar veiculo -> funciona como antes")
print("  Nada deve mudar visualmente — a integracao e invisivel ate")
print("  os SVGs chegarem na pasta assets/veiculos/")
