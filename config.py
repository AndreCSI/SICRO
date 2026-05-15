"""
config.py — Constantes globais do SICRO PCI/AP
Paleta de cores, fontes, diretórios, listas e catálogos.
Extraído do monolito sicro_pci_ap_v16.py — etapa 1 da refatoração.
REGRA: nenhuma lógica aqui, apenas valores.
"""

import sys
import math
from pathlib import Path

# ─────────────────────────────────────────────
#  RESOLUÇÃO DE CAMINHOS (PyInstaller / dev)
# ─────────────────────────────────────────────
def resource_path(relative):
    """Resolve caminhos dentro do .exe (PyInstaller) ou em desenvolvimento."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative
    return Path(__file__).parent / relative


# ─────────────────────────────────────────────
#  DIRETÓRIOS
# ─────────────────────────────────────────────
DIR_CROQUIS = Path.home() / "SicroPCIAP" / "croquis"
DIR_CROQUIS.mkdir(parents=True, exist_ok=True)

DIR_ASSETS = resource_path("assets/veiculos")


# ─────────────────────────────────────────────
#  PALETA OFICIAL PCI/AP
#  Azul Royal + Amarelo + Branco
# ─────────────────────────────────────────────
AZUL_ROYAL   = "#1A3A8F"
AZUL_ESCURO  = "#0D2260"
AZUL_MEDIO   = "#2952C4"
AZUL_CLARO   = "#4F72E0"
AMARELO      = "#F5C800"
AMARELO_ESC  = "#C9A200"
BRANCO       = "#FFFFFF"
CINZA_CLARO  = "#D8DCF0"
CINZA_MEDIO  = "#8890B8"
CINZA_ESCURO = "#3A3F5C"
PRETO_SOFT   = "#12172A"

# Aliases funcionais
COR_FUNDO     = PRETO_SOFT
COR_PAINEL    = AZUL_ESCURO
COR_CARD      = "#162050"
COR_BORDA     = AZUL_MEDIO
COR_TEXTO     = BRANCO
COR_TEXTO_SEC = CINZA_CLARO
COR_SUCESSO   = "#4CD98A"
COR_AVISO     = AMARELO
COR_PERIGO    = "#E05555"
COR_R1        = "#FF1A1A"
COR_R2        = "#0A3D8F"
COR_COTA      = AMARELO


# ─────────────────────────────────────────────
#  FONTES
# ─────────────────────────────────────────────
FONTE_SUB    = ("Segoe UI", 11, "bold")
FONTE_NORMAL = ("Segoe UI", 10)
FONTE_PEQ    = ("Segoe UI", 9)
FONTE_MONO   = ("Consolas", 9)

FONTES_DISPONIVEIS = [
    "Segoe UI", "Arial", "Calibri", "Times New Roman",
    "Courier New", "Verdana", "Tahoma", "Georgia",
]


# ─────────────────────────────────────────────
#  MUNICÍPIOS DO AMAPÁ (ordem oficial)
# ─────────────────────────────────────────────
MUNICIPIOS_AP = [
    "Macapá",
    "Santana",
    "Laranjal do Jari",
    "Oiapoque",
    "Tartarugalzinho",
    "Mazagão",
    "Porto Grande",
    "Calçoene",
    "Pedra Branca do Amapari",
    "Vitória do Jari",
    "Serra do Navio",
    "Amapá",
    "Ferreira Gomes",
    "Itaubal",
    "Cutias",
    "Pracuúba",
]


# ─────────────────────────────────────────────
#  TIPO_INFO — ícone e nome legível por tipo de elemento
# ─────────────────────────────────────────────
TIPO_INFO = {
    "carro":          ("🚗", "Carro"),
    "moto":           ("🏍", "Moto"),
    "caminhao":       ("🚚", "Caminhão"),
    "bicicleta":      ("🚲", "Bicicleta"),
    "pedestre":       ("🚶", "Pedestre"),
    "sc":             ("✕",  "Sítio de colisão"),
    "cota":           ("↔",  "Cota"),
    "r1":             ("R1", "Eixo R1"),
    "r2":             ("R2", "Eixo R2"),
    "via_h":          ("══", "Via horizontal"),
    "via_v":          ("║",  "Via vertical"),
    "texto":          ("T",  "Texto"),
    "_asfalto":       ("▬",  "Asfalto"),
    "_calcada":       ("▭",  "Calçada"),
    "_canteiro":      ("▬",  "Canteiro"),
    "_faixa_h":       ("- -","Faixa H"),
    "_faixa_v":       ("| |","Faixa V"),
    "_rotatoria":     ("◎",  "Rotatória"),
    "_asfalto_terra": ("▬",  "Estrada"),
    # Tipos do editor de via
    "v_asfalto":   ("▬",  "Asfalto"),
    "v_calcada":   ("▭",  "Calçada"),
    "v_faixa_am":  ("══", "Faixa amarela"),
    "v_faixa_br":  ("---","Faixa branca"),
    "v_faixa_ped": ("⊟",  "Faixa pedestre"),
    "v_rotatoria": ("◎",  "Rotatória"),
    "v_semaforo":  ("⬛", "Semáforo"),
    "v_placa":     ("⬡",  "Placa"),
    "v_arvore":    ("✿",  "Árvore"),
    "v_poste":     ("⌂",  "Poste"),
    "v_conflito":  ("⚠",  "Conflito"),
}


# ─────────────────────────────────────────────
#  MODELOS DE VIA — lista para o popup de seleção
# ─────────────────────────────────────────────
MODELOS_VIA = [
    {"nome": "Cruzamento em +", "icone": "cruzamento_mais", "desc": "Interseção ortogonal\nquatro vias"},
    {"nome": "Cruzamento em T", "icone": "cruzamento_t",    "desc": "Interseção em T\ntrês vias"},
    {"nome": "Cruzamento em Y", "icone": "cruzamento_y",    "desc": "Bifurcação em Y\ntrês vias oblíquas"},
    {"nome": "Rua reta",        "icone": "rua_reta",        "desc": "Via simples reta\nduplo sentido"},
    {"nome": "Rua com curva",   "icone": "rua_curva",       "desc": "Via com curva à direita"},
    {"nome": "Avenida larga",   "icone": "avenida",         "desc": "Avenida com canteiro\ncentral"},
    {"nome": "Rotatória",       "icone": "rotatoria",       "desc": "Rotatória / retorno\ncircular"},
    {"nome": "Estrada rural",   "icone": "estrada",         "desc": "Estrada sem pavimento\nzona rural"},
    {"nome": "Em branco",       "icone": "branco",          "desc": "Canvas livre\nsem modelo"},
]


# ─────────────────────────────────────────────
#  FERRAMENTAS DO EDITOR DE VIA
# ─────────────────────────────────────────────
FERRAMENTAS_VIA = [
    ("asfalto",   "▬",  "Asfalto / pista"),
    ("calcada",   "▭",  "Calçada / passeio"),
    ("faixa_am",  "══", "Faixa amarela"),
    ("faixa_br",  "---","Faixa branca"),
    ("faixa_ped", "⊟",  "Faixa de pedestre"),
    ("rotatoria", "◎",  "Rotatória"),
    ("semaforo",  "⬛", "Semáforo"),
    ("placa",     "⬡",  "Placa de trânsito"),
    ("arvore",    "✿",  "Árvore"),
    ("poste",     "⌂",  "Poste"),
    ("conflito",  "⚠",  "Área de conflito"),
]


# ─────────────────────────────────────────────
#  MODELOS DE PLACAS DE TRÂNSITO
# ─────────────────────────────────────────────
MODELOS_PLACA = [
    {"chave": "pare",    "label": "PARE", "cor": "#CC0000", "desc": "Parada obrigatória"},
    {"chave": "vel_30",  "label": "30",   "cor": "#CC6600", "desc": "Velocidade máx. 30km/h"},
    {"chave": "vel_40",  "label": "40",   "cor": "#CC6600", "desc": "Velocidade máx. 40km/h"},
    {"chave": "vel_60",  "label": "60",   "cor": "#CC6600", "desc": "Velocidade máx. 60km/h"},
    {"chave": "vel_80",  "label": "80",   "cor": "#CC6600", "desc": "Velocidade máx. 80km/h"},
    {"chave": "proib",   "label": "🚫",   "cor": "#CC0000", "desc": "Proibido"},
    {"chave": "atencao", "label": "⚠",    "cor": "#CC8800", "desc": "Atenção / perigo"},
    {"chave": "ped",     "label": "🚶",   "cor": "#005500", "desc": "Passagem de pedestre"},
    {"chave": "custom",  "label": "...",  "cor": "#003388", "desc": "Personalizada"},
]


# ─────────────────────────────────────────────
#  GERADOR DE ELEMENTOS DE MODELO DE VIA
# ─────────────────────────────────────────────
def gerar_elementos_modelo(icone, W, H):
    """
    Retorna lista de elementos pré-desenhados para cada modelo de via.
    Recebe o ícone do modelo e as dimensões do canvas (W, H).
    """
    cx, cy = W // 2, H // 2
    v = 80  # largura padrão da via em pixels do mundo

    if icone == "cruzamento_mais":
        return [
            {"tipo": "_asfalto",  "x": 0,       "y": cy-v/2, "x2": W,       "y2": cy+v/2},
            {"tipo": "_asfalto",  "x": cx-v/2,  "y": 0,      "x2": cx+v/2,  "y2": H},
            {"tipo": "_calcada",  "x": 0,        "y": 0,      "x2": cx-v/2,  "y2": cy-v/2},
            {"tipo": "_calcada",  "x": cx+v/2,  "y": 0,      "x2": W,       "y2": cy-v/2},
            {"tipo": "_calcada",  "x": 0,        "y": cy+v/2, "x2": cx-v/2,  "y2": H},
            {"tipo": "_calcada",  "x": cx+v/2,  "y": cy+v/2, "x2": W,       "y2": H},
            {"tipo": "_faixa_h",  "x": 0,        "y": cy,     "x2": cx-v/2,  "y2": cy},
            {"tipo": "_faixa_h",  "x": cx+v/2,  "y": cy,     "x2": W,       "y2": cy},
            {"tipo": "_faixa_v",  "x": cx,       "y": 0,      "x2": cx,      "y2": cy-v/2},
            {"tipo": "_faixa_v",  "x": cx,       "y": cy+v/2, "x2": cx,      "y2": H},
        ]
    elif icone == "cruzamento_t":
        return [
            {"tipo": "_asfalto", "x": 0,       "y": cy-v/2, "x2": W,      "y2": cy+v/2},
            {"tipo": "_asfalto", "x": cx-v/2,  "y": 0,      "x2": cx+v/2, "y2": cy},
            {"tipo": "_calcada", "x": 0,        "y": 0,      "x2": cx-v/2, "y2": cy-v/2},
            {"tipo": "_calcada", "x": cx+v/2,  "y": 0,      "x2": W,      "y2": cy-v/2},
            {"tipo": "_calcada", "x": 0,        "y": cy+v/2, "x2": W,      "y2": H},
            {"tipo": "_faixa_h", "x": 0,        "y": cy,     "x2": cx-v/2, "y2": cy},
            {"tipo": "_faixa_h", "x": cx+v/2,  "y": cy,     "x2": W,      "y2": cy},
            {"tipo": "_faixa_v", "x": cx,       "y": 0,      "x2": cx,     "y2": cy-v/2},
        ]
    elif icone == "rua_reta":
        return [
            {"tipo": "_asfalto", "x": 0, "y": cy-v/2, "x2": W, "y2": cy+v/2},
            {"tipo": "_calcada", "x": 0, "y": 0,       "x2": W, "y2": cy-v/2},
            {"tipo": "_calcada", "x": 0, "y": cy+v/2,  "x2": W, "y2": H},
            {"tipo": "_faixa_h", "x": 0, "y": cy,      "x2": W, "y2": cy},
        ]
    elif icone == "avenida":
        cant = 20
        return [
            {"tipo": "_asfalto",  "x": 0, "y": cy-v-cant//2,  "x2": W, "y2": cy-cant//2},
            {"tipo": "_asfalto",  "x": 0, "y": cy+cant//2,    "x2": W, "y2": cy+v+cant//2},
            {"tipo": "_calcada",  "x": 0, "y": 0,              "x2": W, "y2": cy-v-cant//2},
            {"tipo": "_calcada",  "x": 0, "y": cy+v+cant//2,   "x2": W, "y2": H},
            {"tipo": "_canteiro", "x": 0, "y": cy-cant//2,     "x2": W, "y2": cy+cant//2},
            {"tipo": "_faixa_h",  "x": 0, "y": cy-v/2-cant//2, "x2": W, "y2": cy-v/2-cant//2},
            {"tipo": "_faixa_h",  "x": 0, "y": cy+v/2+cant//2, "x2": W, "y2": cy+v/2+cant//2},
        ]
    elif icone == "rotatoria":
        return [{"tipo": "_rotatoria", "x": cx, "y": cy, "r": v * 1.2}]
    elif icone == "estrada":
        return [
            {"tipo": "_asfalto_terra", "x": 0, "y": cy-v/2, "x2": W, "y2": cy+v/2},
            {"tipo": "_faixa_h",       "x": 0, "y": cy,     "x2": W, "y2": cy},
        ]
    elif icone == "cruzamento_y":
        els = [{"tipo": "_calcada", "x": 0, "y": 0, "x2": W, "y2": H}]
        for ang in [90, 210, 330]:
            rad = math.radians(ang)
            x2 = cx + math.cos(rad) * (W // 2 + 10)
            y2 = cy - math.sin(rad) * (H // 2 + 10)
            els.append({
                "tipo": "_asfalto",
                "x": min(cx, x2) - v/2, "y": min(cy, y2) - v/2,
                "x2": max(cx, x2) + v/2, "y2": max(cy, y2) + v/2,
            })
        return els
    elif icone == "rua_curva":
        return [
            {"tipo": "_asfalto", "x": 0,       "y": cy-v/2, "x2": cx+v/2, "y2": cy+v/2},
            {"tipo": "_asfalto", "x": cx-v/2,  "y": cy-v/2, "x2": cx+v/2, "y2": H},
            {"tipo": "_calcada", "x": 0,        "y": 0,      "x2": W,      "y2": cy-v/2},
            {"tipo": "_calcada", "x": cx+v/2,  "y": 0,      "x2": W,      "y2": H},
            {"tipo": "_calcada", "x": 0,        "y": cy+v/2, "x2": cx-v/2, "y2": H},
        ]
    return []