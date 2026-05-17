"""
desenho/catalogo_veiculos.py — Catálogo declarativo dos veículos/pessoas
do SICRO. DADOS PUROS (sem referência a funções). É a fonte única de
verdade para: nomes, categorias, arquivo SVG esperado, cor editável e
dimensão real em metros.

Quando os SVGs chegarem, basta colocá-los em assets/veiculos/ com o
nome exato do campo "svg". Enquanto não chegam, o motor de render usa
fallback vetorial — o programa funciona normalmente.

Estrutura de cada item:
  chave        : id único interno (usado no elemento do croqui)
  nome         : nome exibido ao perito
  categoria    : agrupa no seletor (carro, moto, caminhao, ...)
  svg          : nome do arquivo SVG esperado em assets/veiculos/
  cor_editavel : True = perito escolhe a cor; False = cor fixa institucional
  cor_padrao   : cor inicial (editáveis) ou cor fixa (institucionais)
  larg_m       : comprimento real do veículo em metros (eixo de deslocamento)
  alt_m        : largura real do veículo em metros (perpendicular)
"""

# Cores de referência (espelham o tema; valores diretos p/ não acoplar)
_AZUL   = "#4F72E0"
_VERDE  = "#3A8A3A"
_VERM   = "#C0392B"
_BRANCO = "#F2F2F2"
_CINZA  = "#8A8A8A"
_AMARELO= "#F0B429"
_PRETO  = "#2A2A2A"

CATALOGO = [
    # ---------------- CARROS ----------------
    {"chave":"carro_sedan","nome":"Carro Sedan","categoria":"carro",
     "svg":"carro_sedan.svg","cor_editavel":True,"cor_padrao":_AZUL,
     "larg_m":4.6,"alt_m":1.8},
    {"chave":"carro_suv","nome":"Carro SUV","categoria":"carro",
     "svg":"carro_suv.svg","cor_editavel":True,"cor_padrao":_VERDE,
     "larg_m":4.7,"alt_m":1.9},
    {"chave":"carro_hatch","nome":"Carro Hatch","categoria":"carro",
     "svg":"carro_hatch.svg","cor_editavel":True,"cor_padrao":_VERM,
     "larg_m":4.0,"alt_m":1.8},
    {"chave":"taxi","nome":"Táxi","categoria":"carro",
     "svg":"taxi.svg","cor_editavel":False,"cor_padrao":_AMARELO,
     "larg_m":4.6,"alt_m":1.8},

    # ---------------- MOTOS ----------------
    {"chave":"moto_urbana","nome":"Moto Urbana","categoria":"moto",
     "svg":"moto_urbana.svg","cor_editavel":True,"cor_padrao":_AZUL,
     "larg_m":2.1,"alt_m":0.8},
    {"chave":"moto_esportiva","nome":"Moto Esportiva","categoria":"moto",
     "svg":"moto_esportiva.svg","cor_editavel":True,"cor_padrao":_VERM,
     "larg_m":2.0,"alt_m":0.7},
    {"chave":"moto_carga","nome":"Motoboy / Carga","categoria":"moto",
     "svg":"moto_carga.svg","cor_editavel":True,"cor_padrao":_VERDE,
     "larg_m":2.2,"alt_m":0.9},

    # ---------------- BICICLETAS ----------------
    {"chave":"bike_urbana","nome":"Bicicleta Urbana","categoria":"bicicleta",
     "svg":"bike_urbana.svg","cor_editavel":True,"cor_padrao":_AZUL,
     "larg_m":1.7,"alt_m":0.6},
    {"chave":"bike_estrada","nome":"Bicicleta Estrada","categoria":"bicicleta",
     "svg":"bike_estrada.svg","cor_editavel":True,"cor_padrao":_VERM,
     "larg_m":1.7,"alt_m":0.6},
    {"chave":"bike_cargueira","nome":"Bicicleta Cargueira","categoria":"bicicleta",
     "svg":"bike_cargueira.svg","cor_editavel":True,"cor_padrao":_VERDE,
     "larg_m":2.2,"alt_m":0.8},

    # ---------------- CAMINHÕES ----------------
    {"chave":"caminhao_leve","nome":"Caminhão Leve","categoria":"caminhao",
     "svg":"caminhao_leve.svg","cor_editavel":True,"cor_padrao":_VERM,
     "larg_m":6.5,"alt_m":2.2},
    {"chave":"caminhao_pesado","nome":"Caminhão Pesado","categoria":"caminhao",
     "svg":"caminhao_pesado.svg","cor_editavel":True,"cor_padrao":"#C06020",
     "larg_m":9.0,"alt_m":2.6},
    {"chave":"carreta_longa","nome":"Carreta Longa","categoria":"caminhao",
     "svg":"carreta_longa.svg","cor_editavel":True,"cor_padrao":_CINZA,
     "larg_m":18.0,"alt_m":2.6},
    {"chave":"reboque_guincho","nome":"Reboque (Guincho)","categoria":"caminhao",
     "svg":"reboque_guincho.svg","cor_editavel":True,"cor_padrao":_AMARELO,
     "larg_m":7.0,"alt_m":2.4},

    # ---------------- VANS ----------------
    {"chave":"van_passageiro","nome":"Van Passageiro","categoria":"van",
     "svg":"van_passageiro.svg","cor_editavel":True,"cor_padrao":_BRANCO,
     "larg_m":5.5,"alt_m":2.0},
    {"chave":"van_furgao","nome":"Van Furgão","categoria":"van",
     "svg":"van_furgao.svg","cor_editavel":True,"cor_padrao":_BRANCO,
     "larg_m":5.5,"alt_m":2.0},

    # ---------------- ÔNIBUS ----------------
    {"chave":"onibus_conv","nome":"Ônibus Convencional","categoria":"onibus",
     "svg":"onibus_conv.svg","cor_editavel":True,"cor_padrao":_AZUL,
     "larg_m":12.0,"alt_m":2.6},
    {"chave":"microonibus","nome":"Microônibus","categoria":"onibus",
     "svg":"microonibus.svg","cor_editavel":True,"cor_padrao":_BRANCO,
     "larg_m":8.0,"alt_m":2.4},
    {"chave":"onibus_leito","nome":"Ônibus Grande (Leito)","categoria":"onibus",
     "svg":"onibus_leito.svg","cor_editavel":True,"cor_padrao":_CINZA,
     "larg_m":14.0,"alt_m":2.6},

    # ---------------- EMERGÊNCIA / INSTITUCIONAL (cor fixa) ----------------
    {"chave":"ambulancia","nome":"Ambulância","categoria":"emergencia",
     "svg":"ambulancia.svg","cor_editavel":False,"cor_padrao":_BRANCO,
     "larg_m":5.5,"alt_m":2.1},
    {"chave":"vtr_pm","nome":"VTR PM","categoria":"emergencia",
     "svg":"vtr_pm.svg","cor_editavel":False,"cor_padrao":_BRANCO,
     "larg_m":4.7,"alt_m":1.9},
    {"chave":"vtr_pci","nome":"VTR PCI","categoria":"emergencia",
     "svg":"vtr_pci.svg","cor_editavel":False,"cor_padrao":_BRANCO,
     "larg_m":4.7,"alt_m":1.9},
    {"chave":"vtr_bm","nome":"VTR BM","categoria":"emergencia",
     "svg":"vtr_bm.svg","cor_editavel":False,"cor_padrao":_VERM,
     "larg_m":6.5,"alt_m":2.3},
    {"chave":"vtr_pc","nome":"VTR PC","categoria":"emergencia",
     "svg":"vtr_pc.svg","cor_editavel":False,"cor_padrao":_PRETO,
     "larg_m":4.7,"alt_m":1.9},
    {"chave":"vtr_pp","nome":"VTR Polícia Penal","categoria":"emergencia",
     "svg":"vtr_pp.svg","cor_editavel":False,"cor_padrao":_CINZA,
     "larg_m":4.7,"alt_m":1.9},

    # ---------------- OUTROS ----------------
    {"chave":"trator","nome":"Trator","categoria":"outros",
     "svg":"trator.svg","cor_editavel":True,"cor_padrao":_VERM,
     "larg_m":4.5,"alt_m":2.2},

    # ---------------- PEDESTRES (cor fixa, neutra) ----------------
    {"chave":"ped_m_dorsal","nome":"Pedestre M. Dorsal","categoria":"pedestre",
     "svg":"ped_m_dorsal.svg","cor_editavel":False,"cor_padrao":"#C8C8C8",
     "larg_m":1.75,"alt_m":0.5},
    {"chave":"ped_m_ventral","nome":"Pedestre M. Ventral","categoria":"pedestre",
     "svg":"ped_m_ventral.svg","cor_editavel":False,"cor_padrao":"#C8C8C8",
     "larg_m":1.75,"alt_m":0.5},
    {"chave":"ped_m_lateral","nome":"Pedestre M. Lateral","categoria":"pedestre",
     "svg":"ped_m_lateral.svg","cor_editavel":False,"cor_padrao":"#C8C8C8",
     "larg_m":1.75,"alt_m":0.5},
    {"chave":"ped_f_dorsal","nome":"Pedestre F. Dorsal","categoria":"pedestre",
     "svg":"ped_f_dorsal.svg","cor_editavel":False,"cor_padrao":"#C8C8C8",
     "larg_m":1.65,"alt_m":0.45},
    {"chave":"ped_f_ventral","nome":"Pedestre F. Ventral","categoria":"pedestre",
     "svg":"ped_f_ventral.svg","cor_editavel":False,"cor_padrao":"#C8C8C8",
     "larg_m":1.65,"alt_m":0.45},
    {"chave":"ped_f_lateral","nome":"Pedestre F. Lateral","categoria":"pedestre",
     "svg":"ped_f_lateral.svg","cor_editavel":False,"cor_padrao":"#C8C8C8",
     "larg_m":1.65,"alt_m":0.45},
]

# Ordem e rótulos das categorias no seletor
CATEGORIAS = [
    ("carro",      "🚗", "Carros"),
    ("moto",       "🏍", "Motos"),
    ("bicicleta",  "🚲", "Bicicletas"),
    ("caminhao",   "🚚", "Caminhões"),
    ("van",        "🚐", "Vans"),
    ("onibus",     "🚌", "Ônibus"),
    ("emergencia", "🚨", "Emergência"),
    ("outros",     "🚜", "Outros"),
    ("pedestre",   "🚶", "Pedestres"),
]

# ── Índices auxiliares (montados uma vez) ──
POR_CHAVE = {it["chave"]: it for it in CATALOGO}

def por_categoria(cat):
    """Lista os itens de uma categoria, na ordem do catálogo."""
    return [it for it in CATALOGO if it["categoria"] == cat]

def get(chave):
    """Retorna o item pela chave, ou None."""
    return POR_CHAVE.get(chave)

def total():
    return len(CATALOGO)


if __name__ == "__main__":
    # Autoteste rápido
    print(f"Total de itens: {total()}")
    assert total() == 32, f"Esperado 32, achei {total()}"
    cats = {}
    for it in CATALOGO:
        cats.setdefault(it["categoria"], 0)
        cats[it["categoria"]] += 1
    print("Por categoria:")
    for cat, ico, nome in CATEGORIAS:
        n = cats.get(cat, 0)
        print(f"  {ico} {nome:14s}: {n}")
    # Conferir chaves únicas
    chaves = [it["chave"] for it in CATALOGO]
    assert len(chaves) == len(set(chaves)), "Há chaves duplicadas!"
    # Conferir svg único
    svgs = [it["svg"] for it in CATALOGO]
    assert len(svgs) == len(set(svgs)), "Há SVGs duplicados!"
    print("\nTodos os checks passaram. Catálogo íntegro.")
