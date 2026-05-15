"""
criar_editor_croqui.py — Cria ui/editor_croqui.py
Contém: DialogoRedimensionar + EditorCroqui + EditorVia + EditorTextoInline
Execute: python criar_editor_croqui.py
"""
from pathlib import Path
import ast, sys

# Lê o monolito
mono = Path("sicro_pci_ap_v16_7.py")
if not mono.exists():
    mono = next(Path(".").glob("sicro_pci_ap_v*.py"), None)
if not mono:
    print("ERRO: monolito nao encontrado")
    sys.exit(1)
print(f"Lendo monolito: {mono}")

with open(mono, 'r', encoding='utf-8') as f:
    all_lines = f.readlines()

# Localiza as classes pelos marcadores exatos
def achar_linha(texto):
    for i, l in enumerate(all_lines):
        if l.strip().startswith(texto):
            return i
    return None

ln_dialogo  = achar_linha("class DialogoRedimensionar")
ln_editor   = achar_linha("class EditorCroqui")
ln_placas   = achar_linha("class PopupPlacas")
ln_via      = achar_linha("class EditorVia")
ln_fontes   = achar_linha("FONTES_DISPONIVEIS")
ln_appsicro = achar_linha("class AppSicro")

print(f"DialogoRedimensionar : linha {ln_dialogo+1}")
print(f"EditorCroqui         : linha {ln_editor+1}")
print(f"PopupPlacas (limite) : linha {ln_placas+1}")
print(f"EditorVia            : linha {ln_via+1}")
print(f"FONTES_DISPONIVEIS   : linha {ln_fontes+1}")
print(f"AppSicro (limite)    : linha {ln_appsicro+1}")

# Cabeçalho com imports
header = (
    "import tkinter as tk\n"
    "from tkinter import ttk, filedialog, messagebox, simpledialog\n"
    "import json, math, datetime\n"
    "import sys\n"
    "from pathlib import Path\n"
    "_raiz = Path(__file__).parent.parent\n"
    "if str(_raiz) not in sys.path:\n"
    "    sys.path.insert(0, str(_raiz))\n"
    "\n"
    "try:\n"
    "    from PIL import Image, ImageTk\n"
    "    PIL_OK = True\n"
    "except ImportError:\n"
    "    PIL_OK = False\n"
    "\n"
    "from config import (\n"
    "    COR_FUNDO, COR_PAINEL, COR_CARD, COR_BORDA,\n"
    "    COR_TEXTO, COR_TEXTO_SEC,\n"
    "    COR_SUCESSO, COR_PERIGO, COR_AVISO,\n"
    "    COR_R1, COR_R2, COR_COTA,\n"
    "    AMARELO, BRANCO, CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_SOFT,\n"
    "    AZUL_MEDIO, AZUL_CLARO,\n"
    "    FONTE_SUB, FONTE_NORMAL, FONTE_PEQ, FONTE_MONO,\n"
    "    DIR_CROQUIS, TIPO_INFO, FERRAMENTAS_VIA, MODELOS_PLACA, MODELOS_VIA,\n"
    "    gerar_elementos_modelo,\n"
    ")\n"
    "from desenho.veiculos_arte import (\n"
    "    arte_sedan, arte_suv, arte_hatch,\n"
    "    arte_moto_esportiva, arte_moto_urbana, arte_moto_carga,\n"
    "    arte_caminhao_leve, arte_caminhao_truck, arte_caminhao_carreta,\n"
    "    arte_bicicleta, arte_pedestre, escurecer,\n"
    ")\n"
    "from popups.popup_veiculo import PopupModeloVeiculo, MODELOS_VEICULOS\n"
    "from popups.popup_placas import PopupPlacas\n"
    "from popups.popup_modelo_via import PopupModeloVia\n"
    "from widgets.editor_texto import EditorTextoInline\n"
    "\n"
    "# Aliases para compatibilidade com codigo interno do EditorCroqui\n"
    "_arte_bicicleta = arte_bicicleta\n"
    "_arte_pedestre  = arte_pedestre\n"
    "\n"
    "# Cache de imagens PNG dos veiculos\n"
    "_IMG_CACHE: dict = {}\n"
    "\n"
    "def carregar_imagem_veiculo(nome_arquivo, cor_hex):\n"
    "    if not PIL_OK: return None\n"
    "    chave = (nome_arquivo, cor_hex)\n"
    "    if chave in _IMG_CACHE: return _IMG_CACHE[chave]\n"
    "    try:\n"
    "        import numpy as np\n"
    "        from collections import deque\n"
    "        from config import DIR_ASSETS\n"
    "        caminho = DIR_ASSETS / nome_arquivo\n"
    "        if not caminho.exists(): return None\n"
    "        img = Image.open(caminho).convert('RGBA')\n"
    "        arr = np.array(img)\n"
    "        alpha = arr[:,:,3]\n"
    "        brightness = arr[:,:,0].astype(int)+arr[:,:,1].astype(int)+arr[:,:,2].astype(int)\n"
    "        if alpha.min()==255:\n"
    "            gray=(brightness//3).clip(0,255).astype('uint8')\n"
    "            visited=np.zeros(gray.shape,dtype=bool)\n"
    "            mask=np.ones(gray.shape,dtype=bool)\n"
    "            h_,w_=gray.shape; threshold=20\n"
    "            starts=([(0,x) for x in range(0,w_,4)]+[(h_-1,x) for x in range(0,w_,4)]+\n"
    "                    [(y,0) for y in range(0,h_,4)]+[(y,w_-1) for y in range(0,h_,4)])\n"
    "            queue=deque()\n"
    "            for sy,sx in starts:\n"
    "                if not visited[sy,sx] and gray[sy,sx]<threshold:\n"
    "                    visited[sy,sx]=True; mask[sy,sx]=False; queue.append((sy,sx))\n"
    "            while queue:\n"
    "                y,x=queue.popleft()\n"
    "                for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:\n"
    "                    ny,nx=y+dy,x+dx\n"
    "                    if 0<=ny<h_ and 0<=nx<w_ and not visited[ny,nx] and gray[ny,nx]<threshold:\n"
    "                        visited[ny,nx]=True; mask[ny,nx]=False; queue.append((ny,nx))\n"
    "            arr[~mask,3]=0\n"
    "        try: cr=int(cor_hex[1:3],16); cg=int(cor_hex[3:5],16); cb_=int(cor_hex[5:7],16)\n"
    "        except: cr,cg,cb_=79,114,224\n"
    "        opaque=arr[:,:,3]>30\n"
    "        escuro=(arr[:,:,0].astype(int)+arr[:,:,1].astype(int)+arr[:,:,2].astype(int))<300\n"
    "        alvo=opaque&escuro\n"
    "        arr[alvo,0]=cr; arr[alvo,1]=cg; arr[alvo,2]=cb_\n"
    "        resultado=Image.fromarray(arr); _IMG_CACHE[chave]=resultado; return resultado\n"
    "    except Exception as e:\n"
    "        print(f'[carregar_imagem_veiculo] erro: {e}'); return None\n"
    "\n"
)

# Extrai blocos do monolito
dialogo_block  = "".join(all_lines[ln_dialogo:ln_editor])
editor_block   = "".join(all_lines[ln_editor:ln_placas])
via_block      = "".join(all_lines[ln_via:ln_fontes])
texto_block    = "".join(all_lines[ln_fontes:ln_appsicro])

content = (
    header
    + "# ─── DialogoRedimensionar ───\n"
    + dialogo_block
    + "\n# ─── EditorCroqui ───\n"
    + editor_block
    + "\n# ─── EditorVia ───\n"
    + via_block
    + "\n# ─── EditorTextoInline ───\n"
    + texto_block
)

dest = Path("ui") / "editor_croqui.py"
dest.write_text(content, encoding="utf-8")
print(f"\nEscrito: {dest} ({len(content.splitlines())} linhas)")

# Valida sintaxe
try:
    ast.parse(content)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO SINTAXE linha {e.lineno}: {e.msg}")
    print(f"  Texto: {repr(e.text)}")
    sys.exit(1)

print("\nPROXIMO PASSO:")
print("  python main.py          <- ainda usa o monolito (nao mudamos nada)")
print("  Se funcionar, teste: python testar_modular.py")