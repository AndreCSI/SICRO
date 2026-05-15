"""
tema.py — Sistema de design centralizado do SICRO PCI/AP
Versao 2 — cores ajustadas para aproximar da proposta visual.
"""

# ─────────────────────────────────────────────
#  PALETA PRINCIPAL
# ─────────────────────────────────────────────
FUNDO_BASE      = "#060B14"   # fundo mais escuro, quase preto azulado
FUNDO_PAINEL    = "#0A1628"   # painel principal
FUNDO_CARD      = "#0F1C35"   # cards e itens de lista
FUNDO_HOVER     = "#142240"   # hover
FUNDO_ATIVO     = "#1A3A8F"   # item selecionado — azul royal sólido
FUNDO_ELEVADO   = "#1E3460"   # painéis flutuantes

DOURADO         = "#F0B429"   # acento principal — mais brilhante
DOURADO_CLARO   = "#F5C842"   # hover
DOURADO_ESCURO  = "#B8880A"   # pressionado
AMARELO_ALERTA  = "#F5C800"   # alertas PCA

AZUL_BORDA      = "#1A3060"   # bordas sutis
AZUL_MEDIO      = "#2952C4"   # destaques
AZUL_CLARO      = "#4F72E0"   # links, ícones ativos
AZUL_GLOW       = "#3A5EAA"   # glow

TEXTO_PRIMARIO  = "#F0F4FF"   # quase branco puro
TEXTO_SECUNDARIO= "#7A88AA"   # labels, descrições
TEXTO_TERCIARIO = "#3A4468"   # placeholders
TEXTO_INVERTIDO = "#060B14"   # sobre fundos claros

COR_SUCESSO     = "#3DB87A"
COR_PERIGO      = "#C94040"
COR_AVISO       = AMARELO_ALERTA
COR_INFO        = AZUL_CLARO
COR_R1          = "#E02020"
COR_R2          = "#1A4FBF"
COR_COTA        = DOURADO

# Aliases compatibilidade
AZUL_ROYAL      = "#1A3A8F"
AZUL_ESCURO     = FUNDO_PAINEL
BRANCO          = TEXTO_PRIMARIO
CINZA_CLARO     = TEXTO_SECUNDARIO
CINZA_MEDIO     = TEXTO_TERCIARIO
CINZA_ESCURO    = "#3A3F5C"
PRETO_SOFT      = FUNDO_BASE
AMARELO         = DOURADO
COR_FUNDO       = FUNDO_BASE
COR_PAINEL      = FUNDO_PAINEL
COR_CARD        = FUNDO_CARD
COR_BORDA       = AZUL_BORDA
COR_TEXTO       = TEXTO_PRIMARIO
COR_TEXTO_SEC   = TEXTO_SECUNDARIO

# ─────────────────────────────────────────────
#  TIPOGRAFIA
# ─────────────────────────────────────────────
FAMILIA         = "Segoe UI"
TAM_DISPLAY     = 28
TAM_H1          = 18
TAM_H2          = 14
TAM_H3          = 11
TAM_BODY        = 10
TAM_SMALL       = 9
TAM_MICRO       = 8

FONTE_DISPLAY   = (FAMILIA, TAM_DISPLAY, "bold")
FONTE_H1        = (FAMILIA, TAM_H1,      "bold")
FONTE_H2        = (FAMILIA, TAM_H2,      "bold")
FONTE_H3        = (FAMILIA, TAM_H3,      "bold")
FONTE_BODY      = (FAMILIA, TAM_BODY)
FONTE_BODY_BOLD = (FAMILIA, TAM_BODY,    "bold")
FONTE_SMALL     = (FAMILIA, TAM_SMALL)
FONTE_SMALL_BOLD= (FAMILIA, TAM_SMALL,   "bold")
FONTE_MICRO     = (FAMILIA, TAM_MICRO)
FONTE_MONO      = ("Consolas", TAM_SMALL)

FONTE_SUB       = FONTE_H3
FONTE_NORMAL    = FONTE_BODY
FONTE_PEQ       = FONTE_SMALL

# ─────────────────────────────────────────────
#  GEOMETRIA
# ─────────────────────────────────────────────
RAIO_BORDA      = 10
RAIO_BORDA_SM   = 6
RAIO_BORDA_LG   = 14

ESPACO_XS       = 4
ESPACO_SM       = 8
ESPACO_MD       = 14
ESPACO_LG       = 20
ESPACO_XL       = 28

LARGURA_SIDEBAR_EDITOR  = 56
LARGURA_SIDEBAR_INICIO  = 220
LARGURA_PAINEL_DIR      = 280

ALTURA_HEADER   = 52
ALTURA_STATUS   = 28
ALTURA_BARRA_TOP= 4

# ─────────────────────────────────────────────
#  SPLASH
# ─────────────────────────────────────────────
SPLASH_W        = 900
SPLASH_H        = 560
SPLASH_DURACAO  = 4000

SPLASH_MSGS = [
    (0,   "Inicializando sistema..."),
    (20,  "Carregando interface..."),
    (45,  "Carregando biblioteca de croquis..."),
    (65,  "Preparando ferramentas periciais..."),
    (85,  "Verificando assets..."),
    (95,  "Pronto."),
]

# ─────────────────────────────────────────────
#  SIDEBAR TELA INICIAL
# ─────────────────────────────────────────────
SIDEBAR_ITENS = [
    ("inicio",       "⌂",  "Início"),
    ("recentes",     "◷",  "Croquis recentes"),
    ("modelos",      "▦",  "Modelos de via"),
    ("biblioteca",   "▤",  "Biblioteca"),
    ("sep", None, None),
    ("configuracoes","⚙",  "Configurações"),
]