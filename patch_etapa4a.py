"""
patch_etapa4a.py — Desacopla a inserção (Sub-etapa 4A)
Cria _inserir_modelo(chave_catalogo, x, y): insere um item do catalogo
independente de popup. O _inserir atual passa a delegar a ela.
INVISIVEL ao usuario — comportamento identico. Prepara atalhos futuros.
"""
from pathlib import Path
import ast

ep = Path("ui")/"editor_croqui.py"
src = ep.read_text(encoding="utf-8")
src_orig = src

# Mapeamento: tipo antigo + chave antiga -> chave do catalogo novo.
# Croquis .sicro antigos usam modelo "sedan"; catalogo usa "carro_sedan".
# Esse mapa garante compatibilidade retroativa.
mapa_compat = '''
# ── Compatibilidade: chave de modelo antiga -> chave do catalogo novo ──
_MAPA_MODELO_LEGADO = {
    ("carro", "sedan"):    "carro_sedan",
    ("carro", "suv"):      "carro_suv",
    ("carro", "hatch"):    "carro_hatch",
    ("moto", "esportiva"): "moto_esportiva",
    ("moto", "urbana"):    "moto_urbana",
    ("moto", "carga"):     "moto_carga",
    ("caminhao", "leve"):    "caminhao_leve",
    ("caminhao", "truck"):   "caminhao_pesado",
    ("caminhao", "carreta"): "carreta_longa",
}

# Tipo base (para rotulo/sigla) a partir da categoria do catalogo
_SIGLA_CATEGORIA = {
    "carro": "V", "moto": "V", "caminhao": "V", "van": "V",
    "onibus": "V", "emergencia": "V", "outros": "V",
    "bicicleta": "B", "pedestre": "P",
}

'''

# Insere o mapa logo antes da classe EditorCroqui
anchor_classe = "class EditorCroqui"
idx = src.find(anchor_classe)
if idx < 0:
    print("ERRO: classe EditorCroqui nao encontrada")
    raise SystemExit
# volta ate o inicio da linha
ini_linha = src.rfind("\n", 0, idx) + 1
if "_MAPA_MODELO_LEGADO" not in src:
    src = src[:ini_linha] + mapa_compat + "\n" + src[ini_linha:]
    print("1 OK - mapa de compatibilidade + siglas inserido")
else:
    print("1 SKIP - mapa ja existe")

# Reescreve _inserir: separa em _inserir (compat) + _inserir_modelo (nucleo)
old_inserir = '''    def _inserir(self,tipo,x,y):
        label=""
        modelo_chave = None
        modelo_larg  = None
        modelo_alt   = None
        modelo_cor   = None

        # ── Popup de seleção de modelo para veículos ──
        if tipo in ("carro", "moto", "caminhao"):
            popup = PopupModeloVeiculo(self.winfo_toplevel(), tipo)
            self.winfo_toplevel().wait_window(popup)
            if popup.resultado is None:
                return   # cancelou / fechou sem escolher
            m = popup.resultado
            modelo_chave = m["chave"]
            modelo_larg  = m["larg"]
            modelo_alt   = m["alt"]
            modelo_cor   = m["cor"]

        if tipo in ("carro","moto","caminhao","bicicleta","pedestre"):
            n=sum(1 for e in self.elementos if e["tipo"]==tipo)+1
            sig={"carro":"V","moto":"V","caminhao":"V","bicicleta":"B","pedestre":"P"}
            # Auto-gera o rotulo — editavel depois no painel Propriedades
            label=f"{sig[tipo]}{n}"
        elif tipo=="texto":
            label = ""  # será preenchido pelo EditorTexto
        elif tipo=="sc":
            label="SC"

        el={"tipo":tipo,"x":x,"y":y,"label":label,"angulo":0}
        if modelo_chave: el["modelo"] = modelo_chave
        if modelo_larg:  el["larg"]   = modelo_larg
        if modelo_alt:   el["alt"]    = modelo_alt
        if modelo_cor:   el["cor"]    = modelo_cor

        self._salvar_historico()
        self.elementos.append(el)
        self.sel_idx=len(self.elementos)-1

        self._atualizar_camadas()
        self._redesenhar()

        # Veiculos: ajuste direto pelos handles/painel (sem dialogo)
        if tipo == "texto":
            # Abre editor de texto inline
            self._abrir_editor_texto(el)'''

new_inserir = '''    def _inserir(self,tipo,x,y):
        """
        Fluxo a partir da TOOLBAR. Para veiculos com modelo, abre o
        seletor; depois delega ao nucleo _inserir_modelo / _inserir_simples.
        """
        # Veiculos que escolhem modelo via popup
        if tipo in ("carro", "moto", "caminhao"):
            popup = PopupModeloVeiculo(self.winfo_toplevel(), tipo)
            self.winfo_toplevel().wait_window(popup)
            if popup.resultado is None:
                return
            m = popup.resultado
            # popup pode retornar chave do catalogo novo OU dict legado
            if isinstance(m, dict):
                chave_cat = m.get("chave_catalogo") or m.get("chave")
                self._inserir_modelo(chave_cat, x, y,
                                     larg_legado=m.get("larg"),
                                     alt_legado=m.get("alt"),
                                     cor_legado=m.get("cor"),
                                     chave_legada=m.get("chave"))
            else:
                self._inserir_modelo(m, x, y)
            return
        # Bicicleta / pedestre: sem popup (modelo unico por enquanto)
        if tipo in ("bicicleta", "pedestre"):
            self._inserir_simples(tipo, x, y)
            return
        # SC / texto
        if tipo in ("sc", "texto"):
            self._inserir_simples(tipo, x, y)
            return

    def _inserir_modelo(self, chave_catalogo, x, y,
                        larg_legado=None, alt_legado=None,
                        cor_legado=None, chave_legada=None):
        """
        NUCLEO desacoplado: insere um veiculo do catalogo pela sua chave.
        Reutilizavel por popup E por futuros atalhos de teclado.
        """
        item = None
        try:
            item = catalogo_veiculos.get(chave_catalogo)
        except Exception:
            item = None

        if item:
            categoria = item["categoria"]
            modelo_chave = item["chave"]
            cor = item["cor_padrao"]
            # larg/alt: usa o legado se veio (compat), senao do catalogo
            larg = larg_legado
            alt  = alt_legado
            if cor_legado:
                cor = cor_legado
        else:
            # Sem item no catalogo: cai no caminho legado (chave antiga)
            categoria = "carro"
            modelo_chave = chave_legada or chave_catalogo
            cor = cor_legado or "#888888"
            larg = larg_legado
            alt  = alt_legado

        sig = _SIGLA_CATEGORIA.get(categoria, "V")
        # Conta por categoria para numerar (V1, V2, P1...)
        n = sum(1 for e in self.elementos
                if _SIGLA_CATEGORIA.get(
                    (catalogo_veiculos.get(e.get("modelo","")) or {}).get(
                        "categoria",""), "V") == sig) + 1
        label = f"{sig}{n}"

        # tipo base mantido para compat de codigo que olha el["tipo"]
        tipo_base = {"carro":"carro","moto":"moto","caminhao":"caminhao",
                     "bicicleta":"bicicleta","pedestre":"pedestre"
                     }.get(categoria, "carro")

        el = {"tipo": tipo_base, "x": x, "y": y,
               "label": label, "angulo": 0, "modelo": modelo_chave}
        if larg: el["larg"] = larg
        if alt:  el["alt"]  = alt
        if cor:  el["cor"]  = cor

        self._salvar_historico()
        self.elementos.append(el)
        self.sel_idx = len(self.elementos) - 1
        self._atualizar_camadas()
        self._redesenhar()

    def _inserir_simples(self, tipo, x, y):
        """Insere bicicleta/pedestre/sc/texto (sem catalogo de modelo)."""
        if tipo in ("bicicleta", "pedestre"):
            n = sum(1 for e in self.elementos if e["tipo"] == tipo) + 1
            sig = {"bicicleta": "B", "pedestre": "P"}[tipo]
            label = f"{sig}{n}"
        elif tipo == "sc":
            label = "SC"
        else:
            label = ""
        el = {"tipo": tipo, "x": x, "y": y, "label": label, "angulo": 0}
        self._salvar_historico()
        self.elementos.append(el)
        self.sel_idx = len(self.elementos) - 1
        self._atualizar_camadas()
        self._redesenhar()
        if tipo == "texto":
            self._abrir_editor_texto(el)'''

if old_inserir in src:
    src = src.replace(old_inserir, new_inserir, 1)
    print("2 OK - _inserir refatorado (nucleo desacoplado)")
else:
    print("2 ERRO - _inserir nao bate exatamente")
    raise SystemExit

ep.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO {e.lineno}: {e.msg}")
    ln=src.split("\n")
    for i in range(max(0,e.lineno-4),min(len(ln),e.lineno+3)):
        print(f"  {i+1:4}: {ln[i]}")
    ep.write_text(src_orig, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste 4A (comportamento deve ser IDENTICO ao atual):")
print("  1. Inserir Carro -> popup atual (3 modelos) -> escolher -> insere")
print("  2. Moto, Caminhao -> idem (popup antigo ainda)")
print("  3. Bicicleta, Pedestre, SC -> inserem direto como antes")
print("  4. Abrir um .sicro ANTIGO -> veiculos aparecem normais")
print("  Nada muda visualmente — so a estrutura interna foi desacoplada")
