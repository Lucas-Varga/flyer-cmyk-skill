"""Finaliza uma imagem gerada para o tamanho exato de uma rede social e gera prévias.

Uso:
    python finalizar_post.py gerada.png --formato instagram-feed --saida entrega/feed
    python finalizar_post.py gerada.png --px 1200x627 --saida entrega/linkedin
    python finalizar_post.py --listar

Faz:
- corte "cover" centralizado e redução (Lanczos) para os pixels exatos do formato;
- salva <saida>.png (sem perdas) e <saida>.jpg (qualidade 92), em sRGB;
- <saida>-previa.png: áreas seguras marcadas (onde a interface da rede cobre a imagem)
  e, no feed do Instagram, o recorte 3:4 que aparece na grade do perfil;
- <saida>-celular.png: a peça a 360 px de largura, como vista num celular, para conferir
  se o texto se lê;
- imprime um resumo e avisa se a imagem gerada era menor que o alvo (ampliação).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

# nome: (largura, altura, (topo, base, esquerda, direita) da área coberta pela interface, descrição)
FORMATOS = {
    'instagram-feed': (1080, 1350, (0, 0, 0, 0), 'Instagram feed retrato 4:5 (o mais visto)'),
    'instagram-quadrado': (1080, 1080, (0, 0, 0, 0), 'Instagram feed quadrado 1:1'),
    'instagram-stories': (1080, 1920, (250, 340, 0, 0), 'Instagram Stories / Reels 9:16'),
    'facebook-feed': (1080, 1350, (0, 0, 0, 0), 'Facebook feed 4:5'),
    'facebook-link': (1200, 630, (0, 0, 0, 0), 'Facebook post com link 1,91:1'),
    'facebook-stories': (1080, 1920, (250, 340, 0, 0), 'Facebook Stories 9:16'),
    'whatsapp-status': (1080, 1920, (220, 300, 0, 0), 'WhatsApp Status 9:16'),
    'whatsapp-imagem': (1080, 1350, (0, 0, 0, 0), 'imagem para enviar no WhatsApp 4:5'),
    'linkedin-post': (1200, 627, (0, 0, 0, 0), 'LinkedIn post horizontal 1,91:1'),
    'linkedin-quadrado': (1080, 1080, (0, 0, 0, 0), 'LinkedIn post quadrado 1:1'),
    'linkedin-retrato': (1080, 1350, (0, 0, 0, 0), 'LinkedIn post retrato 4:5'),
    'x-post': (1600, 900, (0, 0, 0, 0), 'X (Twitter) 16:9'),
    'youtube-capa': (1280, 720, (0, 0, 0, 0), 'capa de vídeo do YouTube 16:9'),
}


def cover(im: Image.Image, w: int, h: int) -> Image.Image:
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=(0.5, 0.5))


def previa(im: Image.Image, seguro, nome: str) -> Image.Image:
    p = im.convert('RGBA')
    camada = Image.new('RGBA', p.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    w, h = p.size
    t, b, l, r = seguro
    vermelho = (230, 40, 40, 110)
    if t:
        d.rectangle((0, 0, w, t), fill=vermelho)
    if b:
        d.rectangle((0, h - b, w, h), fill=vermelho)
    if l:
        d.rectangle((0, 0, l, h), fill=vermelho)
    if r:
        d.rectangle((w - r, 0, w, h), fill=vermelho)
    # margem de respiro (5% de cada lado): texto e logo devem ficar dentro
    m = round(min(w, h) * 0.05)
    d.rectangle((m, m + t, w - m, h - m - b), outline=(0, 200, 255, 230), width=3)
    if nome == 'instagram-feed':  # grade do perfil mostra o centro em 3:4
        g = round(h * 3 / 4)
        x0 = (w - g) // 2
        d.rectangle((x0, 0, x0 + g, h - 1), outline=(255, 210, 0, 230), width=4)
    return Image.alpha_composite(p, camada).convert('RGB')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entrada', nargs='?')
    ap.add_argument('--formato', choices=list(FORMATOS))
    ap.add_argument('--px', help='tamanho personalizado, ex.: 1200x627')
    ap.add_argument('--saida', help='caminho sem extensão, ex.: entrega/instagram-feed')
    ap.add_argument('--listar', action='store_true')
    a = ap.parse_args()

    if a.listar:
        for k, (w, h, s, desc) in FORMATOS.items():
            seg = f' · interface cobre {s[0]} px em cima e {s[1]} px embaixo' if s[0] or s[1] else ''
            print(f'{k:20} {w}×{h}  {desc}{seg}')
        return
    if not a.entrada or not a.saida or not (a.formato or a.px):
        sys.exit('uso: finalizar_post.py gerada.png (--formato NOME | --px LxA) --saida caminho')

    if a.formato:
        w, h, seguro, desc = FORMATOS[a.formato]
    else:
        w, h = (int(v) for v in a.px.lower().split('x'))
        seguro, desc = (0, 0, 0, 0), f'personalizado {w}×{h}'
    im = Image.open(a.entrada)
    im = ImageOps.exif_transpose(im).convert('RGB')
    origem = im.size
    escala = max(w / origem[0], h / origem[1])
    final = cover(im, w, h)

    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    srgb = None
    try:
        from PIL import ImageCms
        srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    except Exception:
        pass
    kw = {'icc_profile': srgb} if srgb else {}
    final.save(saida.with_suffix('.png'), optimize=True, **kw)
    final.save(saida.with_suffix('.jpg'), quality=92, optimize=True, progressive=True,
               subsampling=0, **kw)
    previa(final, seguro, a.formato or '').save(str(saida) + '-previa.png')
    cel = final.resize((360, round(360 * h / w)), Image.LANCZOS)
    cel.save(str(saida) + '-celular.png')

    info = {'formato': a.formato or 'personalizado', 'descricao': desc, 'px': [w, h],
            'origem_px': list(origem), 'ampliada': escala > 1.0,
            'corte_percentual': round(max(0.0, 1 - (w / escala * h / escala) / (origem[0] * origem[1])) * 100, 1),
            'interface_cobre_px': {'topo': seguro[0], 'base': seguro[1]}}
    Path(str(saida) + '.json').write_text(json.dumps(info, ensure_ascii=False, indent=2))
    print(f'OK: {saida}.png / .jpg — {w}×{h} ({desc}); origem {origem[0]}×{origem[1]}, '
          f'corte de {info["corte_percentual"]}%')
    if escala > 1.0:
        print(f'Atenção: a imagem gerada era menor que o alvo (ampliada {escala:.2f}×). '
              'Gere de novo com --px no tamanho do formato.')
    print(f'Prévias: {saida}-previa.png (áreas seguras) e {saida}-celular.png (360 px)')


if __name__ == '__main__':
    main()
