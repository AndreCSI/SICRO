"""
diagnostico.py — NAO MODIFICA NADA. Apenas mostra o estado do arquivo.
Execute: python diagnostico.py > diag.txt
Depois cole o conteudo de diag.txt aqui no chat.
"""
from pathlib import Path
import re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")

print("="*60)
print("DIAGNOSTICO editor_croqui.py")
print("="*60)
print(f"Total de linhas: {len(src.splitlines())}")
print(f"Total de chars: {len(src)}")

print("\n--- 1. BRASAO ---")
if "_brasao_tk" in src:
    print("  TEM referencia a _brasao_tk")
    # Mostra contexto
    idx = src.find("_brasao_tk")
    print("  Contexto:")
    for l in src[max(0,idx-300):idx+300].split("\n"):
        print(f"    {l}")
else:
    print("  NAO tem _brasao_tk")

if "PCI/AP" in src:
    print("  TEM texto 'PCI/AP'")
    idx = src.find("PCI/AP")
    for l in src[max(0,idx-200):idx+100].split("\n"):
        print(f"    {l}")
else:
    print("  NAO tem texto PCI/AP")

print("\n--- 2. BUSSOLA ---")
matches = list(re.finditer(r"def _bussola", src))
print(f"  Ocorrencias de 'def _bussola': {len(matches)}")
m = re.search(r"    def _bussola.*?(?=\n    def )", src, re.DOTALL)
if m:
    print("  Conteudo do _bussola:")
    for l in m.group(0).split("\n"):
        print(f"    {l}")
# Conta quantos create_text com "N"
bussola_txt = m.group(0) if m else ""
n_count = bussola_txt.count('text="N"')
print(f"  create_text com 'N': {n_count}")

print("\n--- 3. _set_ferr ---")
matches = list(re.finditer(r"def _set_ferr\b", src))
print(f"  Ocorrencias de 'def _set_ferr': {len(matches)}")
m = re.search(r"    def _set_ferr\(self, ferr\):.*?(?=\n    def )", src, re.DOTALL)
if m:
    metodo = m.group(0)
    print(f"  Tamanho do metodo: {len(metodo)} chars, {metodo.count(chr(10))} linhas")
    print("  Primeiras 40 linhas:")
    for i, l in enumerate(metodo.split("\n")[:40]):
        print(f"    {i:3}: {l}")
    print(f"  Tem 'FUNDO_ATIVO': {'FUNDO_ATIVO' in metodo}")
    print(f"  Tem 'btns_ferr': {'btns_ferr' in metodo}")
    print(f"  Tem 'f._ind': {'f._ind' in metodo}")

print("\n--- 4. _criar_btn_ferr (cria os botoes) ---")
m = re.search(r"        def _criar_btn_ferr.*?(?=\n        # Botoes de ferramentas normais)", src, re.DOTALL)
if m:
    print("  ENCONTRADO. Conteudo:")
    for i, l in enumerate(m.group(0).split("\n")):
        print(f"    {i:3}: {l}")
else:
    print("  NAO encontrado pelo padrao — buscando alternativa")
    m2 = re.search(r"_criar_btn_ferr", src)
    if m2:
        idx = m2.start()
        print(f"  '_criar_btn_ferr' aparece em char {idx}")
        print("  Contexto (600 chars):")
        for l in src[idx:idx+600].split("\n"):
            print(f"    {l}")

print("\n--- 5. Onde _set_ferr e chamado na init ---")
for m in re.finditer(r'_set_ferr\("?sel"?\)', src):
    idx = m.start()
    linha = src[:idx].count("\n") + 1
    print(f"  Linha {linha}: ...{src[max(0,idx-60):idx+40]}...")

print("\n" + "="*60)
print("FIM DO DIAGNOSTICO")
print("="*60)
