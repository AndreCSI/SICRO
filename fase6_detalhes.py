"""
fase6_detalhes.py — Detalhes finais do editor
1. Bussola N no canto superior direito do canvas
2. Brasao PCI/AP no rodape da toolbar
3. Remove label orfao "BO . data . Perito" do canvas
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# PATCH 1: Neutraliza _rodape (label "BO · data · Perito" no canvas)
# Agora essa info esta no header novo, nao precisa duplicar
# ══════════════════════════════════════════════
old_rodape = '''    def _rodape(self,W,H):
        c=self.canvas
        perito=self.dados_caso.get("perito","")
        bo=self.dados_caso.get("bo","")
        data=self.dados_caso.get("data","")
        c.create_rectangle(0,H-22,W,H,fill=COR_PAINEL,outline="")
        c.create_line(0,H-22,W,H-22,fill=AMARELO,width=1)
        c.create_text(W//2,H-11,
                      text=f"BO {bo}  ·  {data}  ·  Perito: {perito}",
                      fill=CINZA_CLARO,font=FONTE_PEQ)
'''

new_rodape = '''    def _rodape(self, W, H):
        """Rodape do canvas — info do BO ja esta no header novo."""
        pass

    def _bussola(self, W, H):
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

if old_rodape in src:
    src = src.replace(old_rodape, new_rodape, 1)
    print("PATCH 1 OK — _rodape neutralizado, _bussola adicionada")
else:
    print("PATCH 1 SKIP — _rodape antigo nao encontrado")

# ══════════════════════════════════════════════
# PATCH 2: chama _bussola no _redesenhar logo apos _rodape
# Procura "self._rodape(W,H)" ou "self._rodape(W, H)"
# ══════════════════════════════════════════════
padroes_rodape = [
    "self._rodape(W,H)",
    "self._rodape(W, H)",
]
n_chamadas = 0
for p in padroes_rodape:
    if p in src:
        nova = p + "\n        self._bussola(W, H)"
        src = src.replace(p, nova)
        n_chamadas += 1

print(f"PATCH 2 OK — {n_chamadas} chamadas de _bussola adicionadas")

# ══════════════════════════════════════════════
# PATCH 3: Brasao PCI/AP no rodape da toolbar
# Adiciona no final do bloco da toolbar
# ══════════════════════════════════════════════
# Procura "self._btn_modo_via = tk.Frame" — o ultimo elemento da toolbar
# Depois desse bloco vamos adicionar o brasao

# Procura final do bloco de Modo Via
ancora = '''        for w in [self._btn_modo_via] + list(self._btn_modo_via.winfo_children()):
            w.bind("<Button-1>", lambda e: self._toggle_modo_via())
            w.bind("<Enter>", lambda e: hasattr(self, "status") and
                   self.status.config(text="Editor de Via — alterna modo arte"))'''

adicao = '''

        # ─── Brasao PCI/AP no rodape da toolbar ───
        try:
            app = self.winfo_toplevel()
            brasao = getattr(app, "_brasao", None)
            if brasao is not None:
                from PIL import Image, ImageTk
                img = brasao.resize((36, 36), Image.LANCZOS)
                self._brasao_tk = ImageTk.PhotoImage(img)
                bf = tk.Frame(inner, bg=FUNDO_PAINEL)
                bf.pack(side="bottom", pady=10)
                tk.Label(bf, image=self._brasao_tk,
                         bg=FUNDO_PAINEL).pack()
                tk.Label(bf, text="PCI/AP",
                         font=FONTE_MICRO,
                         bg=FUNDO_PAINEL,
                         fg=DOURADO).pack(pady=(2,0))
        except Exception:
            pass'''

if ancora in src and "_brasao_tk" not in src:
    src = src.replace(ancora, ancora + adicao, 1)
    print("PATCH 3 OK — brasao adicionado na toolbar")
else:
    print("PATCH 3 SKIP — ja existe ou ancora nao encontrada")

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
print("  2. Bussola N no canto superior direito do canvas")
print("  3. Brasao PCI/AP no rodape da toolbar esquerda")
print("  4. Aquele label 'BO · data · Perito' antigo deve ter sumido do canvas")
