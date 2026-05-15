"""
fase2_header.py — Header moderno do editor de croqui
- BO + local editaveis inline (clica e edita)
- Botoes Inicio / PDF / Salvar estilizados a direita
- Toggle Modo Vetorial em destaque
- Visual integrado ao tema
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# Localiza o inicio do _build_ui
inicio_marker = "    def _build_ui(self):\n"
fim_marker = "        # Corpo\n        corpo = tk.Frame(self, bg="

i = src.find(inicio_marker)
if i < 0:
    print("ERRO: _build_ui nao encontrado")
    raise SystemExit

f = src.find(fim_marker, i)
if f < 0:
    print("ERRO: fim do header nao encontrado")
    raise SystemExit

# Bloco antigo (do _build_ui ate o # Corpo)
bloco_antigo = src[i:f]

# Novo bloco — header moderno
bloco_novo = '''    def _build_ui(self):
        # ═══════════════════════════════════════════
        # HEADER MODERNO — substitui barra antiga
        # ═══════════════════════════════════════════
        header = tk.Frame(self, bg=FUNDO_PAINEL, height=48)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Faixa dourada inferior (separa do corpo)
        sep_inf = tk.Frame(self, bg=AZUL_BORDA, height=1)
        sep_inf.pack(fill="x")

        # ─── ESQUERDA: BO + local editaveis ───
        esq = tk.Frame(header, bg=FUNDO_PAINEL)
        esq.pack(side="left", fill="y", padx=16)

        bo    = self.dados_caso.get("bo", "—")
        local = self.dados_caso.get("local", "—")

        # Label BO clicavel
        self._lbl_bo = tk.Label(esq,
            text=f"BO {bo}",
            font=("Segoe UI", 11, "bold"),
            bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO,
            cursor="hand2")
        self._lbl_bo.pack(side="left", pady=14)
        self._lbl_bo.bind("<Button-1>", lambda e: self._editar_caso("bo"))

        # Separador
        tk.Label(esq, text="  ·  ", font=("Segoe UI", 10),
                 bg=FUNDO_PAINEL,
                 fg=TEXTO_TERCIARIO).pack(side="left", pady=14)

        # Label Local clicavel
        self._lbl_local = tk.Label(esq,
            text=local,
            font=("Segoe UI", 10),
            bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO,
            cursor="hand2")
        self._lbl_local.pack(side="left", pady=14)
        self._lbl_local.bind("<Button-1>", lambda e: self._editar_caso("local"))

        # Icone lapis pequeno
        tk.Label(esq, text="  ✎", font=("Segoe UI", 9),
                 bg=FUNDO_PAINEL,
                 fg=TEXTO_TERCIARIO).pack(side="left", pady=14)

        # ─── DIREITA: botoes ───
        dir_ = tk.Frame(header, bg=FUNDO_PAINEL)
        dir_.pack(side="right", fill="y", padx=10)

        # Toggle Modo Vetorial (status de calibracao no modo drone)
        self.label_escala = tk.Label(dir_,
            text="📐 Não calibrado" if self.modo=="drone" else "Modo vetorial",
            font=FONTE_SMALL_BOLD,
            bg=FUNDO_PAINEL,
            fg=COR_AVISO if self.modo=="drone" else DOURADO,
            padx=12)
        self.label_escala.pack(side="right", padx=8, pady=12)

        # Separador vertical
        tk.Frame(dir_, bg=AZUL_BORDA, width=1).pack(side="right",
                                                     fill="y", padx=4, pady=8)

        # Botoes de acao
        def _btn_header(parent, icone, texto, cmd, cor_acento=None):
            f = tk.Frame(parent, bg=FUNDO_PAINEL, cursor="hand2")
            f.pack(side="right", padx=2, pady=8)
            inner = tk.Frame(f, bg=FUNDO_PAINEL)
            inner.pack(padx=10, pady=4)
            tk.Label(inner, text=icone, font=("Segoe UI", 11),
                     bg=FUNDO_PAINEL,
                     fg=cor_acento or TEXTO_SECUNDARIO).pack(side="left", padx=(0,4))
            tk.Label(inner, text=texto, font=FONTE_SMALL,
                     bg=FUNDO_PAINEL,
                     fg=TEXTO_PRIMARIO).pack(side="left")
            def _hin(e):
                f.config(bg=FUNDO_HOVER)
                inner.config(bg=FUNDO_HOVER)
                for w in inner.winfo_children(): w.config(bg=FUNDO_HOVER)
            def _hout(e):
                f.config(bg=FUNDO_PAINEL)
                inner.config(bg=FUNDO_PAINEL)
                for w in inner.winfo_children(): w.config(bg=FUNDO_PAINEL)
            def _cl(e): cmd()
            for w in [f, inner] + list(inner.winfo_children()):
                w.bind("<Enter>", _hin)
                w.bind("<Leave>", _hout)
                w.bind("<Button-1>", _cl)
            return f

        _btn_header(dir_, "💾", "Salvar", self._salvar, DOURADO)
        _btn_header(dir_, "📄", "PDF",    self._exportar_pdf)
        _btn_header(dir_, "🏠", "Início", self._voltar)

'''

src = src[:i] + bloco_novo + src[f:]
print(f"Header substituido: {len(bloco_antigo)} chars -> {len(bloco_novo)} chars")

# ═══════════════════════════════════════════
# Adiciona metodo _editar_caso ao EditorCroqui
# ═══════════════════════════════════════════
metodo_editar = '''
    def _editar_caso(self, campo):
        """Permite editar BO ou local inline via simpledialog."""
        from tkinter import simpledialog
        valor_atual = self.dados_caso.get(campo, "")
        labels = {"bo": "Numero do BO:", "local": "Local da ocorrencia:"}
        novo = simpledialog.askstring("Editar " + campo,
                                       labels.get(campo, campo + ":"),
                                       initialvalue=valor_atual,
                                       parent=self.winfo_toplevel())
        if novo is not None and novo.strip():
            self.dados_caso[campo] = novo.strip()
            # Atualiza labels do header
            if campo == "bo":
                self._lbl_bo.config(text=f"BO {novo.strip()}")
            elif campo == "local":
                self._lbl_local.config(text=novo.strip())

'''

# Insere o metodo apos _build_ui (encontra o proximo def apos o nosso novo header)
# Procura por "    def _salvar" como ancora
ancora = "    def _salvar(self):"
idx_ancora = src.find(ancora)
if idx_ancora > 0 and "_editar_caso" not in src:
    src = src[:idx_ancora] + metodo_editar + src[idx_ancora:]
    print("Metodo _editar_caso adicionado")

editor_path.write_text(src, encoding="utf-8")

try:
    ast.parse(src)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO linha {e.lineno}: {e.msg}")
    print("Revertendo...")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

print("\nRode: python main.py")
print("Teste:")
print("  1. Abra um croqui existente")
print("  2. Veja o novo header com BO/local")
print("  3. Clique em 'BO' ou no local — abre dialogo para editar")
print("  4. Confirme Salvar/PDF/Inicio funcionando")
