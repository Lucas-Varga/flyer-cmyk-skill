# 03 · Direção de arte: inauguração da Ápice Academia (redes)

Fontes: `briefing.md`, `01-marketing-social.md` (textos), `02-psicologia-social.md` (limites,
contraste, áreas seguras). Empresa e dados **fictícios**. Modelo: OpenAI `gpt-image-2.6-sunburst`,
modo edição com imagens de referência.

## 1. Conceito visual e paleta

**Conceito:** "A noite antes do grande dia": o azul-noite do flyer como palco, a turma real de bike
indoor como prova de que o lugar é para gente comum, e uma única faixa diagonal laranja→âmbar que
risca a tela como um convite: INAUGURAÇÃO.

| Papel | Cor | Uso | Proporção |
|---|---|---|---|
| Base | azul-noite `#0B1A2A` | fundo, véu sobre a foto (60–85% de opacidade), texto da faixa | ~60% |
| Texto | branco `#FFFFFF` | título, data, apoio, aviso | ~30% (com a foto) |
| Destaque | laranja `#E05F31` → âmbar `#EC9638` (degradê) | **só** a faixa diagonal "INAUGURAÇÃO" (+ o pico do logo) | ≤ 10% |

O logo (`logo-escuro.png`) mantém as próprias cores (o laranja dele não é recolorido). Contrastes:
branco/azul-noite ≈ 17:1; azul-noite/âmbar ≈ 7,5:1; azul-noite/laranja ≈ 4,9:1 (só texto grande
e bold). Nenhum texto laranja ou âmbar; nenhum texto pequeno sobre a faixa.

### Reconciliação marketing × psicologia (decisões desta direção)

O `01` lista mais texto do que os limites do `02` permitem (feed ≤ 20, Stories ≤ 15, LinkedIn ≤ 14
palavras na imagem, contando o aviso). Prevalecem os limites e a regra de transparência; todo texto
abaixo é cópia literal (ou trecho literal) do `01`, e o resto vai para a legenda:

- **Contagem:** toda sequência separada por espaço conta 1 palavra ("R$" conta; "·", "–", "+", "*"
  não contam). O aviso conta.
- **Aviso:** usa-se "Imagem ilustrativa." (forma do `02`, 2 palavras); a forma longa "Imagens
  meramente ilustrativas" fica na legenda.
- **Feed:** saem da imagem o endereço, o WhatsApp, o CTA e o selo de oferta (ficam na legenda, como
  manda o `02`). O teste A/B continua medindo só o ângulo: v1 = título do evento + "Sem
  compromisso."; v2 = título de preço + linha de transparência no **mesmo lugar**.
- **v2/Stories B:** "R$ 49,90" nunca aparece sem "*Plano mensal; depois, R$ 119,90/mês." colado e
  em ≥ 50% do tamanho (regra de transparência).
- **Stories:** o CTA é a figurinha nativa de link ("Chamar no WhatsApp"), aplicada no app; a arte
  só reserva uma área vazia para ela. "Sábado," sai para caber em 15 palavras.
- **LinkedIn:** sem preço; "Sábado," sai para caber em 14 palavras; CTA e endereço vão no post.

| Peça | Palavras | Contagem |
|---|---|---|
| feed-v1 | 18 | 1 + 6 + 2 + 7 + 2 |
| feed-v2 | 20 | 1 + 5 + 5 + 7 + 2 |
| stories (A, se v1) | 15 | 1 + 6 + 6 + 2 |
| stories (B, se v2) | 15 | 1 + 4 + 5 + 3 + 2 |
| linkedin | 14 | 1 + 5 + 6 + 2 |

---

## 2. Prompts por peça

### feed-v1

- **id:** `feed-v1` · ângulo EVENTO
- **Formato:** instagram-feed, 4:5, **1080×1350 px**
- **Referências (ordem e papel):**
  1. IMAGE 1 = `referencias/logo-escuro.png`, logo fiel (PNG transparente).
  2. IMAGE 2 = `referencias/foto-bike.png`, foto principal (manter as pessoas).

```text
Create a finished Instagram feed post, vertical 4:5 portrait, 1080 x 1350 pixels, for the grand opening of a neighborhood gym. Vibrant, energetic but welcoming, premium graphic design with a dark night-blue base. Flat, clean, sharp typography; photographic realism in the photo.

LOGO: Reproduce the logo from IMAGE 1 EXACTLY (same orange peak mark, same "ÁPICE" lettering in white, same "ACADEMIA" in orange underneath, same proportions and colors); do not redraw, restyle or invent any other logo. Place it once, horizontally centered at the top, with its top edge at about 6% of the canvas height; logo width about 30% of the canvas width. It sits on a dark night-blue (#0B1A2A) veil so it is fully legible. The logo appears only once.

PHOTO: Use IMAGE 2 as the main photo, keeping the people exactly as they are: same faces, ages, body types, skin tones, genders, hair, clothes and expressions; do not slim, retouch, rejuvenate, add muscle definition or change any person. The photo fills the full width of the upper part of the canvas, from the top edge down to about 60% of the height. Frame it so every face is complete and none is cut by an edge or covered by text or the logo. A night-blue #0B1A2A gradient veil darkens the top 20% (behind the logo, at least 70% opacity) and the bottom of the photo melts smoothly into solid #0B1A2A between about 45% and 62% of the height. Warm, clean light; no dramatic sweat.

LAYOUT (top to bottom):
1. Logo (top center, as above).
2. Photo (upper 60%).
3. At about 58% to 67% of the height, one bold diagonal band, tilted about 4 degrees upward to the right, bleeding off both side edges, filled with a smooth gradient from orange #E05F31 (left) to amber #EC9638 (right). Inside it, centered, the word INAUGURAÇÃO in a heavy bold condensed sans-serif, all caps, color night-blue #0B1A2A. This is the largest text in the image (cap height about 11% of the canvas width) and the single focal point.
4. Below the band, on solid #0B1A2A, centered: the headline in white #FFFFFF bold condensed sans-serif, two lines, cap height about 4.5% of the canvas width.
5. Directly under the headline, the support line in white, clean regular sans-serif, smaller (about 60% of the headline size).
6. Below that, the date in white bold condensed sans-serif, two lines, about the same size as the headline.
7. At the bottom, the notice in white clean sans-serif, the smallest text (cap height about 2.8% of the canvas width, never smaller), with its baseline at least 6% above the bottom edge.
Hierarchy: INAUGURAÇÃO first, then the date and headline, then the support line, then the notice. Generous spacing between blocks, all text centered.

SAFE AREAS: Keep all text and the logo at least 6% away from every edge, and at least 8% away from the left and right edges so every essential element sits inside the central 3:4 area (the profile grid crop). Only the photo and the diagonal band may bleed to the edges.

TEXT: Render this Brazilian Portuguese text EXACTLY, with all accents, capitalization and punctuation as written, each item on its own line(s) as listed:
- Band: "INAUGURAÇÃO"
- Headline line 1: "Aulas experimentais grátis"
- Headline line 2: "o dia todo"
- Support line: "Sem compromisso."
- Date line 1: "Sábado, 6 de março"
- Date line 2: "8h às 18h"
- Notice: "Imagem ilustrativa."
Spell check: INAUGURAÇÃO (Ç and Ã), grátis (á), março (ç), às (à), Sábado (á). "8h" and "18h" use a lowercase h.

COLOR AND CONTRAST: Only night-blue #0B1A2A, white #FFFFFF, and the orange #E05F31 to amber #EC9638 gradient. Orange/amber appears only in the diagonal band and in the logo's peak, never as text color, outlines or background elsewhere (at most 10% of the area). All text other than INAUGURAÇÃO is white on solid night-blue; any text that overlaps the photo must sit on a night-blue veil of at least 60% opacity. The image must still read clearly in grayscale and at 360 px wide.

RESTRICTIONS: No other text, no extra words, no fake logos, no watermark. Exactly 18 words of text in total; do not add prices, addresses, phone numbers, URLs, @handles, hashtags, emojis, icons, buttons or stickers. No signage, facade, "ÁPICE" lettering or readable text on walls, bikes or clothes in the photo. Keep the real, ordinary, diverse people from the photo; no idealized or bodybuilder bodies, no before/after, no pain or strain expressions. Hands, handlebars, pedals and saddles must be anatomically and mechanically correct.
```

### feed-v2

- **id:** `feed-v2` · ângulo OFERTA (única variável: título + linha de apoio)
- **Formato:** instagram-feed, 4:5, **1080×1350 px**
- **Referências (ordem e papel):**
  1. IMAGE 1 = `referencias/logo-escuro.png`, logo fiel (PNG transparente).
  2. IMAGE 2 = `referencias/foto-bike.png`, foto principal (manter as pessoas).
- Gerar com os mesmos parâmetros do v1 (qualidade, tamanho e, se houver, seed).

```text
Create a finished Instagram feed post, vertical 4:5 portrait, 1080 x 1350 pixels, for the grand opening of a neighborhood gym. Vibrant, energetic but welcoming, premium graphic design with a dark night-blue base. Flat, clean, sharp typography; photographic realism in the photo.

LOGO: Reproduce the logo from IMAGE 1 EXACTLY (same orange peak mark, same "ÁPICE" lettering in white, same "ACADEMIA" in orange underneath, same proportions and colors); do not redraw, restyle or invent any other logo. Place it once, horizontally centered at the top, with its top edge at about 6% of the canvas height; logo width about 30% of the canvas width. It sits on a dark night-blue (#0B1A2A) veil so it is fully legible. The logo appears only once.

PHOTO: Use IMAGE 2 as the main photo, keeping the people exactly as they are: same faces, ages, body types, skin tones, genders, hair, clothes and expressions; do not slim, retouch, rejuvenate, add muscle definition or change any person. The photo fills the full width of the upper part of the canvas, from the top edge down to about 60% of the height. Frame it so every face is complete and none is cut by an edge or covered by text or the logo. A night-blue #0B1A2A gradient veil darkens the top 20% (behind the logo, at least 70% opacity) and the bottom of the photo melts smoothly into solid #0B1A2A between about 45% and 62% of the height. Warm, clean light; no dramatic sweat.

LAYOUT (top to bottom):
1. Logo (top center, as above).
2. Photo (upper 60%).
3. At about 58% to 67% of the height, one bold diagonal band, tilted about 4 degrees upward to the right, bleeding off both side edges, filled with a smooth gradient from orange #E05F31 (left) to amber #EC9638 (right). Inside it, centered, the word INAUGURAÇÃO in a heavy bold condensed sans-serif, all caps, color night-blue #0B1A2A. This is the largest text in the image (cap height about 11% of the canvas width) and the single focal point.
4. Below the band, on solid #0B1A2A, centered: the price headline in white #FFFFFF bold condensed sans-serif, one line, cap height about 5% of the canvas width.
5. Directly under and touching the price headline (no gap larger than half a line), the transparency line in white clean sans-serif, at least 50% of the price headline size and clearly legible; it must read as part of the price, never as fine print.
6. Below that, the date in white bold condensed sans-serif, two lines, about 90% of the price headline size.
7. At the bottom, the notice in white clean sans-serif, the smallest text (cap height about 2.8% of the canvas width, never smaller), with its baseline at least 6% above the bottom edge.
Hierarchy: INAUGURAÇÃO first, then the price headline and the date, then the transparency line, then the notice. Generous spacing between blocks, all text centered.

SAFE AREAS: Keep all text and the logo at least 6% away from every edge, and at least 8% away from the left and right edges so every essential element sits inside the central 3:4 area (the profile grid crop). Only the photo and the diagonal band may bleed to the edges.

TEXT: Render this Brazilian Portuguese text EXACTLY, with all accents, capitalization and punctuation as written, each item on its own line(s) as listed:
- Band: "INAUGURAÇÃO"
- Price headline: "1º mês por R$ 49,90*"
- Transparency line: "*Plano mensal; depois, R$ 119,90/mês."
- Date line 1: "Sábado, 6 de março"
- Date line 2: "8h às 18h"
- Notice: "Imagem ilustrativa."
Spell check: INAUGURAÇÃO (Ç and Ã), "1º" uses the masculine ordinal indicator º (not a degree sign, not "1o"), mês (ê), "R$ 49,90" and "R$ 119,90" use a comma as decimal separator, the asterisk after 49,90 and before "Plano" must both appear, março (ç), às (à), Sábado (á). "8h" and "18h" use a lowercase h.

COLOR AND CONTRAST: Only night-blue #0B1A2A, white #FFFFFF, and the orange #E05F31 to amber #EC9638 gradient. Orange/amber appears only in the diagonal band and in the logo's peak, never as text color, outlines or background elsewhere (at most 10% of the area). The price is white, not orange. All text other than INAUGURAÇÃO is white on solid night-blue; any text that overlaps the photo must sit on a night-blue veil of at least 60% opacity. The image must still read clearly in grayscale and at 360 px wide.

RESTRICTIONS: No other text, no extra words, no fake logos, no watermark. Exactly 20 words of text in total; do not add any other price, no strikethrough price, no "from/to" price, no percentage, no "free month", no addresses, phone numbers, URLs, @handles, hashtags, emojis, icons, buttons or stickers. No signage, facade, "ÁPICE" lettering or readable text on walls, bikes or clothes in the photo. Keep the real, ordinary, diverse people from the photo; no idealized or bodybuilder bodies, no before/after, no pain or strain expressions. Hands, handlebars, pedals and saddles must be anatomically and mechanically correct.
```

### stories

- **id:** `stories` · adaptação da variação de feed aprovada
- **Formato:** instagram-stories, 9:16, **1080×1920 px**
- **Referências (ordem e papel), atenção: a ordem muda nas adaptações:**
  1. IMAGE 1 = **peça de feed aprovada** (`geradas/feed-v1.png` ou `geradas/feed-v2.png`, a final
     conferida), referência de estilo: faixa, cores, tipografia, tratamento da foto.
  2. IMAGE 2 = `referencias/logo-escuro.png`, logo fiel.
  3. IMAGE 3 = `referencias/foto-bike.png`, foto limpa, para reenquadrar sem herdar texto.
- **Texto:** use o bloco **A** se o v1 for aprovado e o bloco **B** se o v2 for aprovado (cole só
  um deles no lugar de `[TEXT BLOCK]`). Depois de gerar, aplique no app a figurinha de link
  "Chamar no WhatsApp" → https://wa.me/5500000000000 na área vazia reservada.

```text
Create a finished Instagram Stories image, vertical 9:16, 1080 x 1920 pixels, for the grand opening of a neighborhood gym. It is a vertical adaptation of the approved feed post shown in IMAGE 1.

REFERENCES: IMAGE 1 is the approved feed post: use it ONLY as the style reference (the same night-blue base, the same orange-to-amber diagonal band with the word INAUGURAÇÃO, the same typefaces, the same photo treatment and mood). Do not copy any of its other text, and do not copy its layout proportions; rebuild the layout for 9:16 as described below. IMAGE 2 is the logo. IMAGE 3 is the clean original photo.

LOGO: Reproduce the logo from IMAGE 2 EXACTLY (same orange peak mark, same "ÁPICE" lettering in white, same "ACADEMIA" in orange underneath, same proportions and colors); do not redraw, restyle or invent any other logo. Place it once, horizontally centered, with its top edge at about 16% of the canvas height (just below the top 14% zone); logo width about 34% of the canvas width, on a night-blue #0B1A2A veil of at least 70% opacity so it is fully legible. Do not take the logo from IMAGE 1; use IMAGE 2.

PHOTO: Use IMAGE 3 as the main photo, keeping the people exactly as they are: same faces, ages, body types, skin tones, genders, hair, clothes and expressions; do not slim, retouch, rejuvenate, add muscle definition or change any person. Reframe it for the vertical format: the photo fills the full width from the top edge down to about 55% of the height. Prefer showing fewer people complete rather than many people cut; no face may be cut by an edge or covered by the logo or text. Do not extend the scene with invented people. A night-blue #0B1A2A veil darkens the top 24% of the photo, and the bottom of the photo melts smoothly into solid #0B1A2A between about 42% and 56% of the height.

LAYOUT (top to bottom):
1. Top 14% (0 to 270 px): photo only, absolutely no text and no logo.
2. Logo at about 16% to 22% of the height.
3. Photo continues down to about 55%.
4. At about 52% to 59% of the height, the bold diagonal band, tilted about 4 degrees upward to the right, bleeding off both side edges, filled with a smooth gradient from orange #E05F31 (left) to amber #EC9638 (right), with INAUGURAÇÃO centered inside in a heavy bold condensed sans-serif, all caps, night-blue #0B1A2A. This is the largest text (cap height about 12% of the canvas width) and the single focal point.
5. From about 61% to 72% of the height, on solid #0B1A2A, centered: the remaining text lines of the text block in white #FFFFFF; headline lines in bold condensed sans-serif (cap height about 5% of the width), the date in bold condensed sans-serif about the same size, any supporting line in clean sans-serif.
6. From about 73% to 80% of the height: an EMPTY calm night-blue area, with nothing in it, reserved for an interactive link sticker that will be added later in the app. Do not draw any button, sticker, arrow or icon there.
7. The notice at about 80% to 81.5% of the height, white clean sans-serif, the smallest text (cap height about 3% of the width).
8. Bottom 18% (1574 to 1920 px): solid night-blue only, absolutely no text and no logo.

SAFE AREAS: Keep all text and the logo at least 6% away from every edge (at least 64 px from the left and right edges). Keep the top 14% and bottom 18% free of text and logo. Only the photo, the background and the diagonal band may reach the edges.

TEXT: Render this Brazilian Portuguese text EXACTLY, with all accents, capitalization and punctuation as written, each item on its own line as listed:
[TEXT BLOCK]

COLOR AND CONTRAST: Only night-blue #0B1A2A, white #FFFFFF, and the orange #E05F31 to amber #EC9638 gradient. Orange/amber appears only in the diagonal band and in the logo's peak, never as text color, outlines or background elsewhere (at most 10% of the area). All text other than INAUGURAÇÃO is white on solid night-blue; any text that overlaps the photo must sit on a night-blue veil of at least 60% opacity. The image must read clearly at 360 px wide.

RESTRICTIONS: No other text, no extra words, no fake logos, no watermark. Exactly 15 words of text in total; do not add any word from IMAGE 1 that is not listed above, and no addresses, phone numbers, URLs, @handles, hashtags, emojis, icons, buttons, stickers, countdowns or progress bars. No signage, facade, "ÁPICE" lettering or readable text in the photo. Keep the real, ordinary, diverse people from the photo; no idealized or bodybuilder bodies, no pain or strain expressions. Hands, handlebars, pedals and saddles must be anatomically and mechanically correct.
```

**[TEXT BLOCK] A (se o feed-v1 for o aprovado), 15 palavras:**

```text
- Band: "INAUGURAÇÃO"
- Headline line 1: "Aulas experimentais grátis"
- Headline line 2: "o dia todo"
- Date: "6 de março · 8h às 18h"
- Notice: "Imagem ilustrativa."
Spell check: INAUGURAÇÃO (Ç and Ã), grátis (á), março (ç), às (à); the middle dot · is a separator; "8h" and "18h" use a lowercase h.
```

**[TEXT BLOCK] B (se o feed-v2 for o aprovado), 15 palavras:**

```text
- Band: "INAUGURAÇÃO"
- Price headline: "1º mês R$ 49,90*"
- Transparency line, directly under and touching the price, at least 50% of its size: "*Plano mensal; depois, R$ 119,90/mês."
- Date: "6 de março"
- Notice: "Imagem ilustrativa."
Spell check: INAUGURAÇÃO (Ç and Ã); "1º" uses the ordinal indicator º; mês (ê); prices use a comma as decimal separator; both asterisks must appear; março (ç). The price is white, never orange; no other price, no strikethrough, no percentage.
```

### linkedin

- **id:** `linkedin` · adaptação institucional, **sem preço**
- **Formato:** linkedin-post, horizontal ~1,91:1, **1200×627 px**
- **Referências (ordem e papel), a ordem muda nas adaptações:**
  1. IMAGE 1 = **peça de feed aprovada** (`geradas/feed-v1.png` ou `geradas/feed-v2.png`),
     referência de estilo.
  2. IMAGE 2 = `referencias/logo-escuro.png`, logo fiel.
  3. IMAGE 3 = `referencias/foto-bike.png`, foto limpa.

```text
Create a finished LinkedIn post image, horizontal landscape about 1.91:1, 1200 x 627 pixels, announcing the grand opening of a neighborhood gym to the local community and businesses. Institutional, confident and welcoming tone; premium graphic design with a dark night-blue base.

REFERENCES: IMAGE 1 is the approved Instagram feed post: use it ONLY as the style reference (night-blue base, the orange-to-amber diagonal band with INAUGURAÇÃO, the same typefaces, the same photo treatment). Do not copy any of its other text (especially no price) and do not copy its layout; rebuild the layout for the horizontal format as described below. IMAGE 2 is the logo. IMAGE 3 is the clean original photo.

LOGO: Reproduce the logo from IMAGE 2 EXACTLY (same orange peak mark, same "ÁPICE" lettering in white, same "ACADEMIA" in orange underneath, same proportions and colors); do not redraw, restyle or invent any other logo. Place it once in the top-right corner, on solid night-blue #0B1A2A, with its top edge at about 9% of the canvas height and its right edge at about 6% from the right edge; logo width about 17% of the canvas width. Do not take the logo from IMAGE 1; use IMAGE 2.

PHOTO: Use IMAGE 3 as the main photo, keeping the people exactly as they are: same faces, ages, body types, skin tones, genders, hair, clothes and expressions; do not slim, retouch, rejuvenate, add muscle definition or change any person. The photo occupies the left 45% of the canvas, full height, bleeding off the top, left and bottom edges. Reframe it so the faces are complete and centered vertically in the upper two-thirds; prefer fewer people complete rather than many people cut; do not invent people. Its right edge dissolves smoothly into solid night-blue #0B1A2A between about 38% and 50% of the width. No text over the photo.

LAYOUT:
- Right text column from about 52% to 94% of the width, on solid #0B1A2A, left-aligned.
- Logo in the top-right corner (as above).
- At about 30% to 44% of the height, the bold diagonal band: tilted about 4 degrees upward to the right, starting at the photo fade and bleeding off the right edge, filled with a smooth gradient from orange #E05F31 (left) to amber #EC9638 (right), with INAUGURAÇÃO inside, left-aligned with the text column, in a heavy bold condensed sans-serif, all caps, night-blue #0B1A2A. This is the largest text (cap height about 13% of the canvas height) and the single focal point.
- Below the band, the headline in white #FFFFFF bold condensed sans-serif, two lines, cap height about 6.5% of the canvas height.
- Below the headline, the date in white bold condensed sans-serif, one line, about 80% of the headline size.
- The notice in white clean sans-serif, the smallest text (cap height about 4% of the canvas height), placed at about 78% to 82% of the height in the text column.
- The bottom 15% of the canvas holds only photo and background: nothing essential, no text, no logo.

SAFE AREAS: Keep all text and the logo at least 6% away from every edge, and keep the bottom 15% free of text and logo. The image must read clearly when shown at 360 x 188 pixels.

TEXT: Render this Brazilian Portuguese text EXACTLY, with all accents, capitalization and punctuation as written, each item on its own line(s) as listed:
- Band: "INAUGURAÇÃO"
- Headline line 1: "Uma academia completa"
- Headline line 2: "no Centro"
- Date: "6 de março · 8h às 18h"
- Notice: "Imagem ilustrativa."
Spell check: INAUGURAÇÃO (Ç and Ã), março (ç), às (à); "Centro" with capital C; the middle dot · is a separator; "8h" and "18h" use a lowercase h.

COLOR AND CONTRAST: Only night-blue #0B1A2A, white #FFFFFF, and the orange #E05F31 to amber #EC9638 gradient. Orange/amber appears only in the diagonal band and in the logo's peak, never as text color, outlines or background elsewhere (at most 10% of the area). All text other than INAUGURAÇÃO is white on solid night-blue.

RESTRICTIONS: No other text, no extra words, no fake logos, no watermark. Exactly 14 words of text in total; absolutely no prices or numbers other than the date and hours; no addresses, phone numbers, URLs, @handles, hashtags, emojis, icons or buttons. No signage, facade, "ÁPICE" lettering or readable text in the photo. Keep the real, ordinary, diverse people from the photo; no idealized or bodybuilder bodies, no pain or strain expressions. Hands, handlebars, pedals and saddles must be anatomically and mechanically correct.
```

---

## 3. Ordem de geração e escolha da variação

**Ordem**
1. `feed-v1` e `feed-v2` em sequência, com os mesmos parâmetros (qualidade alta, mesma proporção
   e, se o modelo permitir, a mesma seed). Gere 2 tentativas de cada se a primeira reprovar.
   Se o tamanho exato não for nativo, gere na proporção suportada mais próxima e redimensione ou
   recorte para 1080×1350. As margens de 6–8% servem para o texto sobreviver a esse ajuste.
2. Conferir ambas pelo checklist da seção 6 de `02-psicologia-social.md` e escolher a aprovada
   (critério abaixo). Salvar a final em `geradas/`.
3. `stories` com IMAGE 1 = feed aprovado, usando o bloco de texto A ou B correspondente.
4. `linkedin` com IMAGE 1 = feed aprovado.
5. Conferir Stories e LinkedIn pelo mesmo checklist, aplicar a figurinha de link no Stories e
   finalizar em `entrega/`.

**Critério para escolher a variação de feed que vira base**
1. **Eliminatório** (reprova a peça, regera): texto diferente do prompt ou acento errado
   (INAUGURAÇÃO, grátis, março, às, 1º, mês); palavra extra; logo redesenhado ou duplicado;
   pessoas trocadas, "afinadas" ou com rosto cortado; artefatos em mãos, bikes ou fundo;
   texto falso na foto; no v2, a linha "depois, R$ 119,90/mês" ausente, separada do preço ou
   com menos de 50% do tamanho.
2. **Leitura:** na miniatura de 120 px, INAUGURAÇÃO e a cena de pessoas são identificáveis; em
   360 px, título e data leem sem zoom; em escala de cinza, INAUGURAÇÃO é o elemento de maior
   contraste.
3. **Fidelidade de marca:** logo idêntico ao IMAGE 1, laranja/âmbar só na faixa e no pico, sem
   texto sobre a foto sem véu.
4. **Desempate:** **v1 (evento)**. Segue o princípio do `02` ("a imagem vende o convite; a
   legenda fecha a oferta"), é a única que mantém a data completa com horário no Stories (o
   bloco B precisa tirar o horário para caber em 15 palavras) e evita expor preço sem contexto
   quando a arte é repostada fora da legenda.

Se o cliente rodar o A/B pago com as duas variações, a base de Stories e LinkedIn continua sendo
a aprovada aqui. Se o v2 vencer depois, regere só o Stories com o bloco B; o LinkedIn não muda,
porque não tem preço.
