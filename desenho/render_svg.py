"""
desenho/render_svg.py — Motor de renderização de veículos via SVG.

Lê um SVG estruturado em camadas (conforme a especificação entregue ao
designer), substitui a cor da camada <g id="corpo"> pela cor escolhida
pelo perito, rasteriza, rotaciona e devolve um PIL.Image pronto para o
canvas. Tudo com cache (performance) e fallback gracioso.

Contrato com o resto do sistema:
    render_veiculo(svg_nome, cor_hex, larg_px, alt_px, angulo) -> PIL.Image | None

Se retornar None, o chamador deve usar a arte vetorial antiga
(o programa nunca quebra por falta de SVG).

Dependências (confirmadas no ambiente alvo):
    svglib 1.6.0, reportlab 4.5.1, PIL 12.x, lxml 6.x
"""
import io
import re
import sys
from pathlib import Path

_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))

# ── Dependências (degradam com elegância se faltarem) ──
try:
    from PIL import Image
    _PIL_OK = True
except Exception:
    _PIL_OK = False

try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    _SVG_OK = True
except Exception:
    _SVG_OK = False

# Placeholder de cor da camada "corpo" (definido na especificação)
_PLACEHOLDER = "#CC0000"

# Caches
_CACHE_BASE = {}   # (svg_nome, cor_hex, larg, alt) -> PIL.Image sem rotacao
_CACHE_ROT  = {}   # (svg_nome, cor_hex, larg, alt, ang) -> PIL.Image rotacionada
_SVG_FALTANDO = set()  # nomes de svg ja constatados ausentes (evita rechecar disco)

_MAX_CACHE = 400   # teto de itens por cache (evita vazar memoria em sessao longa)


def _dir_veiculos():
    """Pasta dos SVGs. Usa o resource_path do config (funciona no .exe)."""
    try:
        from config import DIR_ASSETS
        return Path(DIR_ASSETS)
    except Exception:
        return _raiz / "assets" / "veiculos"


def _norm_cor(cor_hex):
    """Normaliza cor para #RRGGBB maiúsculo. Default cinza se inválida."""
    if not cor_hex:
        return "#888888"
    c = str(cor_hex).strip()
    if not c.startswith("#"):
        c = "#" + c
    if len(c) == 4:  # #RGB -> #RRGGBB
        c = "#" + c[1]*2 + c[2]*2 + c[3]*2
    if len(c) != 7:
        return "#888888"
    try:
        int(c[1:], 16)
        return c.upper()
    except ValueError:
        return "#888888"


def svg_existe(svg_nome):
    """True se o arquivo SVG está disponível na pasta de veículos."""
    if not svg_nome:
        return False
    if svg_nome in _SVG_FALTANDO:
        return False
    p = _dir_veiculos() / svg_nome
    existe = p.is_file()
    if not existe:
        _SVG_FALTANDO.add(svg_nome)
    return existe


def _aplicar_cor(svg_texto, cor_hex):
    """
    Substitui o placeholder da camada corpo pela cor escolhida.
    Cobre tanto fill="#CC0000" quanto style="fill:#CC0000".
    A especificação garante que #CC0000 só aparece na camada corpo.
    """
    cor = _norm_cor(cor_hex)
    # Substituição case-insensitive do placeholder em qualquer forma
    padrao = re.compile(re.escape(_PLACEHOLDER), re.IGNORECASE)
    return padrao.sub(cor, svg_texto)


def _rasterizar(svg_texto, larg_px, alt_px):
    """SVG (texto já com cor aplicada) -> PIL.Image RGBA no tamanho pedido."""
    # svg2rlg lê de arquivo; usamos um buffer temporário em memória via tmp
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".svg")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(svg_texto)
        desenho = svg2rlg(tmp)
        if desenho is None:
            return None
        # Renderiza em PNG na resolução nativa do SVG
        bio = io.BytesIO()
        renderPM.drawToFile(desenho, bio, fmt="PNG")
        bio.seek(0)
        img = Image.open(bio).convert("RGBA")
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass
    # Redimensiona para o tamanho pedido (mantendo nitidez)
    larg_px = max(2, int(larg_px))
    alt_px = max(2, int(alt_px))
    if img.size != (larg_px, alt_px):
        img = img.resize((larg_px, alt_px), Image.LANCZOS)
    return img


def _limpa_cache_se_preciso():
    if len(_CACHE_BASE) > _MAX_CACHE:
        _CACHE_BASE.clear()
    if len(_CACHE_ROT) > _MAX_CACHE:
        _CACHE_ROT.clear()


def render_veiculo(svg_nome, cor_hex, larg_px, alt_px, angulo=0):
    """
    Renderiza um veículo a partir do SVG.

    Retorna PIL.Image (RGBA) pronto para desenhar, ou None se:
      - bibliotecas ausentes
      - SVG não existe na pasta (chamador deve usar fallback vetorial)
      - erro ao processar (degrada para None, nunca lança)

    Argumentos:
      svg_nome : nome do arquivo (ex.: "carro_sedan.svg")
      cor_hex  : cor da carroceria ("#RRGGBB")
      larg_px  : largura desejada em pixels (já com zoom aplicado)
      alt_px   : altura desejada em pixels
      angulo   : graus (sentido horário; 0 = apontando p/ direita)
    """
    if not (_PIL_OK and _SVG_OK):
        return None
    if not svg_existe(svg_nome):
        return None

    cor = _norm_cor(cor_hex)
    larg_px = max(2, int(larg_px))
    alt_px = max(2, int(alt_px))
    ang = int(round(angulo)) % 360

    chave_rot = (svg_nome, cor, larg_px, alt_px, ang)
    cached = _CACHE_ROT.get(chave_rot)
    if cached is not None:
        return cached

    # Base (sem rotação) — reaproveitada entre ângulos diferentes
    chave_base = (svg_nome, cor, larg_px, alt_px)
    base = _CACHE_BASE.get(chave_base)
    if base is None:
        try:
            caminho = _dir_veiculos() / svg_nome
            svg_txt = caminho.read_text(encoding="utf-8")
            svg_txt = _aplicar_cor(svg_txt, cor)
            base = _rasterizar(svg_txt, larg_px, alt_px)
            if base is None:
                return None
            _CACHE_BASE[chave_base] = base
        except Exception as e:
            print(f"[render_svg] falha em {svg_nome}: {e}")
            return None

    # Rotação
    if ang == 0:
        resultado = base
    else:
        try:
            resultado = base.rotate(-ang, expand=True, resample=Image.BICUBIC)
        except Exception as e:
            print(f"[render_svg] rotacao {svg_nome}: {e}")
            resultado = base

    _CACHE_ROT[chave_rot] = resultado
    _limpa_cache_se_preciso()
    return resultado


def status():
    """Diagnóstico rápido do motor (para debug)."""
    return {
        "pil_ok": _PIL_OK,
        "svg_ok": _SVG_OK,
        "dir_veiculos": str(_dir_veiculos()),
        "cache_base": len(_CACHE_BASE),
        "cache_rot": len(_CACHE_ROT),
        "svgs_faltando": sorted(_SVG_FALTANDO),
    }


if __name__ == "__main__":
    # Autoteste: cria um SVG fictício, renderiza em várias cores/ângulos
    print("Status:", status())
    d = _dir_veiculos()
    d.mkdir(parents=True, exist_ok=True)
    teste = d / "_autoteste.svg"
    teste.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100">
  <g id="sombra"><ellipse cx="100" cy="55" rx="90" ry="42" fill="#000000" fill-opacity="0.15"/></g>
  <g id="corpo"><rect x="20" y="20" width="160" height="60" rx="10" fill="#CC0000"/></g>
  <g id="vidros"><rect x="120" y="30" width="40" height="40" fill="#3A4A5A"/></g>
</svg>''', encoding="utf-8")
    try:
        if not (_PIL_OK and _SVG_OK):
            print("\n[ATENCAO] svglib/PIL ausentes NESTE ambiente.")
            print("  pil_ok=%s svg_ok=%s" % (_PIL_OK, _SVG_OK))
            print("  O motor retorna None (fallback). Isso e esperado em")
            print("  ambientes sem svglib. No ambiente do SICRO (com svglib")
            print("  instalado) o motor renderiza normalmente.")
            print("  Instale com: pip install svglib reportlab pillow lxml")
            raise SystemExit(0)
        falhas = 0
        for cor in ("#1E88E5", "#2E7D32", "#F0B429"):
            for ang in (0, 45, 90):
                img = render_veiculo("_autoteste.svg", cor, 120, 60, ang)
                ok = img is not None
                if not ok:
                    falhas += 1
                tam = img.size if ok else "-"
                print(f"  cor={cor} ang={ang:3d} -> {'OK' if ok else 'FALHOU'} {tam}")
        if falhas:
            print(f"\n[ERRO] {falhas} renderizacoes falharam.")
            raise SystemExit(1)
        img = render_veiculo("_autoteste.svg", "#1E88E5", 120, 60, 0)
        if img is None:
            print("[ERRO] render retornou None inesperadamente")
            raise SystemExit(1)
        px = img.convert("RGB").getpixel((60, 30))
        print(f"  Pixel corpo: {px} (esperado ~30,136,229)")
        print("  Cache:", status()["cache_base"], "base /",
              status()["cache_rot"], "rot")
        assert render_veiculo("nao_existe.svg", "#FFF", 100, 50, 0) is None
        print("  Fallback (SVG ausente -> None): OK")
        print("\nMOTOR OK.")
    finally:
        try:
            teste.unlink()
        except Exception:
            pass
