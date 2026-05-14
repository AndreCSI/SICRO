import sys, math
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import AMARELO, BRANCO, COR_PERIGO


def desenhar_via(c, el, tx, ty, zoom, fn_mt):
    t = el['tipo']
    if t in ('_asfalto', '_asfalto_terra'):
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        cor = '#5A4A2A' if t=='_asfalto_terra' else '#606060'
        c.create_rectangle(ax1,ay1,ax2,ay2,fill=cor,outline='#808080',width=1)
    elif t=='_calcada':
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        c.create_rectangle(ax1,ay1,ax2,ay2,fill='#A0A0A0',outline='#C0C0C0',width=1)
    elif t=='_canteiro':
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        c.create_rectangle(ax1,ay1,ax2,ay2,fill='#1A3A1A',outline='')
    elif t in ('_faixa_h','_faixa_v'):
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        c.create_line(ax1,ay1,ax2,ay2,fill=AMARELO,
                      width=max(2,int(2*zoom)),
                      dash=(max(8,int(14*zoom)),max(6,int(10*zoom))))
    elif t=='_rotatoria':
        r=el.get('r',80)*zoom; ri=r*0.4
        c.create_oval(tx-r,ty-r,tx+r,ty+r,fill='#606060',outline='')
        c.create_oval(tx-ri,ty-ri,tx+ri,ty+ri,fill='#1A3A1A',outline='')
        c.create_oval(tx-r,ty-r,tx+r,ty+r,fill='',outline=AMARELO,
                      width=max(1,int(1.5*zoom)),dash=(8,5))
    elif t=='v_asfalto':
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        c.create_rectangle(ax1,ay1,ax2,ay2,fill='#606060',outline='#808080',width=1)
    elif t=='v_calcada':
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        c.create_rectangle(ax1,ay1,ax2,ay2,fill='#A0A0A0',outline='#C0C0C0',width=1)
        p=max(4,int(10*zoom))
        for xi in range(int(ax1),int(ax2),p):
            c.create_line(xi,int(ay1),xi,int(ay2),fill='#888',width=1)
    elif t=='v_conflito':
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        c.create_rectangle(ax1,ay1,ax2,ay2,fill='',outline=COR_PERIGO,width=2,dash=(8,4))
        c.create_text((ax1+ax2)/2,(ay1+ay2)/2,text='CONFLITO',fill=COR_PERIGO,
                      font=('Segoe UI',max(8,int(9*zoom)),'bold'))
    elif t=='v_faixa_am':
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        c.create_line(ax1,ay1,ax2,ay2,fill=AMARELO,
                      width=max(2,int(3*zoom)),
                      dash=(max(10,int(14*zoom)),max(6,int(8*zoom))))
    elif t=='v_faixa_br':
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        c.create_line(ax1,ay1,ax2,ay2,fill=BRANCO,width=max(2,int(2*zoom)))
    elif t=='v_faixa_ped':
        ax1,ay1=fn_mt(el['x'],el['y']); ax2,ay2=fn_mt(el['x2'],el['y2'])
        larg=max(1,ax2-ax1); n=max(3,int(larg/max(1,8*zoom))); passo=larg/n
        for i in range(n):
            lx=ax1+i*passo
            c.create_rectangle(lx,ay1,lx+passo*0.55,ay2,fill=BRANCO,outline='')
    elif t=='v_rotatoria':
        r=el.get('r',60)*zoom; ri=r*0.38
        c.create_oval(tx-r,ty-r,tx+r,ty+r,fill='#606060',outline='#808080',width=1)
        c.create_oval(tx-ri,ty-ri,tx+ri,ty+ri,fill='#1A3A1A',outline='#2A5A2A',width=1)
        c.create_oval(tx-r,ty-r,tx+r,ty+r,fill='',outline=AMARELO,
                      width=max(1,int(1.5*zoom)),dash=(8,5))
    elif t=='v_semaforo':
        r=max(5,int(8*zoom)); bw=r*1.6; bh=r*5
        c.create_rectangle(tx-bw/2,ty-bh/2,tx+bw/2,ty+bh/2,fill='#111',outline='#444',width=1)
        for oy_,cor_ in [(-r*1.6,'#CC2200'),(0,'#CCAA00'),(r*1.6,'#00AA00')]:
            c.create_oval(tx-r*0.6,ty+oy_-r*0.6,tx+r*0.6,ty+oy_+r*0.6,
                          fill=cor_,outline='#222',width=1)
        c.create_line(tx,ty+bh/2,tx,ty+bh/2+r*2,fill='#666',width=max(2,int(2*zoom)))
    elif t=='v_placa':
        lb=el.get('label','PARE'); r=max(6,int(10*zoom))
        cor_p=el.get('cor_placa','#CC0000'); chave_p=el.get('chave_placa','pare')
        c.create_line(tx,ty+r,tx,ty+r*2.5,fill='#666',width=max(1,int(1.5*zoom)))
        if chave_p=='pare':
            pts=[]
            for i in range(8):
                ang=math.radians(i*45+22.5)
                pts.extend([tx+math.cos(ang)*r,ty+math.sin(ang)*r])
            c.create_polygon(pts,fill=cor_p,outline=BRANCO,width=max(1,int(1.5*zoom)))
            c.create_text(tx,ty,text='PARE',fill=BRANCO,
                          font=('Segoe UI',max(5,int(6*zoom)),'bold'))
        elif chave_p in ('vel_30','vel_40','vel_60','vel_80'):
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill=BRANCO,
                          outline='#CC0000',width=max(2,int(2*zoom)))
            c.create_text(tx,ty,text=lb,fill='#CC0000',
                          font=('Segoe UI',max(5,int(6*zoom)),'bold'))
        elif chave_p=='atencao':
            pts=[tx,ty-r,tx+r*0.87,ty+r*0.5,tx-r*0.87,ty+r*0.5]
            c.create_polygon(pts,fill=cor_p,outline=BRANCO,width=max(1,int(1.5*zoom)))
            c.create_text(tx,ty+3,text='!',fill=BRANCO,
                          font=('Segoe UI',max(6,int(8*zoom)),'bold'))
        elif chave_p=='proib':
            c.create_oval(tx-r,ty-r,tx+r,ty+r,fill=BRANCO,
                          outline='#CC0000',width=max(2,int(2*zoom)))
            c.create_line(tx-r*.7,ty-r*.7,tx+r*.7,ty+r*.7,
                          fill='#CC0000',width=max(2,int(2.5*zoom)))
        else:
            c.create_rectangle(tx-r,ty-r,tx+r,ty+r,fill=cor_p,outline=BRANCO,
                               width=max(1,int(1.5*zoom)))
            c.create_text(tx,ty,text=lb[:6],fill=BRANCO,
                          font=('Segoe UI',max(5,int(6*zoom)),'bold'))
    elif t=='v_arvore':
        r=max(8,int(12*zoom))
        c.create_oval(tx-r,ty-r,tx+r,ty+r,fill='#1A6A1A',outline='#2A8A2A',width=1)
        c.create_oval(tx-r*.5,ty-r*.5,tx+r*.5,ty+r*.5,fill='#2A8A2A',outline='')
    elif t=='v_poste':
        r=max(3,int(5*zoom))
        c.create_line(tx,ty-r*3,tx,ty+r*1.5,fill='#888',width=max(2,int(2*zoom)))
        c.create_oval(tx-r,ty-r*4,tx+r,ty-r*2,fill='#FFEE88',outline='#CCCC44',width=1)
        c.create_line(tx-r*2,ty-r*3,tx,ty-r*3,fill='#888',width=max(1,int(1.5*zoom)))
