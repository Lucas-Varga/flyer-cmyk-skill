---
name: impresso-grafica
description: Cria flyers e peças impressas promocionais prontas para a gráfica (flyer, panfleto, folder, cartão, cartaz, voucher, convite, cardápio, canhoto destacável) para qualquer campanha, como inauguração, promoção, evento, lançamento ou indicação. Guia o usuário nas decisões de formato (A6, A5, A4, DL, 10x15, quadrado ou medida personalizada), papel, acabamentos especiais (verniz UV localizado, hot stamping, relevo, tinta branca, faca especial) e geração opcional de imagens com IA (OpenAI, Google, Stability, com a chave no .env). Usa agentes de marketing, psicologia de marketing e design e gera a arte com cores CMYK e Pantone, degradês, efeitos em texto e foto e texto em curvas, mais o PDF/X-1a validado para impressão. Use sempre que o usuário pedir algo para imprimir: "flyer para a gráfica", "panfleto", "arte em CMYK", "PDF para impressão", "folder", "cartaz", "material impresso da campanha", "flyer de inauguração", mesmo que não diga "skill" nem "gráfica".
---

# Impresso para gráfica

Leva o usuário da ideia ao PDF que a gráfica aceita, com qualidade profissional. Esta skill
existe porque impressos feitos com ferramentas de tela falham de três formas:

1. **Conteúdo e persuasão**: o que dizer, em que ordem, sem cara de golpe. Isso fica com
   agentes de marketing e de psicologia de marketing.
2. **Layout exato**: um designer concilia os dois e entrega a arte em medidas de
   milímetro; depois critica a arte renderizada.
3. **Cor de impressão real**: tela e SVG falam RGB, e converter no fim estraga o preto
   e a cor da marca. Aqui cada objeto nasce em CMYK (ou Pantone), e o PDF é desenhado
   direto em CMYK.

**Plataforma:** macOS. Fotos são convertidas com o `sips`, a prévia usa o Google Chrome e
as fontes do sistema estão em `/System/Library/Fonts`. Em Linux ou Windows, avise o
usuário e siga as alternativas do README do repositório.

`<skill>` = a pasta deste SKILL.md. `<pasta>` = a pasta do trabalho do usuário.

## Recursos

| Arquivo | Para quê |
|---|---|
| `scripts/impressao.py` | Biblioteca da arte: `Arte` (face em mm), `formato()`, `FORMATOS`, `PAPEIS`, `Cmyk` (processo ou `spot=` Pantone), `Degrade` (linear/radial), `Fonte` (TTF/OTF/WOFF2/TTC, texto em curvas), texto com `contorno=`/`sombra=`, `forma()` (qualquer path), QR, logo SVG, `imagem(efeitos=)`, ícones, `with arte.acabamento(tipo)` |
| `scripts/pdf_cmyk.py` | `gerar_pdf(...)`: PDF/X-1a CMYK (+ Pantone como Separation, degradês como shading) com marcas de corte; e o PDF de **máscaras de acabamento** |
| `scripts/validar_pdf.py` | Confere o PDF: caixas, RGB, fontes, transparência, tinta máxima pelo papel, cores especiais, QR. `--mascara` para o PDF de acabamentos |
| `scripts/gerar_imagem.py` | Imagens: `gerar` (nova com IA), `editar` (altera ou recria imagem do usuário com IA), `melhorar` (local sem IA, ou `--ia`). Provedores openai (modelo `auto` = melhor da conta) / google / stability; chave lida do `.env`; tamanho calculado para o dpi de impressão |
| `assets/briefing.modelo.md` | Modelo do `briefing.md`: decisões, materiais, tratamento de cada imagem, conteúdo, produção |
| `scripts/previa_svg.sh` | SVG → PNG (Chrome headless) |
| `assets/exemplo/` | Exemplo executável (empresa fictícia): `montar.py` + `marca/` |
| `assets/env.exemplo` | Modelo do `.env` com os nomes das chaves |
| `references/prompts-agentes.md` | Prompts dos agentes (marketing, psicologia, design com direção de imagem) e da crítica. **Leia antes de disparar os agentes** |
| `references/producao-grafica.md` | Regras de cor, papel, formatos, degradês, Pantone, acabamentos, efeitos, imagens de IA, PDF/X, medidas mínimas e armadilhas. **Leia antes de definir a paleta e antes de entregar** |

## Fluxo

Mantenha uma lista de tarefas com estas etapas; o usuário acompanha por ela. Fale com ele
em linguagem simples: ele pode não ser da área gráfica. Logo no início, diga quanto
tempo o processo leva no total (cerca de 30 a 60 minutos, a maior parte com os agentes
trabalhando sozinhos) e quais etapas vão pedir alguma ação dele (decisões, dados,
aprovação das imagens e da arte).

### 1. Decisões guiadas

Faça as perguntas de decisão com a ferramenta de perguntas de múltipla escolha
(`AskUserQuestion`; sem ela, uma lista numerada curta). Até 4 perguntas por rodada,
**a opção recomendada primeiro** e uma linha de consequência em cada opção (custo,
efeito, quando usar). Não pergunte o que o pedido ou os arquivos já respondem.

**Rodada 1:**
- **Formato:** A5 148×210 (recomendado: o mais comum para flyer de mão) · A6 105×148
  (econômico, distribuição em massa) · A4 210×297 (mais informação, cartaz pequeno) ·
  outro. Em "outro", ofereça DL 99×210, 10×15, 15×21, 20×28, quadrado 15×15 ou 21×21,
  cartão 90×50, ou **medida personalizada em mm** (largura × altura; sem limite além
  da folha da gráfica).
- **Faces:** frente e verso (recomendado: a frente atrai, o verso informa) · só frente.
- **Papel:** couché (recomendado: cores vivas, foto bonita) · offset/não revestido
  (sulfite, reciclado: cores mais suaves, aceita caneta).
- **Imagens com IA:** não usar (recomendado se houver fotos reais boas) · sim, OpenAI ·
  sim, outro provedor (Google Gemini ou Stability AI).

**Rodada 2** (só o que fizer sentido):
- **Acabamentos especiais** (múltipla escolha; cada um encarece a tiragem): nenhum ·
  verniz UV localizado (brilho em título/logo/foto) · hot stamping (metalizado
  dourado/prata) · relevo seco · tinta branca (papel colorido/kraft) · faca especial
  (corte em formato).
- **Estilo visual:** deixar o designer propor (recomendado) · sóbrio/elegante ·
  vibrante/energético · premium/luxo.
- **Cor Pantone da marca:** só se a marca tiver uma e o usuário quiser imprimir com ela
  (encarece: é uma tinta extra). Senão, use a equivalência CMYK.

**Se escolher IA:** explique que a chave fica num arquivo `.env` na `<pasta>`, nunca no
chat. Copie `<skill>/assets/env.exemplo` para `<pasta>/.env`, deixe a linha do provedor
para o usuário preencher (OPENAI_API_KEY, GEMINI_API_KEY ou STABILITY_API_KEY) e
garanta que `.env` está no `.gitignore` da pasta. **Nunca peça, leia em voz alta, imprima
nem grave a chave você mesmo.** Se a variável já existir no ambiente, o script a usa e
o `.env` é dispensável. Avise que cada imagem tem custo no provedor.

### 2. Materiais, conteúdo e ativos (passo a passo)

Trabalhe **um assunto por vez**. A cada resposta, **grave em `<pasta>/briefing.md`**
(modelo em `assets/briefing.modelo.md`): decisões, dados, materiais recebidos, o que foi
feito com cada um e o que falta. O `briefing.md` é a fonte da verdade:
- os agentes leem dele;
- se a sessão cair, retome de onde ele parou;
- antes de seguir para os agentes, mostre o resumo ao usuário e peça confirmação.

Procure no projeto antes de perguntar. A ordem:

**2a. Materiais do usuário.** Pergunte (múltipla escolha, pode marcar vários) se ele
tem material para usar como base:
- **imagens**: fotos do local, produto, equipe, logo, artes antigas, referências de
  estilo;
- **frases**: slogan, chamadas, textos já aprovados;
- **fontes de informação**: link de site, PDF, cardápio, tabela de preços,
  regulamento;
- nada.

Peça que coloque os arquivos em `<pasta>/materiais/` ou informe o caminho/link.

**2b. Cada fonte de informação.** Leia por inteiro: o link com a ferramenta de leitura
de páginas, o PDF com a leitura de PDF. Extraia para o `briefing.md` só os fatos úteis
à campanha, **com a origem de cada um** (arquivo/página/URL). Mostre o que extraiu e
pergunte se está certo e completo. Nada entra na peça sem estar no briefing.

**2c. Cada imagem, uma por vez.** Abra e olhe. Diga ao usuário o que vê:
- tamanho em pixels;
- resolução efetiva no tamanho provável de uso (≥ 300 ppi ótimo, 200–300 aceitável,
  < 200 fraco);
- problemas: escura, tremida, ruído, fundo poluído, marca d'água, pessoas
  identificáveis.

Pergunte a intenção, com a recomendação primeiro conforme o diagnóstico:
- **usar como está**;
- **melhorar a qualidade**:
  - `melhorar` local, sem IA: não muda o conteúdo; recomendado para foto real do
    local ou produto;
  - `melhorar --ia`: recupera mais detalhe, mas pode alterar pequenos detalhes;
- **alteração específica com IA** (`editar`): trocar ou limpar o fundo, remover objeto,
  ajustar luz e cor, ampliar o cenário, mudar a estação. Peça a instrução em palavras;
- **recriar com IA** usando a imagem como referência (`editar` com um prompt de
  recriação): mantém a ideia e a composição e melhora a produção;
- **só referência de estilo** para o designer (não entra na arte).

Execute com o provedor que o usuário escolheu (`scripts/gerar_imagem.py`; ver a etapa
5). Com a OpenAI, o `--modelo auto` usa o melhor modelo da conta: a versão mais nova,
variante de qualidade. Mostre o antes e depois e só siga com a aprovação dele. Grave no
briefing: arquivo final, o que foi feito, modelo, aprovado sim/não. Foto real do local
editada por IA: avise que não pode mostrar algo que o local não tem.

**2d. Frases do usuário.** Registre como estão. O marketing pode sugerir ajustes, mas
frase aprovada pelo usuário só muda com o ok dele.

**2e. O que ainda faltar**, em perguntas curtas, um grupo por vez:
- **Empresa:** nome, ramo, cidade, diferencial verdadeiro.
- **Peça:** objetivo e a **1 ação** que ela deve provocar; para quem; onde é entregue.
- **Oferta e regras:** o que se ganha, condições, datas e vigência, limites; **o que
  ainda não está confirmado** (não vai impresso como promessa).
- **Contatos e links:** endereço, horário, WhatsApp/telefone, site, redes, links para os
  QR codes.
- **Texto legal**, se houver.
- **Identidade:** logo em **SVG vetorial** (claro e escuro), cores da marca, fontes
  (arquivos). Sem fontes da marca, proponha fontes do sistema e diga quais
  (`Fonte.faces(arquivo)` lista as faces de um `.ttc`). Logo só em PNG/JPG: ofereça
  vetorizar (redesenhar como formas simples) ou usar como imagem, avisando da perda de
  nitidez.

Para um teste ou demonstração, o usuário pode pedir dados fictícios. Nesse caso, use
dados obviamente fictícios: domínio `example.com`, telefone `(00) 0000-0000`, endereço
genérico.

**Monte a `<pasta>` antes da etapa 2a** (os materiais e o briefing vão para ela):
- copie `<skill>/assets/exemplo/` (fica com `montar.py` e `marca/`);
- copie `<skill>/scripts/impressao.py` e `pdf_cmyk.py` para a raiz;
- copie `<skill>/assets/briefing.modelo.md` como `briefing.md`;
- crie `materiais/` (o que o usuário traz), `fotos/` (imagens finais da arte) e
  `fontes/`;
- crie o ambiente:
  ```bash
  python3 -m venv <pasta>/.venv && <pasta>/.venv/bin/pip install -q -r <skill>/scripts/requirements.txt
  ```

### 3. Agentes de marketing e de psicologia (em paralelo)

Dispare os dois na mesma mensagem com os modelos 1 e 2 de
`references/prompts-agentes.md`. Inclua as decisões da etapa 1 (formato, faces, papel,
acabamentos, estilo). Ao receber, resolva você as dúvidas factuais que eles deixarem,
consultando o projeto ou o usuário.

### 4. Designer: especificação em mm + direção de arte

Dispare o designer (modelo 3) depois dos dois. **Avise o usuário antes**: esta é a
etapa mais demorada (costuma levar de 10 a 20 minutos, porque o designer mede cada
linha com as fontes reais e posiciona tudo em mm) e ele não precisa fazer nada
enquanto isso. Se ele perguntar no meio, diga em que etapa está e o que vem depois.
Ele devolve `03-design.md` com:
- paleta CMYK/Pantone e degradês;
- estilos de texto e efeitos;
- **todos os elementos em mm** a partir do canto de corte, com quebras de linha
  explícitas e conta de altura;
- **camadas de acabamento**;
- **briefing de cada imagem** (prompt em inglês, tamanho em mm, onde fica o espaço livre
  para texto);
- notas de produção e checklist.

Dê a ele o comando para medir texto com as fontes reais (está no modelo).

### 5. Imagens com IA (se escolhido)

Para cada imagem do briefing do designer:
```bash
cd <pasta> && .venv/bin/python <skill>/scripts/gerar_imagem.py gerar --provedor openai \
  --prompt "<prompt do designer>" --mm <L>x<A> --saida fotos/<nome>.png
```
Para imagens do usuário (etapa 2c), use os modos `editar` e `melhorar`:
```bash
.venv/bin/python <skill>/scripts/gerar_imagem.py editar --imagem materiais/<foto> \
  --prompt "<instrução>" --mm <L>x<A> --saida fotos/<nome>.png
.venv/bin/python <skill>/scripts/gerar_imagem.py melhorar --imagem materiais/<foto> \
  --mm <L>x<A> --saida fotos/<nome>.png          # local, sem IA (acrescente --ia para IA)
```
Antes de gerar, diga ao usuário o modelo que será usado (o script mostra) e que cada
chamada tem custo.
**Abra e olhe cada imagem** antes de usar. Refaça (até 2 vezes, ajustando o prompt) se
houver:
- texto, letras ou logos inventados;
- mãos ou rostos deformados;
- objetos impossíveis ou equipamento torto;
- falta de espaço livre onde o texto vai;
- tom que não combina com a paleta.

Abaixo de 200 ppi no tamanho de uso, reduza o quadro ou peça outra imagem. Mostre a
imagem escolhida ao usuário. Coloque "Imagens meramente ilustrativas" no rodapé quando
a imagem gerada sugerir algo real (ambiente, produto, pessoas).

### 6. Implementar literalmente

Adapte o `montar.py`: `DADOS`, a paleta (`Cmyk`), os estilos (`(Fonte, pt, rastreio,
caixa_alta)`) e uma chamada por elemento da especificação. A classe `Face` soma a
sangria às coordenadas de corte. Recursos (detalhes em `producao-grafica.md`):

| Efeito | Como |
|---|---|
| Degradê | `Degrade([(0, corA), (1, corB)], inicio=(x, y), fim=(x, y))` ou `tipo='radial', centro=, raio=`, como `cor` de `ret`, `circulo`, `forma` ou `texto` |
| Pantone | `Cmyk('Marca', c, m, y, k, '#hex', spot='PANTONE 186 C')` (alternativa CMYK para a prova) |
| Texto com contorno / sombra | `texto(..., contorno=(cor, mm), sombra=(dx, dy, cor))` |
| Formas livres | `forma('M… path SVG em mm …', cor)`: faixas inclinadas, selos, blobs |
| Foto em 2 cores / velada / fundida | `imagem(..., efeitos=[('duotone', escura, clara)], [('escurecer', cor, 0.4)], [('fade', 'baixo', cor, 0.5, 1)])` |
| Verniz, hot stamping, relevo, branco, faca | `with arte.acabamento('verniz-uv'): …` (repita a forma ou o texto que recebe o acabamento) |

Gere com `python montar.py --guias` e renderize com `<skill>/scripts/previa_svg.sh`.
**Olhe as imagens**. Procure:
- sobreposição ou texto fora da margem de 5 mm;
- contraste ruim;
- erro de digitação;
- XML inválido (aparece a página de erro do Chrome).

Os avisos de `arte.avisos` (QR pequeno, foto com pouca resolução) precisam ser
resolvidos.

### 7. Crítica do designer

**Retome o mesmo agente de design** (SendMessage) com os PNGs e o modelo 4. Inclua a
prévia com os acabamentos simulados (`svg(simular_acabamentos=True)`). Aplique as
correções numéricas e renderize de novo. Uma rodada costuma bastar; faça outra se ainda
houver erro visível.

### 8. PDF, validação e entrega

`python montar.py --pdf` gera `flyer-grafica.pdf` e, se houver acabamentos,
`flyer-grafica-acabamentos.pdf` (uma página K100 por acabamento e face, alinhada à
arte). Valide os dois e leia o resultado:
```bash
<pasta>/.venv/bin/python <skill>/scripts/validar_pdf.py saida/flyer-grafica.pdf --qr <urls…> --saida saida/prev
<pasta>/.venv/bin/python <skill>/scripts/validar_pdf.py saida/flyer-grafica-acabamentos.pdf --mascara --saida saida/prev
```
O validador sai com erro se encontrar:
- RGB, fonte viva ou transparência;
- tinta acima do limite do papel;
- caixas faltando;
- QR ilegível;
- máscara com cor.

Antes de entregar, **revise todo o texto renderizado** (ortografia, datas, telefone,
endereço, preço): erro impresso não tem volta.

Deixe na `<pasta>`:
- os PDFs;
- os SVG editáveis (com camadas do Inkscape);
- as prévias, incluindo uma com acabamentos simulados;
- os 3 documentos dos agentes;
- o `montar.py`;
- `LEIA-ME-GRAFICA.md`: formato, papel, cores especiais, acabamentos e como estão nos
  arquivos, prova de cor.

Mostre as prévias ao usuário e diga o que depende de terceiros: prova física, teste dos
QR no celular, orçamento dos acabamentos.

## Limites

- **PDF/X-1a não tem transparência.** Sombra suave, brilho difuso e sobreposições
  semitransparentes ficam de fora; resolva com:
  - sombra sólida;
  - degradê;
  - o efeito já pronto dentro da foto (fade/escurecer ou na imagem gerada).

  O PDF/X-4 permitiria transparência, mas exige baixar o perfil ICC; peça permissão ao
  usuário antes.
- Fotos são convertidas com o perfil CMYK genérico do sistema; para cor crítica,
  recomende a conversão pela gráfica.
- Texto alinhado à esquerda, ao centro ou à direita; sem justificar nem hifenizar.

## Princípios

- **Nada inventado**: todo texto vem do usuário (ou é fictício, se ele pediu um teste).
- **Ética**: nada de urgência falsa, "parabéns, você ganhou", preço riscado sem preço real
  anterior, nem imagem de IA apresentada como foto real do local.
- **O PDF é o arquivo da gráfica**; o SVG é a fonte editável.
- **Chaves e downloads**: chave só no `.env` e fora do git; baixar qualquer coisa
  (perfil, fonte) só com permissão.
