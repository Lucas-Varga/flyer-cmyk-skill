# 03 · Design: flyer A5 da inauguração da Ápice Academia

Especificação para implementação literal em SVG vetorial (texto em curvas) e PDF/X-1a CMYK (FOGRA39).
Empresa e dados **fictícios** (`00-fatos.md`). Conteúdo de `01-marketing.md`; diretrizes de `02-psicologia.md`.

**Convenções.** Medidas em mm. **Todas as coordenadas partem do CANTO DE CORTE superior esquerdo**
(x → direita, y → baixo); sangria vai de −3 a 151 (x) e de −3 a 213 (y). Na API `Arte`, cuja
origem é o canto da sangria, **some +3 a todo x e y** (inclusive nos `d` dos paths e nas
coordenadas dos degradês). Texto: `y` = linha de base. Ancoragem: início | meio | fim.
1 pt = 0,3528 mm. Todas as larguras abaixo foram **medidas** com `impressao.Fonte.largura`.
Margem de segurança: nada importante fora de x 5–143 / y 5–205.

---

## 1. Conceito visual

1. **"Ápice é subir":** uma faixa laranja → âmbar, inclinada e subindo da esquerda para a direita, atravessa as duas faces sobre um azul-noite profundo; é energia e ascensão sem grito.
2. **Frente = convite ao evento:** foto quente de uma turma comum de bike indoor que se funde no escuro, "INAUGURAÇÃO" gravada na faixa e a data logo abaixo; um só foco.
3. **Verso = vitrine honesta:** cabeçalho escuro com o preço grande (com o "depois" colado), selo âmbar da matrícula isenta e, no branco, prova, horários e o botão do WhatsApp colado aos QR.

### Decisões de conciliação (1 linha cada)

| # | Divergência | Decisão |
|---|---|---|
| C1 | Palavras na frente: marketing 40 × psicologia ≤ 35 | **35** (sem as notas legais): saíram "Veja a oferta completa no verso" (o asterisco + "*Condições no verso." faz a ponte) e "por". |
| C2 | Palavras no verso: psicologia ≤ 110 com rodapé × conteúdo do marketing | **112 de corpo + 35 do rodapé legal**: o rodapé é obrigatório (CDC) e não comprime; cortei V5 (dia 6, já está na frente), modalidades (já na frente), "vestiários" e o endereço sob o QR 2 (está no bloco de contato ao lado). |
| C3 | Rodapé: psicologia ≥ 6,5 pt × regra ≥ 7 pt | **7 pt**, Avenir Next Medium (nunca Regular em vazado). |
| C4 | QR: quantos e onde | **2 no verso, 26 mm** (≥ 22 mm da psicologia), nenhum na frente (ação da frente é ir no dia 6; marketing e psicologia concordam). |
| C5 | CTA do verso "GARANTA SUA MATRÍCULA ISENTA" não cabe como botão ≥ 14 pt em 59 mm (medido: 64–79 mm) | Vira **linha-guia** "Garanta sua matrícula isenta até 31/03." logo acima do **botão "CHAME NO WHATSAPP"**, colado ao QR (verbo de posse + prazo + ação, D6.1/D6.2). |
| C6 | CTA da frente "VENHA EXPERIMENTAR GRÁTIS" × título do marketing que já diz "grátis" | Título do marketing mantém "grátis"; botão = **"VENHA CONHECER"** (D2.1), para não repetir. |
| C7 | Verniz: marketing (data + preço) × psicologia (pico + INAUGURAÇÃO/data; preço + selo) | Frente: **pico do logo + INAUGURAÇÃO + linha da data** (3 áreas). Verso: **preço R$ 49,90 + selo da matrícula isenta** (2 áreas). |
| C8 | Âncora dos R$ 80: tachado (psicologia) × "valor normal" (marketing) | **"valor normal: R$ 80,00"** sem tachado: evita leitura de "de/por". |
| C9 | Laranja em ≤ 4 elementos por face (logo não conta) | Frente: faixa, horário, preço do selo. Verso: faixa fina, preço, selo, botão. Anel do selo da frente em branco, ícones em K100, sobretítulo do verso em branco. |
| C10 | Frase de acolhimento (D3.1) sem prometer o que não está nos fatos | **"Comece no seu ritmo"** como título do bloco "incluso"; "para todos os níveis" não entra (não confirmado). |
| C11 | Texto pequeno em laranja (contraste e registro) | Nenhum texto < 12 pt em laranja/âmbar; laranja só ≥ 12 pt sobre o escuro. |
| C12 | Imagens (até 2) | **1 imagem** (frente). O verso fica sem foto para respirar; "Imagens meramente ilustrativas." aparece na frente e no rodapé do verso. |

---

## 2. Paleta e degradês

| Nome | C | M | Y | K | Tinta | Uso | Hex de tela |
|---|---|---|---|---|---|---|---|
| **Noite** | 60 | 0 | 0 | 100 | 160% | Fundo da frente, cabeçalho do verso, "INAUGURAÇÃO" na faixa, fade da foto (2 chapas: texto branco vazado < 12 pt permitido) | #000D15 |
| **Laranja Ápice** | 0 | 75 | 95 | 0 | 170% | Pico do logo (#FF5A1F → este), faixa (início), preço (base), botão do verso | #E05F31 |
| **Âmbar** | 0 | 45 | 95 | 0 | 140% | Faixa (fim), horário da frente, preço do selo da frente, selo "matrícula isenta", preço (topo) | #EC9638 |
| **Branco** | 0 | 0 | 0 | 0 | 0% | Papel; textos vazados; "ÁPICE" do logo (#FFFFFF → este); botão da frente; anel do selo | #FFFFFF |
| **Preto texto** | 0 | 0 | 0 | 100 | 100% | Todo texto e ícone sobre branco e sobre âmbar (sobreimpressão) | #1A1A1A |
| **Cinza fio** | 0 | 0 | 0 | 40 | 40% | Fio divisor do rodapé do verso | #9DA09F |

Logo: `#FF5A1F` → Laranja Ápice (C0 M75 Y95 K0); `#FFFFFF` → Branco (vazado, sem tinta); `#14161A`
(logo-claro, não usado nesta peça) → Preto texto K100.

Contrastes (hex de tela, WCAG): Branco/Noite **19,9:1**; Âmbar/Noite **8,5:1**; Laranja/Noite **5,3:1**
(só ≥ 24 pt); K100/Branco **17,4:1**; K100/Âmbar **7,5:1**; Noite/faixa 5,3–8,5:1 (texto 50 pt);
Branco/Laranja **3,7:1** (só no botão, 14 pt Bold = texto grande). Todo corpo de texto ≥ 7:1.

### Degradês (coordenadas de CORTE; some +3 na API)

| ID | Tipo | Paradas | Geometria | Onde |
|---|---|---|---|---|
| **G1** | linear | 0,00 Laranja Ápice · 1,00 Âmbar | início (−3, 122) → fim (151, 88) (de baixo-esquerda para cima-direita, acompanha a inclinação) | F04 |
| **G1v** | linear | 0,00 Laranja Ápice · 1,00 Âmbar | início (−3, 107,5) → fim (151, 98) | V03 |
| **G2** | linear vertical | 0,00 Âmbar · 1,00 Laranja Ápice | início (0, 36,0) → fim (0, 60,0) | V07, V08, V09 (preço) |

Um degradê dominante por face (a faixa); G2 é aplicado só a título ≥ 30 pt. Nenhum degradê passa por cinza.

---

## 3. Tipografia (8 estilos)

| Estilo | Arquivo · índice | Tamanhos | Entrelinha | Rastreio (em) | Caixa | Efeito |
|---|---|---|---|---|---|---|
| **E1 Display** | /System/Library/Fonts/Supplemental/Futura.ttc · **4** (Condensed ExtraBold) | 50 · 30/90/45 · 28 · 24 · 19 · 11 | — (linha única) | 0,01 (preços: 0) | alta | cor chapada ou G2; sem contorno, sem sombra |
| **E2 Título** | /System/Library/Fonts/Avenir Next.ttc · **8** (Heavy) | 18 | 7,5 mm (21,3 pt = 1,18) | 0 | normal | — |
| **E3 Etiqueta / ênfase** | Avenir Next.ttc · **2** (Demi Bold) | 8,5 · 10 · 12 | — | 0 (caixa alta: 0,06–0,10) | conforme elemento | — |
| **E4 Destaque** | Avenir Next.ttc · **0** (Bold) | 10 · 13 · 15 | — | 0 (botão: 0,06) | conforme elemento | — |
| **E5 Corpo** | Avenir Next.ttc · **5** (Medium) | 8,5 · 9 · 9,5 · 10 | 4,3 mm a 9,5 pt (12,2 pt = 1,28); 4,6 mm a 10 pt (1,30) | 0 | normal | — |
| **E6 Condensada botão** | /System/Library/Fonts/Avenir Next Condensed.ttc · **0** (Bold) | 10 · 14 | — | 0 (botão: 0,04) | conforme elemento | — |
| **E7 Condensada selo** | Avenir Next Condensed.ttc · **2** (Demi Bold) | 8,5 | 5,0 mm | 0,04 | alta | — |
| **E8 Legal** | Avenir Next.ttc · **5** (Medium) | 7 | 3,1 mm (8,8 pt = 1,26) | 0 | normal | — |

Sem contorno e sem sombra em nenhum texto (D5.2: evita cara de panfleto genérico).

---

## 4. Elementos

### FRENTE (ordem de desenho; fundo primeiro)

| Nº | Tipo | Posição (corte) | Tamanho | Cor / efeito | Conteúdo / observação |
|---|---|---|---|---|---|
| **F01** | retângulo | x −3, y −3 | 154 × 216 | Noite | Fundo sangrado. |
| **F02** | imagem (IMG-1) | x −3, y −3 | 154 × 121 (até y 118) | 1º escurecer (Noite, 0,15); 2º fade (baixo, Noite, início 0,50, fim 0,90) | Corte "cover", sem canto arredondado. Fade começa em y 57,5 e fica 100% Noite em y 105,9 (abaixo some sob a faixa). |
| **F03** | logo | x 9, y 9 (canto sup. esq. do logo) | largura 34 → altura 15,15 | `logo-escuro.svg`: #FF5A1F → Laranja Ápice; #FFFFFF → Branco | Sobre a área escura da foto (canto sup. esq. pedido no briefing). |
| **F04** | forma (faixa) | `d = M -3 94 L 151 88 L 151 116 L -3 122 Z` | espessura 28 (vertical); sobe 6 mm em 154 | G1 | Faixa do evento. Borda superior y = 94 − 6·(x+3)/154; inferior = superior + 28. |
| **F05** | texto | x 74 (meio), y **109,5** | largura 113,94 (x 17,03–130,97) | Noite, **sem sobreimpressão** (vazar a faixa) | **INAUGURAÇÃO** · E1 50 pt, rastreio 0,01. Topo das maiúsculas 96,20; topo do til do Ã 92,44; pé do Ç 114,26. Folgas medidas à borda da faixa: "I" 3,0 mm acima; til do Ã 2,8 mm; Ç 3,4 mm abaixo. |
| **F06** | texto | x 9 (início), y **134,0** | 82,54 | Branco | **SÁBADO, 6 DE MARÇO** · E1 24 pt, rastreio 0,01. Topo do acento 125,66 (4,1 mm abaixo da faixa em x 9). |
| **F07** | texto | x **94,17** (início), y 134,0 | 45,16 (termina em 139,33) | Âmbar | **· 8H ÀS 18H** · E1 24 pt, rastreio 0,01. (x = 9 + largura medida de "SÁBADO, 6 DE MARÇO " com espaço = 85,17.) |
| **F08** | texto | x 9, y **147,0** | 67,65 | Branco | **Aulas experimentais** · E2 18 pt. |
| **F09** | texto | x 9, y **154,5** | 53,71 | Branco | **grátis o dia todo** · E2 18 pt. |
| **F10** | texto | x 9, y **163,0** | 66,51 | Branco | **Musculação, treino funcional, bike indoor** · E5 10 pt. |
| **F11** | texto | x 9, y **167,6** | 14,02 | Branco | **e ritmos.** · E5 10 pt. |
| **F12** | texto | x **23,80**, y 167,6 | 30,94 (até 54,74) | Branco | **Sem compromisso.** · E3 Demi Bold 10 pt. (x = 9 + "e ritmos. " = 14,80.) |
| **F13** | círculo (selo) | centro (120, 158,5), r 20 | ⌀ 40; com traço: x 99,6–140,4, y 138,1–178,9 | sem preenchimento; traço Branco 0,8 mm | Anel do selo da oferta (vazado). 4 mm abaixo de F07. |
| **F14** | texto | x 120 (meio), y **149,0** | 23,19 | Branco | **MATRÍCULA ISENTA** · E7 8,5 pt, rastreio 0,04. Corda útil nessa altura: 30,4 mm. |
| **F15** | texto | x 120 (meio), y **154,0** | 11,33 | Branco | **+ 1º MÊS** · E7 8,5 pt, rastreio 0,04. |
| **F16** | texto | x **104,30**, y **162,05** | 5,84 (com espaço) | Âmbar | **R$** · E1 11 pt (sobrescrito: topo do R alinhado ao topo dos algarismos, 159,12). |
| **F17** | texto | x **110,14**, y **165,5** | 22,92 | Âmbar | **49,90** · E1 24 pt, rastreio 0. |
| **F18** | texto | x **133,36**, y 165,5 | 2,33 | Âmbar | **\*** · E1 11 pt (o glifo já fica alto). Conjunto R$ 49,90* = 104,30–135,69; corda útil a y 165,5: 101,7–138,3. |
| **F19** | texto | x 120 (meio), y **172,0** | 24,18 (107,91–132,09) | Branco | **\*Condições no verso.** · E8 7 pt. Corda útil no pé da linha: 106,4–133,6. |
| **F20** | ícone `pino` | x 9, y 187,0 (canto sup. esq.) | 5 × 5 | Branco (vazado) | Traço resultante 0,42 mm. |
| **F21** | texto | x **15,5**, y **190,75** | 44,81 (até 60,31) | Branco | **Av. Exemplo, 1000 – Centro** · E3 Demi Bold 10 pt. |
| **F22** | retângulo (botão) | x **72,78**, y **184,0** | 66,22 × 11, raio 5,5 | Branco (vazado em F01) | Único elemento em forma de botão da frente; fim do Z (canto inf. dir.). |
| **F23** | texto | x **105,89** (meio), y **191,43** | 54,22 | Preto texto K100 | **VENHA CONHECER** · E4 Bold 15 pt, rastreio 0,06, caixa alta. Margem interna 6,0 mm de cada lado; centrado na altura (centro 189,5 + metade da altura das maiúsculas 1,93). |
| **F24** | texto | x 9, y **203,0** | 36,59 | Branco | **Imagens meramente ilustrativas.** · E8 7 pt. Pé 203,59 (≤ 205). |

**Conta de altura dos blocos da frente**
- Logo: 34 / 2,2436 = **15,15 mm** (y 9,00–24,15).
- Faixa: 28 mm; INAUGURAÇÃO 50 pt → maiúsculas 50 × 0,266 = 13,30 mm; caixa total com til e cedilha 92,44–114,26 = **21,82 mm** (cabe nos 28 com ≥ 2,8 mm de folga em todos os pontos).
- Data: 24 pt → maiúsculas 6,38 mm; caixa 125,66–136,29 = **10,63 mm**.
- Título: 2 linhas, 18 pt, entrelinha 7,5 mm; caixa 141,95–156,02 = **14,07 mm**. Folga para a data: 5,66 mm.
- Subtítulo: 2 linhas, 10 pt, entrelinha 4,6 mm; caixa 160,29–168,45 = **8,16 mm**. Folga para o título: 4,27 mm.
- Selo: ⌀ 40,8 com traço (138,1–178,9); conteúdo 146,28–172,58 = 26,3 mm, centrado em 159,4 (centro do anel 158,5).
- Linha do botão: 184,0–195,0 = **11 mm**; endereço centrado em 189,5 (ícone 187–192).
- Rodapé: 7 pt; caixa 201,13–203,59.
- Folgas horizontais: título/subtítulo terminam em x ≤ 76,65; o selo começa em 99,6 (folga 22,9 mm). Endereço termina em 60,31; botão começa em 72,78.

**Contagem de palavras da frente (sem logo e sem as notas legais F19/F24):**
INAUGURAÇÃO (1) + data (7) + título (6) + subtítulo (9) + selo (6) + botão (2) + endereço (4) = **35**.

### VERSO (ordem de desenho; fundo primeiro). Impressão cabeça com cabeça.

| Nº | Tipo | Posição (corte) | Tamanho | Cor / efeito | Conteúdo / observação |
|---|---|---|---|---|---|
| **V01** | retângulo | x −3, y −3 | 154 × 216 | Branco (sem tinta) | Fundo. |
| **V02** | forma (cabeçalho) | `d = M -3 -3 L 151 -3 L 151 98 L -3 104 Z` | — | Noite | Borda inferior inclinada, mesma inclinação da faixa da frente (sobe 6 mm). |
| **V03** | forma (faixa fina) | `d = M -3 104 L 151 98 L 151 101.5 L -3 107.5 Z` | espessura 3,5 | G1v | Eco da faixa da frente. Borda inferior: y = 107,5 − 6·(x+3)/154. |
| **V04** | logo | x 113, y 9 | largura 26 → altura 11,59 (até x 139, y 20,59) | `logo-escuro.svg`: #FF5A1F → Laranja Ápice; #FFFFFF → Branco | — |
| **V05** | texto | x 9, y **17,0** | 61,01 | Branco | **OFERTA DE INAUGURAÇÃO** · E3 Demi Bold 12 pt, rastreio 0,06, caixa alta. |
| **V06** | texto | x 9, y **31,0** | 47,58 | Branco | **PLANO MENSAL · 1º MÊS** · E3 Demi Bold 10 pt, rastreio 0,08, caixa alta. |
| **V07** | texto | x **9,00**, y **44,04** | 12,75 | G2 | **R$** · E1 30 pt, rastreio 0 (sobrescrito: topo do R = 36,06 = topo do "4"). |
| **V08** | texto | x **22,95**, y **60,0** | 38,20 (até 61,15) | G2 | **49** · E1 90 pt, rastreio 0. Topo 36,06. |
| **V09** | texto | x **61,75**, y **48,25** | 23,87 (até 85,62) | G2 | **,90** · E1 45 pt, rastreio 0 (sobrescrito: topo do 9 = 36,06; vírgula desce até 51,14). |
| **V10** | texto | x 9, y **68,0** | 47,11 | Branco | **Depois, R$ 119,90/mês.** · E3 Demi Bold 12 pt. Topo 64,67 → 4,7 mm do pé do "49" (≤ 15 mm, D3.2). |
| **V11** | texto | x 9, y **74,0** | 60,65 | Branco | **Novas matrículas de 06/03 a 31/03/2027.** · E5 9 pt. |
| **V12** | círculo (selo) | centro (116,5, 50,5), r 22 | x 94,5–138,5, y 28,5–72,5 | Âmbar | Selo da matrícula isenta. Folga ao preço (85,62): 8,9 mm; ao logo: 7,9 mm. |
| **V13** | texto | x 116,5 (meio), y **45,5** | 33,92 | Preto texto K100 (sobreimpressão) | **MATRÍCULA** · E1 19 pt, rastreio 0,01. Corda útil no topo (38,9): 37,4 mm. |
| **V14** | texto | x 116,5 (meio), y **55,5** | 28,98 | Preto texto K100 (sobreimpressão) | **ISENTA** · E1 28 pt, rastreio 0,01. |
| **V15** | texto | x 116,5 (meio), y **62,5** | 31,66 | Preto texto K100 (sobreimpressão) | **valor normal: R$ 80,00** · E3 Demi Bold 8,5 pt. Corda útil no pé (62,88): 36,4 mm. |
| **V16** | linha | (9, 80,0) → (139, 80,0) | espessura 0,25 | Branco (vazado) | Separa mensal de anual. |
| **V17** | texto | x 9, y **88,5** | 27,13 | Branco | **PLANO ANUAL** · E3 Demi Bold 10 pt, rastreio 0,06, caixa alta. |
| **V18** | texto | x **38,2**, y 88,5 | 83,11 (até 121,34) | Branco | **R$ 99,90/mês em 12x no cartão, com matrícula isenta.** · E5 9,5 pt. Borda do cabeçalho em x 121: y 99,2 (folga ~10 mm). |
| **V19** | texto | x 9, y **117,5** | 46,94 | K100 | **Comece no seu ritmo** · E4 Bold 13 pt. Topo 114,07; borda da faixa em x 9: 107,03. |
| **V20** | texto (3 linhas) | x 9; y **123,0 / 127,3 / 131,6** | 50,68 / 59,60 / 53,41 (≤ 63) | K100 | E5 9,5 pt, quebras explícitas: **Avaliação física e plano de treino** / **montado por profissional de educação** / **física, inclusos em todos os planos.** |
| **V21** | texto | x 9, y **139,5** | 19,48 | K100 | **ESTRUTURA** · E3 Demi Bold 8,5 pt, rastreio 0,10, caixa alta. |
| **V22** | ícone `check` + texto | ícone x 9, y 142,56 (4 × 4); texto x **14,5**, y **145,5** | 35,62 | K100 | **1.200 m² em 2 andares** · E5 9,5 pt. |
| **V23** | ícone `check` + texto | ícone x 9, y 148,06; texto x 14,5, y **151,0** | 46,85 | K100 | **Estacionamento com 40 vagas** · E5 9,5 pt. |
| **V24** | ícone `check` + texto | ícone x 9, y 153,56; texto x 14,5, y **156,5** | 25,76 | K100 | **Ar-condicionado** · E5 9,5 pt. |
| **V25** | ícone `check` + texto | ícone x 9, y 159,06; texto x 14,5, y **162,0** | 32,43 | K100 | **Equipamentos novos** · E5 9,5 pt. |
| **V26** | ícone `pino` + 2 linhas | ícone x 9, y 169,3 (4 × 4); texto x 14,5, y **172,3 / 176,1** | 37,75 / 29,53 | K100 | E5 8,5 pt: **Av. Exemplo, 1000 – Centro** / **Cidade Exemplo – UF** |
| **V27** | ícone `site` + texto | ícone x 9, y 179,2; texto x 14,5, y **182,2** | 27,30 | K100 | **example.com/apice** · E5 8,5 pt. |
| **V28** | ícone `instagram` + texto | ícone x 9, y 185,2; texto x 14,5, y **188,2** | 28,67 | K100 | **@academia.exemplo** · E5 8,5 pt. |
| **V29** | ícone `relogio` | x 80, y 109,4 | 5 × 5 | K100 | Borda da faixa em x 80–85: y ≈ 104,2 (folga 5,2). |
| **V30** | texto | x **87**, y **113,5** | 47,92 (até 134,92) | K100 | **HORÁRIOS A PARTIR DE 08/03** · E3 Demi Bold 8,5 pt, rastreio 0,06, caixa alta. |
| **V31** | texto | x 87, y **119,3** | 39,25 | K100 | **Seg. a sex.: 5h30 às 23h** · E3 Demi Bold 10 pt (D3.4: destaque ≥ 8 pt). |
| **V32** | texto | x 87, y **123,8** | 27,06 | K100 | **Sábado: 8h às 14h** · E5 9 pt. |
| **V33** | texto | x 87, y **128,2** | 44,89 (até 131,89) | K100 | **Domingo e feriados: 8h às 12h** · E5 9 pt. |
| **V34** | texto | x 80, y **137,5** | 55,61 (até 135,61) | K100 | **Garanta sua matrícula isenta até 31/03.** · E6 Condensed Bold 10 pt. |
| **V35** | retângulo (botão) | x **80**, y **141,0** | 59 × 10, raio 5 | Laranja Ápice | Único botão do verso. |
| **V36** | texto | x **109,5** (meio), y **147,8** | 47,03 | Branco (vazado) | **CHAME NO WHATSAPP** · E6 Condensed Bold 14 pt, rastreio 0,04, caixa alta. Margem interna 6,0 mm. |
| **V37** | QR 1 | x **80**, y **155** | 26 × 26 (zona de silêncio de 4 módulos incluída) | escuro K100 sobre papel branco | `https://wa.me/5500000000000` · versão 3 (29 módulos) → módulo 0,70 mm. |
| **V38** | QR 2 | x **113**, y **155** | 26 × 26 | escuro K100 sobre papel branco | `https://maps.google.com/?q=Av.+Exemplo+1000` · versão 4 (33 módulos) → módulo 0,63 mm. |
| **V39** | texto | x 93 (meio), y **184,6** | 14,65 | K100 | **WhatsApp** · E3 Demi Bold 8,5 pt. |
| **V40** | texto | x 93 (meio), y **188,2** | 23,22 | K100 | **(00) 00000-0000** · E5 8,5 pt. |
| **V41** | texto | x 126 (meio), y **184,6** | 18,70 | K100 | **Como chegar** · E3 Demi Bold 8,5 pt. |
| **V42** | linha | (9, 191,5) → (139, 191,5) | espessura 0,2 | Cinza fio K40 | Separa o rodapé legal. |
| **V43** | texto (3 linhas) | x 9; y **195,5 / 198,6 / 201,7** | 117,08 / 110,33 / 36,59 (≤ 130) | K100 | E8 7 pt, quebras explícitas abaixo. Pé 202,29 (≤ 205). |

Texto exato de V43 (3 linhas):
1. `*Oferta válida para novas matrículas de 06/03/2027 a 31/03/2027. Valor de R$ 49,90 apenas no 1º mês`
2. `do plano mensal; demais meses R$ 119,90. Aulas experimentais sujeitas à lotação de cada turma.`
3. `Imagens meramente ilustrativas.`

(A frase do plano anual saiu do rodapé porque a condição já está em V18, em 9,5 pt, no corpo; nada relevante fica só no rodapé, E3.)

Ícones `check` (V22–V25): topo = linha de base − 2,94, para o centro do traço coincidir com o meio da altura-x. Ícones de contato (V26–V28): topo = linha de base − 3,0.

**Conta de altura dos blocos do verso**
- Cabeçalho (bloco 1, oferta): sobretítulo 12 pt (13,19–18,02); rótulo 10 pt (27,80–31,06); preço "49" 90 pt → 0,266 × 90 = 23,94 mm (36,06–60,00); "Depois…" 12 pt (64,67–69,02); validade 9 pt (71,60–74,10); fio 80,0; anual 10/9,5 pt (85,7–88,97). Total útil 13,19–88,97 = **75,8 mm**, dentro do escuro (≥ 98).
- Selo âmbar: ⌀ 44 (28,5–72,5); conteúdo 38,9–62,88 = 23,98 mm, centrado em 50,9 (centro 50,5).
- Coluna esquerda (bloco 2, incluso + estrutura; x 9–72): 114,07–162,8 = **48,7 mm** (título 13 pt; 3 linhas × 4,3 mm; rótulo; 4 itens × 5,5 mm).
- Contato (bloco 5, coluna esquerda): 169,3–188,92 = **19,6 mm**.
- Coluna direita, horários (bloco 3; x 80–139): 109,4–128,96 = **19,6 mm**.
- Coluna direita, CTA + QR (bloco 4): linha-guia 134,83–137,63; botão 141–151; QR 155–181; legendas 182,33–188,67. Total 134,83–188,67 = **53,8 mm**.
- Rodapé (bloco 6): fio 191,5; 3 linhas 7 pt × 3,1 mm: 193,55–202,29 = **8,7 mm**.
- Colunas: esquerda termina em x ≤ 68,60 (V20 linha 2: 9 + 59,60); direita começa em x 80. Contato e legendas terminam juntos (188,2).

**Contagem de palavras do verso:** cabeçalho 35 + incluso 20 + estrutura 13 + contato 9 + horários 21 + CTA 9 + legendas 5 = **112 de corpo**; rodapé legal **35**.

---

## 5. Verniz UV localizado (chapa separada "Verniz UV", 100%, sobreimpressão)

**Frente (3 áreas):**
1. **Pico do logo (parte de F03)**, só o triângulo laranja, em coordenadas de corte:
   `d = M 9 23.245 L 14.759 11.122 L 20.517 23.245 L 17.244 23.245 L 14.759 17.668 L 12.273 23.245 Z`
   (pico do SVG × escala 34/56,09 = 0,606168, deslocado para 9, 9).
2. **F05** (curvas de "INAUGURAÇÃO").
3. **F06 + F07** (curvas da linha da data "SÁBADO, 6 DE MARÇO · 8H ÀS 18H").

**Verso (2 áreas):**
1. **V07 + V08 + V09** (curvas de "R$ 49,90").
2. **V12** (disco do selo "matrícula isenta", inteiro; o texto K100 por cima fica envernizado junto).

**Nunca** sobre: QR (V37, V38), rodapé (F24, V43), "R$ 119,90" (V10), botões, foto, texto < 14 pt.
Todas as áreas a ≥ 5 mm do corte; o menor traço envernizado (hastes de F06/F07 a 24 pt) ≈ 1,2 mm (≥ 0,5 mm).

---

## 6. Imagem

### IMG-1: frente (F02)

- **Quadro (corte):** x −3, y −3, w 154, h 121 (sangra no topo e nas laterais; termina sob a faixa). Corte "cover", sem canto arredondado.
- **Geração:** gpt-image-2, paisagem **1536 × 1024 (3:2)**; ampliar 2× (3072 × 2048) antes de montar → ~430 ppi efetivos no quadro (mínimo aceitável 300). No "cover", a imagem escala para 121 mm de altura e perde ~14 mm em cada lado: os assuntos ficam nos 80% centrais da largura.
- **Efeitos (nesta ordem):** escurecer (cor Noite C60 K100, intensidade 0,15) → fade (lado **baixo**, cor Noite C60 K100, início **0,50**, fim **0,90**). Sem duotone (a foto mantém pele natural e luz quente). Limite de tinta 300%.
- **Espaço vazio:** canto superior esquerdo escuro (logo, F03, em x 9–43, y 9–24); 40% de baixo com pouco detalhe (vira Noite e fica sob a faixa e o texto).

**Prompt (inglês):**

> Wide editorial photograph of a friendly indoor cycling class in a bright, modern neighborhood gym, seen from a slightly low three-quarter angle at the side of the room. Six to eight ordinary riders of mixed ages (early 20s to late 50s), mixed body types (including plus-size), mixed ethnicities and genders, wearing simple everyday workout clothes (t-shirts, leggings, shorts), pedaling with relaxed smiles or light concentration. One clearly mature rider (around 55, grey hair) sits in the right third of the frame; a beginner-looking rider is laughing and chatting with the person beside her. Faces are small in the frame, mostly in profile or three-quarter view, with gentle motion blur on legs and wheels: no close-ups, nobody looking at the camera, no recognizable or celebrity-like faces. Composition, 3:2 landscape: the riders occupy the middle band of the frame, from about 15% to 60% of the image height, kept inside the central 80% of the width; the top-left quarter is a dark, out-of-focus ceiling and wall in deep navy shadow (empty space reserved for a logo); the bottom 40% is a plain dark floor with very little detail, falling into shadow (it will be faded to navy and covered by text). Lighting: warm orange and amber rim light and soft practical lights from the right side, deep navy-blue shadows (#05101A); color palette limited to navy, warm orange (#E05F31), amber (#EC9638) and natural skin tones; no green, purple or neon light. 35 mm lens, f/2.8, shallow depth of field, natural fine film grain, photorealistic. Realistic hands, coherent bike mechanics (handlebars, pedals, flywheels). Strictly no text, letters, numbers, logos, brand marks, screens with interface, signage, posters or building facade. No sweat drama, no bodybuilders, no shirtless people, no extremely toned or idealized bodies, no before/after.

**Rejeitar e gerar de novo se:** mãos ou bicicletas deformadas, qualquer letra/logo, rosto grande e nítido, corpo hiperdefinido, ninguém com mais de 40 anos ou fora do padrão atlético, canto sup. esq. claro.

---

## 7. Notas de produção para a gráfica

1. **Formato:** A5 148 × 210 mm, retrato, frente e verso, **cabeça com cabeça** (virar no eixo vertical, como página de livro: o topo do verso fica no mesmo lado do topo da frente). Sangria 3 mm, marcas de corte fora da sangria, margem de segurança 5 mm.
2. **Papel e acabamento:** couché (sugestão: 250 g/m², encorpado para laminação e verniz; confirmar com a gráfica) → impressão 4/4 → **laminação fosca** frente e verso → **verniz UV localizado** sobre a laminação (frente e verso), pela chapa "Verniz UV" enviada em PDF separado (máscara 100% K, mesma página e mesmo registro). Máscara exatamente nas curvas, sem engorda; a gráfica pode contrair 0,1 mm se o equipamento pedir.
3. **Cor:** PDF/X-1a, intenção de saída Coated FOGRA39 (ISO 12647-2), tinta total ≤ 300%. Máximo nas áreas chapadas: 170% (Laranja Ápice). Foto com limite de 300% aplicado.
4. **Preto:** fundos grandes em preto rico **C60 K100** (2 chapas). Todo texto preto em **K100 puro com sobreimpressão** (sobre branco e sobre o âmbar do selo: 240% no selo). **Exceção:** "INAUGURAÇÃO" (F05) em C60 K100 **vazando** a faixa (sobreimpressão daria 330%).
5. **Textos vazados:** todo texto branco < 12 pt fica sobre Noite (2 chapas), em Medium ou mais pesado; nenhum texto < 12 pt usa 2 ou mais chapas.
6. **Fios e ícones:** fio branco 0,25 mm (vazado), fio K40 0,2 mm (1 chapa), ícones K100 (1 chapa) ou brancos vazados; menor traço de ícone 0,33 mm.
7. **QR:** K100 sobre papel branco, fora do verniz, 26 mm com zona de silêncio; ler na prova impressa com 2 celulares (iOS e Android) antes de liberar.
8. **Texto 100% em curvas** (nenhuma fonte embutida). Imagem em CMYK, ≥ 300 ppi efetivos.
9. **Prova:** prova de cor contratual da frente (atenção à emenda entre o fade da foto e o fundo C60 K100: não pode aparecer faixa nem degrau).

---

## 8. Checklist da arte renderizada (o que vou conferir)

1. [ ] **Foco único:** com desfoque de 8–10 px, só "INAUGURAÇÃO" + data na frente e "R$ 49,90" + selo no verso continuam legíveis.
2. [ ] **Faixa:** nenhuma letra de "INAUGURAÇÃO" (til do Ã, Ç, I) encosta ou passa da borda da faixa; folga ≥ 2,5 mm visível.
3. [ ] **Foto:** fade sem emenda com o fundo Noite; logo legível sobre área escura; pessoas comuns e diversas (≥ 1 com mais de 40 anos ou fora do padrão atlético); sem texto, logo, mãos ou bikes defeituosas (inspeção a 200%); nenhum rosto grande.
4. [ ] **Selo da frente:** "R$ 49,90*" e "*Condições no verso." inteiros dentro do anel, com respiro ≥ 1 mm; anel não toca a data nem o botão.
5. [ ] **Z e CTA:** botão "VENHA CONHECER" no canto inferior direito da frente; botão "CHAME NO WHATSAPP" colado aos QR no verso; exatamente 1 botão por face.
6. [ ] **Texto exato e PT-BR:** acentos (Á, Ç, Ã, Í, º, ², –), "R$ 49,90", "R$ 119,90", "06/03 a 31/03/2027"; zero ocorrências de "vagas" (fora de "40 vagas" de estacionamento), "últimas", "só hoje", "limitad", "sem fidelidade", "1º mês grátis".
7. [ ] **Transparência de preço:** "Depois, R$ 119,90/mês." a ≤ 15 mm do "49", 12 pt, branco pleno; "31/03" junto ao preço; plano anual visível.
8. [ ] **Tamanhos:** menor texto 7 pt (F19, F24, V43); corpo ≥ 8,5 pt; preço 90 pt; manchete 50 pt.
9. [ ] **Contraste:** nenhum texto < 12 pt em laranja/âmbar; texto preto sempre K100; branco < 12 pt só sobre Noite.
10. [ ] **Laranja:** ≤ 15% da área por face (estimado: frente ~14%, verso ~11%); ≤ 4 elementos laranja/âmbar por face, sem contar o logo.
11. [ ] **Verniz:** só nas 3 áreas da frente e 2 do verso listadas na seção 5; nada sobre QR, rodapé, "R$ 119,90" ou foto.
12. [ ] **Margens:** nenhum texto fora de x 5–143 / y 5–205; sangria cheia (fundo, foto, faixas) até −3/151 e −3/213.
13. [ ] **QR:** abrem `https://wa.me/5500000000000` e `https://maps.google.com/?q=Av.+Exemplo+1000`; legendas certas sob cada um.
14. [ ] **Verso cabeça com cabeça** e alinhamento das inclinações (faixa da frente e borda do cabeçalho sobem 6 mm para a direita).
15. [ ] **Pré-impressão:** tinta máxima ≤ 300% no relatório do PDF; F05 vazado (sem sobreimpressão); K100 em sobreimpressão; chapa de verniz separada e registrada.
