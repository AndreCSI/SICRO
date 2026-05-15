"""
patch_camadas.py — Moderniza painel de Camadas para o tema
Usa as strings REAIS do diagnostico. Mantem o Listbox funcional.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# Bloco antigo EXATO (do diagnostico)
# ══════════════════════════════════════════════
old = '''        pd = tk.Frame(corpo, bg=COR_PAINEL, width=220)
        pd.pack(side="right", fill="y")
        pd.pack_propagate(False)
        tk.Frame(pd, bg=AMARELO, height=2).pack(fill="x")

        # --- Seção Camadas ---
        cab_cam = tk.Frame(pd, bg=COR_PAINEL)
        cab_cam.pack(fill="x", padx=6, pady=(8,2))
        tk.Label(cab_cam, text="Camadas", font=FONTE_SUB,
                 bg=COR_PAINEL, fg=AMARELO).pack(side="left")

        # Botões mover camada
        for sym, tip, cmd in [("▲","Subir camada",self._camada_subir),
                                ("▼","Descer camada",self._camada_descer)]:
            b = tk.Button(cab_cam, text=sym, font=("Segoe UI",9),
                          width=2, cursor="hand2",
                          bg=COR_CARD, fg=BRANCO,
                          activebackground=AZUL_MEDIO,
                          relief="flat", pady=1,
                          command=cmd)
            b.pack(side="right", padx=1)
            b.bind("<Enter>", lambda e,t=tip: self.status.config(text=t))

        # Listbox de camadas
        flb = tk.Frame(pd, bg=COR_CARD)
        flb.pack(fill="both", expand=True, padx=4, pady=2)
        scrl_cam = tk.Scrollbar(flb)
        scrl_cam.pack(side="right", fill="y")
        self.lb_camadas = tk.Listbox(
            flb,
            yscrollcommand=scrl_cam.set,
            bg=COR_CARD, fg=BRANCO,
            selectbackground=AZUL_MEDIO,
            selectforeground=BRANCO,
            font=("Segoe UI",9),
            relief="flat", bd=0,
            activestyle="none",
            highlightthickness=0,
        )
        self.lb_camadas.pack(fill="both", expand=True)
        scrl_cam.config(command=self.lb_camadas.yview)
        self.lb_camadas.bind("<<ListboxSelect>>", self._camada_selecionada)

        # Botão apagar da camada
        tk.Button(pd, text="⌫  Apagar selecionado",
                  font=FONTE_PEQ, cursor="hand2",
                  bg="#3A1010", fg="#FF8080",
                  activebackground="#5A1A1A",
                  relief="flat", pady=4,
                  command=self._camada_apagar).pack(fill="x", padx=4, pady=(0,4))

        # --- Separador ---
        tk.Frame(pd, bg=AMARELO, height=1).pack(fill="x", padx=4)'''

new = '''        pd = tk.Frame(corpo, bg=FUNDO_PAINEL, width=240)
        pd.pack(side="right", fill="y")
        pd.pack_propagate(False)
        # Borda esquerda sutil
        tk.Frame(pd, bg=AZUL_BORDA, width=1).pack(side="left", fill="y")

        # --- Seção Camadas ---
        cab_cam = tk.Frame(pd, bg=FUNDO_PAINEL)
        cab_cam.pack(fill="x", padx=14, pady=(14,6))
        tk.Label(cab_cam, text="Camadas", font=FONTE_H3,
                 bg=FUNDO_PAINEL, fg=DOURADO).pack(side="left")

        # Botões mover camada — estilo moderno
        for sym, tip, cmd in [("▲","Subir camada",self._camada_subir),
                                ("▼","Descer camada",self._camada_descer)]:
            b = tk.Label(cab_cam, text=sym, font=("Segoe UI",10),
                         bg=FUNDO_CARD, fg=TEXTO_SECUNDARIO,
                         width=3, cursor="hand2", pady=2)
            b.pack(side="right", padx=2)
            def _mk(cmd=cmd, tip=tip, b=b):
                b.bind("<Button-1>", lambda e: cmd())
                b.bind("<Enter>", lambda e: (b.config(bg=FUNDO_HOVER,
                       fg=TEXTO_PRIMARIO),
                       hasattr(self,"status") and self.status.config(text=tip)))
                b.bind("<Leave>", lambda e: b.config(bg=FUNDO_CARD,
                       fg=TEXTO_SECUNDARIO))
            _mk()

        # Listbox de camadas — cores do tema
        flb = tk.Frame(pd, bg=FUNDO_CARD)
        flb.pack(fill="both", expand=True, padx=10, pady=4)
        scrl_cam = tk.Scrollbar(flb, width=10)
        scrl_cam.pack(side="right", fill="y")
        self.lb_camadas = tk.Listbox(
            flb,
            yscrollcommand=scrl_cam.set,
            bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,
            selectbackground=FUNDO_ATIVO,
            selectforeground=TEXTO_PRIMARIO,
            font=("Segoe UI",9),
            relief="flat", bd=0,
            activestyle="none",
            highlightthickness=0,
        )
        self.lb_camadas.pack(fill="both", expand=True, padx=4, pady=4)
        scrl_cam.config(command=self.lb_camadas.yview)
        self.lb_camadas.bind("<<ListboxSelect>>", self._camada_selecionada)

        # Botão apagar — estilo moderno, vermelho discreto
        btn_apagar = tk.Frame(pd, bg="#2A1414", cursor="hand2")
        btn_apagar.pack(fill="x", padx=10, pady=(4,8))
        _la = tk.Label(btn_apagar, text="⌫  Apagar selecionado",
                       font=FONTE_SMALL, bg="#2A1414", fg="#E08080",
                       pady=7)
        _la.pack()
        def _del_hover_in(e):
            btn_apagar.config(bg="#3D1A1A"); _la.config(bg="#3D1A1A",
                              fg="#FF9999")
        def _del_hover_out(e):
            btn_apagar.config(bg="#2A1414"); _la.config(bg="#2A1414",
                              fg="#E08080")
        for w in (btn_apagar, _la):
            w.bind("<Button-1>", lambda e: self._camada_apagar())
            w.bind("<Enter>", _del_hover_in)
            w.bind("<Leave>", _del_hover_out)

        # --- Separador ---
        tk.Frame(pd, bg=AZUL_BORDA, height=1).pack(fill="x", padx=10, pady=2)'''

if old in src:
    src = src.replace(old, new, 1)
    print("PATCH OK — painel Camadas modernizado")
else:
    print("PATCH ERRO — bloco nao bate exatamente")
    # Debug: mostra diferenca
    m = re.search(r'        pd = tk\.Frame\(corpo.*?Separador.*?\n', src, re.DOTALL)
    if m:
        print("Bloco atual encontrado mas diferente. Primeiras linhas:")
        for l in m.group(0).split("\n")[:10]:
            print(f"  |{l}")
    raise SystemExit

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
print("Esperado: painel Camadas com cores do tema, botoes hover, apagar discreto")
