"""
patch_botao_hover.py — Botao Iniciar mantem cor no hover do card
Guarda ref do botao, pula ele no loop de hover, e da efeito de clarear.
"""
from pathlib import Path
import ast

editor_path = Path("ui") / "tela_inicial.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# Substitui criacao do botao + hover
old = '''        btn_fg = TEXTO_INVERTIDO if cor_acento == DOURADO else TEXTO_PRIMARIO
        tk.Button(inner, text='Iniciar  >',
                  font=FONTE_SMALL_BOLD, cursor='hand2',
                  bg=cor_acento, fg=btn_fg,
                  activebackground=FUNDO_HOVER,
                  relief='flat', bd=0, padx=12, pady=5,
                  command=cmd).pack(anchor='w')
        # Hover
        def _hin(e):
            card.config(bg=FUNDO_HOVER); inner.config(bg=FUNDO_HOVER)
            for w in inner.winfo_children():
                try: w.config(bg=FUNDO_HOVER)
                except Exception: pass
        def _hout(e):
            card.config(bg=FUNDO_CARD); inner.config(bg=FUNDO_CARD)
            for w in inner.winfo_children():
                try: w.config(bg=FUNDO_CARD)
                except Exception: pass
        card.bind('<Enter>', _hin); card.bind('<Leave>', _hout)
        inner.bind('<Enter>', _hin); inner.bind('<Leave>', _hout)'''

new = '''        btn_fg = TEXTO_INVERTIDO if cor_acento == DOURADO else TEXTO_PRIMARIO
        # Cor mais clara para hover do botao
        def _clarear(hexcor, fator=0.18):
            try:
                h = hexcor.lstrip('#')
                r = int(h[0:2],16); g = int(h[2:4],16); b = int(h[4:6],16)
                r = min(255, int(r + (255-r)*fator))
                g = min(255, int(g + (255-g)*fator))
                b = min(255, int(b + (255-b)*fator))
                return f'#{r:02X}{g:02X}{b:02X}'
            except Exception:
                return hexcor
        cor_hover = _clarear(cor_acento)
        btn_iniciar = tk.Button(inner, text='Iniciar  >',
                  font=FONTE_SMALL_BOLD, cursor='hand2',
                  bg=cor_acento, fg=btn_fg,
                  activebackground=cor_hover,
                  activeforeground=btn_fg,
                  relief='flat', bd=0, padx=12, pady=5,
                  command=cmd)
        btn_iniciar.pack(anchor='w')
        # Hover do CARD — pula o botao (mantem cor original)
        def _hin(e):
            card.config(bg=FUNDO_HOVER); inner.config(bg=FUNDO_HOVER)
            for w in inner.winfo_children():
                if w is btn_iniciar:
                    continue  # botao mantem sua cor
                try: w.config(bg=FUNDO_HOVER)
                except Exception: pass
            # Efeito sutil no botao: clareia um pouco
            btn_iniciar.config(bg=cor_hover)
        def _hout(e):
            card.config(bg=FUNDO_CARD); inner.config(bg=FUNDO_CARD)
            for w in inner.winfo_children():
                if w is btn_iniciar:
                    continue
                try: w.config(bg=FUNDO_CARD)
                except Exception: pass
            # Botao volta a cor original
            btn_iniciar.config(bg=cor_acento)
        card.bind('<Enter>', _hin); card.bind('<Leave>', _hout)
        inner.bind('<Enter>', _hin); inner.bind('<Leave>', _hout)'''

if old in src:
    src = src.replace(old, new, 1)
    print("PATCH OK — botao mantem cor no hover")
else:
    print("PATCH ERRO — bloco nao bate")
    raise SystemExit

editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO: {e}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste: hover no card — botao Iniciar CLAREIA levemente,")
print("       tira o mouse — botao volta a cor original (azul/verde/dourado)")
