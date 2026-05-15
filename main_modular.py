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


class AppSicro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("SICRO PCI/AP — Policia Cientifica do Amapa")
        self.configure(bg=COR_FUNDO)
        self.state("zoomed")
        ttk.Style(self).theme_use("clam")
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