"""
patch_props_completo.py — Finaliza R1/R2/Cota editaveis + botao Exportar
1. Botao "PDF" -> "Exportar"
2. Painel: campos Espessura + Cor para r1/r2/cota
3. Desenho R1/R2 le el["cor"]
4. Desenho Cota le el["cor"] e el["espessura"]
"""
from pathlib import Path
import ast

ep = Path("ui")/"editor_croqui.py"
src = ep.read_text(encoding="utf-8")
src_orig = src

# ── 1. Botao PDF -> Exportar ──
old_btn = '_btn_header(dir_, "📄", "PDF",    self._exportar_pdf)'
new_btn = '_btn_header(dir_, "📄", "Exportar", self._exportar_pdf)'
if old_btn in src:
    src = src.replace(old_btn, new_btn, 1)
    print("1 OK — botao Exportar")
else:
    print("1 ERRO — botao PDF nao bate"); raise SystemExit

# ── 2. Painel: Espessura + Cor para r1/r2/cota ──
anchor = '''        # Cor (com seletor)
        if el.get("cor"):'''
novo = '''        # Espessura — linhas R1/R2 e Cota
        if el["tipo"] in ("r1", "r2", "cota"):
            _esp_def = {"r1": 2, "r2": 2, "cota": 1}.get(el["tipo"], 2)
            def set_esp(v):
                el["espessura"] = max(1, int(float(v)))
            _campo("Espessura (px)",
                   str(el.get("espessura", _esp_def)), set_esp)

        # Cor default para r1/r2/cota (para o seletor aparecer)
        if el["tipo"] in ("r1", "r2", "cota") and not el.get("cor"):
            el["cor"] = {"r1": COR_R1, "r2": COR_R2,
                         "cota": COR_COTA}.get(el["tipo"], "#888888")

        # Cor (com seletor)
        if el.get("cor"):'''
if anchor in src:
    src = src.replace(anchor, novo, 1)
    print("2 OK — Espessura + Cor no painel")
else:
    print("2 ERRO — ancora Cor nao bate"); raise SystemExit

# ── 3. Desenho R1/R2 respeita el["cor"] ──
old_r = 'cor_eixo  = COR_R1 if tipo=="r1" else COR_R2'
new_r = 'cor_eixo  = el.get("cor", COR_R1 if tipo=="r1" else COR_R2)'
if old_r in src:
    src = src.replace(old_r, new_r, 1)
    print("3 OK — R1/R2 le el[cor]")
else:
    print("3 ERRO — linha cor_eixo nao bate"); raise SystemExit

# ── 4. Desenho Cota respeita el["cor"] e el["espessura"] ──
old_c = '''            c.create_line(tx,ty,tx2,ty2,fill=COR_COTA,width=1,
                          arrow="both",arrowshape=(6,8,3))
            c.create_text((tx+tx2)/2,(ty+ty2)/2-8,text=label,
                          fill=COR_COTA,font=FONTE_MONO,anchor="s"); return'''
new_c = '''            _cc = el.get("cor", COR_COTA)
            _ce = max(1, int(el.get("espessura", 1)))
            c.create_line(tx,ty,tx2,ty2,fill=_cc,width=_ce,
                          arrow="both",arrowshape=(6,8,3))
            c.create_text((tx+tx2)/2,(ty+ty2)/2-8,text=label,
                          fill=_cc,font=FONTE_MONO,anchor="s"); return'''
if old_c in src:
    src = src.replace(old_c, new_c, 1)
    print("4 OK — Cota le el[cor] e el[espessura]")
else:
    print("4 ERRO — desenho cota nao bate"); raise SystemExit

ep.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO {e.lineno}: {e.msg}")
    ln=src.split("\n")
    for i in range(max(0,e.lineno-4),min(len(ln),e.lineno+3)):
        print(f"  {i+1:4}: {ln[i]}")
    ep.write_text(src_orig, encoding="utf-8")
    print("REVERTIDO"); raise SystemExit

print("\nRode: python main.py")
print("Teste completo:")
print("  1. Header diz 'Exportar'")
print("  2. R1: selecione -> Espessura + Cor -> mude -> linha muda")
print("  3. R2: idem")
print("  4. Cota: Rotulo + Pos X/Y + Espessura + Cor -> tudo aplica")
