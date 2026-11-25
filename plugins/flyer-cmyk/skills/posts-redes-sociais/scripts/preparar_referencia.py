"""Prepara uma imagem do usuário para servir de REFERÊNCIA na geração (logo, foto,
produto): converte SVG/PDF/PNG/JPG/WEBP/HEIC em PNG, no tamanho certo para a API.

Uso:
    python preparar_referencia.py marca/logo.svg --saida referencias/logo.png
    python preparar_referencia.py materiais/produto.heic --saida referencias/produto.png

- SVG: renderizado pelo Chrome headless (macOS) com fundo transparente, 1600 px de largura.
- PDF (1ª página): renderizado com PyMuPDF.
- Fotos: orientação corrigida (EXIF), convertidas para sRGB e limitadas a 2048 px no
  maior lado (a API não precisa de mais e o envio fica rápido).
- Logo com fundo branco chapado: use --fundo-transparente para remover o branco.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def svg_para_png(svg: Path, largura: int = 1600) -> Image.Image:
    import re
    txt = svg.read_text()
    vb = re.search(r'viewBox="([^"]+)"', txt)
    w, h = (float(v) for v in vb.group(1).split()[2:]) if vb else (1, 1)
    altura = max(1, round(largura * h / w))
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / 'r.html'
        png = Path(tmp) / 'r.png'
        html.write_text(f'<html><body style="margin:0;background:transparent">'
                        f'<img src="file://{svg.resolve()}" style="width:{largura}px;'
                        f'height:{altura}px;display:block"></body></html>')
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        f'--user-data-dir={tmp}/perfil', '--default-background-color=00000000',
                        f'--window-size={largura},{altura}', f'--screenshot={png}',
                        f'file://{html}'], check=True, capture_output=True)
        return Image.open(png).convert('RGBA')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('entrada')
    ap.add_argument('--saida', required=True)
    ap.add_argument('--max', type=int, default=2048, help='maior lado em px (padrão 2048)')
    ap.add_argument('--fundo-transparente', action='store_true',
                    help='torna transparente o branco puro do fundo (logos em JPG/PNG)')
    a = ap.parse_args()
    ent = Path(a.entrada)
    if not ent.is_file():
        sys.exit(f'arquivo não encontrado: {ent}')
    suf = ent.suffix.lower()
    if suf == '.svg':
        if sys.platform != 'darwin':
            sys.exit('SVG usa o Chrome do macOS; em outro sistema, exporte o logo em PNG.')
        im = svg_para_png(ent)
    elif suf == '.pdf':
        import pymupdf
        pg = pymupdf.open(ent)[0]
        pix = pg.get_pixmap(dpi=300, alpha=True)
        im = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples)
    else:
        if suf in ('.heic', '.heif') and sys.platform == 'darwin':
            with tempfile.TemporaryDirectory() as tmp:
                conv = Path(tmp) / 'c.png'
                subprocess.run(['sips', '-s', 'format', 'png', str(ent), '--out', str(conv)],
                               check=True, capture_output=True)
                im = Image.open(conv)
                im.load()
        else:
            im = Image.open(ent)
        im = ImageOps.exif_transpose(im)
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
    if a.fundo_transparente:
        im = im.convert('RGBA')
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, al = px[x, y]
                if r > 245 and g > 245 and b > 245:
                    px[x, y] = (255, 255, 255, 0)
    if max(im.size) > a.max:
        k = a.max / max(im.size)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    im.save(saida, optimize=True)
    print(f'OK: {saida} ({im.width}×{im.height} px, {im.mode})')


if __name__ == '__main__':
    main()
