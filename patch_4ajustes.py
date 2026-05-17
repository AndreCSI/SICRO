"""
patch_4ajustes.py
1. Remove popup "Identificacao (V1)" ao inserir veiculo (auto-gera)
2. FERRAMENTAS: nomes Carro/Motocicleta/Caminhao/Bicicleta
3. Label da toolbar nao corta mais no "—"
4. messagebox Voltar/Salvo: mantem (sao do tkinter, dificil estilizar
   sem reescrever — faremos popup custom so se quiser depois)
"""
from pathlib import Path
import ast

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")
src_original = src

# ══════════════════════════════════════════════
# AJUSTE 1: Remove o popup de Identificacao — auto-gera o label
# ══════════════════════════════════════════════
old_id = '''        if tipo in ("carro","moto","caminhao","bicicleta","pedestre"):
            n=sum(1 for e in self.elementos if e["tipo"]==tipo)+1
            sig={"carro":"V","moto":"V","caminhao":"V","bicicleta":"B","pedestre":"P"}
            label=simpledialog.askstring(
                "Identificação","Identificação (ex: V1 — FIORINO):",
                initialvalue=f"{sig[tipo]}{n}",
                parent=self.winfo_toplevel()) or f"{sig[tipo]}{n}"
        elif tipo=="texto":'''

new_id = '''        if tipo in ("carro","moto","caminhao","bicicleta","pedestre"):
            n=sum(1 for e in self.elementos if e["tipo"]==tipo)+1
            sig={"carro":"V","moto":"V","caminhao":"V","bicicleta":"B","pedestre":"P"}
            # Auto-gera o rotulo — editavel depois no painel Propriedades
            label=f"{sig[tipo]}{n}"
        elif tipo=="texto":'''

if old_id in src:
    src = src.replace(old_id, new_id, 1)
    print("AJUSTE 1 OK — popup Identificacao removido")
else:
    print("AJUSTE 1 ERRO — bloco nao bate")
    raise SystemExit

# ══════════════════════════════════════════════
# AJUSTE 1b: Remove o DialogoRedimensionar automatico ao inserir
# (agora temos handles + painel propriedades, nao precisa do dialogo)
# ══════════════════════════════════════════════
old_dlg = '''        # Abre automaticamente o diálogo de ajuste
        if tipo in ("carro","moto","caminhao","bicicleta","pedestre","sc"):
            dlg=DialogoRedimensionar(self.winfo_toplevel(),el,self._redesenhar)
            self.winfo_toplevel().wait_window(dlg)
            self._atualizar_camadas()
            self._redesenhar()
        elif tipo == "texto":
            # Abre editor de texto inline
            self._abrir_editor_texto(el)'''

new_dlg = '''        # Veiculos: ajuste direto pelos handles/painel (sem dialogo)
        if tipo == "texto":
            # Abre editor de texto inline
            self._abrir_editor_texto(el)'''

if old_dlg in src:
    src = src.replace(old_dlg, new_dlg, 1)
    print("AJUSTE 1b OK — DialogoRedimensionar automatico removido")
else:
    print("AJUSTE 1b SKIP — bloco nao encontrado (ok se ja removido)")

# ══════════════════════════════════════════════
# AJUSTE 2: FERRAMENTAS — nomes corretos
# ══════════════════════════════════════════════
old_ferr = '''        ("carro",     "🚗", "Veículo — carro"),
        ("moto",      "🏍", "Veículo — moto"),
        ("caminhao",  "🚚", "Veículo — caminhão"),
        ("bicicleta", "🚲", "Veículo — bicicleta"),'''
new_ferr = '''        ("carro",     "🚗", "Carro"),
        ("moto",      "🏍", "Motocicleta"),
        ("caminhao",  "🚚", "Caminhão"),
        ("bicicleta", "🚲", "Bicicleta"),'''

if old_ferr in src:
    src = src.replace(old_ferr, new_ferr, 1)
    print("AJUSTE 2 OK — nomes das ferramentas corrigidos")
else:
    print("AJUSTE 2 ERRO — FERRAMENTAS nao bate")
    raise SystemExit

# ══════════════════════════════════════════════
# AJUSTE 3: Label toolbar nao corta no "—"
# Antes: dica.split("—")[0].split("/")[0].strip()
# Depois: usa a dica completa (ja esta limpa agora)
# ══════════════════════════════════════════════
old_lbl = 'lbl_txt = tk.Label(f, text=dica.split("—")[0].split("/")[0].strip(),'
new_lbl = 'lbl_txt = tk.Label(f, text=dica.split("(")[0].strip(),'

if old_lbl in src:
    src = src.replace(old_lbl, new_lbl, 1)
    print("AJUSTE 3 OK — label toolbar usa nome completo")
else:
    print("AJUSTE 3 ERRO — lbl_txt nao bate")
    raise SystemExit

editor_path.write_text(src, encoding="utf-8")
try:
    ast.parse(src)
    print("\nSintaxe OK")
except SyntaxError as e:
    print(f"\nERRO linha {e.lineno}: {e.msg}")
    editor_path.write_text(src_original, encoding="utf-8")
    print("REVERTIDO")
    raise SystemExit

print("\nRode: python main.py")
print("Teste:")
print("  1. Toolbar: Carro / Motocicleta / Caminhao / Bicicleta (nomes certos)")
print("  2. Inserir veiculo: SEM popup de identificacao, vai direto")
print("  3. Rotulo auto (V1, V2...) editavel no painel Propriedades")
print("  4. Sem dialogo de redimensionar — usa handles")
