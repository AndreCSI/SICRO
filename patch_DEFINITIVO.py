"""
patch_DEFINITIVO.py — Corrige os 3 problemas usando assinaturas REAIS
1. Remove chamada self._norte() (N duplicado) — mantem so _bussola
2. _set_ferr(self, c) ganha codigo de visual da toolbar ativa
3. Remove brasao da toolbar
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: Remove a chamada self._norte(...) do _redesenhar
# Mantem apenas self._bussola(W, H)
# ══════════════════════════════════════════════
# A L1933-1934 tem: self._norte(W-40,40) \n self._rodape(W,H) \n self._bussola(W,H)
# Remove so a linha self._norte(...)
m = re.search(r'\n\s*self\._norte\(W-40,40\)', src)
if m:
    src = src[:m.start()] + src[m.end():]
    print("PATCH 1 OK — chamada self._norte() removida (N duplicado eliminado)")
else:
    # Tenta variantes
    m = re.search(r'\n\s*self\._norte\([^)]*\)', src)
    if m:
        src = src[:m.start()] + src[m.end():]
        print("PATCH 1 OK — self._norte() removido (variante)")
    else:
        print("PATCH 1 SKIP — self._norte nao encontrado")

# ══════════════════════════════════════════════
# PATCH 2: _set_ferr(self, c) — adiciona visual da toolbar
# Assinatura REAL: def _set_ferr(self, c):
# ══════════════════════════════════════════════
old_set_ferr = '''    def _set_ferr(self, c):
        self.ferramenta = c
        if c == "calibrar" and self.modo == "zero":
            messagebox.showinfo("Calibração","Disponível apenas no modo drone.")
            self._set_ferr("sel")'''

new_set_ferr = '''    def _set_ferr(self, c):
        self.ferramenta = c
        if c == "calibrar" and self.modo == "zero":
            messagebox.showinfo("Calibração","Disponível apenas no modo drone.")
            self._set_ferr("sel")
            return
        # ──── VISUAL: marca ferramenta ativa na toolbar ────
        if hasattr(self, "btns_ferr"):
            for ch, fr in self.btns_ferr.items():
                if not isinstance(fr, tk.Frame):
                    continue
                ativo = (ch == c)
                fr._ativo = ativo
                if ativo:
                    fr.config(bg=FUNDO_ATIVO)
                    fr._ind.config(bg=DOURADO)
                    fr._ico.config(bg=FUNDO_ATIVO, fg=DOURADO)
                    fr._txt.config(bg=FUNDO_ATIVO, fg=TEXTO_PRIMARIO,
                                   font=FONTE_SMALL_BOLD)
                else:
                    fr.config(bg=FUNDO_PAINEL)
                    fr._ind.config(bg=FUNDO_PAINEL)
                    fr._ico.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO)
                    fr._txt.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO,
                                   font=FONTE_SMALL)
        # Desmarca botoes de via quando usa ferramenta normal
        if hasattr(self, "btns_via"):
            for ch, fr in self.btns_via.items():
                if not isinstance(fr, tk.Frame):
                    continue
                fr._ativo = False
                fr.config(bg=FUNDO_PAINEL)
                fr._ind.config(bg=FUNDO_PAINEL)
                fr._ico.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO)
                fr._txt.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO,
                               font=FONTE_SMALL)'''

if old_set_ferr in src:
    src = src.replace(old_set_ferr, new_set_ferr, 1)
    print("PATCH 2 OK — _set_ferr agora pinta toolbar ativa")
else:
    print("PATCH 2 ERRO — _set_ferr nao bate exatamente")
    # Mostra o que tem
    m = re.search(r"    def _set_ferr\(self, c\):.*?(?=\n    def |\n    #)", src, re.DOTALL)
    if m:
        print("  Conteudo atual:")
        for l in m.group(0).split("\n"):
            print(f"    |{l}")

# ══════════════════════════════════════════════
# PATCH 3: _set_ferr_via(self, f) — adiciona visual tambem
# Assinatura REAL: def _set_ferr_via(self, f):
# ══════════════════════════════════════════════
old_via = '''    def _set_ferr_via(self, f):
        """Define ferramenta no modo via."""
        self._ferr_via = f
        dica = next((d for ch,i,d in FERRAMENTAS_VIA if ch==f), f)
        self.status.config(text=f"🛣 Via: {dica}  — clique e arraste")'''

new_via = '''    def _set_ferr_via(self, f):
        """Define ferramenta no modo via."""
        self._ferr_via = f
        dica = next((d for ch,i,d in FERRAMENTAS_VIA if ch==f), f)
        self.status.config(text=f"🛣 Via: {dica}  — clique e arraste")
        # Visual: marca ativo nos botoes de via
        if hasattr(self, "btns_via"):
            for ch, fr in self.btns_via.items():
                if not isinstance(fr, tk.Frame):
                    continue
                ativo = (ch == f)
                fr._ativo = ativo
                if ativo:
                    fr.config(bg=FUNDO_ATIVO)
                    fr._ind.config(bg=DOURADO)
                    fr._ico.config(bg=FUNDO_ATIVO, fg=DOURADO)
                    fr._txt.config(bg=FUNDO_ATIVO, fg=TEXTO_PRIMARIO,
                                   font=FONTE_SMALL_BOLD)
                else:
                    fr.config(bg=FUNDO_PAINEL)
                    fr._ind.config(bg=FUNDO_PAINEL)
                    fr._ico.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO)
                    fr._txt.config(bg=FUNDO_PAINEL, fg=TEXTO_SECUNDARIO,
                                   font=FONTE_SMALL)'''

if old_via in src:
    src = src.replace(old_via, new_via, 1)
    print("PATCH 3 OK — _set_ferr_via pinta ativo")
else:
    print("PATCH 3 SKIP — _set_ferr_via formato diferente")

# ══════════════════════════════════════════════
# PATCH 4: Remove o bloco do brasao da toolbar
# ══════════════════════════════════════════════
pat_brasao = re.compile(
    r'\n\s*# ─── Brasao PCI/AP no rodape da toolbar ───\n'
    r'\s*try:\n'
    r'.+?'
    r'\s*except Exception:\n'
    r'\s*pass',
    re.DOTALL
)
n = len(pat_brasao.findall(src))
if n:
    src = pat_brasao.sub('', src)
    print(f"PATCH 4 OK — {n} bloco do brasao removido")
else:
    print("PATCH 4 SKIP — brasao nao encontrado pelo padrao")

# ══════════════════════════════════════════════
# PATCH 5: Garante _set_ferr("sel") apos toolbar criada
# Ja existe na L1131/1415/1428 — verificar se ha um apos _build
# Adiciona um after() no final do _build_ui se nao houver
# ══════════════════════════════════════════════
# Procura final do _build_ui (antes do proximo def) e injeta after
if 'self.after(60, lambda: self._set_ferr("sel"))' not in src:
    # Acha "self._set_ferr(\"sel\")" dentro do build inicial
    # Adiciona um reforço com after para garantir que pinta apos toolbar pronta
    m = re.search(r'(\n        self\._set_ferr\("sel"\)\n)', src)
    if m:
        src = src[:m.end()] + '        self.after(60, lambda: self._set_ferr("sel"))\n' + src[m.end():]
        print("PATCH 5 OK — reforco after _set_ferr(sel)")

# ══════════════════════════════════════════════
# Salva e valida
# ══════════════════════════════════════════════
editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\n✓ Sintaxe OK")
except SyntaxError as e:
    print(f"\n✗ ERRO linha {e.lineno}: {e.msg}")
    linhas = src.split("\n")
    for i in range(max(0,e.lineno-4), min(len(linhas),e.lineno+3)):
        print(f"  {i+1:4}: {linhas[i]}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO — nada foi alterado")
    raise SystemExit

print("\nRode: python main.py")
print("Esperado:")
print("  - Bussola com UM N so")
print("  - Sem brasao na toolbar")
print("  - Clicar ferramenta: fundo azul + barra dourada + texto branco bold")
