"""
patch_seletor_cor.py — Substitui colorchooser nativo pelo seletor do tema
Requer: widgets/seletor_cor.py instalado.
"""
from pathlib import Path
import ast, re

if not (Path("widgets")/"seletor_cor.py").exists():
    print("ATENCAO: widgets/seletor_cor.py NAO encontrado.")
    print("Baixe seletor_cor.py e coloque em widgets/ antes deste patch.")
    raise SystemExit

ep = Path("ui")/"editor_croqui.py"
src = ep.read_text(encoding="utf-8")
src_orig = src

# Acha todos os usos de colorchooser
usos = list(re.finditer(r'colorchooser', src))
print(f"Ocorrencias de 'colorchooser': {len(usos)}")
for m in usos:
    ln = src[:m.start()].count("\n")+1
    print(f"  L{ln}: {src[m.start()-10:m.start()+90].splitlines()[0] if m.start()>10 else ''}")

# Padrao tipico (do diagnostico anterior):
old = '''            def _trocar_cor(event):
                from tkinter import colorchooser
                cor = colorchooser.askcolor(
                    initialcolor=el.get("cor", "#888888"),
                    parent=self.winfo_toplevel())
                if cor and cor[1]:
                    el["cor"] = cor[1]
                    swatch.config(bg=cor[1])
                    self._redesenhar()'''

new = '''            def _trocar_cor(event):
                from widgets.seletor_cor import escolher_cor
                nova = escolher_cor(self.winfo_toplevel(),
                                    el.get("cor", "#888888"))
                if nova:
                    el["cor"] = nova
                    swatch.config(bg=nova)
                    self._redesenhar()
                    if self.sel_idx is not None:
                        self._mostrar_props(self.sel_idx)'''

if old in src:
    src = src.replace(old, new, 1)
    print("\nPATCH OK — _trocar_cor usa seletor do tema")
else:
    print("\nPATCH: padrao exato nao bateu. Tentando substituicao generica...")
    # Substituicao mais flexivel: troca o corpo do askcolor
    pat = re.compile(
        r'from tkinter import colorchooser\n'
        r'(\s*)cor = colorchooser\.askcolor\(\s*'
        r'initialcolor=([^,]+),\s*'
        r'parent=self\.winfo_toplevel\(\)\)\n'
        r'\s*if cor and cor\[1\]:\n'
        r'(\s*)el\["cor"\] = cor\[1\]\n'
        r'\s*swatch\.config\(bg=cor\[1\]\)\n'
        r'\s*self\._redesenhar\(\)'
    )
    def _rep(m):
        ind = m.group(1)
        init = m.group(2).strip()
        return (f'from widgets.seletor_cor import escolher_cor\n'
                f'{ind}nova = escolher_cor(self.winfo_toplevel(), {init})\n'
                f'{ind}if nova:\n'
                f'{ind}    el["cor"] = nova\n'
                f'{ind}    swatch.config(bg=nova)\n'
                f'{ind}    self._redesenhar()')
    src2, n = pat.subn(_rep, src)
    if n:
        src = src2
        print(f"PATCH OK (generico) — {n} substituicao(oes)")
    else:
        print("ERRO: nao foi possivel localizar o bloco colorchooser")
        print("Cole as linhas ao redor de 'colorchooser' para ajuste manual")
        raise SystemExit

ep.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO {e.lineno}: {e.msg}")
    ep.write_text(src_orig, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste: selecione um veiculo/R1/R2/cota -> clique no quadradinho")
print("de Cor -> abre o seletor NO TEMA (paleta + hex), nao o do Windows")
