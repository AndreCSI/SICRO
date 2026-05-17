"""
arquivo/prancha.py — Geracao da prancha pericial (PDF e PNG)
Layout A4 paisagem: cabecalho institucional + croqui + legenda
automatica + quadro de distancias + rodape tecnico.

Uso:
    from arquivo.prancha import gerar_prancha
    gerar_prancha(path, formato, dados_caso, elementos,
                  img_croqui_png, calibrado, k, u_k, brasao_pil)
"""
import io
import datetime
import sys
from pathlib import Path

_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))

try:
    from PIL import Image
    PIL_OK = True
except Exception:
    PIL_OK = False

try:
    from config import TIPO_INFO
except Exception:
    TIPO_INFO = {}


# Cores institucionais (RGB 0-1 para reportlab)
_AZUL  = (0.05, 0.12, 0.30)
_OURO  = (0.94, 0.70, 0.16)
_CINZA = (0.45, 0.45, 0.50)
_PRETO = (0.10, 0.10, 0.12)
_LINHA = (0.75, 0.75, 0.78)


def _nome_tipo(tipo):
    info = TIPO_INFO.get(tipo)
    if info:
        return info[1]
    return tipo.replace("_", " ").capitalize()


def _coletar_legenda(elementos):
    """Lista de (label, nome_tipo) dos elementos identificaveis."""
    itens = []
    vistos = set()
    for el in elementos:
        t = el.get("tipo", "")
        lbl = el.get("label", "")
        if t in ("carro", "moto", "caminhao", "bicicleta",
                 "pedestre", "sc") and lbl:
            chave = (lbl, t)
            if chave not in vistos:
                vistos.add(chave)
                itens.append((lbl, _nome_tipo(t)))
    return itens


def _coletar_distancias(elementos):
    """Lista de (label, medida) das cotas."""
    out = []
    for el in elementos:
        if el.get("tipo") == "cota":
            med = el.get("label", "").strip()
            if med:
                out.append(med)
    return out


def _croqui_para_png_bytes(img_pil, max_lado=2200):
    """Normaliza a imagem do croqui para embutir."""
    img = img_pil
    if max(img.width, img.height) > max_lado:
        if img.width >= img.height:
            nh = int(img.height * max_lado / img.width)
            img = img.resize((max_lado, nh), Image.LANCZOS)
        else:
            nw = int(img.width * max_lado / img.height)
            img = img.resize((nw, max_lado), Image.LANCZOS)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════
#  GERACAO EM PDF (reportlab)
# ══════════════════════════════════════════════════════
def _gerar_pdf(path, dados, elementos, img_croqui,
               calibrado, k, u_k, brasao):
    from reportlab.pdfgen import canvas as rl
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader

    W, H = landscape(A4)          # 842 x 595 pt aprox
    cv = rl.Canvas(path, pagesize=(W, H))

    M = 12 * mm                   # margem
    # Moldura externa
    cv.setStrokeColorRGB(*_PRETO)
    cv.setLineWidth(1.2)
    cv.rect(M, M, W - 2*M, H - 2*M)

    # ---- CABECALHO ----
    cab_h = 26 * mm
    cab_y = H - M - cab_h
    cv.setLineWidth(0.8)
    cv.line(M, cab_y, W - M, cab_y)

    # Brasao
    if brasao is not None and PIL_OK:
        try:
            b = brasao.convert("RGBA")
            bio = io.BytesIO(); b.save(bio, format="PNG"); bio.seek(0)
            cv.drawImage(ImageReader(bio), M + 4*mm, cab_y + 4*mm,
                         width=18*mm, height=18*mm, mask='auto')
        except Exception:
            pass

    # Titulo central
    cv.setFillColorRGB(*_PRETO)
    cv.setFont("Helvetica-Bold", 15)
    cv.drawCentredString(W/2, cab_y + cab_h - 9*mm,
                         "CROQUI PERICIAL DE ACIDENTE DE TRÂNSITO")
    cv.setFont("Helvetica", 8)
    cv.setFillColorRGB(*_CINZA)
    cv.drawCentredString(W/2, cab_y + cab_h - 14*mm,
                         "POLÍCIA CIENTÍFICA DO AMAPÁ — Coordenação de Perícias de Trânsito")
    cv.drawCentredString(W/2, cab_y + cab_h - 18*mm,
                         "SICRO PCI/AP — Sistema de Croqui Pericial · v1.0")

    # Bloco identificacao (direita)
    bo   = dados.get("bo", "—")
    cv.setFont("Helvetica-Bold", 11)
    cv.setFillColorRGB(*_AZUL)
    cv.drawRightString(W - M - 4*mm, cab_y + cab_h - 7*mm,
                       f"BO Nº {bo}")
    cv.setFont("Helvetica", 7.5)
    cv.setFillColorRGB(*_PRETO)
    info_y = cab_y + cab_h - 12*mm
    for txt in (
        f"Data: {dados.get('data','—')}",
        f"Local: {dados.get('local','—')}  ·  {dados.get('municipio','')}",
        f"Requisição: {dados.get('requisicao','—')}",
        f"Perito: {dados.get('perito','—')}",
    ):
        cv.drawRightString(W - M - 4*mm, info_y, txt[:60])
        info_y -= 3.6*mm

    # ---- RODAPE ----
    rod_h = 30 * mm
    rod_y = M + rod_h
    cv.setLineWidth(0.8)
    cv.line(M, rod_y, W - M, rod_y)

    # 3 colunas no rodape
    col_w = (W - 2*M) / 3.0
    cx1 = M
    cx2 = M + col_w
    cx3 = M + 2*col_w
    cv.line(cx2, M, cx2, rod_y)
    cv.line(cx3, M, cx3, rod_y)

    # Col 1: Observacoes
    cv.setFont("Helvetica-Bold", 8)
    cv.setFillColorRGB(*_AZUL)
    cv.drawString(cx1 + 4*mm, rod_y - 5*mm, "OBSERVAÇÕES")
    cv.setFont("Helvetica", 6.8)
    cv.setFillColorRGB(*_PRETO)
    obs = [
        "- Medidas expressas em metros.",
        "- Croqui em escala; ver escala numérica.",
        "- Sistema de referência: plano local.",
    ]
    oy = rod_y - 9*mm
    for o in obs:
        cv.drawString(cx1 + 4*mm, oy, o); oy -= 3.4*mm

    # Col 2: Quadro de distancias
    cv.setFont("Helvetica-Bold", 8)
    cv.setFillColorRGB(*_AZUL)
    cv.drawString(cx2 + 4*mm, rod_y - 5*mm, "QUADRO DE DISTÂNCIAS")
    cv.setFont("Helvetica", 6.8)
    cv.setFillColorRGB(*_PRETO)
    dists = _coletar_distancias(elementos)
    dy = rod_y - 9*mm
    if dists:
        for i, d in enumerate(dists[:6], 1):
            cv.drawString(cx2 + 4*mm, dy, f"Cota {i}:  {d}")
            dy -= 3.4*mm
    else:
        cv.setFillColorRGB(*_CINZA)
        cv.drawString(cx2 + 4*mm, dy, "Sem cotas registradas.")

    # Col 3: Assinatura / escala
    cv.setFont("Helvetica-Bold", 8)
    cv.setFillColorRGB(*_AZUL)
    cv.drawString(cx3 + 4*mm, rod_y - 5*mm, "IDENTIFICAÇÃO TÉCNICA")
    cv.setFont("Helvetica", 6.8)
    cv.setFillColorRGB(*_PRETO)
    ey = rod_y - 9*mm
    if calibrado and k:
        cv.drawString(cx3 + 4*mm, ey,
                      f"Escala: k = {k:.5f} m/px")
        ey -= 3.4*mm
        if u_k:
            cv.drawString(cx3 + 4*mm, ey,
                          f"Incerteza: ± {u_k*1000:.3f} mm/px")
            ey -= 3.4*mm
    else:
        cv.drawString(cx3 + 4*mm, ey, "Escala: não calibrada")
        ey -= 3.4*mm
    ey -= 6*mm
    cv.line(cx3 + 4*mm, ey, cx3 + col_w - 6*mm, ey)
    cv.setFont("Helvetica", 6.5)
    cv.setFillColorRGB(*_CINZA)
    cv.drawString(cx3 + 4*mm, ey - 4*mm,
                  dados.get("perito", "Perito responsável"))

    # ---- CORPO: croqui (esq) + legenda (dir) ----
    leg_w = 52 * mm
    corpo_x0 = M
    corpo_x1 = W - M - leg_w
    corpo_y0 = rod_y
    corpo_y1 = cab_y
    # divisoria legenda
    cv.setLineWidth(0.8)
    cv.line(corpo_x1, corpo_y0, corpo_x1, corpo_y1)

    # Croqui
    if img_croqui is not None and PIL_OK:
        try:
            buf = _croqui_para_png_bytes(img_croqui)
            cimg = Image.open(buf)
            iw, ih = cimg.size
            area_w = corpo_x1 - corpo_x0 - 8*mm
            area_h = corpo_y1 - corpo_y0 - 8*mm
            esc = min(area_w/iw, area_h/ih)
            dw, dh = iw*esc, ih*esc
            px = corpo_x0 + (corpo_x1 - corpo_x0 - dw)/2
            py = corpo_y0 + (corpo_y1 - corpo_y0 - dh)/2
            buf.seek(0)
            cv.drawImage(ImageReader(buf), px, py,
                         width=dw, height=dh)
        except Exception as e:
            cv.setFont("Helvetica", 9)
            cv.setFillColorRGB(*_CINZA)
            cv.drawCentredString((corpo_x0+corpo_x1)/2,
                                 (corpo_y0+corpo_y1)/2,
                                 f"[croqui indisponível: {e}]")

    # Legenda (coluna direita)
    lx = corpo_x1 + 4*mm
    ly = corpo_y1 - 6*mm
    cv.setFont("Helvetica-Bold", 9)
    cv.setFillColorRGB(*_AZUL)
    cv.drawString(lx, ly, "LEGENDA")
    ly -= 6*mm
    cv.setFont("Helvetica", 7.5)
    cv.setFillColorRGB(*_PRETO)
    leg = _coletar_legenda(elementos)
    if leg:
        for lbl, nome in leg[:18]:
            cv.setFont("Helvetica-Bold", 7.5)
            cv.drawString(lx, ly, f"{lbl}")
            cv.setFont("Helvetica", 7.5)
            cv.drawString(lx + 12*mm, ly, f"— {nome}")
            ly -= 4.4*mm
    else:
        cv.setFillColorRGB(*_CINZA)
        cv.drawString(lx, ly, "Sem elementos")
        ly -= 4.4*mm

    # Norte (simples) no rodape da legenda
    ly = corpo_y0 + 14*mm
    cv.setFont("Helvetica-Bold", 8)
    cv.setFillColorRGB(*_PRETO)
    cv.drawString(lx, ly, "↑ N")
    cv.setFont("Helvetica", 6.5)
    cv.setFillColorRGB(*_CINZA)
    cv.drawString(lx, ly - 4*mm, "Norte para cima")

    # Marca rodape inferior
    cv.setFont("Helvetica", 6)
    cv.setFillColorRGB(*_CINZA)
    cv.drawString(M + 2*mm, M - 4*mm + 2*mm,
                  f"Gerado pelo SICRO PCI/AP · {datetime.date.today()}")
    cv.drawRightString(W - M - 2*mm, M - 4*mm + 2*mm,
                       "Página 1 de 1")

    cv.save()
    return path


# ══════════════════════════════════════════════════════
#  GERACAO EM PNG (renderiza a mesma prancha via PIL)
# ══════════════════════════════════════════════════════
def _gerar_png(path, dados, elementos, img_croqui,
               calibrado, k, u_k, brasao):
    from PIL import Image, ImageDraw, ImageFont

    # A4 paisagem @ ~150 dpi
    W, H = 1754, 1240
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    def _font(sz, bold=False):
        try:
            nome = "arialbd.ttf" if bold else "arial.ttf"
            return ImageFont.truetype(nome, sz)
        except Exception:
            return ImageFont.load_default()

    P = (26, 26, 30)
    AZ = (13, 30, 76)
    CZ = (115, 115, 128)

    M = 30
    d.rectangle([M, M, W-M, H-M], outline=P, width=2)

    # Cabecalho
    cab_b = M + 130
    d.line([M, cab_b, W-M, cab_b], fill=P, width=2)
    if brasao is not None:
        try:
            b = brasao.convert("RGBA").resize((96, 96))
            img.paste(b, (M+16, M+16), b)
        except Exception:
            pass
    d.text((W//2, M+34), "CROQUI PERICIAL DE ACIDENTE DE TRÂNSITO",
           font=_font(30, True), fill=P, anchor="mm")
    d.text((W//2, M+70),
           "POLÍCIA CIENTÍFICA DO AMAPÁ — Coordenação de Perícias de Trânsito",
           font=_font(15), fill=CZ, anchor="mm")
    d.text((W//2, M+94),
           "SICRO PCI/AP — Sistema de Croqui Pericial · v1.0",
           font=_font(14), fill=CZ, anchor="mm")
    bo = dados.get("bo", "—")
    d.text((W-M-16, M+22), f"BO Nº {bo}",
           font=_font(20, True), fill=AZ, anchor="ra")
    iy = M+52
    for txt in (
        f"Data: {dados.get('data','—')}",
        f"Local: {dados.get('local','—')}  ·  {dados.get('municipio','')}",
        f"Requisição: {dados.get('requisicao','—')}",
        f"Perito: {dados.get('perito','—')}",
    ):
        d.text((W-M-16, iy), txt[:58], font=_font(13),
               fill=P, anchor="ra")
        iy += 20

    # Rodape
    rod_t = H - M - 150
    d.line([M, rod_t, W-M, rod_t], fill=P, width=2)
    cw = (W - 2*M)//3
    c1, c2, c3 = M, M+cw, M+2*cw
    d.line([c2, rod_t, c2, H-M], fill=P, width=1)
    d.line([c3, rod_t, c3, H-M], fill=P, width=1)

    d.text((c1+16, rod_t+12), "OBSERVAÇÕES",
           font=_font(15, True), fill=AZ)
    oy = rod_t+42
    for o in ["- Medidas em metros.",
              "- Croqui em escala.",
              "- Referência: plano local."]:
        d.text((c1+16, oy), o, font=_font(13), fill=P); oy += 22

    d.text((c2+16, rod_t+12), "QUADRO DE DISTÂNCIAS",
           font=_font(15, True), fill=AZ)
    dists = _coletar_distancias(elementos)
    dy = rod_t+42
    if dists:
        for i, ds in enumerate(dists[:5], 1):
            d.text((c2+16, dy), f"Cota {i}:  {ds}",
                   font=_font(13), fill=P); dy += 22
    else:
        d.text((c2+16, dy), "Sem cotas registradas.",
               font=_font(13), fill=CZ)

    d.text((c3+16, rod_t+12), "IDENTIFICAÇÃO TÉCNICA",
           font=_font(15, True), fill=AZ)
    ey = rod_t+42
    if calibrado and k:
        d.text((c3+16, ey), f"Escala: k={k:.5f} m/px",
               font=_font(13), fill=P); ey += 22
        if u_k:
            d.text((c3+16, ey), f"Incerteza: ±{u_k*1000:.3f} mm/px",
                   font=_font(13), fill=P); ey += 22
    else:
        d.text((c3+16, ey), "Escala: não calibrada",
               font=_font(13), fill=P); ey += 22
    ey += 30
    d.line([c3+16, ey, c3+cw-30, ey], fill=P, width=1)
    d.text((c3+16, ey+8), dados.get("perito", "Perito responsável"),
           font=_font(12), fill=CZ)

    # Corpo: croqui + legenda
    leg_w = 250
    cx0, cx1 = M, W-M-leg_w
    cy0, cy1 = cab_b, rod_t
    d.line([cx1, cy0, cx1, cy1], fill=P, width=2)

    if img_croqui is not None:
        try:
            buf = _croqui_para_png_bytes(img_croqui)
            cimg = Image.open(buf).convert("RGB")
            aw, ah = cx1-cx0-30, cy1-cy0-30
            esc = min(aw/cimg.width, ah/cimg.height)
            nw, nh = int(cimg.width*esc), int(cimg.height*esc)
            cimg = cimg.resize((nw, nh), Image.LANCZOS)
            px = cx0 + (cx1-cx0-nw)//2
            py = cy0 + (cy1-cy0-nh)//2
            img.paste(cimg, (px, py))
        except Exception as e:
            d.text(((cx0+cx1)//2, (cy0+cy1)//2),
                   f"[croqui indisponível]", font=_font(16),
                   fill=CZ, anchor="mm")

    lx = cx1+16
    ly = cy0+20
    d.text((lx, ly), "LEGENDA", font=_font(17, True), fill=AZ)
    ly += 32
    for lbl, nome in _coletar_legenda(elementos)[:16]:
        d.text((lx, ly), lbl, font=_font(14, True), fill=P)
        d.text((lx+50, ly), f"— {nome}", font=_font(14), fill=P)
        ly += 26

    d.text((lx, cy1-50), "↑ N", font=_font(16, True), fill=P)
    d.text((lx, cy1-26), "Norte p/ cima", font=_font(12), fill=CZ)

    d.text((M+8, H-M+6),
           f"Gerado pelo SICRO PCI/AP · {datetime.date.today()}",
           font=_font(11), fill=CZ)

    img.save(path, "PNG")
    return path


# ══════════════════════════════════════════════════════
#  API publica
# ══════════════════════════════════════════════════════
def gerar_prancha(path, formato, dados_caso, elementos,
                   img_croqui, calibrado, k, u_k, brasao=None):
    """
    formato: 'pdf' ou 'png'
    img_croqui: PIL.Image do croqui capturado (ou None)
    Retorna o path gerado.
    """
    if formato == "pdf":
        return _gerar_pdf(path, dados_caso, elementos, img_croqui,
                          calibrado, k, u_k, brasao)
    elif formato == "png":
        return _gerar_png(path, dados_caso, elementos, img_croqui,
                          calibrado, k, u_k, brasao)
    raise ValueError(f"Formato desconhecido: {formato}")
