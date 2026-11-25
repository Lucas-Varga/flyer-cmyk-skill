# Produção gráfica: regras e números que funcionaram

Consulte esta referência ao montar a paleta, ao revisar a especificação do designer e
antes de entregar o arquivo à gráfica.

## Cor (CMYK, Coated FOGRA39)

- **Valores CMYK fixos por objeto**, nunca convertidos de RGB. Converter um SVG/HTML RGB
  para CMYK transforma o preto puro em preto de 4 cores (texto borrado por registro) e
  muda o vermelho da marca. Por isso o PDF é desenhado direto em CMYK (`pdf_cmyk.py`).
- **Tinta total (TAC) ≤ 300%** para couché FOGRA39. Ex.: vermelho Pantone 186 C ≈ C0 M100
  Y81 K4 (185%).
- **Fundo escuro grande:** preto rico de 2 chapas, **C60 K100** (160%). Com C+M+Y+K,
  o texto vazado fino sofre com registro e a tinta passa do limite.
- **Texto preto sobre claro:** só **K100**. Cinzas: K75 (grafite), K25 (linhas). Fundo
  "quase branco": K4 (uma chapa, retícula estável).
- **Texto pequeno (< 12 pt) e linhas finas:** uma chapa só, ou vazado de no máximo 2
  chapas. Menor texto vazado em fundo escuro: cerca de 9,5 pt bold / 11 pt peso 500.
- **Vermelho/destaque:** só no CTA e na marca, ≤ 10% da área da face. Nunca em rodapé,
  data, condição ou número de passo. Vermelho sobre preto dá cerca de 3,3:1 e não serve
  para texto.
- **Fotos raster:** converta para CMYK antes do PDF (`sips -m "<perfil CMYK>.icc"`) e
  reduza a cerca de 350 dpi no tamanho de uso. O Generic CMYK do macOS deu até 294% de
  TAC na foto, abaixo de 300%. Se houver um perfil FOGRA39 instalado, prefira ele
  (`PERFIL_CMYK_FOTO` em `pdf_cmyk.py`).
- **Ilustrações vetoriais com cores hex (RGB):** não entram no PDF CMYK. O `pdf_cmyk.py`
  recusa de propósito. Converta as cores para a paleta antes ou use como raster CMYK.
- **Prévia de tela de CMYK:** o C60 K100 aparece azulado no PyMuPDF e em visualizadores
  simples. Isso é só a conversão ingênua de tela; impresso, fica preto profundo.
  Avise o usuário.

## SVG "CMYK"

O SVG não tem CMYK de verdade. A técnica usada:

- o atributo `fill="#hex"` traz a prévia sRGB, que todo programa lê;
- o `style="fill:#hex icc-color(FOGRA39, c, m, y, k)"` traz o CMYK (0–1). O Inkscape
  preserva isso; navegadores ignoram e usam o atributo;
- o `<color-profile name="FOGRA39">` vai no `<defs>`, e um comentário por amostra lista
  o CMYK;
- todo texto vai **em curvas** (fontTools + HarfBuzz, com kerning). A gráfica não
  precisa das fontes.

Entregue os SVG como fonte editável. O **arquivo da gráfica é o PDF**.

**Armadilha vista:** ao trocar as cores do logo com regex, um hex de destino igual a uma
chave de origem (ex.: `#E5434D → #C8102E` e depois a chave `#C8102E`) aplica o `style`
duas vezes. O resultado é um XML inválido ("Attribute 'style' is redefined") e o
navegador mostra a página de erro. Mapeie só as cores que existem no arquivo de origem.

## PDF para a gráfica

- Use **PDF/X-1a:2003**: PDF 1.4, só CMYK/cinza, sem transparência, fontes embutidas (aqui
  não há nenhuma: tudo em curvas), `OutputIntent` com `OutputConditionIdentifier`
  **FOGRA39** e `RegistryName http://www.color.org`. Por ser uma condição registrada,
  **não precisa embutir o perfil ICC**, então não é preciso baixar nada.
- O PDF/X-4 exigiria o ICC do FOGRA39 embutido, o que significa baixar o perfil. Se for
  preciso, peça permissão ao usuário antes de baixar (arquivo, origem, tamanho).
- Caixas: **TrimBox** = formato final; **BleedBox** = +3 mm; **MediaBox** = +12 mm, para
  as marcas de corte.
- Marcas de corte em cor de registro (C100 M100 Y100 K100), 0,25 pt, afastadas 3 mm do
  corte, com 5 mm de comprimento. Linha de informação (slug) em K100 de 6 pt fora da
  sangria: formato, sangria, picote, perfil, face.
- `Trapped /False`, `GTS_PDFXVersion (PDF/X-1a:2003)`, `/ID` (o pikepdf grava).
- **Armadilhas do reportlab:** (1) cada página começa com `BT /F1 12 Tf 14.4 TL ET` e
  declara Helvetica sem embutir, e o preflight acusaria fonte não embutida; o
  `pdf_cmyk.py` remove o bloco e o recurso `/Font`. (2) Use
  `enforceColorSpace='cmyk'`: qualquer cor RGB vira erro na hora. (3) Glifos usam regra
  de preenchimento **não-zero** (`FILL_NON_ZERO`); com par-ímpar, letras como "o" e "a"
  podem perder o miolo.
- Overprint: com tudo em K sobre fundo K, não faz diferença e não foi ligado. Se houver
  texto K100 sobre fundo colorido, peça à gráfica sobreimpressão de preto (ou ligue no
  reportlab e reconfira a transparência no validador).
- Entregue 1 PDF com as faces em sequência (pág. 1 = frente, pág. 2 = verso) e uma
  variante sem picote (linha de recorte impressa), se houver picote.

## Medidas e legibilidade (público amplo, 40+)

| Item | Valor que funcionou |
|---|---|
| Margem de segurança | 5 mm do corte e de cada lado do picote/dobra |
| Sangria | 3 mm |
| Título principal | 28 pt (D-DIN Exp Bold) |
| Corpo | 11 pt (mínimo); 12 se couber |
| Rodapé legal | 8 pt (mínimo absoluto) |
| Rótulos em caixa alta | 9,5 pt, +0,08 em de espaçamento, ≤ 3 palavras |
| Contraste do corpo | ≥ 7:1 |
| QR | ≥ 18 mm (20 mm para o principal), correção M, zona de silêncio de 4 módulos, só K100 sobre branco; URL curta (com `?text=` o QR fica denso demais) |
| Picote | micro-serrilha a uma posição fixa (ex.: 145 mm do topo); troca de cor do fundo 2 mm abaixo do picote, para absorver a tolerância (±1 mm) |
| Campo para escrever à mão | quadradinhos de 7×9 mm; linha de nome com ≥ 8 mm livres; sem laminação nem verniz nessa área |
| Papel | couché fosco 250 g/m² (aceita caneta e picote) |

## Notas para a gráfica (modelo)

- Formato, 4/4 cores, frente e verso cabeça com cabeça, sangria, marcas de corte.
- Papel e gramatura; o que não pode ter laminação ou verniz.
- Posição e tipo do picote/dobra, com tolerância.
- Tinta máxima; texto vazado de 2 chapas pede registro apertado; trapping de 0,1 mm
  para o vermelho dentro de fundo escuro.
- Prova de cor contratual + prova física no papel final, para testar a caneta, o picote,
  a leitura dos QR com Android e iPhone a 20 cm e a leitura do rodapé de 8 pt a 40 cm.
