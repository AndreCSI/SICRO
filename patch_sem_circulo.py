"""
patch_sem_circulo.py — Remove o circulo amarelo de selecao dos veiculos
A area de clique NAO depende do circulo (e o _em(x,y) que detecta).
Remove apenas o desenho visual.
"""
from pathlib import Path
import ast

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# O bloco exato da L2474 (veiculos)
old = '''            if sel:
                r=16*self.zoom
                c.create_oval(tx-r,ty-r,tx+r,ty+r,
                              outline=AMARELO,width=2,dash=(4,3))'''

new = '''            if sel:
                # Circulo de selecao removido — handles ja indicam selecao
                pass'''

if old in src:
    src = src.replace(old, new, 1)
    print("PATCH OK — circulo amarelo do veiculo removido")
else:
    print("PATCH ERRO — bloco nao bate exatamente. Tentando variantes...")
    import re
    # Procura variante com espacos diferentes
    pat = re.compile(
        r'            if sel:\n'
        r'                r=16\*self\.zoom\n'
        r'                c\.create_oval\(tx-r,ty-r,tx\+r,ty\+r,\n'
        r'                              outline=AMARELO,width=2,dash=\(4,3\)\)'
    )
    m = pat.search(src)
    if m:
        src = src[:m.start()] + new + src[m.end():]
        print("PATCH OK — via regex")
    else:
        print("NAO ENCONTRADO. Mostrando contexto da L2474:")
        linhas = src.split("\n")
        for i in range(2470, 2480):
            if i < len(linhas):
                print(f"  {i+1}: {linhas[i]}")
        raise SystemExit

editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO linha {e.lineno}: {e.msg}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste:")
print("  1. Selecione um veiculo")
print("  2. Circulo amarelo NAO aparece mais")
print("  3. Mas clicar no veiculo ainda seleciona (area de clique intacta)")
print("  4. Handles de canto/borda/rotacao continuam funcionando")
