"""Confere um PDF de impressão gerado por pdf_cmyk.py e renderiza as páginas.

Uso:  python validar_pdf.py arquivo.pdf [--qr URL1 URL2 ...] [--tac 300] [--saida pasta]
      python validar_pdf.py arquivo-acabamentos.pdf --mascara

O que confere (sai com código 1 se algo falhar):
- versão, GTS_PDFXVersion, Trapped e OutputIntent (FOGRA39 couché / FOGRA29 offset);
- MediaBox / BleedBox / TrimBox de cada página (impressos em mm);
- cores: nenhum operador ou espaço de cor RGB (inclusive em degradês e imagens);
  lista as cores especiais (Separation/Pantone);
- nenhuma fonte (tudo em curvas) e nenhuma transparência (ExtGState com CA/ca < 1,
  SMask ou modo de mesclagem);
- tinta total máxima (TAC) dentro da BleedBox (limite pelo papel: FOGRA39 300%,
  FOGRA29 280%, ou --tac);
- com --mascara: só preto (K) — é a máscara de um acabamento;
- leitura dos QR codes (OpenCV, 2 detectores) e comparação com as URLs esperadas;
- salva prévias PNG (<saida>/<nome>-pN.png a 300 dpi e -tela.png a 110 dpi).
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
TAC_PAPEL = {'FOGRA39': 300, 'FOGRA29': 280}
RGB = {'/DeviceRGB', '/CalRGB'}


def _espacos(obj, vistos=None):
    """Nomes de espaços de cor usados em um dicionário de recursos (recursivo)."""
    vistos = vistos if vistos is not None else set()
    achados = []
    if isinstance(obj, pikepdf.Name):
        achados.append(str(obj))
    elif isinstance(obj, pikepdf.Array):
        if len(obj) and isinstance(obj[0], pikepdf.Name):
            nome = str(obj[0])
            if nome == '/Separation':
                achados.append(f'Separation:{obj[1]}')
                achados += _espacos(obj[2], vistos)
            elif nome == '/ICCBased':
                n = int(obj[1].get('/N', 0))
                achados.append({1: '/DeviceGray', 3: '/DeviceRGB', 4: '/DeviceCMYK'}.get(n, '?'))
            else:
                for x in obj:
                    achados += _espacos(x, vistos)
        else:
            for x in obj:
                achados += _espacos(x, vistos)
    return achados


def _recursos_cor(res) -> list[str]:
    usados = []
    for nome, cs in (res.get('/ColorSpace') or {}).items():
        usados += _espacos(cs)
    for nome, sh in (res.get('/Shading') or {}).items():
        usados += _espacos(sh.get('/ColorSpace'))
    for nome, pat in (res.get('/Pattern') or {}).items():
        sh = pat.get('/Shading')
        if sh is not None:
            usados += _espacos(sh.get('/ColorSpace'))
    for nome, xo in (res.get('/XObject') or {}).items():
        if xo.get('/Subtype') == '/Image':
            usados += _espacos(xo.get('/ColorSpace'))
        elif '/Resources' in xo:
            usados += _recursos_cor(xo.Resources)
    return usados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--qr', nargs='*', default=[], help='URLs que os QR devem conter')
    ap.add_argument('--tac', type=float, default=None, help='tinta total máxima (%%)')
    ap.add_argument('--mascara', action='store_true', help='PDF de máscaras de acabamento')
    ap.add_argument('--saida', default=None, help='pasta das prévias PNG')
    a = ap.parse_args()

    caminho = Path(a.pdf)
    saida = Path(a.saida) if a.saida else caminho.parent
    saida.mkdir(parents=True, exist_ok=True)
    erros: list[str] = []

    pdf = pikepdf.open(caminho)
    info = pdf.docinfo
    print(f'{caminho.name}: PDF {pdf.pdf_version} · '
          f'{info.get("/GTS_PDFXVersion", "sem GTS_PDFXVersion")} · Trapped {info.get("/Trapped", "?")}')
    oi = pdf.Root.get('/OutputIntents')
    cond = str(oi[0].get('/OutputConditionIdentifier')) if oi else None
    if not oi:
        erros.append('sem OutputIntent')
    else:
        print(f'OutputIntent: {cond}')
    if '/GTS_PDFXVersion' not in info:
        erros.append('sem GTS_PDFXVersion')
    tac_max = a.tac or TAC_PAPEL.get(cond, 300)

    spots: set[str] = set()
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
        for nome, gs in (res.get('/ExtGState') or {}).items():
            transp = [k for k in ('/SMask', '/BM') if k in gs and str(gs[k]) not in ('/None', '/Normal')]
            transp += [k for k in ('/CA', '/ca') if k in gs and float(gs[k]) < 1]
            if transp:
                erros.append(f'pág {i}: transparência em {nome} ({transp}) — proibida no PDF/X-1a')
        usados = _recursos_cor(res)
        rgb = [u for u in usados if u in RGB]
        if rgb:
            erros.append(f'pág {i}: espaço de cor RGB em recursos ({set(rgb)})')
        spots.update(u.split(':', 1)[1] for u in usados if u.startswith('Separation:'))
        for nome, xo in (res.get('/XObject') or {}).items():
            if xo.get('/Subtype') == '/Image':
                print(f'  imagem {nome}: {xo.get("/ColorSpace")} {xo.Width}×{xo.Height}')
    if spots:
        print(f'cores especiais (Separation): {sorted(spots)}')

    doc = pymupdf.open(caminho)
    dets = [cv2.QRCodeDetector(), cv2.QRCodeDetectorAruco()]
    lidos: set[str] = set()
    for i, pg in enumerate(doc, 1):
        obj = pdf.pages[i - 1].obj
        x0, y0, x1, y1 = [float(v) for v in (obj.get('/BleedBox') or obj.MediaBox)]
        H = float(obj.MediaBox[3])
        # recua 0,5 mm: as marcas de corte (registro, 400%) começam na borda da sangria
        d = 0.5 * MM
        clip = pymupdf.Rect(x0 + d, H - y1 + d, x1 - d, H - y0 - d)
        pix = pg.get_pixmap(dpi=300, colorspace=pymupdf.csCMYK, clip=clip)
        arr = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :4]
        tot = arr.astype(np.int32).sum(axis=2) / 255 * 100
        tac = tot.max()
        print(f'pág {i}: tinta máxima {tac:.0f}% (p99,9 {np.percentile(tot, 99.9):.0f}%; '
              f'limite {tac_max:.0f}%)')
        if tac > tac_max + 1:
            erros.append(f'pág {i}: tinta {tac:.0f}% > {tac_max:.0f}%')
        if a.mascara and arr[..., :3].max() > 3:
            erros.append(f'pág {i}: máscara de acabamento com C/M/Y (deve ser só K)')
        png = saida / f'{caminho.stem}-p{i}.png'
        pg.get_pixmap(dpi=300).save(png)
        pg.get_pixmap(dpi=110).save(saida / f'{caminho.stem}-p{i}-tela.png')
        if not a.mascara:
            img = cv2.imread(str(png))
            achados = []
            for det in dets:  # o detector clássico às vezes perde QR lado a lado
                ok, dec, _, _ = det.detectAndDecodeMulti(img)
                achados += [x for x in (dec if ok else []) if x and x not in achados]
            lidos.update(achados)
            print(f'  QR lidos: {achados or "nenhum"}')

    faltam = [u for u in a.qr if u not in lidos]
    if faltam:
        erros.append(f'QR não lidos: {faltam}')
    print(f'prévias em {saida}')
    print('\n' + ('OK — nenhum problema encontrado' if not erros
                  else 'PROBLEMAS:\n- ' + '\n- '.join(erros)))
    sys.exit(1 if erros else 0)


if __name__ == '__main__':
    main()
