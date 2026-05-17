"""
patch_sicro_v1.py — Novo formato .sicro v1.0
- Imagem do drone embutida em base64
- versao_sicro, metadata, config, norte_angulo, timestamps
- _salvar reescrito + _abrir (main.py) atualizado
- arquivo/salvar.py reescrito para o novo formato
"""
from pathlib import Path
import ast

# ══════════════════════════════════════════════
# PARTE A: editor_croqui.py — novo _salvar
# ══════════════════════════════════════════════
ep = Path("ui") / "editor_croqui.py"
src = ep.read_text(encoding="utf-8")
src_orig = src

old_salvar = '''    def _salvar(self):
        dados={**self.dados_caso,"modo":self.modo,"k":self.k,
               "u_k":self.u_k,"calibrado":self.calibrado,
               "elementos":self.elementos}
        bo=self.dados_caso.get("bo","").replace("/","-")
        nome=f"BO_{bo}_{datetime.date.today()}.sicro"
        cam=DIR_CROQUIS/nome
        with open(cam,"w",encoding="utf-8") as f:
            json.dump(dados,f,ensure_ascii=False,indent=2)
        messagebox.showinfo("Salvo",f"Croqui salvo:\\n{cam}")'''

new_salvar = '''    def _salvar(self):
        import base64, io
        agora = datetime.datetime.now().isoformat(timespec="seconds")
        # Imagem base (drone) embutida em base64
        imagem_base = {"presente": False, "dados_b64": None,
                       "largura": 0, "altura": 0}
        if self.img_drone is not None and PIL_OK:
            try:
                buf = io.BytesIO()
                self.img_drone.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                imagem_base = {
                    "presente": True,
                    "dados_b64": b64,
                    "largura": self.img_drone.width,
                    "altura": self.img_drone.height,
                }
            except Exception as e:
                print("Aviso: falha ao embutir imagem:", e)
        # Preserva criado_em se ja existia
        criado = getattr(self, "_criado_em", None) or agora
        self._criado_em = criado
        dados = {
            "versao_sicro": "1.0",
            "metadata": {
                "bo":        self.dados_caso.get("bo", ""),
                "requisicao":self.dados_caso.get("requisicao", ""),
                "local":     self.dados_caso.get("local", ""),
                "municipio": self.dados_caso.get("municipio", ""),
                "perito":    self.dados_caso.get("perito", ""),
                "data":      self.dados_caso.get("data", ""),
                "criado_em":    criado,
                "modificado_em": agora,
            },
            "config": {
                "modo":         self.modo,
                "calibrado":    self.calibrado,
                "k":            self.k,
                "u_k":          self.u_k,
                "norte_angulo": getattr(self, "norte_angulo", 0),
            },
            "imagem_base": imagem_base,
            "elementos": self.elementos,
            "historico": [],
        }
        bo = self.dados_caso.get("bo", "").replace("/", "-")
        nome = f"BO_{bo}_{datetime.date.today()}.sicro"
        cam = DIR_CROQUIS / nome
        with open(cam, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        kb = cam.stat().st_size / 1024
        messagebox.showinfo("Salvo",
            f"Croqui salvo:\\n{cam}\\n\\nTamanho: {kb:.0f} KB"
            + ("\\nImagem do drone embutida." if imagem_base["presente"] else ""))'''

if old_salvar in src:
    src = src.replace(old_salvar, new_salvar, 1)
    print("PARTE A OK — novo _salvar")
else:
    print("PARTE A ERRO — _salvar nao bate exatamente")
    raise SystemExit

ep.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("  Sintaxe editor_croqui.py OK")
except SyntaxError as e:
    print(f"  ERRO {e.lineno}: {e.msg}")
    ep.write_text(src_orig, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PARTE B: main.py — _abrir carrega novo formato
# ══════════════════════════════════════════════
mp = Path("main.py")
m = mp.read_text(encoding="utf-8")
m_orig = m

old_abrir = '''    def _abrir(self, caminho):
        try:
            with open(caminho, encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return
        caso = {k: dados[k] for k in
                ("bo", "requisicao", "local", "municipio", "perito", "data")
                if k in dados}
        editor = EditorCroqui(self, caso,
                              modo=dados.get("modo", "zero"),
                              elementos_iniciais=dados.get("elementos", []))
        editor.calibrado = dados.get("calibrado", False)
        editor.k   = dados.get("k")
        editor.u_k = dados.get("u_k")
        if editor.calibrado and editor.k:
            editor.label_escala.config(
                text=f"k={editor.k*1000:.3f}mm/px",
                fg=COR_SUCESSO)
        editor._redesenhar()
        self._trocar(editor)'''

new_abrir = '''    def _abrir(self, caminho):
        import base64, io
        try:
            with open(caminho, encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return
        if dados.get("versao_sicro") != "1.0":
            messagebox.showerror("Formato incompativel",
                "Este arquivo nao esta no formato .sicro 1.0.")
            return
        meta = dados.get("metadata", {})
        cfg  = dados.get("config", {})
        caso = {k: meta.get(k, "") for k in
                ("bo", "requisicao", "local", "municipio", "perito", "data")}
        # Reconstroi imagem do drone do base64
        img_drone = None
        ib = dados.get("imagem_base", {})
        if ib.get("presente") and ib.get("dados_b64") and PIL_OK:
            try:
                raw = base64.b64decode(ib["dados_b64"])
                img_drone = Image.open(io.BytesIO(raw)).convert("RGBA")
            except Exception as e:
                messagebox.showwarning("Imagem",
                    f"Falha ao carregar imagem embutida: {e}")
        editor = EditorCroqui(self, caso,
                              modo=cfg.get("modo", "zero"),
                              img_drone=img_drone,
                              elementos_iniciais=dados.get("elementos", []))
        editor.calibrado = cfg.get("calibrado", False)
        editor.k   = cfg.get("k")
        editor.u_k = cfg.get("u_k")
        editor.norte_angulo = cfg.get("norte_angulo", 0)
        editor._criado_em = meta.get("criado_em")
        if editor.calibrado and editor.k:
            editor.label_escala.config(
                text=f"k={editor.k*1000:.3f}mm/px",
                fg=COR_SUCESSO)
        editor._redesenhar()
        self._trocar(editor)'''

if old_abrir in m:
    m = m.replace(old_abrir, new_abrir, 1)
    mp.write_text(m, encoding="utf-8")
    try:
        ast.parse(m)
        print("PARTE B OK — _abrir carrega novo formato + imagem")
    except SyntaxError as e:
        print(f"PARTE B ERRO {e.lineno}: {e.msg}")
        mp.write_text(m_orig, encoding="utf-8")
        ep.write_text(src_orig, encoding="utf-8")
        raise SystemExit
else:
    print("PARTE B ERRO — _abrir nao bate")
    ep.write_text(src_orig, encoding="utf-8")
    raise SystemExit

# ══════════════════════════════════════════════
# PARTE C: arquivo/salvar.py — reescreve para v1.0
# ══════════════════════════════════════════════
sp = Path("arquivo") / "salvar.py"
novo_salvar_py = '''"""
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
'''
sp.write_text(novo_salvar_py, encoding="utf-8")
try:
    ast.parse(novo_salvar_py)
    print("PARTE C OK — arquivo/salvar.py reescrito para v1.0")
except SyntaxError as e:
    print(f"PARTE C ERRO: {e}")
    raise SystemExit

print("\n" + "="*50)
print("FORMATO .sicro 1.0 IMPLEMENTADO")
print("="*50)
print("Rode: python main.py")
print("Teste:")
print("  1. Croqui modo drone -> insere foto -> desenha -> Salvar")
print("     (mensagem mostra tamanho + 'Imagem embutida')")
print("  2. Volta ao inicio -> Abrir croqui existente")
print("  3. A FOTO DO DRONE deve reaparecer (antes se perdia)")
print("  4. Croqui modo zero (sem foto) tambem salva/abre normal")
