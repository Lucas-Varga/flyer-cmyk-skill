"""Confere um PDF de impressão gerado por pdf_cmyk.py e renderiza as páginas.

Uso:  python validar_pdf.py arquivo.pdf [--qr URL1 URL2 ...] [--tac 300] [--saida pasta]

O que confere (e sai com código 1 se algo falhar):
- versão PDF, GTS_PDFXVersion, Trapped e OutputIntent (FOGRA39 ou outro);
- MediaBox / BleedBox / TrimBox de cada página (impressos em mm);
- nenhum operador de cor RGB (rg/RG), nenhuma fonte, nenhum ExtGState (transparência);
- imagens: espaço de cor (só DeviceCMYK/DeviceGray) e resolução efetiva;
- tinta total máxima (TAC) dentro da BleedBox, renderizando em CMYK a 300 dpi;
- leitura dos QR codes (OpenCV) e comparação com as URLs esperadas;
- salva PNG de prévia de cada página (<saida>/<nome>-pN.png).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import cv2
import numpy as np
import pikepdf
import pymupdf

MM = 72 / 25.4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--qr', nargs='*', default=[], help='URLs que os QR devem conter')
    ap.add_argument('--tac', type=float, default=300.0, help='tinta total máxima (%%)')
    ap.add_argument('--saida', default=None, help='pasta das prévias PNG')
    a = ap.parse_args()

    caminho = Path(a.pdf)
    saida = Path(a.saida) if a.saida else caminho.parent
    saida.mkdir(parents=True, exist_ok=True)
    erros: list[str] = []

    pdf = pikepdf.open(caminho)
    info = pdf.docinfo
    print(f'PDF {pdf.pdf_version} · {info.get("/GTS_PDFXVersion", "sem GTS_PDFXVersion")} · '
          f'Trapped {info.get("/Trapped", "?")}')
    oi = pdf.Root.get('/OutputIntents')
    if not oi:
        erros.append('sem OutputIntent')
    else:
        print(f'OutputIntent: {oi[0].get("/OutputConditionIdentifier")}')
    if '/GTS_PDFXVersion' not in info:
        erros.append('sem GTS_PDFXVersion')

    for i, pg in enumerate(pdf.pages, 1):
        f = lambda b: [round(float(v) / MM, 2) for v in b]
        caixas = {k: f(pg.obj[k]) for k in ('/MediaBox', '/BleedBox', '/TrimBox') if k in pg.obj}
        print(f'pág {i}: ' + '  '.join(f'{k[1:]} {v}' for k, v in caixas.items()))
        if '/TrimBox' not in pg.obj or '/BleedBox' not in pg.obj:
            erros.append(f'pág {i}: falta TrimBox/BleedBox')
        cont = pg.obj.Contents
        dados = b''.join(x.read_bytes() for x in (cont if isinstance(cont, pikepdf.Array) else [cont]))
        if re.search(rb'(^|\s)(rg|RG)(\s|$)', dados):
            erros.append(f'pág {i}: operador de cor RGB no conteúdo')
        if re.search(rb'\bTf\b', dados):
            erros.append(f'pág {i}: texto vivo (Tf); converter em curvas')
        res = pg.obj.Resources
        if '/Font' in res and len(res.Font):
            erros.append(f'pág {i}: {len(res.Font)} fonte(s) declarada(s)')
        if '/ExtGState' in res and len(res.ExtGState):
            erros.append(f'pág {i}: ExtGState (transparência/overprint?) — conferir')
        for nome, xo in (res.get('/XObject') or {}).items():
            cs = str(xo.get('/ColorSpace'))
            print(f'  imagem {nome}: {cs} {xo.Width}×{xo.Height}')
            if cs not in ('/DeviceCMYK', '/DeviceGray'):
                erros.append(f'pág {i}: imagem {nome} em {cs}')

    doc = pymupdf.open(caminho)
    dets = [cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco()]
    lidos: set[str] = set()
    for i, pg in enumerate(doc, 1):
        bleed = pdf.pages[i - 1].obj.get('/BleedBox') or pdf.pages[i - 1].obj.MediaBox
        x0, y0, x1, y1 = [float(v) for v in bleed]
        H = float(pdf.pages[i - 1].obj.MediaBox[3])
        # PyMuPDF usa y para baixo. Recua 0,5 mm: as marcas de corte (registro, 400%)
        # começam na borda da sangria e o antisserrilhado delas contaminaria a medida.
        d = 0.5 * MM
        clip = pymupdf.Rect(x0 + d, H - y1 + d, x1 - d, H - y0 - d)
        pix = pg.get_pixmap(dpi=300, colorspace=pymupdf.csCMYK, clip=clip)
        arr = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :4]
        tot = arr.astype(np.int32).sum(axis=2) / 255 * 100
        tac = tot.max()
        print(f'pág {i}: tinta máxima {tac:.0f}% (p99,9 {np.percentile(tot, 99.9):.0f}%)')
        if tac > a.tac + 1:
            erros.append(f'pág {i}: tinta {tac:.0f}% > {a.tac:.0f}%')
        png = saida / f'{caminho.stem}-p{i}.png'
        pg.get_pixmap(dpi=300).save(png)
        img = cv2.imread(str(png))
        achados = []
        # o detector clássico às vezes perde QR lado a lado; o Aruco complementa
        for detector in dets:
            ok, dec, _, _ = detector.detectAndDecodeMulti(img)
            achados += [x for x in (dec if ok else []) if x and x not in achados]
        lidos.update(achados)
        print(f'  QR lidos: {achados or "nenhum"}  · prévia: {png}')
        pg.get_pixmap(dpi=110).save(saida / f'{caminho.stem}-p{i}-tela.png')

    faltam = [u for u in a.qr if u not in lidos]
    if faltam:
        erros.append(f'QR não lidos: {faltam}')

    print('\n' + ('OK — nenhum problema encontrado' if not erros else 'PROBLEMAS:\n- ' + '\n- '.join(erros)))
    sys.exit(1 if erros else 0)


if __name__ == '__main__':
    main()
