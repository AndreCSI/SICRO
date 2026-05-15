"""
fase3_status_bar.py — Barra de status estruturada no editor de croqui
Substitui o label simples por uma barra com varios campos:
Ferramenta | Escala | Zoom | X,Y | Objetos | Camada
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: substitui criacao do self.status pelo bloco da nova barra
# ══════════════════════════════════════════════
old_status = (
    '        # Status bar\n'
    '        self.status = tk.Label(self, text="Pronto",\n'
    '                               font=FONTE_MONO, bg=COR_PAINEL,\n'
    '                               fg=CINZA_MEDIO, anchor="w")\n'
    '        self.status.pack(fill="x", side="bottom", padx=8, pady=2)\n'
)

new_status = (
    '        # ═══════════════════════════════════════\n'
    '        # BARRA DE STATUS ESTRUTURADA\n'
    '        # ═══════════════════════════════════════\n'
    '        sbar = tk.Frame(self, bg=FUNDO_PAINEL, height=28)\n'
    '        sbar.pack(fill="x", side="bottom")\n'
    '        sbar.pack_propagate(False)\n'
    '        # Separador superior\n'
    '        tk.Frame(self, bg=AZUL_BORDA, height=1).pack(fill="x", side="bottom")\n'
    '\n'
    '        def _campo(parent, label, valor, fg_valor=None, side="left"):\n'
    '            f = tk.Frame(parent, bg=FUNDO_PAINEL)\n'
    '            f.pack(side=side, padx=10, pady=6)\n'
    '            tk.Label(f, text=label + ":", font=FONTE_MICRO,\n'
    '                     bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(side="left")\n'
    '            lbl = tk.Label(f, text=" " + str(valor), font=FONTE_SMALL_BOLD,\n'
    '                           bg=FUNDO_PAINEL,\n'
    '                           fg=fg_valor or TEXTO_PRIMARIO)\n'
    '            lbl.pack(side="left")\n'
    '            return lbl\n'
    '\n'
    '        def _sep(parent):\n'
    '            tk.Frame(parent, bg=AZUL_BORDA, width=1).pack(\n'
    '                side="left", fill="y", padx=2, pady=6)\n'
    '\n'
    '        # Campos da esquerda\n'
    '        self._st_ferramenta = _campo(sbar, "Ferramenta", "Selecionar", DOURADO)\n'
    '        _sep(sbar)\n'
    '        self._st_escala = _campo(sbar, "Escala",\n'
    '            f"1 px = {1.0:.3f} m" if not self.calibrado else f"k = {self.k:.4f} m/px")\n'
    '        _sep(sbar)\n'
    '        self._st_zoom = _campo(sbar, "Zoom", "100%")\n'
    '        _sep(sbar)\n'
    '        self._st_xy = _campo(sbar, "X, Y", "0.00 m, 0.00 m")\n'
    '\n'
    '        # Campos da direita\n'
    '        self._st_camada = _campo(sbar, "Camada", "—",\n'
    '            fg_valor=TEXTO_SECUNDARIO, side="right")\n'
    '        _sep(sbar)\n'
    '        self._st_objetos = _campo(sbar, "Objetos",\n'
    '            str(len(self.elementos)), side="right")\n'
    '\n'
    '        # Label de status texto (mensagens temporarias — mantém compat)\n'
    '        self.status = tk.Label(sbar, text="Pronto",\n'
    '                               font=FONTE_SMALL,\n'
    '                               bg=FUNDO_PAINEL,\n'
    '                               fg=TEXTO_TERCIARIO, anchor="w")\n'
    '        self.status.pack(side="left", padx=20, pady=6, fill="x", expand=True)\n'
)

if old_status in src:
    src = src.replace(old_status, new_status, 1)
    print("PATCH 1 OK — barra de status substituida")
else:
    print("PATCH 1 SKIP — formato antigo nao encontrado")

# ══════════════════════════════════════════════
# PATCH 2: atualiza _set_ferr para refletir na barra
# ══════════════════════════════════════════════
# Procura def _set_ferr e injeta atualizacao do _st_ferramenta
old_set_ferr_marker = "    def _set_ferr(self, ferr):"
idx = src.find(old_set_ferr_marker)
if idx > 0:
    # Encontra o final da assinatura (proximo \n)
    inicio_corpo = src.find("\n", idx) + 1
    # Adiciona atualizacao do status logo no inicio do corpo
    injecao = (
        '        # Atualiza barra de status\n'
        '        nomes = {"sel":"Selecionar","r1":"Eixo R1","r2":"Eixo R2",\n'
        '                 "carro":"Carro","moto":"Moto","caminhao":"Caminhao",\n'
        '                 "bicicleta":"Bicicleta","pedestre":"Pedestre",\n'
        '                 "sc":"Sitio de colisao","cota":"Cota","texto":"Texto",\n'
        '                 "apagar":"Apagar"}\n'
        '        if hasattr(self, "_st_ferramenta"):\n'
        '            self._st_ferramenta.config(text=" " + nomes.get(ferr, ferr.title()))\n'
    )
    src = src[:inicio_corpo] + injecao + src[inicio_corpo:]
    print("PATCH 2 OK — _set_ferr atualiza barra")

# ══════════════════════════════════════════════
# PATCH 3: atualiza objetos no _atualizar_camadas
# ══════════════════════════════════════════════
old_atu = "    def _atualizar_camadas(self):"
idx = src.find(old_atu)
if idx > 0:
    inicio_corpo = src.find("\n", idx) + 1
    injecao = (
        '        # Atualiza contador na barra de status\n'
        '        if hasattr(self, "_st_objetos"):\n'
        '            self._st_objetos.config(text=" " + str(len(self.elementos)))\n'
    )
    src = src[:inicio_corpo] + injecao + src[inicio_corpo:]
    print("PATCH 3 OK — contador de objetos")

# ══════════════════════════════════════════════
# PATCH 4: atualiza zoom no _zoom_d
# ══════════════════════════════════════════════
old_zoom = "    def _zoom_d(self,"
idx = src.find(old_zoom)
if idx > 0:
    # Procura por self._redesenhar() dentro de _zoom_d
    fim = src.find("\n    def ", idx + 10)
    bloco = src[idx:fim]
    if "self._st_zoom" not in bloco:
        # Insere atualizacao apos self.zoom *= ou self.zoom =
        nova_linha = (
            "\n        if hasattr(self, '_st_zoom'):\n"
            "            self._st_zoom.config(text=f' {int(self.zoom*100)}%')\n"
        )
        # Insere antes do self._redesenhar()
        m = re.search(r"(\n\s+)(self\._redesenhar\(\))", bloco)
        if m:
            novo_bloco = bloco[:m.start()] + nova_linha + bloco[m.start():]
            src = src[:idx] + novo_bloco + src[fim:]
            print("PATCH 4 OK — zoom atualiza barra")

# ══════════════════════════════════════════════
# Salva e valida
# ══════════════════════════════════════════════
editor_path.write_text(src, encoding="utf-8")

try:
    ast.parse(src)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO linha {e.lineno}: {e.msg}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("Revertido")
    raise SystemExit

print("\nRode: python main.py")
print("Teste:")
print("  1. Abra um croqui")
print("  2. Veja a barra inferior com Ferramenta, Escala, Zoom, X/Y, Objetos, Camada")
print("  3. Mude a ferramenta — campo Ferramenta atualiza")
print("  4. De zoom — campo Zoom atualiza")
print("  5. Insira/apague objetos — campo Objetos atualiza")
