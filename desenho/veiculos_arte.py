from config import BRANCO, CINZA_CLARO, CINZA_ESCURO
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))

def escurecer(cor_hex):
    try:
        r=int(cor_hex[1:3],16); g=int(cor_hex[3:5],16); b=int(cor_hex[5:7],16)
        r=max(0,int(r*0.65)); g=max(0,int(g*0.65)); b=max(0,int(b*0.65))
        return f'#{r:02x}{g:02x}{b:02x}'
    except: return cor_hex

def arte_sedan(c,cx,cy,sc,cor):
    w,h=28*sc,14*sc
    c.create_rectangle(cx-w/2,cy-h/2,cx+w/2,cy+h/2,fill=cor,outline=BRANCO,width=1)

def arte_suv(c,cx,cy,sc,cor): pass
def arte_hatch(c,cx,cy,sc,cor): pass
def arte_moto_esportiva(c,cx,cy,sc,cor): pass
def arte_moto_urbana(c,cx,cy,sc,cor): pass
def arte_moto_carga(c,cx,cy,sc,cor): pass
def arte_caminhao_leve(c,cx,cy,sc,cor): pass
def arte_caminhao_truck(c,cx,cy,sc,cor): pass
def arte_caminhao_carreta(c,cx,cy,sc,cor): pass
def arte_bicicleta(c,cx,cy,sc,cor): pass
def arte_pedestre(c,cx,cy,sc,cor): pass
