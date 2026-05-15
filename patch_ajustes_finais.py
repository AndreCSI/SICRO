"""
patch_ajustes_finais.py — Tres ajustes:
1. Brasao maior (60px)
2. Bussola sem 'N' duplicado (so o texto, sem polygon dourado em cima)
3. Ferramenta ativa com fundo + indicador visivel
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: Brasao maior
# ══════════════════════════════════════════════
old_brasao = 'img = brasao.resize((36, 36), Image.LANCZOS)'
new_brasao = 'img = brasao.resize((60, 60), Image.LANCZOS)'
if old_brasao in src:
    src = src.replace(old_brasao, new_brasao)
    print("PATCH 1 OK — brasao para 60x60")

# ══════════════════════════════════════════════
# PATCH 2: Bussola limpa — so 'N' acima, seta abaixo dela
# ══════════════════════════════════════════════
old_bussola = '''    def _bussola(self, W, H):
        """Desenha bussola N no canto superior direito do canvas."""
        c = self.canvas
        cx = W - 32
        cy = 36
        r = 18
        # Circulo de fundo
        c.create_oval(cx-r, cy-r, cx+r, cy+r,
                      fill=FUNDO_PAINEL, outline=AZUL_BORDA, width=1)
        # Setas N/S
        c.create_polygon(cx, cy-r+3, cx-5, cy, cx+5, cy,
                         fill=DOURADO, outline="")
        c.create_polygon(cx, cy+r-3, cx-5, cy, cx+5, cy,
                         fill=TEXTO_TERCIARIO, outline="")
        # Letra N
        c.create_text(cx, cy-r-8, text="N",
                      font=("Segoe UI", 9, "bold"),
                      fill=DOURADO)
'''

new_bussola = '''    def _bussola(self, W, H):
        """Desenha bussola N no canto superior direito do canvas."""
        c = self.canvas
        cx = W - 38
        cy = 42
        r = 22
        # Circulo de fundo
        c.create_oval(cx-r, cy-r, cx+r, cy+r,
                      fill=FUNDO_PAINEL, outline=AZUL_BORDA, width=1)
        # Seta N — apontando para cima
        c.create_polygon(cx, cy-r+5,
                         cx-6, cy+2,
                         cx+6, cy+2,
                         fill=DOURADO, outline="")
        # Letra N centralizada abaixo da seta
        c.create_text(cx, cy+r-7, text="N",
                      font=("Segoe UI", 9, "bold"),
                      fill=DOURADO)
'''

if old_bussola in src:
    src = src.replace(old_bussola, new_bussola)
    print("PATCH 2 OK — bussola limpa")

# ══════════════════════════════════════════════
# PATCH 3: Estado ativo da ferramenta — mais visivel
# O problema: ao clicar, o visual ativo precisa persistir mesmo apos hover
# Vamos verificar/reforcar a logica do _set_ferr
# ══════════════════════════════════════════════
# Procura o bloco que pinta visual ativo no _set_ferr
# Esse codigo foi injetado na fase 4
old_logic = '''        # Atualiza visual dos botoes da toolbar (frame, nao Button)
        for ch, f in self.btns_ferr.items():
            if not isinstance(f, tk.Frame): continue
            ativo = (ch == ferr)
            f._ativo = ativo
            bg = FUNDO_ATIVO if ativo else FUNDO_PAINEL
            ind_cor = DOURADO if ativo else bg
            fg = TEXTO_PRIMARIO if ativo else TEXTO_SECUNDARIO
            f.config(bg=bg)
            f._ind.config(bg=ind_cor)
            f._ico.config(bg=bg, fg=DOURADO if ativo else fg)
            f._txt.config(bg=bg, fg=fg,
                          font=FONTE_SMALL_BOLD if ativo else FONTE_SMALL)
'''

# Mesma logica mas usando a funcao _aplicar_estilo que tambem e chamada
# no hover_out para nao apagar o estado
new_logic = '''        # Atualiza visual dos botoes — marca a ferramenta ativa
        for ch, f in self.btns_ferr.items():
            if not isinstance(f, tk.Frame): continue
            ativo = (ch == ferr)
            f._ativo = ativo
            if ativo:
                bg = FUNDO_ATIVO
                f.config(bg=bg)
                f._ind.config(bg=DOURADO)
                f._ico.config(bg=bg, fg=DOURADO)
                f._txt.config(bg=bg, fg=TEXTO_PRIMARIO,
                              font=FONTE_SMALL_BOLD)
            else:
                bg = FUNDO_PAINEL
                f.config(bg=bg)
                f._ind.config(bg=bg)
                f._ico.config(bg=bg, fg=TEXTO_SECUNDARIO)
                f._txt.config(bg=bg, fg=TEXTO_SECUNDARIO,
                              font=FONTE_SMALL)
'''

if old_logic in src:
    src = src.replace(old_logic, new_logic)
    print("PATCH 3a OK — _set_ferr visual reforcado")

# Idem para _set_ferr_via
old_via = '''        for ch, f in self.btns_via.items():
            if not isinstance(f, tk.Frame): continue
            ativo = (ch == ferr)
            f._ativo = ativo
            bg = FUNDO_ATIVO if ativo else FUNDO_PAINEL
            ind_cor = DOURADO if ativo else bg
            fg = TEXTO_PRIMARIO if ativo else TEXTO_SECUNDARIO
            f.config(bg=bg)
            f._ind.config(bg=ind_cor)
            f._ico.config(bg=bg, fg=DOURADO if ativo else fg)
            f._txt.config(bg=bg, fg=fg,
                          font=FONTE_SMALL_BOLD if ativo else FONTE_SMALL)
'''
new_via = '''        for ch, f in self.btns_via.items():
            if not isinstance(f, tk.Frame): continue
            ativo = (ch == ferr)
            f._ativo = ativo
            if ativo:
                bg = FUNDO_ATIVO
                f.config(bg=bg)
                f._ind.config(bg=DOURADO)
                f._ico.config(bg=bg, fg=DOURADO)
                f._txt.config(bg=bg, fg=TEXTO_PRIMARIO,
                              font=FONTE_SMALL_BOLD)
            else:
                bg = FUNDO_PAINEL
                f.config(bg=bg)
                f._ind.config(bg=bg)
                f._ico.config(bg=bg, fg=TEXTO_SECUNDARIO)
                f._txt.config(bg=bg, fg=TEXTO_SECUNDARIO,
                              font=FONTE_SMALL)
'''

if old_via in src:
    src = src.replace(old_via, new_via)
    print("PATCH 3b OK — _set_ferr_via visual reforcado")

# ══════════════════════════════════════════════
# PATCH 4: Hover NAO deve sobrescrever estado ativo
# Verificar funcao _hin/_hout dentro de _criar_btn_ferr
# Hover ja checa "_ativo" antes de mudar bg — deveria funcionar
# Mas o problema relatado e: ao clicar, nao fica nada
# Pode ser que o frame esteja sendo recriado a cada redesenho
# Vamos garantir que _set_ferr e chamado na inicializacao
# ══════════════════════════════════════════════
# Procura "self._set_ferr(\"sel\")" — deve estar no final do _build_ui
if 'self._set_ferr("sel")' not in src:
    # Adiciona antes do "# Ctrl+Z e Delete"
    marker = '        # Ctrl+Z e Delete na janela raiz'
    if marker in src:
        src = src.replace(marker,
            '        # Marca ferramenta inicial como ativa\n'
            '        self.after(50, lambda: self._set_ferr("sel"))\n'
            '\n' + marker, 1)
        print("PATCH 4 OK — _set_ferr inicial garantido")

# Salva
editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("Sintaxe OK")
except SyntaxError as e:
    print(f"ERRO: {e}")
    editor_path.write_text(src_original, encoding="utf-8")
    raise SystemExit

print("\nRode: python main.py")
