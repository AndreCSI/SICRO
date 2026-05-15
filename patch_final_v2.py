"""
patch_final_v2.py — Tres correcoes:
1. Remove brasao+texto PCI/AP da toolbar
2. Bussola com UM N apenas
3. Ferramenta ativa com highlight visivel
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: REMOVE brasao da toolbar
# ══════════════════════════════════════════════
# Procura o bloco do brasao e remove
pattern = re.compile(
    r'\n        # ─── Brasao PCI/AP no rodape da toolbar ───\n'
    r'        try:\n'
    r'.+?'
    r'        except Exception:\n'
    r'            pass',
    re.DOTALL
)
n = len(pattern.findall(src))
src = pattern.sub('', src)
print(f"PATCH 1: removeu {n} bloco do brasao")

# ══════════════════════════════════════════════
# PATCH 2: Bussola — SEM letra N duplicada
# Procura QUALQUER versao do _bussola e substitui pela limpa
# ══════════════════════════════════════════════
pattern_bussola = re.compile(
    r'    def _bussola\(self, W, H\):\n'
    r'(?:        .+\n|\n)+?'
    r'(?=    def )',
    re.MULTILINE
)
bussola_nova = '''    def _bussola(self, W, H):
        """Bussola N no canto superior direito do canvas."""
        c = self.canvas
        cx = W - 38
        cy = 42
        r = 22
        # Circulo de fundo
        c.create_oval(cx-r, cy-r, cx+r, cy+r,
                      fill=FUNDO_PAINEL, outline=AZUL_BORDA, width=1)
        # Seta dourada apontando para cima
        c.create_polygon(cx, cy-r+6,
                         cx-7, cy+3,
                         cx+7, cy+3,
                         fill=DOURADO, outline="")
        # APENAS UM N — abaixo da seta
        c.create_text(cx, cy+r-7, text="N",
                      font=("Segoe UI", 9, "bold"),
                      fill=DOURADO)

'''

n_bussola = len(pattern_bussola.findall(src))
src = pattern_bussola.sub(bussola_nova, src)
print(f"PATCH 2: substituiu {n_bussola} versao da bussola")

# ══════════════════════════════════════════════
# PATCH 3: Ferramenta ativa com fundo visivel
# Vou DEBUGAR primeiro: imprimir o estado atual de _set_ferr
# ══════════════════════════════════════════════
print("\nVerificando _set_ferr atual...")
match = re.search(
    r"(    def _set_ferr\(self, ferr\):.*?)(    def )",
    src, re.DOTALL
)
if match:
    metodo = match.group(1)
    if "FUNDO_ATIVO" in metodo:
        print("  Codigo de ativacao visual JA EXISTE em _set_ferr")
    else:
        print("  Codigo de ativacao visual NAO existe em _set_ferr")

# Reescreve _set_ferr completo, sem confiar no estado anterior
pattern_set_ferr = re.compile(
    r'    def _set_ferr\(self, ferr\):\n'
    r'(?:        .+\n|\n)+?'
    r'(?=    def )',
    re.DOTALL
)

# Captura o metodo atual para preservar a logica de negocio
match = pattern_set_ferr.search(src)
if not match:
    print("ERRO: _set_ferr nao encontrado")
    raise SystemExit

metodo_atual = match.group(0)

# Pega so as linhas que NAO sao de visual (preserva logica de negocio)
linhas_negocio = []
for linha in metodo_atual.split("\n"):
    s = linha.strip()
    # Pula linhas relacionadas a visual antigo
    if any(x in linha for x in [
        "for ch, f in self.btns_ferr",
        "if not isinstance(f, tk.Frame)",
        "ativo = (ch == ferr)",
        "f._ativo = ativo",
        "if ativo:",
        "else:",
        "bg = FUNDO_ATIVO",
        "bg = FUNDO_PAINEL",
        "f.config(bg=bg)",
        "f._ind.config",
        "f._ico.config",
        "f._txt.config",
        "ind_cor = ",
        "fg = ",
    ]):
        continue
    linhas_negocio.append(linha)

# Reconstroi o metodo
prefixo = "    def _set_ferr(self, ferr):\n"
visual = '''        # ──── ATUALIZA VISUAL DA TOOLBAR ────
        for ch, f in self.btns_ferr.items():
            if not isinstance(f, tk.Frame):
                continue
            ativo = (ch == ferr)
            f._ativo = ativo
            if ativo:
                f.config(bg=FUNDO_ATIVO)
                f._ind.config(bg=DOURADO)
                f._ico.config(bg=FUNDO_ATIVO, fg=DOURADO)
                f._txt.config(bg=FUNDO_ATIVO, fg=TEXTO_PRIMARIO,
                              font=FONTE_SMALL_BOLD)
            else:
                f.config(bg=FUNDO_PAINEL)
                f._ind.config(bg=FUNDO_PAINEL)
                f._ico.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO)
                f._txt.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO,
                              font=FONTE_SMALL)
'''
# Junta tudo: prefixo + visual + corpo limpo
corpo_limpo = "\n".join(linhas_negocio[1:])  # pula o def... linha 0
novo_metodo = prefixo + visual + corpo_limpo

if not novo_metodo.endswith("\n"):
    novo_metodo += "\n"

src = pattern_set_ferr.sub(novo_metodo, src, count=1)
print("PATCH 3: _set_ferr reescrito com visual no inicio")

# Idem para _set_ferr_via
pattern_via = re.compile(
    r'    def _set_ferr_via\(self, ferr\):\n'
    r'(?:        .+\n|\n)+?'
    r'(?=    def )',
    re.DOTALL
)
match_via = pattern_via.search(src)
if match_via:
    metodo_via_atual = match_via.group(0)
    linhas_via = []
    for linha in metodo_via_atual.split("\n"):
        if any(x in linha for x in [
            "for ch, f in self.btns_via",
            "if not isinstance(f, tk.Frame)",
            "ativo = (ch == ferr)",
            "f._ativo = ativo",
            "if ativo:",
            "bg = FUNDO_ATIVO",
            "bg = FUNDO_PAINEL",
            "f.config(bg=bg)",
            "f._ind.config",
            "f._ico.config",
            "f._txt.config",
            "ind_cor = ",
        ]):
            continue
        linhas_via.append(linha)

    visual_via = '''        # ──── VISUAL TOOLBAR VIA ────
        for ch, f in self.btns_via.items():
            if not isinstance(f, tk.Frame):
                continue
            ativo = (ch == ferr)
            f._ativo = ativo
            if ativo:
                f.config(bg=FUNDO_ATIVO)
                f._ind.config(bg=DOURADO)
                f._ico.config(bg=FUNDO_ATIVO, fg=DOURADO)
                f._txt.config(bg=FUNDO_ATIVO, fg=TEXTO_PRIMARIO,
                              font=FONTE_SMALL_BOLD)
            else:
                f.config(bg=FUNDO_PAINEL)
                f._ind.config(bg=FUNDO_PAINEL)
                f._ico.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO)
                f._txt.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO,
                              font=FONTE_SMALL)
'''
    corpo_via_limpo = "\n".join(linhas_via[1:])
    novo_via = "    def _set_ferr_via(self, ferr):\n" + visual_via + corpo_via_limpo
    if not novo_via.endswith("\n"):
        novo_via += "\n"
    src = pattern_via.sub(novo_via, src, count=1)
    print("PATCH 3b: _set_ferr_via reescrito")

# Salva
editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO linha {e.lineno}: {e.msg}")
    linhas = src.split("\n")
    for i in range(max(0, e.lineno-3), min(len(linhas), e.lineno+3)):
        print(f"{i+1:4}: {linhas[i]}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("Revertido")
    raise SystemExit

print("\nRode: python main.py")
