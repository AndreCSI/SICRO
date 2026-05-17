"""
diag_svglib.py — Verifica dependencias do motor SVG no SEU ambiente.
Nao modifica nada. So testa o que esta instalado e o que falta.
"""
from pathlib import Path
import sys
out=[]
def P(s=""): out.append(str(s))

P("="*60)
P("DIAGNOSTICO DEPENDENCIAS — MOTOR SVG")
P("="*60)
P(f"Python: {sys.version.split()[0]}")
P(f"Executavel: {sys.executable}")

# Testa cada biblioteca necessaria
libs = {
    "svglib": "svglib.svglib",
    "reportlab": "reportlab",
    "PIL": "PIL",
    "lxml": "lxml",
}
P("\nBibliotecas:")
faltando = []
for nome, mod in libs.items():
    try:
        __import__(mod)
        v = ""
        try:
            m = __import__(mod.split(".")[0])
            v = getattr(m, "__version__", "")
        except Exception:
            pass
        P(f"  [OK]    {nome} {v}")
    except ImportError as e:
        P(f"  [FALTA] {nome}  -> {e}")
        faltando.append(nome)

# Teste funcional real: criar SVG ficticio, trocar cor, rasterizar
P("\n"+"="*60)
P("TESTE FUNCIONAL (SVG ficticio -> troca cor -> PNG)")
P("="*60)
if not faltando:
    try:
        import io, re
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        from PIL import Image

        svg_teste = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60">
  <g id="sombra"><ellipse cx="50" cy="32" rx="44" ry="22" fill="#000000" fill-opacity="0.15"/></g>
  <g id="corpo"><rect x="15" y="12" width="70" height="36" rx="6" fill="#CC0000"/></g>
  <g id="vidros"><rect x="55" y="18" width="22" height="24" fill="#3A4A5A"/></g>
</svg>'''
        # Troca a cor do corpo
        nova_cor = "#1E88E5"
        svg_mod = svg_teste.replace("#CC0000", nova_cor)
        P(f"Troca de cor: #CC0000 -> {nova_cor}")
        P(f"Ocorrencias trocadas: {svg_teste.count('#CC0000')}")

        # Rasteriza
        tmp = Path("/tmp/_sicro_svgtest.svg") if Path("/tmp").exists() else Path("_svgtest.svg")
        tmp.write_text(svg_mod, encoding="utf-8")
        desenho = svg2rlg(str(tmp))
        if desenho is None:
            P("[ERRO] svg2rlg retornou None")
        else:
            P(f"svg2rlg OK — dimensoes: {desenho.width:.0f} x {desenho.height:.0f}")
            png_path = str(tmp).replace(".svg", ".png")
            renderPM.drawToFile(desenho, png_path, fmt="PNG")
            img = Image.open(png_path)
            P(f"Rasterizacao OK — PNG {img.size}, modo {img.mode}")
            # Confirma que a cor mudou (pega um pixel do centro)
            img = img.convert("RGB")
            cx, cy = img.width//2, img.height//2
            px = img.getpixel((cx, cy))
            P(f"Pixel central RGB: {px}  (esperado proximo de azul ~30,136,229)")
            # Rotacao
            img_rot = img.rotate(45, expand=True)
            P(f"Rotacao 45deg OK — novo size {img_rot.size}")
            try:
                tmp.unlink(); Path(png_path).unlink()
            except Exception:
                pass
        P("\n>>> MOTOR SVG VIAVEL NESTE AMBIENTE <<<")
    except Exception as e:
        import traceback
        P(f"[ERRO no teste funcional] {e}")
        P(traceback.format_exc())
else:
    P(f"Instale antes: pip install {' '.join(faltando)}")
    P("Comando sugerido:")
    P(f"  pip install svglib reportlab pillow lxml")

Path("diag_svglib.txt").write_text("\n".join(out), encoding="utf-8")
print("OK diag_svglib.txt")
