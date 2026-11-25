# flyer-cmyk-skill

**Skill para o Claude criar flyers e impressos promocionais prontos para a gráfica, para
qualquer campanha: CMYK e Pantone de verdade, degradês, efeitos, acabamentos especiais,
imagens com IA e PDF/X-1a validado.**

*A Claude skill that guides you from idea to a print-ready flyer: true CMYK/Pantone,
gradients, special finishes (spot UV, foil…), optional AI imagery, validated PDF/X-1a.
Docs in Brazilian Portuguese.*

| Frente | Verso |
|---|---|
| ![Frente do flyer de exemplo](docs/exemplo-frente.png) | ![Verso do flyer de exemplo](docs/exemplo-verso.png) |

<sub>Flyer de teste gerado com a skill para uma academia fictícia, com imagem por IA.
O PDF real sai em CMYK; as imagens acima são a prévia de tela.</sub>

## O que ela faz

Você pede, por exemplo, "faz um flyer da inauguração da minha loja para mandar para a
gráfica", e o Claude:

1. **Guia as decisões** com perguntas de múltipla escolha, sempre com uma opção
   recomendada e o impacto de cada escolha:
   - **formato**: A6, A5, A4, A3, DL, 10×14, 10×15, 15×21, 20×28, quadrado 15 ou 21,
     cartão de visita, ou **qualquer medida em mm**;
   - **faces**: só frente ou frente e verso;
   - **papel**: couché ou offset (o perfil de cor e o limite de tinta mudam juntos);
   - **acabamentos especiais**: verniz UV localizado, hot stamping, relevo seco, tinta
     branca, faca especial;
   - **estilo visual** e **cor Pantone** da marca;
   - **imagens com IA**: OpenAI, Google Gemini ou Stability AI, com a chave num `.env`.
2. **Pergunta o que falta**: oferta, regras, contatos, links dos QR codes, logo, cores,
   fontes e fotos. Antes, procura nos arquivos do seu projeto. Não inventa nada.
3. **Monta uma equipe de agentes**:
   - um **estrategista de marketing**: conteúdo, hierarquia, chamada para ação;
   - um **especialista em psicologia de marketing**: leitura em 3 segundos, objeções,
     legibilidade, cores, ética;
   - um **designer gráfico**: conceito, paleta, degradês, efeitos e acabamentos, todos
     os elementos em mm e o briefing das imagens.
4. **Gera as imagens com IA** (se você quiser) já no tamanho certo para impressão e
   confere defeitos.
5. **Implementa a arte**:
   - SVG vetorial com texto em curvas;
   - cores CMYK ou Pantone (Separation);
   - degradês, contorno e sombra em texto, formas livres;
   - fotos com duotone, véu ou fusão no fundo.
6. **Mostra a arte ao designer**, que critica e corrige.
7. **Gera os PDFs para a gráfica**:
   - arte em **PDF/X-1a:2003 CMYK nativo**, com marcas de corte, sangria e
     TrimBox/BleedBox;
   - **máscaras de acabamento** num PDF separado (K100), o formato que as gráficas
     pedem.
8. **Valida automaticamente**: confere que não há RGB, fontes nem transparência, que a
   tinta respeita o limite do papel, que as máscaras usam só preto e que os QR codes
   são lidos.

## Instalação

**Com o [skills.sh](https://skills.sh)** (Claude Code, Cursor, Codex e outros):

```bash
npx skills add Lucas-Varga/flyer-cmyk-skill --skill impresso-grafica -a claude-code -g
```

Sem `-g`, a skill fica só no projeto atual (`.claude/skills/`).

**Como plugin do Claude Code:**

```
/plugin marketplace add Lucas-Varga/flyer-cmyk-skill
/plugin install flyer-cmyk@flyer-cmyk-skill
```

**Manual:** copie a pasta `skills/impresso-grafica` para `~/.claude/skills/`.

Depois é só pedir: *"crie um flyer A5 frente e verso da inauguração da nossa academia
para mandar para a gráfica"*.

## Imagens com IA (opcional)

Se você escolher gerar imagens, a chave da API fica num arquivo **`.env`** na pasta do
trabalho, nunca no chat. Use o modelo `skills/impresso-grafica/assets/env.exemplo`:

```
OPENAI_API_KEY=sua-chave          # OpenAI (gpt-image-2)
GEMINI_API_KEY=sua-chave          # Google Gemini (gemini-2.5-flash-image)
STABILITY_API_KEY=sua-chave       # Stability AI (Stable Image Core)
```

Preencha só a do provedor que vai usar e mantenha o `.env` fora do git. Se a variável
já existir no seu ambiente, o `.env` é dispensável. Cada imagem tem custo no provedor.
O provedor **OpenAI foi testado**; Google e Stability seguem a documentação pública e
podem precisar de ajuste se a API mudar.

A IA é instruída a **não** gerar texto nem logos: todo o texto fica na arte vetorial,
sem erro de digitação. A imagem vai para CMYK com limite de tinta, e o rodapé recebe
"Imagens meramente ilustrativas".

## Requisitos

> ⚠️ **Feita e testada para macOS.** Em Linux e Windows, funciona com as trocas da seção
> seguinte.

- macOS com **Python 3.10+** e **Google Chrome** em `/Applications`;
- pacotes de `skills/impresso-grafica/scripts/requirements.txt` (o Claude cria um
  ambiente virtual e instala sozinho);
- para o resultado sair com a sua marca: **logo em SVG vetorial** e as **fontes** (TTF,
  OTF, WOFF2 ou TTC). Sem as fontes da marca, a skill propõe fontes do sistema.

O que usa recursos do macOS:

| Etapa | No macOS | Arquivo |
|---|---|---|
| Foto para CMYK e prévia | `sips` + perfis *Generic CMYK* e *sRGB* do ColorSync | `scripts/impressao.py` → `_sips`, `PERFIL_*` |
| Prévia do SVG | Chrome headless em `/Applications/Google Chrome.app` | `scripts/previa_svg.sh` (zsh) |
| Fontes do exemplo | Arial e Futura/Avenir em `/System/Library/Fonts` | `assets/exemplo/montar.py`, `exemplos/` |

## Linux e Windows: o que trocar

**Windows:** o caminho mais simples é usar o **WSL** (Ubuntu) e seguir as instruções de
Linux.

**Conversão de cor das fotos** (troque `_sips` e `PERFIL_CMYK` em `impressao.py`):

- **Pillow (ImageCms)**, sem programa externo. Precisa de um perfil ICC CMYK, de
  preferência FOGRA39 ou ISO Coated v2, da [ECI](https://www.eci.org) ou da
  [color.org](https://www.color.org):
  ```python
  from PIL import ImageCms
  srgb = ImageCms.createProfile('sRGB')
  cmyk = ImageCms.getOpenProfile('/caminho/ISOcoated_v2_eci.icc')
  res = ImageCms.profileToProfile(im, srgb, cmyk, outputMode='CMYK',
                                  renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
  ```
- **ImageMagick:**
  `magick foto.jpg -profile sRGB.icc -profile ISOcoated_v2_eci.icc foto-cmyk.tif`

Com `PERFIL_CMYK` apontando para esse perfil, a prévia de cores (`Cmyk.rgb_tela`) também
volta a ser fiel. Sem perfil, ela usa uma aproximação simples.

**Prévia do SVG** (troque `scripts/previa_svg.sh`):

- Linux: `google-chrome --headless=new --screenshot=...` ou `chromium --headless ...`;
  ou `rsvg-convert -d 300 -p 300 arte.svg -o arte.png` (pacote `librsvg2-bin`).
- Windows nativo: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new ...`
  em PowerShell; ou `inkscape arte.svg --export-type=png --export-dpi=300`.

**Fontes:**

- Linux: Liberation Sans (`fonts-liberation`) ou qualquer fonte do Google Fonts
  (Montserrat, Inter, Bebas Neue, Oswald);
- Windows: `C:\Windows\Fonts\arial.ttf`, `arialbd.ttf`, `impact.ttf`, `bahnschrift.ttf`.

O resto é Python puro e roda igual nos três sistemas: texto em curvas, degradês,
Pantone, QR codes, PDF CMYK, máscaras, validação e geração de imagens.

## Estrutura

```
skills/impresso-grafica/
├── SKILL.md                     # o fluxo guiado que o Claude segue
├── scripts/
│   ├── impressao.py             # arte: CMYK/Pantone, degradês, texto em curvas, efeitos, acabamentos
│   ├── pdf_cmyk.py              # PDF/X-1a CMYK + PDF de máscaras de acabamento
│   ├── validar_pdf.py           # confere cores, tinta, transparência, caixas e QR
│   ├── gerar_imagem.py          # imagens com IA (OpenAI / Google / Stability) via .env
│   ├── previa_svg.sh            # SVG → PNG (Chrome headless)
│   └── requirements.txt
├── assets/
│   ├── exemplo/                 # exemplo simples executável (empresa fictícia)
│   └── env.exemplo              # modelo do .env
└── references/
    ├── prompts-agentes.md       # prompts dos agentes de marketing, psicologia e design
    └── producao-grafica.md      # papel, formatos, cor, degradê, Pantone, efeitos, acabamentos, IA, PDF/X
exemplos/academia-inauguracao/   # flyer de teste completo: documentos dos agentes, montar.py, PDFs
```

## Limites e cuidados

- **PDF/X-1a não tem transparência**: sombra suave, brilho difuso e objetos
  semitransparentes viram sombra sólida, degradê ou efeito pronto na imagem. O PDF/X-4
  permitiria transparência, mas exige embutir um perfil ICC.
- Fotos são convertidas com o perfil CMYK genérico do sistema; para cor crítica, deixe a
  gráfica converter.
- Acabamentos e Pantone dependem da gráfica (disponibilidade, custo, tiragem mínima).
  Confirme antes.
- **Peça sempre prova de cor e prova física** antes da tiragem.

## Licença

[MIT](LICENSE)
