---
name: impresso-grafica
description: Cria peças impressas promocionais prontas para a gráfica (flyer, panfleto, folder, cartão, guia rápido, cartaz, voucher, canhoto destacável). Usa uma equipe de agentes de marketing, psicologia de marketing e design. Gera a arte em SVG vetorial com cores CMYK e texto em curvas e o PDF/X-1a CMYK nativo com marcas de corte, sangria e QR codes validados. Use sempre que o usuário pedir algo para imprimir, como "flyer para a gráfica", "arte em CMYK", "panfleto A5", "PDF para impressão", "material impresso da campanha", "folder", "cartão com QR", ou um SVG/PDF em CMYK, mesmo que não diga "skill" nem "gráfica".
---

# Impresso para gráfica

Produz uma peça impressa completa, do conteúdo ao PDF que a gráfica aceita. O método
veio de um flyer real de campanha de indicação e resolve três problemas que estragam
impressos feitos com ferramentas de tela:

1. **Conteúdo e persuasão**: o que dizer, em que ordem, sem cara de golpe. Isso fica com
   dois agentes especialistas que trabalham em paralelo.
2. **Layout exato**: um designer concilia os dois e entrega coordenadas em mm, que são
   implementadas literalmente e depois criticadas por ele sobre a arte renderizada.
3. **Cor de impressão real**: navegador e SVG só falam RGB. Converter no fim
   transforma o preto K100 em preto de 4 cores e muda a cor da marca. Aqui cada objeto
   nasce com o seu CMYK, e o PDF é desenhado direto em CMYK.

**Plataforma:** macOS. A foto é convertida para CMYK com o `sips`, a prévia do SVG usa o
Google Chrome e o exemplo usa a Arial do sistema. Em Linux ou Windows, avise o usuário e
siga as alternativas do README do repositório antes de começar.

Neste documento, `<skill>` é a pasta onde está este SKILL.md (ex.:
`~/.claude/skills/impresso-grafica` ou `.claude/skills/impresso-grafica` do projeto).

## Recursos

| Arquivo | Para quê |
|---|---|
| `scripts/impressao.py` | Biblioteca da arte: `Arte` (face em mm com sangria), `Cmyk`, `Fonte` (texto em curvas, HarfBuzz), `quebrar` (quebra de linha), QR vetorial, logo SVG com troca de cor, foto, ícones de traço. Grava o SVG e uma lista de desenho (`arte.ops`) |
| `scripts/pdf_cmyk.py` | `gerar_pdf([faces], destino, titulo, rotulos, fonte_slug, autor)`: refaz a lista de desenho em PDF CMYK nativo, com marcas de corte, Trim/BleedBox e PDF/X-1a:2003 FOGRA39 |
| `scripts/validar_pdf.py` | Confere o PDF: caixas, ausência de RGB/fontes/transparência, tinta máxima, leitura dos QR. Gera prévias PNG |
| `scripts/previa_svg.sh` | Renderiza o SVG para PNG (Chrome headless) |
| `scripts/requirements.txt` | Dependências Python |
| `assets/exemplo/` | Exemplo completo e executável (empresa fictícia): `montar.py` + `marca/` com logos. Ponto de partida do script do trabalho |
| `references/prompts-agentes.md` | Modelos de prompt dos 3 agentes e da rodada de crítica. **Leia antes de disparar os agentes** |
| `references/producao-grafica.md` | Regras de cor, PDF/X, medidas mínimas, armadilhas. **Leia ao montar a paleta e antes de entregar** |

## Fluxo

Mantenha uma lista de tarefas com estes passos. Eles são longos e o usuário acompanha
pela lista.

### 1. Pergunte o que falta e junte os ativos

A skill não traz dados de nenhuma empresa. Tudo o que vai impresso precisa vir do usuário
ou dos arquivos dele. Antes de disparar os agentes, procure as respostas no projeto
(documentos, código, configurações, site). Depois **pergunte ao usuário, numa mensagem
só**, o que ainda faltar desta lista:

- **Empresa:** nome, ramo, cidade; o que a diferencia (1–2 frases verdadeiras).
- **Peça:** objetivo e a **1 ação** que ela deve provocar; para quem é; onde é entregue
  (balcão, correio, evento, rua); formato (padrão: A5 frente e verso).
- **Oferta e regras:** o que cada lado ganha, condições, quem pode participar, vigência,
  limites. Pergunte também **o que ainda não está confirmado**, porque isso não pode
  ser impresso como promessa.
- **Contatos:** endereço, horário, telefone/WhatsApp, site; links para os QR codes
  (site, WhatsApp, mapa, termos).
- **Texto legal** obrigatório, ou onde estão os termos completos.
- **Identidade visual:** logo em **SVG vetorial** (versões para fundo claro e escuro),
  cores da marca (CMYK ou Pantone, se tiver), arquivos das fontes (TTF/OTF/WOFF2).
- **Fotos reais** (fachada, equipe, produto), em resolução cheia, se houver.
- **Gráfica:** papel, acabamento, picote/dobra, se já souber.

Monte a **pasta de trabalho** (na pasta do projeto, se o usuário quiser guardar):

- copie `<skill>/assets/exemplo/` inteira (fica com `montar.py` e `marca/`);
- copie para a raiz dela `<skill>/scripts/impressao.py` e `<skill>/scripts/pdf_cmyk.py`.
  Assim a pasta regera a peça sozinha no futuro;
- acrescente `fontes/`, `fotos/` e os documentos de fonte (regras, briefing, contatos).

Crie o ambiente uma vez:
```bash
python3 -m venv <pasta>/.venv && <pasta>/.venv/bin/pip install -q -r <skill>/scripts/requirements.txt
```

Sem logo vetorial ou sem as fontes da marca? Diga ao usuário qual é a consequência
(logo raster perde nitidez; fonte genérica muda a identidade) e combine a solução. Não
troque em silêncio.

### 2. Agentes de marketing e de psicologia (em paralelo)

Dispare os dois na mesma mensagem com os modelos 1 e 2 de
`references/prompts-agentes.md`. Preencha os fatos confirmados e o que **não** está
confirmado. Os entregáveis vão em `01-marketing.md` e `02-psicologia.md`, com resposta
curta.

Ao receber: confira no projeto ou com o usuário qualquer dúvida factual que eles
deixarem aberta. Resolva você, sem repassar ao designer. Exemplo: o tamanho real de um
código que o cliente vai escrever à mão muda o desenho do campo.

### 3. Agente de design: especificação em mm

Dispare o designer (modelo 3) só depois dos dois. Ele concilia as tensões (ex.: o
marketing quer mais texto na frente e a psicologia limita palavras) e devolve
`03-design.md` com:
- a paleta CMYK;
- até 8 estilos de texto;
- todos os elementos com x/y em mm a partir do **canto de corte** (texto com y na linha
  de base) e as quebras de linha explícitas;
- a conta de altura de cada bloco;
- as notas de produção e o checklist.

Dê a ele o comando para medir larguras com as fontes reais (está no modelo). Assim as
quebras não estouram na implementação.

### 4. Implementar literalmente

Adapte o `montar.py` copiado:
- `DADOS` recebe o conteúdo;
- a paleta vira objetos `Cmyk('Nome', c, m, y, k, '#hexDeTela')`;
- os estilos viram tuplas `(Fonte, pt, rastreio_em, caixa_alta)`;
- cada linha da especificação vira uma chamada. A classe `Face` já soma a sangria (+3)
  às coordenadas de corte e tem `p()` para parágrafo com limite de linhas.

Detalhes que importam:
- `arte.logo(arquivo, x, y, largura, {hexOrigem: Cmyk})`: mapeie **todos** os hex que
  existem no SVG do logo e **só** eles (ver a armadilha em `producao-grafica.md`).
- `arte.qr(url, x, y, lado, PRETO, PAPEL)`: zona de silêncio de 4 módulos, correção M.
- Ícones disponíveis: check, pino, relogio, balao, tesoura, presente, qr, seta (mais
  "ciclo" no exemplo). Para outro ícone, acrescente um desenho de traço 24×24 em
  `_ICONES`.
- Gere com `python montar.py --guias` (linha de corte + margem de 5 mm) e renderize com
  `<skill>/scripts/previa_svg.sh saida/flyer-frente.svg saida/frente.png`. **Olhe as
  imagens** antes de seguir: sobreposição, texto fora da margem, XML inválido (o
  Chrome mostra uma página de erro em vez da arte).

### 5. Crítica do designer

**Retome o mesmo agente de design** (SendMessage), em vez de criar um novo, com os PNGs
e o modelo 4. Ele aplica o próprio checklist e devolve correções numéricas. Aplique,
renderize de novo e confira. Uma rodada costuma bastar.

### 6. PDF para a gráfica + validação

`python montar.py --pdf` chama `gerar_pdf`. Se houver picote, gere também a variante
"sem picote", com a linha de recorte impressa (parâmetro na função `frente`).

Valide sempre e leia o resultado:
```bash
<pasta>/.venv/bin/python <skill>/scripts/validar_pdf.py <pasta>/saida/flyer-grafica.pdf --qr <url1> <url2> … --saida <pasta>/saida/prev
```
O script sai com erro se encontrar RGB, fonte, transparência, tinta acima de 300%,
caixas faltando ou QR ilegível. Abra uma prévia `-tela.png` de cada página. O fundo
C60 K100 aparece azulado na prévia; é só a conversão de tela (avise o usuário).

### 7. Entrega

Deixe na pasta do trabalho:
- o PDF da gráfica (+ variante sem picote);
- os SVG editáveis e as prévias PNG;
- `LEIA-ME-GRAFICA.md`: o que mandar, formato, papel, picote, tabela CMYK, prova de cor;
- os 3 documentos dos agentes. Com o `montar.py`, eles permitem regerar quando um texto
  mudar.

Mostre as prévias ao usuário. Diga o que depende de terceiros: dado não confirmado,
prova física, teste dos QR no celular, picote.

## Princípios

- **Nada inventado**: todo texto sai do usuário ou dos arquivos dele; o que não está
  confirmado não vai impresso como promessa.
- **Ética**: nada de "parabéns, você ganhou", urgência falsa, "grátis" em destaque nem
  carimbos falsos. Isso faz o impresso parecer golpe, e o público descarta.
- **O PDF é o arquivo da gráfica**; o SVG é fonte editável. Não entregue PDF convertido
  de RGB.
- **Downloads**: o PDF/X-1a não precisa de perfil ICC. Se algo exigir baixar (perfil
  FOGRA39 para PDF/X-4, fonte), peça permissão ao usuário antes.
