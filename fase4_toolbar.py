"""
fase4_toolbar.py — Toolbar lateral redesenhada
- Largura expandida (180px) com icone + label textual
- Estados visuais claros (ativo, hover)
- Indicador lateral dourado quando ativo
- Botoes de zoom agrupados embaixo
"""
from pathlib import Path
import ast

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# Substitui bloco da toolbar antiga pelo novo
# ══════════════════════════════════════════════
old_toolbar = '''        # ── Toolbar esquerda ──
        self._tb = tk.Frame(corpo, bg=COR_PAINEL, width=56)
        self._tb.pack(side="left", fill="y")
        self._tb.pack_propagate(False)
        tb = self._tb

        # Faixa topo
        tk.Frame(tb, bg=AMARELO, height=2).pack(fill="x")

        # Botões de ferramentas normais
        self.btns_ferr = {}
        for chave, icone, dica in self.FERRAMENTAS:
            btn = tk.Button(tb, text=icone, font=("Segoe UI",12),
                            width=3, cursor="hand2",
                            bg=COR_PAINEL, fg=BRANCO,
                            activebackground=AZUL_MEDIO, relief="flat",
                            command=lambda c=chave: self._set_ferr(c))
            btn.pack(pady=1, padx=3)
            btn.bind("<Enter>", lambda e,d=dica: self.status.config(text=d))
            self.btns_ferr[chave] = btn

        # Botões de ferramentas de via (ocultos inicialmente)
        self.btns_via = {}
        for chave, icone, dica in FERRAMENTAS_VIA:
            btn = tk.Button(tb, text=icone, font=("Segoe UI",12),
                            width=3, cursor="hand2",
                            bg=COR_PAINEL, fg=BRANCO,
                            activebackground=AZUL_MEDIO, relief="flat",
                            command=lambda c=chave: self._set_ferr_via(c))
            btn.bind("<Enter>", lambda e,d=dica: self.status.config(text=d))
            self.btns_via[chave] = btn
            # NÃO faz pack ainda — serão mostrados ao entrar no modo via

        # Botões de zoom (sempre visíveis)
        self._sep_zoom = tk.Frame(tb, bg=COR_BORDA, height=1)
        self._sep_zoom.pack(fill="x", pady=3)
        self._btns_zoom = []
        for txt, cmd in [("+",lambda: self._zoom_d(1.2)),
                          ("−",lambda: self._zoom_d(1/1.2)),
                          ("⌂",self._reset_view)]:
            b = tk.Button(tb, text=txt, font=("Segoe UI",13), width=3,
                          bg=COR_PAINEL, fg=BRANCO, relief="flat", cursor="hand2",
                          command=cmd)
            b.pack(pady=1, padx=3)
            self._btns_zoom.append(b)

        # Botão 🛣 — base da toolbar, sempre visível
        tk.Frame(tb, height=1, bg=COR_FUNDO).pack(fill="x", expand=True)
        tk.Frame(tb, height=2, bg=AMARELO).pack(fill="x")
        self._btn_modo_via = tk.Button(tb, text="🛣",
                                       font=("Segoe UI",18),
                                       width=3, cursor="hand2",
                                       bg="#162810", fg=AMARELO,
                                       activebackground="#2A4A1A",
                                       relief="flat", pady=4,
                                       command=self._toggle_modo_via)
        self._btn_modo_via.pack(fill="x", padx=2, pady=2)
        self._btn_modo_via.bind("<Enter>", lambda e: self.status.config(
            text="Editor de Via  —  alterna modo arte"))
        tk.Frame(tb, height=2, bg=AMARELO).pack(fill="x")
'''

new_toolbar = '''        # ═══════════════════════════════════════
        # TOOLBAR LATERAL EXPANDIDA (180px)
        # icone + label textual + estado visual
        # ═══════════════════════════════════════
        self._tb = tk.Frame(corpo, bg=FUNDO_PAINEL, width=180)
        self._tb.pack(side="left", fill="y")
        self._tb.pack_propagate(False)
        tb = self._tb

        # Borda direita
        tk.Frame(tb, bg=AZUL_BORDA, width=1).pack(side="right", fill="y")

        # Container interno
        inner = tk.Frame(tb, bg=FUNDO_PAINEL)
        inner.pack(fill="both", expand=True)

        # Topo: espacamento
        tk.Frame(inner, bg=FUNDO_PAINEL, height=12).pack()

        # Helper para criar botoes
        def _criar_btn_ferr(parent, chave, icone, dica, fn_set):
            f = tk.Frame(parent, bg=FUNDO_PAINEL, cursor="hand2")
            f.pack(fill="x", pady=1)
            # Indicador lateral (3px)
            ind = tk.Frame(f, bg=FUNDO_PAINEL, width=3)
            ind.pack(side="left", fill="y")
            # Icone
            lbl_ico = tk.Label(f, text=icone, font=("Segoe UI", 12),
                               bg=FUNDO_PAINEL, fg=TEXTO_SECONDARIO,
                               width=2)
            lbl_ico.pack(side="left", padx=(8,4), pady=6)
            # Label
            lbl_txt = tk.Label(f, text=dica.split("—")[0].split("/")[0].strip(),
                               font=FONTE_SMALL,
                               bg=FUNDO_PAINEL, fg=TEXTO_SECONDARIO,
                               anchor="w")
            lbl_txt.pack(side="left", fill="x", expand=True)
            # Hover
            def _hin(e):
                if not getattr(f, "_ativo", False):
                    f.config(bg=FUNDO_HOVER)
                    ind.config(bg=FUNDO_HOVER)
                    lbl_ico.config(bg=FUNDO_HOVER)
                    lbl_txt.config(bg=FUNDO_HOVER)
                if hasattr(self, "status"):
                    self.status.config(text=dica)
            def _hout(e):
                if not getattr(f, "_ativo", False):
                    f.config(bg=FUNDO_PAINEL)
                    ind.config(bg=FUNDO_PAINEL)
                    lbl_ico.config(bg=FUNDO_PAINEL)
                    lbl_txt.config(bg=FUNDO_PAINEL)
            def _cl(e):
                fn_set(chave)
            for w in [f, ind, lbl_ico, lbl_txt]:
                w.bind("<Enter>", _hin)
                w.bind("<Leave>", _hout)
                w.bind("<Button-1>", _cl)
            # Armazena refs para poder marcar ativo
            f._ind = ind
            f._ico = lbl_ico
            f._txt = lbl_txt
            return f

        # Botoes de ferramentas normais
        self.btns_ferr = {}
        for chave, icone, dica in self.FERRAMENTAS:
            f = _criar_btn_ferr(inner, chave, icone, dica, self._set_ferr)
            self.btns_ferr[chave] = f

        # Botoes de ferramentas de via (criados mas nao empacotados)
        self.btns_via = {}
        for chave, icone, dica in FERRAMENTAS_VIA:
            f = _criar_btn_ferr(inner, chave, icone, dica, self._set_ferr_via)
            f.pack_forget()
            self.btns_via[chave] = f

        # Separador antes do zoom
        self._sep_zoom = tk.Frame(inner, bg=AZUL_BORDA, height=1)
        self._sep_zoom.pack(fill="x", padx=12, pady=8)

        # Botoes de zoom
        def _criar_btn_zoom(parent, icone, label, cmd):
            f = tk.Frame(parent, bg=FUNDO_PAINEL, cursor="hand2")
            f.pack(fill="x", pady=1)
            tk.Frame(f, bg=FUNDO_PAINEL, width=3).pack(side="left", fill="y")
            tk.Label(f, text=icone, font=("Segoe UI", 13),
                     bg=FUNDO_PAINEL, fg=TEXTO_SECONDARIO,
                     width=2).pack(side="left", padx=(8,4), pady=4)
            tk.Label(f, text=label, font=FONTE_SMALL,
                     bg=FUNDO_PAINEL, fg=TEXTO_SECONDARIO,
                     anchor="w").pack(side="left", fill="x", expand=True)
            def _hin(e):
                f.config(bg=FUNDO_HOVER)
                for w in f.winfo_children():
                    try: w.config(bg=FUNDO_HOVER)
                    except: pass
            def _hout(e):
                f.config(bg=FUNDO_PAINEL)
                for w in f.winfo_children():
                    try: w.config(bg=FUNDO_PAINEL)
                    except: pass
            def _cl(e): cmd()
            for w in [f] + list(f.winfo_children()):
                w.bind("<Enter>", _hin)
                w.bind("<Leave>", _hout)
                w.bind("<Button-1>", _cl)
            return f

        self._btns_zoom = []
        self._btns_zoom.append(_criar_btn_zoom(inner, "+", "Zoom +",
                                                lambda: self._zoom_d(1.2)))
        self._btns_zoom.append(_criar_btn_zoom(inner, "−", "Zoom −",
                                                lambda: self._zoom_d(1/1.2)))
        self._btns_zoom.append(_criar_btn_zoom(inner, "⌂", "Zoom total",
                                                self._reset_view))

        # Botao Modo Via na base
        tk.Frame(inner, bg=FUNDO_PAINEL).pack(fill="x", expand=True)
        tk.Frame(inner, bg=AZUL_BORDA, height=1).pack(fill="x")

        self._btn_modo_via = tk.Frame(inner, bg="#162810", cursor="hand2")
        self._btn_modo_via.pack(fill="x")
        tk.Frame(self._btn_modo_via, bg=DOURADO, width=3).pack(side="left", fill="y")
        tk.Label(self._btn_modo_via, text="🛣",
                 font=("Segoe UI", 14),
                 bg="#162810", fg=DOURADO,
                 width=2).pack(side="left", padx=(8,4), pady=10)
        tk.Label(self._btn_modo_via, text="Modo Via",
                 font=FONTE_SMALL_BOLD,
                 bg="#162810", fg=DOURADO,
                 anchor="w").pack(side="left", fill="x", expand=True)
        for w in [self._btn_modo_via] + list(self._btn_modo_via.winfo_children()):
            w.bind("<Button-1>", lambda e: self._toggle_modo_via())
            w.bind("<Enter>", lambda e: hasattr(self, "status") and
                   self.status.config(text="Editor de Via — alterna modo arte"))
'''

# CORRIGE: TEXTO_SECONDARIO -> TEXTO_SECUNDARIO
new_toolbar = new_toolbar.replace("TEXTO_SECONDARIO", "TEXTO_SECUNDARIO")

if old_toolbar in src:
    src = src.replace(old_toolbar, new_toolbar, 1)
    print("PATCH 1 OK — toolbar substituida")
else:
    print("PATCH 1 SKIP — toolbar antiga nao encontrada (formato diferente?)")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 2: atualiza _set_ferr para marcar visual ativo
# Antes ele faz btn.config(bg=...). Agora precisa pintar o Frame.
# ══════════════════════════════════════════════
# Procura _set_ferr e injeta logica de visual ativo
import re
match = re.search(r"(    def _set_ferr\(self, ferr\):\n)", src)
if match:
    inicio_corpo = match.end()
    injecao = (
        '        # Atualiza visual dos botoes da toolbar (frame, nao Button)\n'
        '        for ch, f in self.btns_ferr.items():\n'
        '            if not isinstance(f, tk.Frame): continue\n'
        '            ativo = (ch == ferr)\n'
        '            f._ativo = ativo\n'
        '            bg = FUNDO_ATIVO if ativo else FUNDO_PAINEL\n'
        '            ind_cor = DOURADO if ativo else bg\n'
        '            fg = TEXTO_PRIMARIO if ativo else TEXTO_SECUNDARIO\n'
        '            f.config(bg=bg)\n'
        '            f._ind.config(bg=ind_cor)\n'
        '            f._ico.config(bg=bg, fg=DOURADO if ativo else fg)\n'
        '            f._txt.config(bg=bg, fg=fg,\n'
        '                          font=FONTE_SMALL_BOLD if ativo else FONTE_SMALL)\n'
    )
    src = src[:inicio_corpo] + injecao + src[inicio_corpo:]
    print("PATCH 2 OK — _set_ferr atualiza visual")

# Mesmo tratamento para _set_ferr_via
match = re.search(r"(    def _set_ferr_via\(self, ferr\):\n)", src)
if match:
    inicio_corpo = match.end()
    injecao = (
        '        for ch, f in self.btns_via.items():\n'
        '            if not isinstance(f, tk.Frame): continue\n'
        '            ativo = (ch == ferr)\n'
        '            f._ativo = ativo\n'
        '            bg = FUNDO_ATIVO if ativo else FUNDO_PAINEL\n'
        '            ind_cor = DOURADO if ativo else bg\n'
        '            fg = TEXTO_PRIMARIO if ativo else TEXTO_SECUNDARIO\n'
        '            f.config(bg=bg)\n'
        '            f._ind.config(bg=ind_cor)\n'
        '            f._ico.config(bg=bg, fg=DOURADO if ativo else fg)\n'
        '            f._txt.config(bg=bg, fg=fg,\n'
        '                          font=FONTE_SMALL_BOLD if ativo else FONTE_SMALL)\n'
    )
    src = src[:inicio_corpo] + injecao + src[inicio_corpo:]
    print("PATCH 3 OK — _set_ferr_via atualiza visual")

# ══════════════════════════════════════════════
# PATCH 4: _toggle_modo_via tem pack/pack_forget de btns_ferr e btns_via
# Os antigos eram Buttons, agora sao Frames. Verificar se o pack
# ainda funciona — precisa garantir fill='x' nos packs
# ══════════════════════════════════════════════
# Busca padroes pack/pack_forget de btns_via/btns_ferr e ajusta para fill='x'
src = re.sub(
    r'(\.btns_via\[ch\]\.pack)\(pady=1, padx=3\)',
    r"\1(fill='x', pady=1)",
    src)
src = re.sub(
    r'(self\.btns_ferr\[ch\]\.pack)\(pady=1, padx=3\)',
    r"\1(fill='x', pady=1)",
    src)
print("PATCH 4 OK — pack ajustado para fill='x'")

# Salva
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
print("  2. Toolbar lateral agora tem icone + nome")
print("  3. Clique numa ferramenta — fica em azul royal com indicador dourado")
print("  4. Hover suave em cada item")
print("  5. Clique em 'Modo Via' — alterna ferramentas")
