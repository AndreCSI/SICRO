"""
criar_io.py — Cria io/salvar.py
Execute com: python criar_io.py
"""
from pathlib import Path

linhas = [
    "import json\n",
    "import datetime\n",
    "import sys\n",
    "from pathlib import Path\n",
    "_raiz = Path(__file__).parent.parent\n",
    "if str(_raiz) not in sys.path:\n",
    "    sys.path.insert(0, str(_raiz))\n",
    "from config import DIR_CROQUIS\n",
    "\n",
    "\n",
    "def salvar_croqui(dados_caso, modo, elementos, calibrado, k, u_k):\n",
    "    dados = {\n",
    "        **dados_caso,\n",
    "        'modo':      modo,\n",
    "        'k':         k,\n",
    "        'u_k':       u_k,\n",
    "        'calibrado': calibrado,\n",
    "        'elementos': elementos,\n",
    "    }\n",
    "    bo   = dados_caso.get('bo', '').replace('/', '-')\n",
    "    nome = f\"BO_{bo}_{datetime.date.today()}.sicro\"\n",
    "    cam  = DIR_CROQUIS / nome\n",
    "    with open(cam, 'w', encoding='utf-8') as f:\n",
    "        json.dump(dados, f, ensure_ascii=False, indent=2)\n",
    "    return cam\n",
    "\n",
    "\n",
    "def carregar_croqui(caminho):\n",
    "    with open(caminho, encoding='utf-8') as f:\n",
    "        dados = json.load(f)\n",
    "    caso = {k: dados[k] for k in\n",
    "            ('bo', 'requisicao', 'local', 'municipio', 'perito', 'data')\n",
    "            if k in dados}\n",
    "    return {\n",
    "        'caso':       caso,\n",
    "        'modo':       dados.get('modo', 'zero'),\n",
    "        'elementos':  dados.get('elementos', []),\n",
    "        'calibrado':  dados.get('calibrado', False),\n",
    "        'k':          dados.get('k'),\n",
    "        'u_k':        dados.get('u_k'),\n",
    "    }\n",
    "\n",
    "\n",
    "def listar_croquis():\n",
    "    return sorted(DIR_CROQUIS.glob('*.sicro'), reverse=True)\n",
]

dest = Path("arquivo") / "salvar.py"
dest.write_text("".join(linhas), encoding="utf-8")
print(f"OK — {dest} criado com {len(linhas)} linhas")

import importlib.util
spec = importlib.util.spec_from_file_location("salvar", dest)
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
fns = ["salvar_croqui", "carregar_croqui", "listar_croquis"]
ok  = all(hasattr(mod, f) for f in fns)
print(f"Funcoes {fns}: {'OK!' if ok else 'ERRO!'}")
print("Rode: python main.py")