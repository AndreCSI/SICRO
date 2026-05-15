"""
testar_modular.py — Testa se ui/editor_croqui.py importa corretamente
SEM alterar o main.py nem o monolito.
Execute: python testar_modular.py
"""
import sys
from pathlib import Path

print("=" * 50)
print("Teste de importacao do modulo ui/editor_croqui.py")
print("=" * 50)

erros = []

# 1. Testa config
try:
    import config
    print("OK config")
except Exception as e:
    erros.append(f"config: {e}")
    print(f"ERRO config: {e}")

# 2. Testa desenho.veiculos_arte
try:
    from desenho.veiculos_arte import arte_sedan
    print("OK desenho.veiculos_arte")
except Exception as e:
    erros.append(f"veiculos_arte: {e}")
    print(f"ERRO veiculos_arte: {e}")

# 3. Testa popups
for mod, cls in [
    ("popups.popup_veiculo",    "PopupModeloVeiculo"),
    ("popups.popup_placas",     "PopupPlacas"),
    ("popups.popup_modelo_via", "PopupModeloVia"),
]:
    try:
        m = __import__(mod, fromlist=[cls])
        getattr(m, cls)
        print(f"OK {mod}")
    except Exception as e:
        erros.append(f"{mod}: {e}")
        print(f"ERRO {mod}: {e}")

# 4. Testa widgets
for mod, cls in [
    ("widgets.editor_texto",    "EditorTextoInline"),
    ("widgets.painel_camadas",  "PainelCamadas"),
]:
    try:
        m = __import__(mod, fromlist=[cls])
        getattr(m, cls)
        print(f"OK {mod}")
    except Exception as e:
        erros.append(f"{mod}: {e}")
        print(f"ERRO {mod}: {e}")

# 5. Testa ui.editor_croqui (o novo modulo)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "editor_croqui",
        Path("ui") / "editor_croqui.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Verifica classes essenciais
    for cls in ["DialogoRedimensionar", "EditorCroqui", "EditorVia"]:
        if hasattr(mod, cls):
            print(f"OK ui.editor_croqui -> {cls}")
        else:
            erros.append(f"ui.editor_croqui: {cls} nao encontrado")
            print(f"ERRO {cls} nao encontrado")
except Exception as e:
    erros.append(f"ui.editor_croqui: {e}")
    print(f"ERRO ui.editor_croqui: {e}")

print()
print("=" * 50)
if erros:
    print(f"FALHOU — {len(erros)} erro(s):")
    for e in erros:
        print(f"  - {e}")
else:
    print("TUDO OK — modulo pronto para uso!")
    print()
    print("Quando confirmar que python main.py funciona,")
    print("avise para atualizar o main.py para usar os modulos.")
print("=" * 50)