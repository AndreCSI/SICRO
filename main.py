"""
main_modular.py — Ponto de entrada usando a estrutura modular
TESTE: python main_modular.py
Se funcionar igual ao main.py, o main.py pode ser substituido.
O main.py original continua intacto ate confirmacao.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json, sys
from pathlib import Path

# Garante que a raiz esta no path
_raiz = Path(__file__).parent
if str(_raiz) not in sys.path:
    sys.path.insert(0, str(_raiz))

try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

# Imports dos modulos extraidos
from config import (
    COR_FUNDO, COR_SUCESSO,
    gerar_elementos_modelo,
)
from ui.splash       import SplashScreen
from ui.tela_inicial import TelaInicial
from ui.dialogo_caso import DialogoDadosCaso
from ui.editor_croqui import EditorCroqui
from popups.popup_modelo_via import PopupModeloVia


class TitleBar:
    """Barra de titulo customizada — substitui a barra padrao do Windows."""

    def __init__(self, janela, titulo="SICRO PCI/AP"):
        from tema import (
            FUNDO_PAINEL, DOURADO, TEXTO_PRIMARIO,
            TEXTO_TERCIARIO, FUNDO_HOVER
        )
        self._win = janela
        self._drag_x = 0
        self._drag_y = 0

        bar = tk.Frame(janela, bg=FUNDO_PAINEL, height=32)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Faixa dourada topo
        tk.Frame(janela, bg=DOURADO, height=4).pack(fill="x", side="top")
        # Reempacota: dourada em cima, bar embaixo
        bar.pack_forget()
        tk.Frame(janela, bg=DOURADO, height=4).pack(fill="x")
        bar = tk.Frame(janela, bg=FUNDO_PAINEL, height=32)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Logo + titulo
        esq = tk.Frame(bar, bg=FUNDO_PAINEL)
        esq.pack(side="left", padx=14, fill="y")
        tk.Label(esq, text="SICRO", font=("Segoe UI", 11, "bold"),
                 bg=FUNDO_PAINEL, fg=TEXTO_PRIMARIO).pack(side="left")
        tk.Label(esq, text="  Sistema de Croquis Periciais",
                 font=("Segoe UI", 8),
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack(side="left")
        # Data e instituicao no centro
        import datetime
        centro = tk.Frame(bar, bg=FUNDO_PAINEL)
        centro.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(centro,
                 text=f'Policia Cientifica do Amapa  |  '
                      f'{datetime.date.today().strftime("%d/%m/%Y")}',
                 font=("Segoe UI", 8),
                 bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO).pack()

        # Botoes de controle
        dir_ = tk.Frame(bar, bg=FUNDO_PAINEL)
        dir_.pack(side="right", fill="y")

        def _btn(parent, texto, cmd, hover_cor="#C42B2B", fg=TEXTO_PRIMARIO):
            b = tk.Button(parent, text=texto,
                          font=("Segoe UI", 11),
                          bg=FUNDO_PAINEL, fg=fg,
                          activebackground=hover_cor,
                          activeforeground=TEXTO_PRIMARIO,
                          relief="flat", bd=0,
                          padx=14, pady=4,
                          cursor="hand2",
                          command=cmd)
            b.pack(side="left", fill="y")
            return b

        _btn(dir_, "─", self._minimizar,  hover_cor=FUNDO_HOVER)
        self._btn_max = _btn(dir_, "□", self._maximizar, hover_cor=FUNDO_HOVER)
        _btn(dir_, "✕", self._fechar,     hover_cor="#C42B2B")

        # Drag para mover janela (so funciona fora do modo zoomed)
        for w in [bar, esq] + list(esq.winfo_children()):
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<B1-Motion>",       self._drag_move)
            w.bind("<Double-Button-1>", self._maximizar)

    def _drag_start(self, e):
        if self._win.state() == "zoomed": return
        self._drag_x = e.x_root - self._win.winfo_x()
        self._drag_y = e.y_root - self._win.winfo_y()

    def _drag_move(self, e):
        if self._win.state() == "zoomed": return
        self._win.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    def _minimizar(self):
        self._win.iconify()

    def _maximizar(self, event=None):
        if self._win.state() == "zoomed":
            self._win.state("normal")
            self._btn_max.config(text="□")
        else:
            self._win.state("zoomed")
            self._btn_max.config(text="❐")

    def _fechar(self):
        self._win.destroy()


class AppSicro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("SICRO PCI/AP — Policia Cientifica do Amapa")
        self.configure(bg=COR_FUNDO)
        self.state("zoomed")
        ttk.Style(self).theme_use("clam")
        # Remove barra de titulo padrao do Windows
        self.overrideredirect(True)
        # Barra de titulo customizada do SICRO
        self._titlebar = TitleBar(self)
        # Atalhos de teclado
        self.bind('<Escape>',  lambda e: self.state('normal'))
        self.bind('<F11>',     lambda e: self._titlebar._maximizar())
        self.bind('<Alt-F4>', lambda e: self.destroy())
        self._frame  = None
        self._brasao = None

        arq = Path(__file__).parent / "brasao_pci_ap.png"
        if PIL_OK:
            try:
                if arq.exists():
                    self._brasao = Image.open(arq).convert("RGBA")
            except Exception:
                pass

        splash = SplashScreen(self, img_brasao=self._brasao)
        self.update()
        self.after(4000, lambda: self._pos_splash(splash))

    def _pos_splash(self, splash):
        splash.fechar()
        self.deiconify()
        self.mostrar_inicio()

    def mostrar_inicio(self):
        self._trocar(TelaInicial(self,
                                  on_novo=self._novo,
                                  on_abrir=self._abrir,
                                  img_brasao=self._brasao))

    def _novo(self, modo):
        dlg = DialogoDadosCaso(self, modo=modo)
        self.wait_window(dlg)
        if not dlg.resultado:
            return

        img_drone = None
        if modo == "drone":
            if not PIL_OK:
                messagebox.showerror("Pillow", "pip install Pillow")
                return
            cam = filedialog.askopenfilename(
                title="Foto do drone (ja retificada)",
                filetypes=[("Imagens", "*.jpg *.jpeg *.png *.tif")])
            if not cam:
                return
            img_drone = Image.open(cam)

        popup = PopupModeloVia(self)
        self.wait_window(popup)
        res = popup.resultado or {"icone": "branco"}

        els = []
        if res.get("icone", "branco") != "branco":
            W = max(self.winfo_width(), 800)
            H = max(self.winfo_height(), 600)
            els = gerar_elementos_modelo(res["icone"], W, H)

        editor = EditorCroqui(self, dlg.resultado, modo=modo,
                              img_drone=img_drone, elementos_iniciais=els)
        self._trocar(editor)

    def _abrir(self, caminho):
        try:
            with open(caminho, encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return
        caso = {k: dados[k] for k in
                ("bo", "requisicao", "local", "municipio", "perito", "data")
                if k in dados}
        editor = EditorCroqui(self, caso,
                              modo=dados.get("modo", "zero"),
                              elementos_iniciais=dados.get("elementos", []))
        editor.calibrado = dados.get("calibrado", False)
        editor.k   = dados.get("k")
        editor.u_k = dados.get("u_k")
        if editor.calibrado and editor.k:
            editor.label_escala.config(
                text=f"k={editor.k*1000:.3f}mm/px",
                fg=COR_SUCESSO)
        editor._redesenhar()
        self._trocar(editor)

    def _trocar(self, novo):
        if self._frame:
            self._frame.destroy()
        self._frame = novo
        novo.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = AppSicro()
    app.mainloop()