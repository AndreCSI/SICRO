# SICRO PCI/AP
### Sistema Inteligente de Croquis e Reconstrução de Ocorrências
**Polícia Científica do Amapá — Seção de Perícias de Trânsito**

---

> ⚠️ **Este projeto está em desenvolvimento ativo.**
> Funcionalidades podem mudar, quebrar ou ser removidas a qualquer momento.
> Não use em produção sem validação da equipe responsável.

---

## O que é

O SICRO PCI/AP é um software desktop desenvolvido em Python para auxiliar peritos criminais da Polícia Científica do Amapá na confecção de **croquis periciais de trânsito** — os desenhos técnicos que registram a posição de veículos, vítimas, marcas de frenagem e outros elementos em ocorrências de trânsito.

O software substitui o processo manual de desenho, permitindo ao perito:

- Criar croquis vetoriais sobre foto aérea de drone ou em canvas limpo
- Posicionar veículos, pedestres e sinalização com precisão
- Calibrar a escala real usando lona de 2m como referência física
- Exportar o croqui em PDF para anexar ao laudo pericial

## Status atual

| Módulo | Status |
|--------|--------|
| Interface principal (canvas, toolbar, camadas) | ✅ Funcional |
| Inserção de veículos (carro, moto, caminhão, bicicleta, pedestre) | ✅ Funcional |
| Eixos R1 e R2 (livre ângulo) | ✅ Funcional |
| Cotas de distância | ✅ Funcional |
| Sítio de colisão (SC) | ✅ Funcional |
| Editor de texto inline | ✅ Funcional |
| Modo arte de via (asfalto, calçadas, faixas, semáforo, placa...) | 🔧 Em desenvolvimento |
| Calibração por drone + cálculo GUM | ✅ Funcional |
| Salvar / carregar (.sicro) | ✅ Funcional |
| Exportar PDF | 🔧 Parcial |
| Refatoração modular | 🔧 Em andamento |
| Testes automatizados | ❌ Não iniciado |
| Instalador (.exe) | ❌ Não iniciado |
| Documentação de uso | ❌ Não iniciado |

## Tecnologias

- **Python 3.10+**
- **Tkinter** — interface gráfica nativa
- **Pillow** — processamento de imagens PNG e foto de drone
- **ReportLab** — exportação PDF
- **Git / GitHub** — controle de versão

## Como rodar

```bash
# Clone o repositório
git clone https://github.com/AndreCSI/SICRO.git
cd SICRO

# Instale as dependências
pip install Pillow reportlab

# Execute
python main.py
```

> Requer Python 3.10 ou superior instalado no Windows.

## Estrutura do projeto

```
SICRO/
├── sicro_pci_ap_v16.py   ← monolito principal (em refatoração)
├── main.py               ← ponto de entrada
├── config.py             ← constantes e paleta de cores
├── assets/veiculos/      ← imagens PNG dos veículos
├── desenho/              ← funções de desenho vetorial
├── popups/               ← janelas de seleção
├── widgets/              ← componentes reutilizáveis
├── arquivo/              ← salvar/carregar arquivos
├── modos/                ← (em construção)
└── ui/                   ← (em construção)
```

## Autor

**André Ricardo Barroso**
Perito Criminal — Polícia Científica do Amapá
Seção de Perícias de Trânsito

---

*Desenvolvido para uso interno da PCI/AP. Distribuição sujeita a autorização.*