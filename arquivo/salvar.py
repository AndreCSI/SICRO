import json
import datetime
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import DIR_CROQUIS


def salvar_croqui(dados_caso, modo, elementos, calibrado, k, u_k):
    dados = {
        **dados_caso,
        'modo':      modo,
        'k':         k,
        'u_k':       u_k,
        'calibrado': calibrado,
        'elementos': elementos,
    }
    bo   = dados_caso.get('bo', '').replace('/', '-')
    nome = f"BO_{bo}_{datetime.date.today()}.sicro"
    cam  = DIR_CROQUIS / nome
    with open(cam, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return cam


def carregar_croqui(caminho):
    with open(caminho, encoding='utf-8') as f:
        dados = json.load(f)
    caso = {k: dados[k] for k in
            ('bo', 'requisicao', 'local', 'municipio', 'perito', 'data')
            if k in dados}
    return {
        'caso':       caso,
        'modo':       dados.get('modo', 'zero'),
        'elementos':  dados.get('elementos', []),
        'calibrado':  dados.get('calibrado', False),
        'k':          dados.get('k'),
        'u_k':        dados.get('u_k'),
    }


def listar_croquis():
    return sorted(DIR_CROQUIS.glob('*.sicro'), reverse=True)
