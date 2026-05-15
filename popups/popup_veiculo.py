import tkinter as tk
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import (
    COR_FUNDO, COR_PAINEL, COR_CARD, AMARELO, BRANCO, CINZA_CLARO,
    FONTE_SUB, FONTE_PEQ, AZUL_CLARO, COR_PERIGO,
)
from desenho.veiculos_arte import (
    arte_sedan, arte_suv, arte_hatch,
    arte_moto_esportiva, arte_moto_urbana, arte_moto_carga,
    arte_caminhao_leve, arte_caminhao_truck, arte_caminhao_carreta,
)


# Catalogo de modelos de veiculos
MODELOS_VEICULOS = {
    'carro': [
        {'chave':'sedan',  'nome':'Sedan',       'desc':'4 portas',        'arte':arte_sedan,          'png':'sedan.png', 'larg':28,'alt':14,'cor':AZUL_CLARO},
        {'chave':'suv',    'nome':'SUV / Picape', 'desc':'4x4, utilitario', 'arte':arte_suv,            'png':'suv.png',   'larg':30,'alt':16,'cor':'#3A8A3A'},
        {'chave':'hatch',  'nome':'Hatchback',    'desc':'Compacto',        'arte':arte_hatch,          'png':'hatch.png', 'larg':24,'alt':13,'cor':'#A04040'},
    ],
    'moto': [
        {'chave':'esportiva','nome':'Esportiva',      'desc':'Moto baixa',    'arte':arte_moto_esportiva,'larg':20,'alt':7,'cor':'#9B3030'},
        {'chave':'urbana',   'nome':'Urbana / Naked', 'desc':'Guidad alto',   'arte':arte_moto_urbana,  'larg':18,'alt':8,'cor':'#9B6BDF'},
        {'chave':'carga',    'nome':'Motoboy / Carga','desc':'Com bau',       'arte':arte_moto_carga,   'larg':22,'alt':9,'cor':'#3A6A3A'},
    ],
    'caminhao': [
        {'chave':'leve',   'nome':'Caminhao leve', 'desc':'VUC / 3/4',           'arte':arte_caminhao_leve,   'larg':36,'alt':16,'cor':COR_PERIGO},
        {'chave':'truck',  'nome':'Caminhao truck','desc':'Toco / truck',         'arte':arte_caminhao_truck,  'larg':48,'alt':18,'cor':'#C06020'},
        {'chave':'carreta','nome':'Carreta',        'desc':'Bitrem / semirreboque','arte':arte_caminhao_carreta,'larg':56,'alt':17,'cor':'#606060'},
    ],
}


class PopupModeloVeiculo(tk.Toplevel):
    def __init__(self, parent, tipo_base):
        super().__init__(parent)
        self.title(f'Escolha o modelo - {tipo_base.capitalize()}')
        self.configure(bg=COR_FUNDO)
        self.resizable(False, False)
        self.resultado = None
        modelos = MODELOS_VEICULOS.get(tipo_base, [])
        n = len(modelos)
        card_w, card_h = 210, 175
        pad = 12
        w = n * card_w + (n + 1) * pad
        h = 310
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        self.lift()
        self.focus_force()
        self.grab_set()
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x')
        cab = tk.Frame(self, bg=COR_PAINEL)
        cab.pack(fill='x')
        icone_cat = {'carro':'🚗','moto':'🏍','caminhao':'🚚'}.get(tipo_base,'🚗')
        tk.Label(cab, text=f'{icone_cat}  Escolha o modelo de {tipo_base}',
                 font=FONTE_SUB, bg=COR_PAINEL, fg=AMARELO).pack(
                     side='left', padx=16, pady=10)
        grid_frame = tk.Frame(self, bg=COR_FUNDO)
        grid_frame.pack(fill='both', expand=True, padx=pad, pady=pad)
        for col, modelo in enumerate(modelos):
            self._card(grid_frame, modelo, col, card_w, card_h)
        tk.Frame(self, bg=AMARELO, height=4).pack(fill='x', side='bottom')

    def _card(self, parent, modelo, col, cw, ch):
        card = tk.Frame(parent, bg=COR_CARD, cursor='hand2', width=cw, height=ch)
        card.grid(row=0, column=col, padx=8, pady=4, sticky='nsew')
        card.grid_propagate(False)
        parent.grid_columnconfigure(col, weight=1)
        prev = tk.Canvas(card, width=cw-16, height=105, bg='#0D1830', highlightthickness=0)
        prev.pack(padx=8, pady=(10,4))
        self._desenhar_preview(prev, modelo, cw-16, 105)
        lbl_nome = tk.Label(card, text=modelo['nome'],
                            font=('Segoe UI',10,'bold'), bg=COR_CARD, fg=BRANCO)
        lbl_nome.pack()
        lbl_desc = tk.Label(card, text=modelo['desc'],
                            font=FONTE_PEQ, bg=COR_CARD, fg=CINZA_CLARO)
        lbl_desc.pack()
        def sel(m=modelo):
            self.resultado = m
            self.destroy()
        def hover_in(e, f=card):
            f.config(bg='#2A3060')
            for w in f.winfo_children():
                try: w.config(bg='#2A3060')
                except Exception: pass
        def hover_out(e, f=card):
            f.config(bg=COR_CARD)
            for w in f.winfo_children():
                try: w.config(bg=COR_CARD)
                except Exception: pass
        for widget in [card, prev, lbl_nome, lbl_desc]:
            widget.bind('<Button-1>', lambda e, m=modelo: sel(m))
        card.bind('<Enter>', hover_in)
        card.bind('<Leave>', hover_out)

    def _desenhar_preview(self, c, modelo, pw, ph):
        cx, cy = pw // 2, ph // 2
        larg_ref = modelo['larg']
        sc = min((pw - 24) / (larg_ref * 2.2), 1.6)
        sc = max(sc, 0.5)
        modelo['arte'](c, cx, cy, sc, modelo['cor'])
