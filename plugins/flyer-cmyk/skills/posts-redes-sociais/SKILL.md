---
name: posts-redes-sociais
description: >-
  Cria posts, banners e artes promocionais para redes sociais e meios digitais (Instagram
  feed e Stories, Facebook, WhatsApp, LinkedIn, X, capa de YouTube) gerados com IA de
  imagem, com o texto, o logo e as fotos do próprio usuário como referência, para qualquer
  campanha (inauguração, promoção, evento, lançamento). Guia o usuário passo a passo,
  guarda tudo num briefing e trabalha com agentes de marketing, psicologia de marketing e
  direção de arte; gera variações em vários formatos no tamanho exato de cada rede, confere
  o texto da imagem e entrega legenda, hashtags e texto alternativo. Use sempre que o
  usuário pedir "post para Instagram", "banner para redes sociais", "arte para o feed",
  "story", "imagem para divulgar no WhatsApp", "post do LinkedIn" ou um flyer digital. Se
  for para imprimir, use a skill impresso-grafica.
---

# Posts para redes sociais com IA

Peças digitais (RGB, pixels) feitas inteiras pela IA de imagem: visual, texto e logo,
com o material do usuário como referência. É bem mais rápido que o impresso: cerca de
10 a 20 minutos, contra 30 a 60, porque não há vetor, CMYK, sangria nem PDF.

A qualidade vem de três coisas:
1. **Briefing completo antes de gerar:** perguntas passo a passo, tudo gravado; a geração
   acontece só no final.
2. **Agentes:** marketing e psicologia definem o que dizer; um diretor de arte transforma
   isso em prompts precisos por formato.
3. **Referências reais:** o logo, as fotos e o produto do usuário vão junto para o modelo.
   Testado: com o logo como imagem de referência, o modelo da OpenAI reproduz a marca com
   fidelidade, e o texto em português sai certo, com acentos. Mesmo assim, **tudo é
   conferido** antes da entrega.

**Plataforma:** macOS (o `preparar_referencia.py` usa o Chrome para SVG). `<skill>` = a
pasta deste SKILL.md; `<pasta>` = a pasta do trabalho do usuário.

## Recursos

| Arquivo | Para quê |
|---|---|
| `scripts/gerar_imagem.py` | `gerar` (sem referência) e `editar` (com imagens de referência: logo, fotos, produto) com `--px LxA`; provedor openai (modelo `auto` = melhor da conta), google, stability; chave no `.env` |
| `scripts/preparar_referencia.py` | Converte o material do usuário (SVG, PDF, HEIC, JPG, PNG) em PNG pronto para servir de referência |
| `scripts/finalizar_post.py` | Corta e reduz para o tamanho exato de cada formato (`--listar` mostra todos); salva PNG e JPG em sRGB, prévia das áreas seguras e prévia de celular |
| `assets/briefing-social.modelo.md` | Modelo do `briefing.md` |
| `assets/env.exemplo` | Modelo do `.env` |
| `references/formatos-redes.md` | Tamanhos, proporções, áreas seguras e boas práticas por rede |
| `references/prompts-agentes-social.md` | Prompts dos agentes (marketing, psicologia, diretor de arte) e da conferência. **Leia antes de disparar os agentes** |

## Fluxo

Mantenha uma lista de tarefas com estas etapas. No início, diga ao usuário que o processo
leva de 10 a 20 minutos e que ele vai responder perguntas curtas; as imagens só são
geradas no final, depois que tudo estiver definido.

### 0. Destino da peça

Se o pedido não deixar claro, pergunte primeiro (múltipla escolha):
- **Redes sociais / digital** (recomendado para post, story, WhatsApp): siga esta skill.
- **Impressão** (gráfica): use a skill `impresso-grafica`.
- **Ambos**: faça o impresso pela `impresso-grafica` e, com o mesmo `briefing.md` e os
  documentos dos agentes, gere aqui os posts. Assim, mensagem e identidade ficam
  coerentes e não se pergunta nada duas vezes.

### 1. Decisões guiadas

Com a ferramenta de perguntas de múltipla escolha (`AskUserQuestion`), até 4 por rodada,
**recomendada primeiro**:
- **Onde vai publicar** (múltipla): Instagram feed 4:5 (recomendado) · Instagram Stories
  ou Reels 9:16 · Facebook · WhatsApp (status ou envio) · LinkedIn · outro (X, capa de
  YouTube, medida personalizada em px). Veja `references/formatos-redes.md`.
- **Quantas variações** por formato: 2 (recomendado, para escolher ou fazer teste A/B) ·
  1 · 3.
- **Estilo visual:** deixar o diretor de arte propor (recomendado) · vibrante · elegante ·
  minimalista · igual a uma referência que o usuário mandar.
- **Provedor de IA:** OpenAI (recomendado, testado) · Google Gemini · Stability AI. A
  chave fica no `.env` da `<pasta>`: copie `assets/env.exemplo` para `<pasta>/.env` e deixe
  o usuário preencher. **Nunca peça, imprima nem grave a chave.** Se a variável já existir
  no ambiente, o script a usa. Avise que cada imagem tem custo no provedor.

### 2. Materiais e conteúdo (passo a passo, tudo no briefing)

Crie a `<pasta>` com `materiais/`, `referencias/`, `geradas/` e `entrega/`, e copie
`assets/briefing-social.modelo.md` como `briefing.md`. Trabalhe **um assunto por vez** e
grave cada resposta no `briefing.md` (a fonte da verdade; se a sessão cair, retome por
ele). Procure no projeto antes de perguntar.

- **2a. Materiais do usuário** (múltipla escolha): logo, fotos (local, produto, equipe),
  peças anteriores ou referência de estilo, frases prontas, fontes de informação (site,
  PDF, cardápio), nada.
- **2b. Logo:** peça o arquivo (SVG de preferência; PNG com fundo transparente serve).
  Prepare com `preparar_referencia.py`. Pergunte se há versão para fundo claro e para
  escuro e qual usar. **O logo do usuário sempre vai como referência**; nunca deixe a IA
  inventar um logo. Sem logo: o nome da empresa vai em texto simples e limpo, e diga isso
  ao usuário.
- **2c. Cada foto, uma por vez:** abra, diga o que vê (resolução, problemas) e pergunte a
  intenção: usar como referência fiel (o modelo mantém pessoas e objetos) · usar só como
  inspiração · não usar. Pessoas reais identificáveis: confirme que o usuário tem direito
  de uso da imagem.
- **2d. Fontes de informação:** leia por inteiro (site, PDF) e extraia os fatos com a
  origem. Mostre o que extraiu e confirme.
- **2e. Conteúdo que falta**, em grupos curtos:
  - empresa, ramo, cidade; objetivo e a **1 ação** do post;
  - oferta, datas, preços, condições; **o que não está confirmado** (não vai no post);
  - contatos: endereço, WhatsApp, @ da rede, site;
  - cores da marca (hex) e tom de voz;
  - frases do usuário (ficam como estão, salvo ok dele).

Para teste ou demonstração com dados fictícios, use dados obviamente fictícios
(`example.com`, `(00) 00000-0000`).

Antes de seguir, **mostre o resumo do briefing e peça confirmação**.

### 3. Agentes (em paralelo) e diretor de arte

Dispare **marketing** e **psicologia** juntos (modelos 1 e 2 de
`references/prompts-agentes-social.md`); são versões curtas, para feed e celular. Depois, o
**diretor de arte** (modelo 3) escreve **um prompt por formato e variação**, com o texto
exato, as referências e as áreas seguras. Avise o usuário que essa etapa leva alguns
minutos.

### 4. Geração (no final, com tudo definido)

Para cada prompt do diretor de arte:
```bash
cd <pasta> && .venv/bin/python <skill>/scripts/gerar_imagem.py editar \
  --imagem referencias/logo.png referencias/foto-1.png \
  --px 1080x1350 --prompt "<prompt>" --saida geradas/feed-v1.png
```
- Com referência (logo e fotos), use `editar`; sem nenhuma referência, `gerar --permitir-texto`.
- `--px` é o tamanho final do formato; o script gera no múltiplo de 16 logo acima.
- `--escala 1.5` deixa o texto miúdo mais nítido (custa mais); use em Stories com muito
  texto.
- Cerca de 30 a 40 s por imagem. Diga ao usuário o modelo usado (o script mostra) e
  quantas imagens serão geradas.

Ambiente na primeira vez:
`python3 -m venv <pasta>/.venv && <pasta>/.venv/bin/pip install -q -r <skill>/scripts/requirements.txt`

### 5. Conferência obrigatória (você mesmo, olhando cada imagem)

Abra cada imagem gerada e confira, item por item, contra o `briefing.md`:
1. **Texto:** cada palavra, acento, número, preço, data, horário, telefone, @ e endereço,
   letra por letra. Nenhuma palavra a mais ou inventada.
2. **Logo:** igual à referência (forma, cores, letras, proporção), sem distorção nem
   duplicado.
3. **Fotos de referência:** pessoas e produto mantidos, sem deformação (mãos, rostos,
   objetos).
4. **Áreas seguras e respiro:** nada importante nas faixas da interface (Stories) nem
   colado na borda.
5. **Diretrizes da psicologia:** inclusão, nada de promessa irreal, contraste e
   legibilidade no celular (`finalizar_post.py` gera a prévia de 360 px).

Errou algo: corrija **só o trecho** com `editar` (passe a própria imagem gerada como
1ª referência e peça a correção pontual) ou gere de novo com o prompt ajustado. Até 3
tentativas por peça; se persistir, diga ao usuário o que não ficou bom. **Nunca entregue
imagem com texto ou logo errado.**

### 6. Finalizar e entregar

```bash
.venv/bin/python <skill>/scripts/finalizar_post.py geradas/feed-v1.png --formato instagram-feed --saida entrega/instagram-feed-v1
```
Para cada peça aprovada, ficam:
- `.png` e `.jpg` no tamanho exato, em sRGB;
- prévia das áreas seguras;
- prévia de celular.

Mostre as peças ao usuário (lado a lado, com as variações) e entregue também, em
`entrega/textos.md`:
- **legenda** por rede (com a chamada para ação e o texto legal ou condições, que não
  cabem na imagem);
- **hashtags** (poucas e relevantes);
- **texto alternativo** (acessibilidade) de cada imagem, **escrito ou revisado a partir da
  imagem final**. O que o marketing escreveu antes da geração costuma citar textos que o
  diretor de arte cortou, e texto alternativo que não bate com a imagem engana quem usa
  leitor de tela.

Avise que as imagens são geradas por IA: algumas redes pedem que conteúdo gerado ou
alterado por IA seja sinalizado, conforme o caso. Se a imagem sugerir algo real (o local,
um produto), inclua "imagens meramente ilustrativas" na legenda.

## Princípios

- **Nada inventado:** todo texto vem do briefing; o que não está confirmado não aparece.
- **Material do usuário primeiro:** logo, fotos e frases dele são referência obrigatória
  quando existem.
- **Ética:** sem urgência falsa, sem "de/por" sem preço real anterior, sem corpo ou
  resultado irreal, sem imagem de IA se passando por foto real do local.
- **Chave só no `.env`**, fora do git. Downloads só com permissão do usuário.
