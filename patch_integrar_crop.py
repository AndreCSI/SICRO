"""
patch_integrar_crop.py — Integra CropadorImagem ao fluxo _novo do main.py
Apos escolher a foto, abre o cropador antes de entrar no editor.
"""
from pathlib import Path
import ast, shutil

# 1. Copia cropador.py para ui/
src_crop = Path("/mnt/user-data/outputs/cropador.py")
# (no PC do usuario o script roda da raiz; aqui simulamos a logica)
# O usuario deve ter baixado cropador.py para ui/ — verificamos
destino = Path("ui") / "cropador.py"
if not destino.exists():
    print("ATENCAO: ui/cropador.py NAO encontrado.")
    print("Baixe cropador.py e coloque em ui/ antes de rodar este patch.")
    raise SystemExit

# 2. Patch no main.py
mp = Path("main.py")
m = mp.read_text(encoding="utf-8")
m_orig = m

# Adiciona import do cropador junto aos outros imports de ui
old_imp = "from ui.editor_croqui import EditorCroqui"
new_imp = ("from ui.editor_croqui import EditorCroqui\n"
           "from ui.cropador import CropadorImagem")
if old_imp in m and "from ui.cropador import CropadorImagem" not in m:
    m = m.replace(old_imp, new_imp, 1)
    print("Import do CropadorImagem adicionado")
else:
    print("Import ja existe ou linha base nao encontrada (ok)")

# Insere o cropador apos Image.open(cam)
old_open = '''            cam = filedialog.askopenfilename(
                title="Foto do drone (ja retificada)",
                filetypes=[("Imagens", "*.jpg *.jpeg *.png *.tif")])
            if not cam:
                return
            img_drone = Image.open(cam)'''

new_open = '''            cam = filedialog.askopenfilename(
                title="Foto do drone (ja retificada)",
                filetypes=[("Imagens", "*.jpg *.jpeg *.png *.tif")])
            if not cam:
                return
            img_orig = Image.open(cam)
            # Ferramenta de recorte: foca na area do acidente,
            # reduz resolucao e deixa o trabalho mais fluido
            crop = CropadorImagem(self, img_orig)
            self.wait_window(crop)
            if crop.resultado is None:
                return   # usuario cancelou o recorte
            img_drone = crop.resultado'''

if old_open in m:
    m = m.replace(old_open, new_open, 1)
    print("Cropador integrado ao fluxo _novo")
else:
    print("ERRO: bloco Image.open(cam) nao bate exatamente")
    print("Conteudo atual ao redor:")
    import re
    mm = re.search(r'cam = filedialog.*?img_drone = Image\.open\(cam\)', m, re.DOTALL)
    if mm:
        for l in mm.group(0).split("\n"):
            print(f"  |{l}")
    raise SystemExit

mp.write_text(m, encoding="utf-8")
try:
    ast.parse(m)
    print("\nSintaxe main.py OK")
except SyntaxError as e:
    print(f"\nERRO {e.lineno}: {e.msg}")
    mp.write_text(m_orig, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\n" + "="*50)
print("CROPADOR INTEGRADO")
print("="*50)
print("Rode: python main.py")
print("Teste:")
print("  1. Novo croqui -> Croqui com Drone -> preenche dados")
print("  2. Escolhe a foto 4K do drone")
print("  3. Abre o CROPADOR: arraste sobre a area do acidente")
print("  4. Escolha resolucao (2500px recomendado)")
print("  5. 'Recortar' -> editor abre LEVE, so com a area util")
print("  6. Botao 'Usar imagem inteira' = pula recorte (so reduz res)")
