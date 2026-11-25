# flyer-cmyk

**English.** Claude plugin with two skills for promotional pieces, for any campaign,
working with marketing, marketing-psychology and graphic-design agents:

- **`impresso-grafica` (print):** guides you from idea to a print-ready flyer or leaflet.
  It produces vector artwork in true CMYK/Pantone, with gradients, effects and outlined
  text, plus a validated PDF/X-1a and separate finish masks (spot UV, foil, embossing,
  white ink, die-cut).
- **`posts-redes-sociais` (social media):** creates posts and banners for Instagram feed
  and Stories, Facebook, WhatsApp and LinkedIn, generated with AI using your own logo and
  photos as reference images. It checks every line of text, exports at the exact size of
  each platform, and writes captions, hashtags and alt text.

Both ask whether the piece is for print, social media or both, collect your material step
by step into a briefing, and generate at the end. AI images use OpenAI, Google or
Stability, with the API key in a `.env` file. Built for macOS. The skills speak
Brazilian Portuguese.

**Português.** Plugin do Claude com duas skills para peças promocionais de qualquer
campanha, trabalhando com agentes de marketing, psicologia de marketing e design:

- **`impresso-grafica` (impressão):** leva da ideia ao flyer ou panfleto pronto para a
  gráfica. Gera a arte vetorial em CMYK/Pantone de verdade, com degradês, efeitos e
  texto em curvas, mais o PDF/X-1a validado e as máscaras de acabamento separadas (verniz
  UV, hot stamping, relevo, tinta branca, faca).
- **`posts-redes-sociais` (redes sociais):** cria posts e banners para Instagram (feed e
  Stories), Facebook, WhatsApp e LinkedIn, gerados com IA usando o seu logo e as suas
  fotos como referência. Confere cada linha de texto, exporta no tamanho exato de cada
  rede e escreve legenda, hashtags e texto alternativo.

As duas perguntam se a peça é para impressão, redes sociais ou ambos, coletam o seu
material passo a passo num briefing e geram no final. As imagens com IA usam OpenAI,
Google ou Stability, com a chave num arquivo `.env`. Feito para macOS.

Install / instalar (Claude Code):

```
/plugin marketplace add Lucas-Varga/flyer-cmyk-skill
/plugin install flyer-cmyk@flyer-cmyk-skill
```

Use: *"create an A5 flyer for our grand opening to send to the print shop"* · *"create
Instagram posts for our grand opening"* / *"crie um flyer A5 da nossa inauguração para a
gráfica"* · *"crie posts para o Instagram da nossa inauguração"*.

Full documentation / documentação completa: https://github.com/Lucas-Varga/flyer-cmyk-skill
