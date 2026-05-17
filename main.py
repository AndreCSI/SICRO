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
from ui.cropador import CropadorImagem
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
        # iconify nao funciona com overrideredirect — usa withdraw
        # mas precisa de uma janela fantasma na taskbar para restaurar
        self._win.overrideredirect(False)
        self._win.iconify()
        # Quando user clica na taskbar, restaura
        self._win.bind('<Map>', self._restaurar_de_minimizar)

    def _restaurar_de_minimizar(self, event=None):
        if self._win.state() != 'iconic':
            self._win.overrideredirect(True)
            self._win.unbind('<Map>')

    def _maximizar(self, event=None):
        if getattr(self._win, '_maximizado', False):
            # Restaura tamanho anterior
            self._win.geometry(self._win._geo_anterior)
            self._win._maximizado = False
            self._btn_max.config(text="□")
        else:
            # Salva geometria atual antes de maximizar
            self._win._geo_anterior = self._win.geometry()
            # Tamanho da tela menos taskbar (48px)
            sw = self._win.winfo_screenwidth()
            sh = self._win.winfo_screenheight() - 48
            self._win.geometry(f'{sw}x{sh}+0+0')
            self._win._maximizado = True
            self._btn_max.config(text="❐")
        self._win.after(50, lambda: self._win.overrideredirect(True))

    def _fechar(self):
        self._win.destroy()


class AppSicro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("SICRO PCI/AP — Policia Cientifica do Amapa")
        self.configure(bg=COR_FUNDO)
        ttk.Style(self).theme_use("clam")
        # Tamanho fixo inicial — confortavel para qualquer monitor
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w_inicial = min(1400, sw - 100)
        h_inicial = min(800,  sh - 100)
        x = (sw - w_inicial) // 2
        y = (sh - h_inicial) // 2
        self.geometry(f'{w_inicial}x{h_inicial}+{x}+{y}')
        self.update_idletasks()
        self.overrideredirect(True)
        self.after(10, self._setup_taskbar)
        # Estado: NAO maximizado (icone do botao = □)
        self._geo_anterior = f'{w_inicial}x{h_inicial}+{x}+{y}'
        self._maximizado = False
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

    def _setup_taskbar(self):
        """Garante presenca na taskbar com overrideredirect."""
        try:
            self.wm_attributes('-toolwindow', False)
        except Exception:
            pass

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
        # modo: "zero" (manual), "drone", "modelo"
        usar_modelo = (modo == "modelo")
        modo_editor = "drone" if modo == "drone" else "zero"

        dlg = DialogoDadosCaso(self, modo=modo_editor)
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
            img_orig = Image.open(cam)
            # Ferramenta de recorte: foca na area do acidente,
            # reduz resolucao e deixa o trabalho mais fluido
            crop = CropadorImagem(self, img_orig)
            self.wait_window(crop)
            if crop.resultado is None:
                return   # usuario cancelou o recorte
            img_drone = crop.resultado

        els = []
        if usar_modelo:
            # Vai DIRETO para a grade de modelos (sem pergunta redundante)
            from popups.popup_modelo_via import GridModelos
            grid = GridModelos(self)
            self.wait_window(grid)
            if not grid.resultado:
                return
            icone = grid.resultado.get("icone", "branco")
            if icone != "branco":
                W = max(self.winfo_width(), 800)
                H = max(self.winfo_height(), 600)
                els = gerar_elementos_modelo(icone, W, H)

        editor = EditorCroqui(self, dlg.resultado, modo=modo_editor,
                              img_drone=img_drone, elementos_iniciais=els)
        self._trocar(editor)

    def _abrir(self, caminho):
        import base64, io
        try:
            with open(caminho, encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return
        if dados.get("versao_sicro") != "1.0":
            messagebox.showerror("Formato incompativel",
                "Este arquivo nao esta no formato .sicro 1.0.")
            return
        meta = dados.get("metadata", {})
        cfg  = dados.get("config", {})
        caso = {k: meta.get(k, "") for k in
                ("bo", "requisicao", "local", "municipio", "perito", "data")}
        # Reconstroi imagem do drone do base64
        img_drone = None
        ib = dados.get("imagem_base", {})
        if ib.get("presente") and ib.get("dados_b64") and PIL_OK:
            try:
                raw = base64.b64decode(ib["dados_b64"])
                img_drone = Image.open(io.BytesIO(raw)).convert("RGBA")
            except Exception as e:
                messagebox.showwarning("Imagem",
                    f"Falha ao carregar imagem embutida: {e}")
        editor = EditorCroqui(self, caso,
                              modo=cfg.get("modo", "zero"),
                              img_drone=img_drone,
                              elementos_iniciais=dados.get("elementos", []))
        editor.calibrado = cfg.get("calibrado", False)
        editor.k   = cfg.get("k")
        editor.u_k = cfg.get("u_k")
        editor.norte_angulo = cfg.get("norte_angulo", 0)
        editor._criado_em = meta.get("criado_em")
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