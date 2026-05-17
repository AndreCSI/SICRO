"""
patch_modovia_dev.py — Modo Via: aviso "em desenvolvimento"
Substitui o corpo de _toggle_modo_via por um aviso no tema.
O codigo original e PRESERVADO como _toggle_modo_via_ORIGINAL
(comentado/renomeado) para retomar depois.
"""
from pathlib import Path
import ast, re

ep = Path("ui")/"editor_croqui.py"
src = ep.read_text(encoding="utf-8")
src_orig = src

# Localiza o metodo _toggle_modo_via inteiro
m = re.search(r"    def _toggle_modo_via\(self\):.*?(?=\n    def )", src, re.DOTALL)
if not m:
    print("ERRO: _toggle_modo_via nao encontrado")
    raise SystemExit

metodo_original = m.group(0)

# Renomeia o original para _PRESERVADO (mantem o codigo intacto no arquivo)
preservado = metodo_original.replace(
    "    def _toggle_modo_via(self):",
    "    def _toggle_modo_via_PRESERVADO(self):", 1)

# Novo metodo: aviso elegante no tema
novo = '''    def _toggle_modo_via(self):
        """Modo Via temporariamente desabilitado (em desenvolvimento)."""
        win = tk.Toplevel(self)
        win.overrideredirect(True)
        win.configure(bg=FUNDO_PAINEL,
                      highlightbackground=DOURADO, highlightthickness=1)
        win.grab_set()
        win.attributes("-topmost", True)
        ww, wh = 380, 200
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")
        tk.Frame(win, bg=DOURADO, height=3).pack(fill="x")
        tk.Label(win, text="🛣  Modo Via", font=FONTE_H3,
                 bg=FUNDO_PAINEL, fg=DOURADO).pack(pady=(20, 6))
        tk.Label(win,
                 text="Esta funcionalidade está em desenvolvimento\\n"
                      "e será disponibilizada em uma próxima versão.",
                 font=FONTE_BODY, bg=FUNDO_PAINEL,
                 fg=TEXTO_PRIMARIO, justify="center").pack(pady=4)
        tk.Label(win,
                 text="Use os modelos de via prontos na tela inicial.",
                 font=FONTE_SMALL, bg=FUNDO_PAINEL,
                 fg=TEXTO_SECUNDARIO, justify="center").pack(pady=(2, 14))
        bok = tk.Frame(win, bg=AZUL_MEDIO, cursor="hand2")
        bok.pack()
        lo = tk.Label(bok, text="Entendi", font=FONTE_BODY_BOLD,
                      bg=AZUL_MEDIO, fg=TEXTO_PRIMARIO, padx=24, pady=7)
        lo.pack()
        for w in (bok, lo):
            w.bind("<Button-1>", lambda e: win.destroy())
            w.bind("<Enter>", lambda e: (bok.config(bg=AZUL_CLARO),
                                          lo.config(bg=AZUL_CLARO)))
            w.bind("<Leave>", lambda e: (bok.config(bg=AZUL_MEDIO),
                                          lo.config(bg=AZUL_MEDIO)))
        tk.Frame(win, bg=DOURADO, height=3).pack(fill="x", side="bottom")
        win.bind("<Escape>", lambda e: win.destroy())
        win.bind("<Return>", lambda e: win.destroy())

'''

# Substitui: novo metodo + logo abaixo o preservado
src = src[:m.start()] + novo + preservado + "\n" + src[m.end():]

ep.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("Sintaxe OK")
    print("_toggle_modo_via -> aviso 'em desenvolvimento'")
    print("Codigo original preservado como _toggle_modo_via_PRESERVADO")
except SyntaxError as e:
    print(f"ERRO {e.lineno}: {e.msg}")
    ln=src.split("\n")
    for i in range(max(0,e.lineno-4),min(len(ln),e.lineno+3)):
        print(f"  {i+1:4}: {ln[i]}")
    ep.write_text(src_orig, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste: clicar 'Modo Via' -> aviso elegante no tema, nao entra no modo bugado")
