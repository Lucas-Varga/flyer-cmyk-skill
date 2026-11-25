# Ápice Academia: flyer de inauguração (arquivos para a gráfica)

> Empresa e dados **fictícios**: flyer de teste da skill `impresso-grafica`.

## Arquivos
| Arquivo | O que é |
|---|---|
| `flyer-grafica.pdf` | **Arte**: 2 páginas (1 = frente, 2 = verso), PDF/X-1a:2003, CMYK, Coated FOGRA39 |
| `flyer-grafica-acabamentos.pdf` | **Máscara do verniz UV localizado**: pág. 1 = frente, pág. 2 = verso. Preto (K100) = área com verniz. Mesmo tamanho, caixas e marcas da arte |
| `flyer-frente.svg`, `flyer-verso.svg` | Fonte editável (Inkscape), com a camada do verniz oculta |
| `previa-*.png` | Prévias de tela, incluindo a simulação do verniz |

## Especificação
- **Formato:** A5 148×210 mm, retrato, 4/4 cores, frente e verso **cabeça com cabeça**.
  Sangria 3 mm; marcas de corte afastadas 3 mm.
- **Papel:** couché 250 g/m² (sugestão), **laminação fosca** frente e verso + **verniz UV
  localizado** sobre a laminação, pela máscara do PDF de acabamentos.
- **Cor:** CMYK, FOGRA39, tinta máxima medida de 269% (limite 300%). Fundo escuro em preto
  rico C60 K100 (2 chapas). Texto em curvas; nenhuma fonte no arquivo.
- **Preto:** todo K100 está **vazado** (knockout). Se a gráfica preferir sobreimpressão
  de preto no RIP, ela pode ser ativada para o texto K100, **exceto "INAUGURAÇÃO"**
  (C60 K100 sobre a faixa laranja: com sobreimpressão chegaria a 330%).
- **QR codes:** K100 sobre branco, 26 mm (WhatsApp e mapa), fora do verniz.
  Lidos por software; testar na prova com Android e iPhone.
- **Imagem:** gerada por IA (gpt-image-2.6-sunburst, editada com IA para trocar as
  janelas por parede), convertida para CMYK com limite de tinta. 299 ppi no tamanho de
  uso. Rodapé com "Imagens meramente ilustrativas".

## Prova
Peça prova de cor contratual (atenção à emenda entre a foto e o fundo escuro) e prova
física com laminação e verniz, para conferir o registro do verniz sobre "INAUGURAÇÃO",
a data, o preço e o selo.
