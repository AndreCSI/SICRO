"""
arquivo/salvar.py — Formato nativo .sicro v1.0
Funcoes utilitarias. A logica principal de salvar esta no
EditorCroqui._salvar (embute imagem). Aqui ficam helpers de
listagem e leitura de metadata sem abrir o editor.
"""
import json
import sys
from pathlib import Path
_raiz = Path(__file__).parent.parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))
from config import DIR_CROQUIS

VERSAO_SICRO = "1.0"


def carregar_croqui(caminho):
    """Le um .sicro v1.0 e retorna dict estruturado (sem decodificar imagem)."""
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    if dados.get("versao_sicro") != VERSAO_SICRO:
        raise ValueError("Formato .sicro incompativel (esperado 1.0)")
    meta = dados.get("metadata", {})
    cfg = dados.get("config", {})
    caso = {k: meta.get(k, "") for k in
            ("bo", "requisicao", "local", "municipio", "perito", "data")}
    return {
        "caso":        caso,
        "metadata":    meta,
        "config":      cfg,
        "modo":        cfg.get("modo", "zero"),
        "elementos":   dados.get("elementos", []),
        "calibrado":   cfg.get("calibrado", False),
        "k":           cfg.get("k"),
        "u_k":         cfg.get("u_k"),
        "norte_angulo":cfg.get("norte_angulo", 0),
        "imagem_base": dados.get("imagem_base", {"presente": False}),
    }


def ler_metadata(caminho):
    """Le SO a metadata (rapido, nao carrega imagem nem elementos)."""
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        return dados.get("metadata", {})
    except Exception:
        return {}


def listar_croquis():
    return sorted(DIR_CROQUIS.glob("*.sicro"), reverse=True)
