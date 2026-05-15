"""
fase5_v2.py — Painel de propriedades editavel (versao segura)
Substitui SOMENTE o _mostrar_props para criar campos editaveis.
Nao mexe no resto da estrutura.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# Localiza _mostrar_props e substitui
# ══════════════════════════════════════════════
# Captura todo o metodo ate o proximo 'def' ou final de classe
match = re.search(
    r"(    def _mostrar_props\(self, idx\):\n)((?:        .+\n|\n)+?)(    def |\nclass )",
    src
)

if not match:
    print("ERRO: _mostrar_props nao encontrado")
    raise SystemExit

inicio = match.start()
fim_metodo = match.start(3)  # comeco do proximo def
print(f"_mostrar_props encontrado: linhas ~{src[:inicio].count(chr(10))+1} a ~{src[:fim_metodo].count(chr(10))+1}")

# Novo metodo
novo_metodo = '''    def _mostrar_props(self, idx):
        """Mostra propriedades editaveis do elemento selecionado."""
        el = self.elementos[idx]

        # Se nao tem painel novo, usa fallback antigo
        if not hasattr(self, "_props"):
            linhas = []
            icone, nome = TIPO_INFO.get(el["tipo"], ("?", el["tipo"]))
            linhas.append(f"{icone}  {nome}")
            if el.get("label"):      linhas.append(f"Rotulo: {el['label']}")
            if el.get("angulo") is not None and el["tipo"] != "_rotatoria":
                linhas.append(f"Angulo: {el.get('angulo',0):.0f}graus")
            if el.get("larg"):       linhas.append(f"Largura: {el['larg']} px")
            if el.get("alt"):        linhas.append(f"Altura: {el['alt']} px")
            if hasattr(self, "label_prop"):
                self.label_prop.config(text="\\n".join(linhas))
            tipos_redim = ("carro","moto","caminhao","bicicleta",
                           "pedestre","sc","via_h","via_v","r1","r2")
            if el["tipo"] in tipos_redim:
                self.btn_redim.config(state="normal", fg=DOURADO)
            else:
                self.btn_redim.config(state="disabled", fg=TEXTO_TERCIARIO)
            return

        # ──── PAINEL NOVO COM CAMPOS EDITAVEIS ────
        # Limpa campos antigos
        for w in self._props.winfo_children():
            w.destroy()

        icone, nome = TIPO_INFO.get(el["tipo"], ("?", el["tipo"]))

        # Cabecalho
        hdr = tk.Frame(self._props, bg=FUNDO_PAINEL)
        hdr.pack(fill="x", pady=(0,8))
        tk.Label(hdr, text=icone, font=("Segoe UI", 14),
                 bg=FUNDO_PAINEL, fg=DOURADO).pack(side="left")
        tk.Label(hdr, text="  " + nome, font=FONTE_BODY_BOLD,
                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side="left")

        def _campo(label, valor_str, on_change):
            """Cria um campo Entry editavel."""
            f = tk.Frame(self._props, bg=FUNDO_PAINEL)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                     width=11, anchor="w").pack(side="left")
            var = tk.StringVar(value=valor_str)
            e = tk.Entry(f, textvariable=var, font=FONTE_SMALL,
                         bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,
                         insertbackground=DOURADO,
                         relief="flat", bd=4, width=10,
                         highlightthickness=1,
                         highlightcolor=DOURADO,
                         highlightbackground=AZUL_BORDA)
            e.pack(side="left", fill="x", expand=True)
            def _apply(event=None):
                try:
                    on_change(var.get())
                    self._redesenhar()
                except Exception:
                    var.set(valor_str)
            e.bind("<Return>", _apply)
            e.bind("<FocusOut>", _apply)

        # Rotulo
        if el.get("label") is not None:
            def set_label(v):
                el["label"] = v
            _campo("Rotulo", str(el.get("label", "")), set_label)

        # Posicao
        k = self.k if (self.calibrado and self.k) else 1.0
        unidade = "m" if self.calibrado else "px"
        fator = k if self.calibrado else 1.0

        if "x" in el and "y" in el:
            def set_x(v):
                el["x"] = float(v) / fator
            def set_y(v):
                el["y"] = float(v) / fator
            _campo(f"Pos X ({unidade})",
                   f"{el.get('x', 0) * fator:.2f}", set_x)
            _campo(f"Pos Y ({unidade})",
                   f"{el.get('y', 0) * fator:.2f}", set_y)

        # Angulo
        if el.get("angulo") is not None and el["tipo"] != "_rotatoria":
            def set_ang(v):
                el["angulo"] = float(v)
            _campo("Rotacao", f"{el.get('angulo', 0):.1f}", set_ang)

        # Largura
        if el.get("larg") is not None:
            def set_larg(v):
                el["larg"] = float(v) / fator
            _campo(f"Largura ({unidade})",
                   f"{el['larg'] * fator:.2f}", set_larg)

        # Altura
        if el.get("alt") is not None:
            def set_alt(v):
                el["alt"] = float(v) / fator
            _campo(f"Altura ({unidade})",
                   f"{el['alt'] * fator:.2f}", set_alt)

        # Cor (com seletor)
        if el.get("cor"):
            cf = tk.Frame(self._props, bg=FUNDO_PAINEL)
            cf.pack(fill="x", pady=2)
            tk.Label(cf, text="Cor", font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                     width=11, anchor="w").pack(side="left")
            cor_atual = el.get("cor", "#888888")
            swatch = tk.Frame(cf, bg=cor_atual, width=24, height=18,
                              cursor="hand2", relief="solid", bd=1)
            swatch.pack(side="left", padx=(0,6))
            swatch.pack_propagate(False)
            def _trocar_cor(event):
                from tkinter import colorchooser
                cor = colorchooser.askcolor(
                    initialcolor=el.get("cor", "#888888"),
                    parent=self.winfo_toplevel())
                if cor and cor[1]:
                    el["cor"] = cor[1]
                    swatch.config(bg=cor[1])
                    self._redesenhar()
            swatch.bind("<Button-1>", _trocar_cor)
            tk.Label(cf, text=cor_atual, font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO).pack(side="left")

        # Botao redimensionar
        tipos_redim = ("carro","moto","caminhao","bicicleta",
                       "pedestre","sc","via_h","via_v","r1","r2")
        if el["tipo"] in tipos_redim:
            self.btn_redim.config(state="normal", fg=DOURADO)
        else:
            self.btn_redim.config(state="disabled", fg=TEXTO_TERCIARIO)

'''

src = src[:inicio] + novo_metodo + src[fim_metodo:]
print("_mostrar_props substituido")

# ══════════════════════════════════════════════
# Garante que existe self._props no _build_ui
# Procura pela seçao Propriedades antiga e substitui pelo container
# ══════════════════════════════════════════════
old_label = '''        # --- Seção Propriedades ---
        tk.Label(pd, text="Propriedades", font=FONTE_SUB,
                 bg=COR_PAINEL, fg=AMARELO).pack(pady=(6,2))
        self.label_prop = tk.Label(pd,
                                   text="Selecione um\\nelemento",
                                   font=FONTE_PEQ,
                                   bg=COR_PAINEL, fg=CINZA_CLARO,
                                   justify="left", wraplength=200)
        self.label_prop.pack(padx=10, anchor="w")'''

new_label = '''        # --- Seção Propriedades (painel rico) ---
        tk.Label(pd, text="Propriedades", font=FONTE_H3,
                 bg=FUNDO_PAINEL, fg=DOURADO).pack(pady=(10,4), anchor="w", padx=10)
        # Container que recebera os campos editaveis
        self._props = tk.Frame(pd, bg=FUNDO_PAINEL)
        self._props.pack(fill="x", padx=10, pady=2)
        # Placeholder inicial
        self.label_prop = tk.Label(self._props,
            text="Selecione um\\nelemento no canvas",
            font=FONTE_SMALL,
            bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
            justify="left", wraplength=240)
        self.label_prop.pack(anchor="w", pady=4)'''

if old_label in src:
    src = src.replace(old_label, new_label, 1)
    print("Container _props criado")
elif "self._props = tk.Frame" not in src:
    print("AVISO: nao consegui criar self._props automaticamente")

# Salva e valida
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
print("Teste: clique num veiculo — campos editaveis devem aparecer")
