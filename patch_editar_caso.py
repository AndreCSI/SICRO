"""
patch_editar_caso.py — Adiciona metodo _editar_caso ao EditorCroqui
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")

if "_editar_caso" in src and "def _editar_caso" in src:
    print("Metodo _editar_caso ja existe — abortando")
    raise SystemExit

# Procura QUALQUER metodo da classe EditorCroqui para inserir antes
# Padrao: "    def _" precedido por uma linha em branco
match = re.search(r"\n(    def _salvar\b)", src)
if not match:
    match = re.search(r"\n(    def _exportar_pdf\b)", src)
if not match:
    match = re.search(r"\n(    def _voltar\b)", src)
if not match:
    # Fallback: insere depois do _build_ui — procura proximo "    def "
    idx = src.find("    def _build_ui(self):")
    if idx > 0:
        # Acha proximo "\n    def " apos _build_ui
        match = re.search(r"\n    def \w+\(self", src[idx + 100:])
        if match:
            insert_at = idx + 100 + match.start() + 1
        else:
            insert_at = -1
    else:
        insert_at = -1
else:
    insert_at = match.start() + 1

if insert_at < 0:
    print("ERRO: nao encontrei lugar para inserir")
    raise SystemExit

metodo = '''    def _editar_caso(self, campo):
        """Permite editar BO ou local inline via simpledialog."""
        from tkinter import simpledialog
        valor_atual = self.dados_caso.get(campo, "")
        labels = {"bo": "Numero do BO:", "local": "Local da ocorrencia:"}
        novo = simpledialog.askstring(
            "Editar " + campo,
            labels.get(campo, campo + ":"),
            initialvalue=valor_atual,
            parent=self.winfo_toplevel())
        if novo is not None and novo.strip():
            self.dados_caso[campo] = novo.strip()
            if campo == "bo":
                self._lbl_bo.config(text=f"BO {novo.strip()}")
            elif campo == "local":
                self._lbl_local.config(text=novo.strip())

'''

src_novo = src[:insert_at] + metodo + src[insert_at:]

# Valida antes de salvar
try:
    ast.parse(src_novo)
    editor_path.write_text(src_novo, encoding="utf-8")
    print("OK — _editar_caso adicionado")
    # Confirma posicao
    linhas_antes = src[:insert_at].count("\n") + 1
    print(f"Inserido na linha ~{linhas_antes}")
except SyntaxError as e:
    print(f"ERRO sintaxe: {e}")

print("\nRode: python main.py")
