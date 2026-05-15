"""
instalar.py — Script auxiliar de instalação
Execute com: python instalar.py
Cria os arquivos dos módulos corretamente no Windows.
"""
from pathlib import Path

VEICULOS_ARTE = '''import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import BRANCO, CINZA_CLARO, CINZA_ESCURO


def escurecer(cor_hex):
    try:
        r = int(cor_hex[1:3], 16); g = int(cor_hex[3:5], 16); b = int(cor_hex[5:7], 16)
        r = max(0, int(r * 0.65)); g = max(0, int(g * 0.65)); b = max(0, int(b * 0.65))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return cor_hex


def arte_sedan(c, cx, cy, sc, cor):
    w, h = 28*sc, 14*sc
    c.create_rectangle(cx-w/2, cy-h/2, cx+w/2, cy+h/2, fill=cor, outline=BRANCO, width=1)
    c.create_polygon(cx-w/2+3*sc, cy-h/2, cx+w/4, cy-h/2,
                     cx+w/4, cy-h/2+4*sc, cx-w/2+2*sc, cy-h/2+4*sc, fill="#A0C8F0", outline="")
    c.create_polygon(cx+w/4, cy-h/2, cx+w/2-2*sc, cy-h/2,
                     cx+w/2-2*sc, cy-h/2+4*sc, cx+w/4, cy-h/2+4*sc, fill="#A0C8F0", outline="")
    rw, rh = 3*sc, 4*sc
    for rx, ry in [(-w/2+2*sc,-h/2-rh/2),(-w/2+2*sc,h/2-rh/2),(w/2-4*sc,-h/2-rh/2),(w/2-4*sc,h/2-rh/2)]:
        c.create_rectangle(cx+rx-rw/2, cy+ry, cx+rx+rw/2, cy+ry+rh, fill="#222", outline="#555", width=1)


def arte_suv(c, cx, cy, sc, cor):
    w, h = 30*sc, 16*sc
    c.create_rectangle(cx-w/2, cy-h/2, cx+w/2, cy+h/2, fill=cor, outline=BRANCO, width=1)
    c.create_rectangle(cx-w/2, cy-h/2, cx-w/2+8*sc, cy+h/2, fill=escurecer(cor), outline="")
    c.create_polygon(cx-w/2+8*sc, cy-h/2+2*sc, cx-w/2+14*sc, cy-h/2+2*sc,
                     cx-w/2+14*sc, cy+h/2-2*sc, cx-w/2+8*sc, cy+h/2-2*sc, fill="#A0C8F0", outline="")
    rw, rh = 4*sc, 5*sc
    for rx, ry in [(-w/2+3*sc,-h/2-rh/2),(-w/2+3*sc,h/2-rh/2),(w/2-5*sc,-h/2-rh/2),(w/2-5*sc,h/2-rh/2)]:
        c.create_rectangle(cx+rx-rw/2, cy+ry, cx+rx+rw/2, cy+ry+rh, fill="#222", outline="#555", width=1)


def arte_hatch(c, cx, cy, sc, cor):
    w, h = 24*sc, 13*sc
    c.create_rectangle(cx-w/2, cy-h/2, cx+w/2, cy+h/2, fill=cor, outline=BRANCO, width=1)
    c.create_polygon(cx-w/2+4*sc, cy-h/2+2*sc, cx+w/2-3*sc, cy-h/2+2*sc,
                     cx+w/2-3*sc, cy+h/2-2*sc, cx-w/2+4*sc, cy+h/2-2*sc, fill=escurecer(cor), outline="")
    c.create_polygon(cx-w/2+2*sc, cy-h/2, cx-w/2+7*sc, cy-h/2,
                     cx-w/2+6*sc, cy-h/2+3*sc, cx-w/2+2*sc, cy-h/2+3*sc, fill="#A0C8F0", outline="")
    rw, rh = 3*sc, 4*sc
    for rx, ry in [(-w/2+2*sc,-h/2-rh/2),(-w/2+2*sc,h/2-rh/2),(w/2-4*sc,-h/2-rh/2),(w/2-4*sc,h/2-rh/2)]:
        c.create_rectangle(cx+rx-rw/2, cy+ry, cx+rx+rw/2, cy+ry+rh, fill="#222", outline="#555", width=1)


def arte_moto_esportiva(c, cx, cy, sc, cor):
    w, h = 20*sc, 7*sc
    c.create_polygon(cx-w/2, cy, cx-w/2+4*sc, cy-h/2, cx+w/2-3*sc, cy-h/2+1*sc,
                     cx+w/2, cy, cx+w/2-3*sc, cy+h/2-1*sc, cx-w/2+4*sc, cy+h/2,
                     fill=cor, outline=BRANCO, width=1)
    c.create_line(cx-w/2+3*sc, cy-h/2-2*sc, cx-w/2+3*sc, cy+h/2+2*sc, fill=CINZA_CLARO, width=int(1.5*sc))
    rr = 3.5*sc
    c.create_oval(cx-w/2+1*sc-rr/2, cy-rr/2, cx-w/2+1*sc+rr/2, cy+rr/2, fill="#222", outline=CINZA_CLARO, width=1)
    c.create_oval(cx+w/2-2*sc-rr/2, cy-rr/2, cx+w/2-2*sc+rr/2, cy+rr/2, fill="#222", outline=CINZA_CLARO, width=1)


def arte_moto_urbana(c, cx, cy, sc, cor):
    w, h = 18*sc, 8*sc
    c.create_rectangle(cx-w/2+3*sc, cy-h/2, cx+w/2-3*sc, cy+h/2, fill=cor, outline=BRANCO, width=1)
    c.create_line(cx-w/2+2*sc, cy-h/2-3*sc, cx-w/2+2*sc, cy+h/2+3*sc, fill=CINZA_CLARO, width=int(2*sc))
    c.create_line(cx-w/2+1*sc, cy-h/2-3*sc, cx-w/2+4*sc, cy-h/2-3*sc, fill=CINZA_CLARO, width=1)
    c.create_line(cx-w/2+1*sc, cy+h/2+3*sc, cx-w/2+4*sc, cy+h/2+3*sc, fill=CINZA_CLARO, width=1)
    rr = 3*sc
    c.create_oval(cx-w/2-rr/2, cy-rr/2, cx-w/2+rr/2, cy+rr/2, fill="#222", outline=CINZA_CLARO, width=1)
    c.create_oval(cx+w/2-rr/2, cy-rr/2, cx+w/2+rr/2, cy+rr/2, fill="#222", outline=CINZA_CLARO, width=1)


def arte_moto_carga(c, cx, cy, sc, cor):
    w, h = 22*sc, 9*sc
    c.create_rectangle(cx-w/2+4*sc, cy-h/2+1*sc, cx+w/4, cy+h/2-1*sc, fill=cor, outline=BRANCO, width=1)
    c.create_rectangle(cx+w/4, cy-h/2, cx+w/2, cy+h/2, fill=CINZA_ESCURO, outline=CINZA_CLARO, width=1)
    c.create_line(cx-w/2+3*sc, cy-h/2-2*sc, cx-w/2+3*sc, cy+h/2+2*sc, fill=CINZA_CLARO, width=int(1.5*sc))
    rr = 3.5*sc
    c.create_oval(cx-w/2-rr/2, cy-rr/2, cx-w/2+rr/2, cy+rr/2, fill="#222", outline=CINZA_CLARO, width=1)
    c.create_oval(cx+w/2-rr/2, cy-rr/2, cx+w/2+rr/2, cy+rr/2, fill="#222", outline=CINZA_CLARO, width=1)


def arte_caminhao_leve(c, cx, cy, sc, cor):
    w, h = 36*sc, 16*sc; cab = 10*sc
    c.create_rectangle(cx-w/2+cab, cy-h/2, cx+w/2, cy+h/2, fill=escurecer(cor), outline=BRANCO, width=1)
    c.create_rectangle(cx-w/2, cy-h/2, cx-w/2+cab, cy+h/2, fill=cor, outline=BRANCO, width=1)
    c.create_polygon(cx-w/2+1*sc, cy-h/2+2*sc, cx-w/2+cab-1*sc, cy-h/2+2*sc,
                     cx-w/2+cab-1*sc, cy+h/2-2*sc, cx-w/2+1*sc, cy+h/2-2*sc, fill="#A0C8F0", outline="")
    rw, rh = 4*sc, 5*sc
    for rx, ry in [(-w/2+2*sc,-h/2-rh/2),(-w/2+2*sc,h/2-rh/2),(w/4,-h/2-rh/2),(w/4,h/2-rh/2),(w/2-4*sc,-h/2-rh/2),(w/2-4*sc,h/2-rh/2)]:
        c.create_rectangle(cx+rx-rw/2, cy+ry, cx+rx+rw/2, cy+ry+rh, fill="#222", outline="#555", width=1)


def arte_caminhao_truck(c, cx, cy, sc, cor):
    w, h = 48*sc, 18*sc; cab = 10*sc
    c.create_rectangle(cx-w/2+cab, cy-h/2, cx+w/2, cy+h/2, fill=escurecer(cor), outline=BRANCO, width=1)
    for lx in [cx-w/2+cab+8*sc, cx-w/2+cab+16*sc, cx-w/2+cab+24*sc]:
        c.create_line(lx, cy-h/2+1, lx, cy+h/2-1, fill=CINZA_ESCURO, width=1)
    c.create_rectangle(cx-w/2, cy-h/2+1*sc, cx-w/2+cab, cy+h/2-1*sc, fill=cor, outline=BRANCO, width=1)
    c.create_polygon(cx-w/2+1*sc, cy-h/2+3*sc, cx-w/2+cab-1*sc, cy-h/2+3*sc,
                     cx-w/2+cab-1*sc, cy+h/2-3*sc, cx-w/2+1*sc, cy+h/2-3*sc, fill="#A0C8F0", outline="")
    rw, rh = 4*sc, 6*sc
    for rx, ry in [(-w/2+2*sc,-h/2-rh/2),(-w/2+2*sc,h/2-rh/2),(0,-h/2-rh/2),(0,h/2-rh/2),(w/4,-h/2-rh/2),(w/4,h/2-rh/2),(w/2-4*sc,-h/2-rh/2),(w/2-4*sc,h/2-rh/2)]:
        c.create_rectangle(cx+rx-rw/2, cy+ry, cx+rx+rw/2, cy+ry+rh, fill="#222", outline="#555", width=1)


def arte_caminhao_carreta(c, cx, cy, sc, cor):
    w, h = 56*sc, 17*sc; cab = 10*sc
    c.create_rectangle(cx-w/2+cab+4*sc, cy-h/2, cx+w/2, cy+h/2, fill=escurecer(cor), outline=BRANCO, width=1)
    for lx in [cx-w/2+cab+14*sc, cx-w/2+cab+26*sc, cx-w/2+cab+38*sc]:
        c.create_line(lx, cy-h/2+1, lx, cy+h/2-1, fill=CINZA_ESCURO, width=1)
    c.create_oval(cx-w/2+cab, cy-3*sc, cx-w/2+cab+4*sc, cy+3*sc, fill=CINZA_CLARO, outline="")
    c.create_rectangle(cx-w/2, cy-h/2+2*sc, cx-w/2+cab, cy+h/2-2*sc, fill=cor, outline=BRANCO, width=1)
    c.create_polygon(cx-w/2+1*sc, cy-h/2+4*sc, cx-w/2+cab-1*sc, cy-h/2+4*sc,
                     cx-w/2+cab-1*sc, cy+h/2-4*sc, cx-w/2+1*sc, cy+h/2-4*sc, fill="#A0C8F0", outline="")
    rw, rh = 4*sc, 5*sc
    for rx, ry in [(-w/2+2*sc,-h/2-rh/2),(-w/2+2*sc,h/2-rh/2),(w/4-2*sc,-h/2-rh/2),(w/4-2*sc,h/2-rh/2),(w/2-4*sc,-h/2-rh/2),(w/2-4*sc,h/2-rh/2)]:
        c.create_rectangle(cx+rx-rw/2, cy+ry, cx+rx+rw/2, cy+ry+rh, fill="#222", outline="#555", width=1)


def arte_bicicleta(c, cx, cy, sc, cor):
    w, h = 16*sc, 5*sc
    c.create_line(cx-w/2+2*sc, cy, cx+w/2-2*sc, cy, fill=cor, width=int(2*sc))
    c.create_line(cx, cy, cx-w/6, cy-h/2, fill=cor, width=int(1.5*sc))
    c.create_line(cx, cy, cx-w/6, cy+h/2, fill=cor, width=int(1.5*sc))
    c.create_line(cx-w/2+1*sc, cy-h/2-1*sc, cx-w/2+1*sc, cy+h/2+1*sc, fill=CINZA_CLARO, width=int(1.5*sc))
    rr = 3*sc
    c.create_oval(cx-w/2-rr/2, cy-rr/2, cx-w/2+rr/2, cy+rr/2, fill="#222", outline=CINZA_CLARO, width=1)
    c.create_oval(cx+w/2-rr/2, cy-rr/2, cx+w/2+rr/2, cy+rr/2, fill="#222", outline=CINZA_CLARO, width=1)


def arte_pedestre(c, cx, cy, sc, cor):
    r_cab = 4*sc
    c.create_oval(cx-r_cab, cy-r_cab, cx+r_cab, cy+r_cab, fill=cor, outline=BRANCO, width=1)
    c.create_rectangle(cx-3*sc, cy+r_cab, cx+3*sc, cy+r_cab+7*sc, fill=cor, outline=BRANCO, width=1)
    c.create_line(cx-3*sc, cy+r_cab+2*sc, cx-7*sc, cy+r_cab+5*sc, fill=cor, width=int(1.5*sc))
    c.create_line(cx+3*sc, cy+r_cab+2*sc, cx+7*sc, cy+r_cab+5*sc, fill=cor, width=int(1.5*sc))
    c.create_line(cx-2*sc, cy+r_cab+7*sc, cx-3*sc, cy+r_cab+13*sc, fill=cor, width=int(2*sc))
    c.create_line(cx+2*sc, cy+r_cab+7*sc, cx+3*sc, cy+r_cab+13*sc, fill=cor, width=int(2*sc))
'''

# Escreve o arquivo
dest = Path("desenho") / "veiculos_arte.py"
dest.write_text(VEICULOS_ARTE, encoding="utf-8")
print(f"OK — {dest} escrito com {len(VEICULOS_ARTE.splitlines())} linhas")

# Verifica
import importlib.util
spec = importlib.util.spec_from_file_location("veiculos_arte", dest)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fns = [f for f in dir(mod) if f.startswith("arte_")]
print(f"Funções encontradas: {fns}")
print("Tudo OK! Rode: python main.py")