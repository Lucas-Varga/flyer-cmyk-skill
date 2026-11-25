# Produção gráfica: regras, recursos e armadilhas

Consulte esta referência antes de definir a paleta, ao revisar a especificação do
designer e antes de entregar.

Sumário:
[Papel e perfil](#papel-e-perfil) · [Formatos](#formatos) · [Cor](#cor) · [Degradês](#degradês) ·
[Pantone](#pantone--cores-especiais) · [Efeitos](#efeitos) · [Acabamentos](#acabamentos-especiais) ·
[Imagens de IA](#imagens-geradas-por-ia) · [SVG](#svg) · [PDF](#pdf-para-a-gráfica) ·
[Medidas](#medidas-e-legibilidade) · [Notas para a gráfica](#notas-para-a-gráfica-modelo)

## Papel e perfil

| Papel | `papel=` | Condição (OutputIntent) | Tinta máx. | Quando usar |
|---|---|---|---|---|
| Couché brilho/fosco | `couche` | FOGRA39 | 300% | flyer comum, foto, cores vivas |
| Offset / sulfite / reciclado | `offset` | FOGRA29 | 280% | aceita caneta, visual natural; cores ficam mais suaves e escuras |

O limite de tinta vale para a arte e para as fotos (o `imagem()` aplica sozinho). Em
offset, evite fundos chapados enormes de preto rico: o papel absorve, demora a secar e
"decalca".

## Formatos

`formato('A5')`, `formato('10x15', 'paisagem')` ou `formato((120, 180))` para medida
personalizada. Mais pedidos: A6 105×148, A5 148×210, A4 210×297, A3 297×420, DL 99×210,
10×14, 10×15, 15×21, 20×28, quadrado 15×15 e 21×21, cartão 90×50.
Escala dos elementos: num A6, título ~22–26 pt e corpo 9–10 pt; num A4, título 40–60 pt
e corpo 11–12 pt. Margem de segurança: 5 mm em todos (8 mm em A3 ou maior).

## Cor

- **Valores CMYK fixos por objeto**, nunca convertidos de RGB no fim. Converter um
  SVG/HTML RGB transforma o preto em preto de 4 cores (texto borrado por registro) e
  muda a cor da marca.
- **Fundo escuro grande:** preto rico de 2 chapas, **C60 K100** (160%), ou
  C60 M40 Y40 K100 (240%) se quiser mais profundo em couché. Nunca 4×100.
- **Texto preto sobre claro:** só **K100**. Cinzas: K75, K50, K25 (uma chapa).
- **Texto pequeno (< 12 pt) e linhas finas:** uma chapa, ou vazado de no máximo 2
  chapas. Menor texto vazado em fundo escuro: ~9 pt bold / 10 pt médio.
- **Cor de destaque:** reserve para a chamada (CTA) e a marca, ≤ 10–15% da face.
  Vermelho sobre preto (~3:1) não serve para texto.
- **Contraste:** corpo de texto ≥ 7:1 (público amplo); títulos ≥ 4,5:1.
- **Prévia de tela:** `Cmyk.rgb_tela` converte pelo perfil CMYK do sistema e fica fiel.
  Passe `tela='#hex'` só para cores da marca já calibradas. Visualizadores simples de PDF
  (PyMuPDF) mostram o C60 K100 azulado; impresso, ele fica preto.

## Degradês

- `Degrade([(0, corA), (0.6, corB), (1, corC)], inicio=(x, y), fim=(x, y))` (linear) ou
  `Degrade(..., tipo='radial', centro=(x, y), raio=r)`. Coordenadas no sistema da Arte
  (canto da sangria); com a classe `Face`, some a sangria (`deslocar(S, S)`).
- Vira shading CMYK no PDF: sem transparência, válido em PDF/X-1a, sem faixas.
- Só cores de processo (sem Pantone). Para "sumir" no fundo, termine o degradê na **cor
  exata do fundo**, não em "transparente".
- Degradê longo e sutil (variação < 15% numa chapa) pode mostrar degraus (banding) em
  algumas impressoras digitais. Prefira variações de 20% ou mais, ou mova duas chapas
  juntas.
- Degradê em texto (`texto(..., cor=Degrade(...))`) só em títulos grandes (≥ 24 pt).

## Pantone / cores especiais

- `Cmyk('Marca', 0, 100, 81, 4, '#c8102e', spot='PANTONE 186 C')`: vai para o PDF como
  **Separation** (uma chapa extra com o nome da tinta), com a alternativa CMYK para prova
  e para quem imprimir em 4 cores.
- Cada Pantone é uma tinta a mais no orçamento. Use só se a marca exigir cor exata ou se
  a cor estiver fora do CMYK (laranjas e verdes vibrantes, metálicos Pantone 871–877).
- O nome precisa ser **exatamente** o da escala da gráfica (ex.: "PANTONE 186 C" para
  couché, "PANTONE 186 U" para offset).
- Não use Pantone em degradê; use a alternativa CMYK.

## Efeitos

Todos vetoriais ou já aplicados na foto, sem transparência:

| Efeito | Recurso | Dica |
|---|---|---|
| Contorno no texto | `contorno=(cor, mm)` | 0,3–0,8 mm; traço por fora (não come a letra) |
| Sombra sólida | `sombra=(dx, dy, cor)` | 0,6–1,5 mm; estilo esportivo/retrô; cor escura do fundo |
| Faixas, selos, formas | `forma(d, cor)` | path SVG em mm: faixas inclinadas, estrelas de oferta, ondas |
| Duotone | `('duotone', escura, clara)` | foto nas cores da marca; ótimo para unificar fotos ruins |
| Velar foto | `('escurecer', cor, 0.3–0.6)` | aumenta o contraste do texto por cima |
| Fundir foto no fundo | `('fade', 'baixo', cor_do_fundo, 0.5, 1.0)` | a foto "derrete" na cor do fundo, sem emenda |

**Sombra suave, brilho difuso (glow) e objetos semitransparentes** exigiriam
transparência. Use as alternativas: sombra sólida; degradê radial atrás do objeto (cor
do fundo → cor mais clara); ou o efeito já pronto dentro da imagem (gerada ou tratada).

## Acabamentos especiais

`with arte.acabamento('verniz-uv'):` e desenhe as formas, textos ou fotos que recebem o
acabamento. Elas não entram na arte; viram a **máscara** daquele acabamento.

| Tipo | Para quê | Regras |
|---|---|---|
| `verniz-uv` | brilho localizado sobre papel **fosco laminado** | ≥ 1 mm de folga entre áreas; traços ≥ 0,5 mm; ótimo em título, logo, foto |
| `hot-stamping` | metalizado (ouro, prata, holográfico) | elementos ≥ 0,3 mm de traço; evite letras < 8 pt; geralmente **sem tinta por baixo** (deixe a área sem cor na arte ou combine com a gráfica) |
| `relevo` | alto-relevo seco | formas simples e grandes; papel ≥ 250 g |
| `branco` | tinta branca em papel colorido, kraft ou transparente | o branco vai **por baixo** das cores |
| `faca` | corte em formato especial | desenhe só o **contorno** (linha); cantos com raio ≥ 2 mm; 3 mm de sangria além da faca |

Saída: `*-acabamentos.pdf`, com uma página por acabamento e face, em K100 (preto =
área do acabamento) e as mesmas caixas e marcas da arte. É o formato que as gráficas
pedem. No SVG, cada acabamento é uma camada do Inkscape oculta. A prévia
`svg(simular_acabamentos=True)` mostra como fica, para o cliente aprovar.

Sempre confirme com a gráfica: disponibilidade, custo, papel e tiragem mínima.

## Imagens geradas por IA

- O briefing vem do designer: prompt em inglês, tamanho em mm, **onde fica o espaço
  livre para o texto** e luz e cores alinhadas à paleta.
- O `gerar_imagem.py` acrescenta "sem texto, letras, logos ou marcas d'água". A IA erra
  letras; **todo texto fica na arte vetorial**.
- Peça a resolução certa: o script calcula os pixels pelo tamanho de uso a 300 dpi
  (múltiplos de 16 no OpenAI). Abaixo de 200 ppi, reduza o quadro.
- Revise sempre: mãos, rostos, equipamentos, logos falsos, objetos fundidos. Refaça
  quando precisar.
- Ética: imagem gerada não pode se passar por foto real do estabelecimento (ex.: "nossa
  academia" com uma sala que não existe). Use "Imagens meramente ilustrativas" no rodapé
  e prefira cenas genéricas (pessoa treinando, textura, ambiente sem identificação).
- A imagem entra como qualquer foto: `imagem('fundo.png', ..., efeitos=[...])`; vai
  para CMYK com limite de tinta.

## SVG

- O SVG não tem CMYK de verdade. Técnica usada:
  - `fill="#hex"` traz a prévia;
  - `style="fill:#hex icc-color(FOGRA39, c, m, y, k)"` traz o CMYK (o Inkscape
    preserva);
  - degradês usam `<linearGradient>`/`<radialGradient>` com o mesmo esquema nos stops.
- Camadas do Inkscape: `ARTE (CMYK)` + uma por acabamento (ocultas).
- **Armadilha:** no logo, mapeie todos os hex do arquivo, e só eles. O `logo()` agora
  recusa se faltar algum e troca em 2 passos, para evitar a troca em cascata que gerava
  `style` duplicado (XML inválido).

## PDF para a gráfica

- **PDF/X-1a:2003**: PDF 1.4, CMYK + Separation, sem transparência, tudo em curvas,
  OutputIntent com a condição registrada do papel (FOGRA39 ou FOGRA29, RegistryName
  `http://www.color.org`). Não precisa embutir perfil, então não precisa baixar nada.
- Caixas: TrimBox = formato final; BleedBox = +3 mm; MediaBox = +12 mm (marcas de corte
  em cor de registro, 0,25 pt, afastadas 3 mm).
- Slug (fora da sangria): formato, papel, limite de tinta, face, nome do acabamento.
- **Armadilhas do reportlab, já tratadas no `pdf_cmyk.py`:**
  - bloco `BT /F1 … ET` e Helvetica declarada em cada página: removidos;
  - `enforceColorSpace='sep_cmyk'`: RGB vira erro na hora;
  - preenchimento **não-zero** (com par-ímpar, letras perdem o miolo).
- Overprint não é usado: os acabamentos vão em arquivo separado.

## Medidas e legibilidade

| Item | Valor de referência |
|---|---|
| Sangria | 3 mm |
| Margem de segurança | 5 mm (8 mm em A3+), também dos dois lados de picote/dobra |
| Corpo de texto | 9–10 pt em A6; 10–11 pt em A5; 11–12 pt em A4 |
| Rodapé legal | ≥ 7 pt (8 pt para público 40+) |
| Título | grande o bastante para ler a 1,5 m (A5: 28–60 pt) |
| QR | ≥ 18 mm (20–25 mm para o principal), correção M, zona de silêncio de 4 módulos, escuro sobre branco, módulo ≥ 0,4 mm (o `qr()` avisa) |
| Fotos | ≥ 300 ppi no tamanho de uso (200 é o mínimo) |
| Picote | micro-serrilha; troca de cor do fundo 2 mm depois do picote (tolerância ±1 mm) |

## Notas para a gráfica (modelo)

- Formato, cores (4/4, 4/0, + Pantone), frente e verso (cabeça com cabeça).
- Papel, gramatura, laminação (fosca, brilho) e acabamentos, com o arquivo de máscaras.
- Tinta máxima; cores especiais pelo nome exato; textos vazados finos pedem registro
  apertado.
- Prova de cor contratual + prova física; teste dos QR no celular a 20 cm.
