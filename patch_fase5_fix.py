"""
patch_fase5_fix.py — Conserta o erro de sintaxe da fase 5
O PATCH 3 substituiu o label_prop.config dentro de um else: que ficou vazio
e o codigo nao indentou corretamente. Vamos detectar e corrigir.
"""
from pathlib import Path
import ast, re

editor_path = Path("ui") / "editor_croqui.py"
src = editor_path.read_text(encoding="utf-8")

# Tenta parsear pra ver onde esta o erro
try:
    ast.parse(src)
    print("Sintaxe OK — nada a fazer")
    raise SystemExit
except SyntaxError as e:
    print(f"Erro detectado linha {e.lineno}: {e.msg}")

# Olha as linhas 1705-1720 para ver o estado
linhas = src.split("\n")
print("\nContexto do erro:")
for i in range(max(0, 1705), min(len(linhas), 1720)):
    print(f"{i+1:4}: {linhas[i]}")

# O problema: meu replace colocou bloco de codigo multilinha onde antes
# havia 1 linha. Se essa 1 linha estava sozinha apos else:, o else fica vazio
# Procurar padrao else: seguido de bloco placeholder mal-indentado

# Estrategia: procurar 'else:' isolado seguido de # Restaura placeholder
# fora do nivel correto

# Vou reverter o PATCH 3 — restaurar a linha simples original do label_prop
# e re-aplicar de forma mais segura

# Padrao do bloco que pode estar mal-indentado:
# else:
#         # Restaura placeholder no painel de propriedades
#         if hasattr(self, "_props"):
# ...

# Detectar e ajustar indentacao quando aparece "else:" sem corpo seguido de novo bloco
# Simplificacao: trocar o bloco grande dentro de else por placeholder simples

# Reverte: troca o bloco do placeholder pelo label_prop.config simples
bloco_novo = '''        # Restaura placeholder no painel de propriedades
        if hasattr(self, "_props"):
            for w in self._props.winfo_children():
                w.destroy()
            self._props_placeholder = tk.Label(self._props,
                text="Selecione um\\nelemento no canvas",
                font=FONTE_SMALL,
                bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                justify="left")
            self._props_placeholder.pack(anchor="w", pady=4)
            self.label_prop = self._props_placeholder
'''

# Substitui de volta por uma versao com fallback compativel
# Versao corrigida: se label_prop ainda existir (compat antiga), so chama config
# Senao usa o painel novo
bloco_corrigido = '''        # Placeholder no painel de propriedades
        if hasattr(self, "_props"):
            for w in self._props.winfo_children():
                w.destroy()
            ph = tk.Label(self._props,
                text="Selecione um\\nelemento no canvas",
                font=FONTE_SMALL,
                bg=FUNDO_PAINEL, fg=TEXTO_TERCIARIO,
                justify="left")
            ph.pack(anchor="w", pady=4)
            self.label_prop = ph
        else:
            if hasattr(self, "label_prop"):
                self.label_prop.config(text="Selecione um\\nelemento")
'''

# Procura todos os locais onde o bloco_novo apareceu e revisa indentacao
# olhando o contexto. O problema eh: alguns desses estao dentro de "else:"
# de um if/else maior, e o bloco grande quebra o fluxo.

# Solucao mais simples: encontrar blocos quebrados e adicionar 'pass'
# quando necessario

# Vou ler o erro de novo e fazer fix manual da linha 1711-1713
print("\nTentando correcao automatica...")

# Encontra todos os "else:" seguidos imediatamente por linha em branco
# ou comentario fora de indentacao
nova_src = re.sub(
    r"(\n        else:\n)(\s*# Placeholder no painel de propriedades\n)",
    r"\1            pass\n\2",
    src,
    flags=0
)

# Reescreve o bloco placeholder com indentacao consistente
# Se ele esta dentro de else: ele precisa estar mais indentado
# Vou substituir o bloco quebrado por um if/else inline mais simples

# Approach: substituir bloco_novo por bloco_corrigido
if bloco_novo in src:
    nova_src = src.replace(bloco_novo, bloco_corrigido)
    print(f"Bloco substituido por versao com fallback")

# Salva e testa
editor_path.write_text(nova_src, encoding="utf-8")
try:
    ast.parse(nova_src)
    print("Sintaxe agora OK!")
except SyntaxError as e:
    print(f"Ainda com erro linha {e.lineno}: {e.msg}")
    print("\nLinhas ao redor:")
    nl = nova_src.split("\n")
    for i in range(max(0, e.lineno-5), min(len(nl), e.lineno+5)):
        print(f"{i+1:4}: {nl[i]}")
