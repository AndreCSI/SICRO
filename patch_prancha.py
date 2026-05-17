"""
patch_prancha.py — Substitui _exportar_pdf por exportacao de prancha
(PDF + PNG), captura o croqui inteiro (zoom total antes), restaura estado.
Requer: arquivo/prancha.py instalado.
"""
from pathlib import Path
import ast, re

if not (Path("arquivo")/"prancha.py").exists():
    print("ATENCAO: arquivo/prancha.py NAO encontrado.")
    print("Baixe prancha.py e coloque em arquivo/ antes deste patch.")
    raise SystemExit

ep = Path("ui")/"editor_croqui.py"
src = ep.read_text(encoding="utf-8")
src_orig = src

# Localiza _exportar_pdf inteiro e substitui
m = re.search(r"    def _exportar_pdf\(self\):.*?(?=\n    def )", src, re.DOTALL)
if not m:
    print("ERRO: _exportar_pdf nao encontrado")
    raise SystemExit

novo_metodo = '''    def _exportar_pdf(self):
        """Exporta a prancha pericial em PDF ou PNG."""
        if not PIL_OK:
            messagebox.showerror("Pillow", "pip install Pillow")
            return
        # Pergunta o formato
        win = tk.Toplevel(self)
        win.overrideredirect(True)
        win.configure(bg=FUNDO_PAINEL,
                      highlightbackground=DOURADO, highlightthickness=1)
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        ww, wh = 320, 170
        win.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")
        win.grab_set(); win.attributes("-topmost", True)
        tk.Frame(win, bg=DOURADO, height=3).pack(fill="x")
        tk.Label(win, text="Exportar prancha pericial",
                 font=FONTE_H3, bg=FUNDO_PAINEL,
                 fg=TEXTO_PRIMARIO).pack(pady=(16, 4))
        tk.Label(win, text="Escolha o formato do documento:",
                 font=FONTE_SMALL, bg=FUNDO_PAINEL,
                 fg=TEXTO_SECUNDARIO).pack(pady=(0, 12))
        escolha = {"fmt": None}
        bf = tk.Frame(win, bg=FUNDO_PAINEL); bf.pack()
        def _pick(f):
            escolha["fmt"] = f; win.destroy()
        for txt, fmt, cor in (("PDF", "pdf", AZUL_MEDIO),
                              ("PNG", "png", FUNDO_CARD)):
            b = tk.Frame(bf, bg=cor, cursor="hand2")
            b.pack(side="left", padx=8)
            lb = tk.Label(b, text=txt, font=FONTE_BODY_BOLD,
                          bg=cor, fg=TEXTO_PRIMARIO, padx=26, pady=9)
            lb.pack()
            for w in (b, lb):
                w.bind("<Button-1>", lambda e, f=fmt: _pick(f))
        tk.Label(win, text="Esc para cancelar", font=FONTE_MICRO,
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(pady=(12, 0))
        win.bind("<Escape>", lambda e: win.destroy())
        self.wait_window(win)
        fmt = escolha["fmt"]
        if not fmt:
            return

        ext = ".pdf" if fmt == "pdf" else ".png"
        bo = self.dados_caso.get("bo", "").replace("/", "_")
        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[(fmt.upper(), f"*{ext}")],
            initialfile=f"Prancha_BO_{bo}{ext}")
        if not path:
            return

        # Captura o croqui INTEIRO: salva estado, da zoom total
        z0, px0, py0 = self.zoom, self.pan_x, self.pan_y
        try:
            self._enquadrar_tudo()
        except Exception:
            pass
        self.update_idletasks()
        self.canvas.update()

        img_croqui = None
        try:
            from PIL import ImageGrab
            x0 = self.canvas.winfo_rootx()
            y0 = self.canvas.winfo_rooty()
            x1 = x0 + self.canvas.winfo_width()
            y1 = y0 + self.canvas.winfo_height()
            img_croqui = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        except Exception as e:
            messagebox.showwarning("Captura",
                f"Nao foi possivel capturar o croqui: {e}")

        # Restaura estado do canvas
        self.zoom, self.pan_x, self.pan_y = z0, px0, py0
        self._redesenhar()

        # Brasao (do app principal)
        brasao = getattr(self.winfo_toplevel(), "_brasao", None)

        try:
            from arquivo.prancha import gerar_prancha
            gerar_prancha(path, fmt, self.dados_caso, self.elementos,
                          img_croqui, self.calibrado, self.k,
                          self.u_k, brasao)
        except ImportError as e:
            messagebox.showerror("Dependencia",
                f"Falta biblioteca: {e}\\n\\nPara PDF: pip install reportlab")
            return
        except Exception as e:
            messagebox.showerror("Erro ao gerar", str(e))
            return
        messagebox.showinfo("Prancha exportada",
            f"Documento salvo:\\n{path}")
'''

src = src[:m.start()] + novo_metodo + src[m.end():]

# Adiciona _enquadrar_tudo se nao existir
if "def _enquadrar_tudo" not in src:
    helper = '''    def _enquadrar_tudo(self):
        """Ajusta zoom/pan para mostrar todos os elementos (para captura)."""
        pts = []
        for el in self.elementos:
            for kx, ky in (("x","y"), ("x2","y2")):
                if kx in el and ky in el:
                    pts.append((el[kx], el[ky]))
        if not pts:
            return
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        marg = 60
        bw = max(1, maxx - minx); bh = max(1, maxy - miny)
        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        z = min((cw - 2*marg)/bw, (ch - 2*marg)/bh)
        z = max(0.1, min(10.0, z))
        self.zoom = z
        cx_m = (minx + maxx)/2
        cy_m = (miny + maxy)/2
        self.pan_x = cw/2 - cx_m*z
        self.pan_y = ch/2 - cy_m*z
        self._redesenhar()

'''
    idx = src.find("    def _exportar_pdf(self):")
    src = src[:idx] + helper + src[idx:]
    print("Helper _enquadrar_tudo adicionado")

ep.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("Sintaxe editor_croqui.py OK")
except SyntaxError as e:
    print(f"ERRO {e.lineno}: {e.msg}")
    linhas = src.split("\n")
    for i in range(max(0,e.lineno-4), min(len(linhas),e.lineno+3)):
        print(f"  {i+1:4}: {linhas[i]}")
    ep.write_text(src_orig, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste:")
print("  1. Monte um croqui com veiculos (V1,V2) e cotas")
print("  2. Botao PDF -> escolhe PDF ou PNG")
print("  3. Prancha gerada: cabecalho + croqui inteiro + legenda + distancias")
