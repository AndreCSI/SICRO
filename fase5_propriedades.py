"""
fase5_propriedades.py — Painel de propriedades expandido
- Campos editaveis para cada propriedade
- Posicao X/Y em metros (usa escala calibrada)
- Rotacao, escala, dimensoes
- Cor, transparencia
- Atualiza elemento e canvas em tempo real
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: substitui o label_prop e botao redim pelo novo painel
# ══════════════════════════════════════════════
old_block = '''        # --- Seção Propriedades ---
        tk.Label(pd, text="Propriedades", font=FONTE_SUB,
                 bg=COR_PAINEL, fg=AMARELO).pack(pady=(6,2))
        self.label_prop = tk.Label(pd,
                                   text="Selecione um\\nelemento",
                                   font=FONTE_PEQ,
                                   bg=COR_PAINEL, fg=CINZA_CLARO,
                                   justify="left", wraplength=200)
        self.label_prop.pack(padx=10, anchor="w")

        # Botão redimensionar
        self.btn_redim = tk.Button(pd, text="⇲  Redimensionar",
                                   font=FONTE_PEQ, cursor="hand2",
                                   bg=COR_CARD, fg=CINZA_CLARO,
                                   activebackground=AZUL_MEDIO,
                                   relief="flat", pady=4, state="disabled",
                                   command=self._abrir_redimensionar)
        self.btn_redim.pack(fill="x", padx=4, pady=(6,2))
'''

new_block = '''        # --- SEÇÃO PROPRIEDADES — painel rico ---
        tk.Label(pd, text="Propriedades", font=FONTE_H3,
                 bg=FUNDO_PAINEL, fg=DOURADO).pack(pady=(10,4), anchor="w", padx=10)

        # Container do painel de propriedades
        self._props = tk.Frame(pd, bg=FUNDO_PAINEL)
        self._props.pack(fill="x", padx=10, pady=2)

        # Estado: nenhuma selecao
        self._props_placeholder = tk.Label(self._props,
            text="Selecione um\\nelemento no canvas",
            font=FONTE_SMALL,
            bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
            justify="left")
        self._props_placeholder.pack(anchor="w", pady=4)

        # Frames de campos (criados sob demanda)
        self._props_campos = {}

        # Botão redimensionar (mantido para compatibilidade)
        self.btn_redim = tk.Button(pd, text="⇲  Redimensionar",
                                   font=FONTE_SMALL, cursor="hand2",
                                   bg=FUNDO_CARD, fg=TEXTO_TERCIARIO,
                                   activebackground=AZUL_MEDIO,
                                   relief="flat", pady=4, state="disabled",
                                   command=self._abrir_redimensionar)
        self.btn_redim.pack(fill="x", padx=4, pady=(8,4), side="bottom")

        # label_prop alias para compatibilidade — nao mais visivel mas
        # mantem para nao quebrar codigo antigo que faz config(text=...)
        self.label_prop = self._props_placeholder
'''

if old_block in src:
    src = src.replace(old_block, new_block, 1)
    print("PATCH 1 OK — painel reestruturado")
else:
    print("PATCH 1 SKIP — bloco antigo nao encontrado")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 2: substitui _mostrar_props pelo novo metodo
# que cria campos editaveis
# ══════════════════════════════════════════════
old_mostrar = '''    def _mostrar_props(self, idx):
        el = self.elementos[idx]
        linhas = []
        icone, nome = TIPO_INFO.get(el["tipo"],("?",el["tipo"]))
        linhas.append(f"{icone}  {nome}")
        if el.get("label"):      linhas.append(f"Rótulo: {el['label']}")
        if el.get("angulo") is not None and el["tipo"] != "_rotatoria":
            linhas.append(f"Ângulo: {el.get('angulo',0):.0f}°")
        if el.get("larg"):       linhas.append(f"Largura: {el['larg']} px")
        if el.get("alt"):        linhas.append(f"Altura: {el['alt']} px")
        self.label_prop.config(text="\\n".join(linhas))

        # Habilita botão redimensionar apenas para tipos redimensionáveis
        tipos_redim = ("carro","moto","caminhao","bicicleta",
                       "pedestre","sc","via_h","via_v","r1","r2")
        if el["tipo"] in tipos_redim:
            self.btn_redim.config(state="normal", fg=AMARELO)
        else:
            self.btn_redim.config(state="disabled", fg=CINZA_CLARO)
'''

new_mostrar = '''    def _mostrar_props(self, idx):
        """Mostra propriedades do elemento selecionado com campos editaveis."""
        el = self.elementos[idx]
        # Limpa campos antigos
        for w in self._props.winfo_children():
            w.destroy()
        self._props_campos.clear()

        icone, nome = TIPO_INFO.get(el["tipo"], ("?", el["tipo"]))

        # Cabecalho com tipo
        hdr = tk.Frame(self._props, bg=FUNDO_PAINEL)
        hdr.pack(fill="x", pady=(0,8))
        tk.Label(hdr, text=icone, font=("Segoe UI", 14),
                 bg=FUNDO_PAINEL, fg=DOURADO).pack(side="left")
        tk.Label(hdr, text="  " + nome, font=FONTE_BODY_BOLD,
                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side="left")

        # Helper para criar campo editavel
        def _campo(label, valor, on_change, largura=12):
            f = tk.Frame(self._props, bg=FUNDO_PAINEL)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                     width=11, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(valor))
            e = tk.Entry(f, textvariable=var, font=FONTE_SMALL,
                         bg=FUNDO_CARD, fg=TEXTO_PRIMARIO,
                         insertbackground=DOURADO,
                         relief="flat", bd=4, width=largura,
                         highlightthickness=1,
                         highlightcolor=DOURADO,
                         highlightbackground=AZUL_BORDA)
            e.pack(side="left", fill="x", expand=True)
            def _apply(event=None):
                try:
                    on_change(var.get())
                    self._redesenhar()
                except Exception:
                    var.set(str(valor))  # reverte em erro
            e.bind("<Return>", _apply)
            e.bind("<FocusOut>", _apply)
            return var

        # Helper read-only
        def _info(label, valor):
            f = tk.Frame(self._props, bg=FUNDO_PAINEL)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                     width=11, anchor="w").pack(side="left")
            tk.Label(f, text=str(valor), font=FONTE_SMALL,
                     bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO,
                     anchor="w").pack(side="left", fill="x", expand=True)

        # Calcula posicao em metros (usa escala k se calibrada)
        k = self.k if self.calibrado and self.k else 1.0
        x_m = (el.get("x", 0) - getattr(self, "_offx", 0)) * k
        y_m = (el.get("y", 0) - getattr(self, "_offy", 0)) * k

        # --- Campos universais ---
        if el.get("label") is not None:
            def set_label(v): el["label"] = v
            _campo("Rotulo", el.get("label", ""), set_label)

        # Posicao (em metros se calibrado)
        if "x" in el and "y" in el:
            unidade = "m" if self.calibrado else "px"
            fator = k if self.calibrado else 1.0
            def set_x(v):
                try: el["x"] = float(v) / fator + getattr(self, "_offx", 0)
                except: pass
            def set_y(v):
                try: el["y"] = float(v) / fator + getattr(self, "_offy", 0)
                except: pass
            _campo(f"Pos X ({unidade})", f"{x_m:.2f}", set_x)
            _campo(f"Pos Y ({unidade})", f"{y_m:.2f}", set_y)

        # Angulo
        if el.get("angulo") is not None and el["tipo"] != "_rotatoria":
            def set_ang(v):
                try: el["angulo"] = float(v)
                except: pass
            _campo("Rotacao", f"{el.get('angulo', 0):.1f}", set_ang)

        # Dimensoes
        if el.get("larg") is not None:
            def set_larg(v):
                try: el["larg"] = float(v)
                except: pass
            unidade_d = "m" if self.calibrado else "px"
            fator_d = k if self.calibrado else 1.0
            valor_l = el["larg"] * fator_d
            _campo(f"Largura ({unidade_d})", f"{valor_l:.2f}",
                   lambda v, f=fator_d: el.__setitem__("larg", float(v)/f))

        if el.get("alt") is not None:
            unidade_d = "m" if self.calibrado else "px"
            fator_d = k if self.calibrado else 1.0
            valor_a = el["alt"] * fator_d
            _campo(f"Altura ({unidade_d})", f"{valor_a:.2f}",
                   lambda v, f=fator_d: el.__setitem__("alt", float(v)/f))

        # Cor
        if el.get("cor"):
            cf = tk.Frame(self._props, bg=FUNDO_PAINEL)
            cf.pack(fill="x", pady=2)
            tk.Label(cf, text="Cor", font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                     width=11, anchor="w").pack(side="left")
            cor_atual = el.get("cor", "#888888")
            swatch = tk.Frame(cf, bg=cor_atual, width=24, height=18,
                              cursor="hand2", relief="solid", bd=1,
                              highlightbackground=AZUL_BORDA)
            swatch.pack(side="left", padx=(0,4))
            swatch.pack_propagate(False)
            def _trocar_cor(e):
                from tkinter import colorchooser
                cor = colorchooser.askcolor(initialcolor=el.get("cor", "#888"),
                                            parent=self.winfo_toplevel())
                if cor[1]:
                    el["cor"] = cor[1]
                    swatch.config(bg=cor[1])
                    self._redesenhar()
            swatch.bind("<Button-1>", _trocar_cor)
            tk.Label(cf, text=cor_atual, font=FONTE_MICRO,
                     bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO).pack(side="left")

        # Info adicional
        if el["tipo"] in ("r1", "r2"):
            _info("Tipo", "Eixo de referencia")
        elif el["tipo"] == "cota":
            _info("Tipo", "Medida / cota")

        # Habilita redimensionar
        tipos_redim = ("carro","moto","caminhao","bicicleta",
                       "pedestre","sc","via_h","via_v","r1","r2")
        if el["tipo"] in tipos_redim:
            self.btn_redim.config(state="normal", fg=DOURADO)
        else:
            self.btn_redim.config(state="disabled", fg=TEXTO_TERCIARIO)
'''

if old_mostrar in src:
    src = src.replace(old_mostrar, new_mostrar, 1)
    print("PATCH 2 OK — _mostrar_props redesenhado")
else:
    print("PATCH 2 SKIP")
    raise SystemExit

# ══════════════════════════════════════════════
# PATCH 3: ao desselecionar, mostra placeholder
# ══════════════════════════════════════════════
old_des = '        self.label_prop.config(text="Selecione um\\nelemento")\n'
new_des = '''        # Restaura placeholder no painel de propriedades
        if hasattr(self, "_props"):
            for w in self._props.winfo_children():
                w.destroy()
            self._props_placeholder = tk.Label(self._props,
                text="Selecione um\\nelemento no canvas",
                font=FONTE_SMALL,
                bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                justify="left")
            self._props_placeholder.pack(anchor="w", pady=4)
            self.label_prop = self._props_placeholder
'''

n_subs = src.count(old_des)
src = src.replace(old_des, new_des)
print(f"PATCH 3 OK — {n_subs} placeholders atualizados")

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
print("  2. Clique em um veiculo — painel direito mostra campos editaveis")
print("  3. Mude rotulo, posicao, rotacao — canvas atualiza ao apertar Enter")
print("  4. Clique no quadradinho de cor — abre seletor de cor")
print("  5. Desselecione — volta a placeholder 'Selecione...'")
