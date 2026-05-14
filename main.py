"""
SICRO PCI/AP — Ponto de entrada
Durante a refatoração, este arquivo roda o monolito original.
À medida que os módulos forem extraídos, este arquivo será atualizado.
"""
# Por enquanto importa e roda direto do monolito
import runpy
runpy.run_path("sicro_pci_ap_v16_7.py", run_name="__main__")