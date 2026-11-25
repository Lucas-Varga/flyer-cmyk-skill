# Formatos e boas práticas por rede

Os tamanhos são os de `finalizar_post.py --listar`. As áreas seguras são aproximadas: as
interfaces mudam com o tempo e entre aparelhos. Por isso, deixe folga e confira na prévia.

| Formato (`--formato`) | Pixels | Proporção | Interface cobre | Observações |
|---|---|---|---|---|
| `instagram-feed` | 1080×1350 | 4:5 | — | o que mais ocupa a tela no feed. A grade do perfil mostra só o centro em **3:4**: mantenha título e logo dentro da faixa central (a prévia marca em amarelo) |
| `instagram-quadrado` | 1080×1080 | 1:1 | — | carrossel e repost |
| `instagram-stories` | 1080×1920 | 9:16 | ~250 px em cima, ~340 px embaixo | nome do perfil em cima, campo de resposta e botões embaixo; texto e logo no miolo. Serve para capa de Reels |
| `facebook-feed` | 1080×1350 | 4:5 | — | igual ao feed do Instagram (dá para reaproveitar) |
| `facebook-link` | 1200×630 | 1,91:1 | — | imagem de post com link |
| `facebook-stories` | 1080×1920 | 9:16 | ~250 / ~340 px | igual aos Stories do Instagram |
| `whatsapp-status` | 1080×1920 | 9:16 | ~220 / ~300 px | — |
| `whatsapp-imagem` | 1080×1350 | 4:5 | — | para enviar em conversa ou grupo; o WhatsApp comprime, então prefira texto grande |
| `linkedin-post` | 1200×627 | 1,91:1 | — | tom mais sóbrio; o LinkedIn também aceita 1080×1080 e 1080×1350 |
| `x-post` | 1600×900 | 16:9 | — | o X corta prévias: centro importante |
| `youtube-capa` | 1280×720 | 16:9 | canto inferior direito (duração) | texto curto e grande |
| personalizado (`--px`) | qualquer | — | — | banners de site, e-mail marketing, telas |

## Regras de legibilidade no celular

- Teste na prévia de **360 px** (`*-celular.png`): o título precisa ser lido de relance e
  o texto secundário, sem zoom.
- **Pouco texto na imagem:** título de até 6 palavras, 2 ou 3 linhas de apoio, 1 chamada
  para ação. Condições, regulamento e detalhes vão na **legenda**.
- Contraste alto, sem texto sobre área com muito detalhe da foto.
- 5% de respiro em cada borda, mais as áreas da interface.
- Um ponto focal por peça. Em carrossel, uma ideia por imagem.

## Variações e reaproveitamento

- Gere o formato principal primeiro (normalmente o feed 4:5), aprove com o usuário e só
  depois adapte para Stories e LinkedIn. Usar a peça aprovada como referência (`editar`
  com ela como 1ª imagem e o pedido de recompor em 9:16) mantém a identidade.
- Para teste A/B, as variações mudam **uma coisa** de cada vez: título, imagem ou cor do
  destaque.

## Entrega

- PNG (sem perdas) e JPG 92 em sRGB. As redes recomprimem, e JPG de boa qualidade evita
  dupla compressão ruim.
- Nome dos arquivos: `<rede>-<formato>-v<n>.png`.
- `textos.md`: legenda por rede, hashtags (de 3 a 8 relevantes) e texto alternativo de
  cada imagem.
