"""Motor PDF para as artes de `impressao.Arte`: CMYK nativo (sem conversão de cor),
texto em curvas, marcas de corte, TrimBox/BleedBox e PDF/X-1a:2003 (FOGRA39).

Uso:
    from pdf_cmyk import gerar_pdf
    gerar_pdf([arte_frente, arte_verso], 'saida.pdf', titulo='...', rotulos=['FRENTE', 'VERSO'])
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pikepdf
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

import impressao
from impressao import Cmyk, Fonte

MM = 72 / 25.4           # pontos por mm
MARGEM = 12.0            # área além da sangria para marcas de corte (mm)
REGISTRO = Cmyk('Registro', 100, 100, 100, 100)
PERFIL_CMYK_FOTO = '/System/Library/ColorSync/Profiles/Generic CMYK Profile.icc'
DPI_FOTO = 350


class _PenCanvas(BasePen):
    """Pen do fontTools que desenha num path do reportlab (quadráticas → cúbicas)."""

    def __init__(self, path, glyphSet=None):
        super().__init__(glyphSet)
        self.p = path

    def _moveTo(self, pt):
        self.p.moveTo(*pt)

    def _lineTo(self, pt):
        self.p.lineTo(*pt)

    def _curveToOne(self, p1, p2, p3):
        self.p.curveTo(*p1, *p2, *p3)

    def _closePath(self):
        self.p.close()

    def _endPath(self):
        pass


def _cmyk(c, cor: Cmyk, traco=False):
    v = (cor.c / 100, cor.m / 100, cor.y / 100, cor.k / 100)
    (c.setStrokeColorCMYK if traco else c.setFillColorCMYK)(*v)


def _transform_attr(s: str | None) -> Transform:
    t = Transform()
    if not s:
        return t
    for nome, args in re.findall(r'(\w+)\(([^)]*)\)', s):
        n = [float(v) for v in re.split(r'[ ,]+', args.strip()) if v]
        if nome == 'translate':
            t = t.translate(n[0], n[1] if len(n) > 1 else 0)
        elif nome == 'scale':
            t = t.scale(n[0], n[1] if len(n) > 1 else n[0])
        elif nome == 'matrix':
            t = t.transform(n)
        else:
            raise ValueError(f'transform não suportado: {nome}')
    return t


def _svg_pen_path(c, d: str, t: Transform):
    p = c.beginPath()
    parse_path(d, TransformPen(_PenCanvas(p), t))
    return p


class MotorPdf:
    def __init__(self, c, arte: impressao.Arte):
        self.c, self.a = c, arte

    # ── primitivas ──
    def ret(self, x, y, w, h, cor, r, traco, traco_mm, tracejado):
        c = self.c
        c.saveState()
        if cor:
            _cmyk(c, cor)
        if traco:
            _cmyk(c, traco, True)
            c.setLineWidth(traco_mm)
            if tracejado:
                c.setDash([float(v) for v in tracejado.replace(',', ' ').split()])
        if r:
            c.roundRect(x, y, w, h, r, stroke=1 if traco else 0, fill=1 if cor else 0)
        else:
            c.rect(x, y, w, h, stroke=1 if traco else 0, fill=1 if cor else 0)
        c.restoreState()

    def circ(self, cx, cy, r, cor, traco, traco_mm):
        c = self.c
        c.saveState()
        if cor:
            _cmyk(c, cor)
        if traco:
            _cmyk(c, traco, True)
            c.setLineWidth(traco_mm)
        c.circle(cx, cy, r, stroke=1 if traco else 0, fill=1 if cor else 0)
        c.restoreState()

    def linha(self, x1, y1, x2, y2, cor, esp, tracejado):
        c = self.c
        c.saveState()
        _cmyk(c, cor, True)
        c.setLineWidth(esp)
        if tracejado:
            c.setDash([float(v) for v in tracejado.replace(',', ' ').split()])
        c.line(x1, y1, x2, y2)
        c.restoreState()

    def texto(self, fonte: Fonte, txt, x, y, tam_pt, rastreio, cor):
        esc = tam_pt * impressao.PT / fonte.upm
        glifos, _ = fonte.moldar(txt, rastreio)
        p = self.c.beginPath()
        pen = _PenCanvas(p, fonte.glyphs)
        for nome, gx, gy in glifos:
            fonte.glyphs[nome].draw(
                TransformPen(pen, (esc, 0, 0, -esc, x + gx * esc, y - gy * esc)))
        self.c.saveState()
        _cmyk(self.c, cor)
        self.c.drawPath(p, stroke=0, fill=1, fillMode=rl_canvas.FILL_NON_ZERO)
        self.c.restoreState()

    def qr(self, modulos, m, cor, url):
        p = self.c.beginPath()
        for px, py in modulos:
            p.rect(px, py, m, m)
        self.c.saveState()
        _cmyk(self.c, cor)
        self.c.drawPath(p, stroke=0, fill=1, fillMode=rl_canvas.FILL_NON_ZERO)
        self.c.restoreState()

    def logo(self, arquivo, x, y, esc, cores):
        src = impressao._arquivo(arquivo, 'marca').read_text()
        raiz = ET.fromstring(src)
        vb = [float(v) for v in raiz.get('viewBox').split()]
        base = Transform().translate(x, y).scale(esc).translate(-vb[0], -vb[1])
        mapa = {k.lower(): v for k, v in cores.items()}
        self._svg_no(raiz, base, None, mapa)

    def _svg_no(self, no, t: Transform, fill, mapa):
        tag = no.tag.split('}')[-1]
        t = t.transform(_transform_attr(no.get('transform')))
        f = no.get('fill', fill)
        if tag == 'path':
            if not f or f == 'none':
                return
            cor = mapa.get(f.lower())
            if cor is None:
                raise ValueError(f'cor {f} do logo sem CMYK definido')
            p = _svg_pen_path(self.c, no.get('d'), t)
            self.c.saveState()
            _cmyk(self.c, cor)
            self.c.drawPath(p, stroke=0, fill=1, fillMode=rl_canvas.FILL_NON_ZERO)
            self.c.restoreState()
        for filho in no:
            self._svg_no(filho, t, f, mapa)

    def icone(self, nome, x, y, tam, cor):
        g = ET.fromstring(f'<g>{impressao._ICONES[nome]}</g>')
        t = Transform().translate(x, y).scale(tam / 24)
        c = self.c
        for el in g:
            tag = el.tag
            if tag == 'path':
                p = _svg_pen_path(c, el.get('d'), t)
            elif tag == 'circle':
                cx, cy, r = (float(el.get(k)) for k in ('cx', 'cy', 'r'))
                p = c.beginPath()
                cx2, cy2 = t.transformPoint((cx, cy))
                p.circle(cx2, cy2, r * tam / 24)
            elif tag == 'rect':
                x0, y0 = t.transformPoint((float(el.get('x')), float(el.get('y'))))
                w, h = float(el.get('width')) * tam / 24, float(el.get('height')) * tam / 24
                rx = float(el.get('rx', 0)) * tam / 24
                p = c.beginPath()
                p.roundRect(x0, y0, w, h, rx) if rx else p.rect(x0, y0, w, h)
            else:
                raise ValueError(f'elemento de ícone não suportado: {tag}')
            preench = el.get('fill') != 'none'
            sw = el.get('stroke-width')
            c.saveState()
            _cmyk(c, cor)
            _cmyk(c, cor, True)
            c.setLineCap({'round': 1, 'square': 2}.get(el.get('stroke-linecap'), 0))
            c.setLineJoin({'round': 1, 'bevel': 2}.get(el.get('stroke-linejoin'), 0))
            if sw:
                c.setLineWidth(float(sw) * tam / 24)
            c.drawPath(p, stroke=1 if sw else 0, fill=1 if preench else 0,
                       fillMode=rl_canvas.FILL_NON_ZERO)
            c.restoreState()

    def img(self, arquivo: Path, x, y, w, h, r):
        cmyk = _foto_cmyk(arquivo, w, h)
        c = self.c
        c.saveState()
        if r:
            p = c.beginPath()
            p.roundRect(x, y, w, h, r)
            c.clipPath(p, stroke=0, fill=0)
        c.translate(x, y + h)
        c.scale(1, -1)
        c.drawImage(ImageReader(cmyk), 0, 0, w, h)
        c.restoreState()

    def ilustracao(self, arquivo):
        raise NotImplementedError(
            f'{arquivo}: ilustração SVG em RGB não entra no PDF CMYK; converta antes.')

    def desenhar(self):
        for op in self.a.ops:
            getattr(self, op[0])(*op[1:])


def _foto_cmyk(arquivo: Path, w_mm, h_mm) -> Image.Image:
    if sys.platform != 'darwin':
        raise RuntimeError(
            'A conversão da foto para CMYK usa o `sips` do macOS. Em Linux/Windows, troque '
            'esta função por PIL.ImageCms ou ImageMagick (veja o README do repositório).')
    """Recorta em 'slice' na proporção do quadro, reduz a DPI_FOTO e converte para CMYK
    com o ColorSync (perfil CMYK do sistema)."""
    im = Image.open(arquivo).convert('RGB')
    alvo = w_mm / h_mm
    W, H = im.size
    if W / H > alvo:
        nw = round(H * alvo)
        im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
    else:
        nh = round(W / alvo)
        im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
    px = round(w_mm / 25.4 * DPI_FOTO)
    im = im.resize((px, round(px / alvo)), Image.LANCZOS)
    with tempfile.TemporaryDirectory() as tmp:
        rgb, out = Path(tmp) / 'rgb.tif', Path(tmp) / 'cmyk.tif'
        im.save(rgb)
        subprocess.run(['sips', '-m', PERFIL_CMYK_FOTO, str(rgb), '--out', str(out)],
                       check=True, capture_output=True)
        res = Image.open(out)
        res.load()
    if res.mode != 'CMYK':
        raise RuntimeError(f'conversão CMYK falhou: modo {res.mode}')
    return res


def _marcas(c, arte, rotulo, fonte_slug: Fonte | None):
    """Marcas de corte (afastamento = sangria, 5 mm) em cor de registro + linha de info."""
    s, l, a = arte.s, arte.l, arte.a
    c.saveState()
    _cmyk(c, REGISTRO, True)
    c.setLineWidth(0.25 / MM * 1.0)  # 0,25 pt
    off, comp = s, 5.0
    for xc in (s, s + l):
        for yc in (s, s + a):
            dx = -1 if xc == s else 1
            dy = -1 if yc == s else 1
            c.line(xc + dx * off, yc, xc + dx * (off + comp), yc)   # horizontal
            c.line(xc, yc + dy * off, xc, yc + dy * (off + comp))   # vertical
    c.restoreState()
    if fonte_slug and rotulo:
        m = MotorPdf(c, arte)
        m.texto(fonte_slug, rotulo, s + 12, -7.0, 6, 0, Cmyk('K', 0, 0, 0, 100))


def gerar_pdf(artes: list, destino, titulo: str, rotulos: list[str] | None = None,
              fonte_slug: Fonte | None = None, autor: str = ''):
    destino = Path(destino)
    a0 = artes[0]
    Wmm, Hmm = a0.L + 2 * MARGEM, a0.A + 2 * MARGEM
    tmp = destino.with_suffix('.tmp.pdf')
    c = rl_canvas.Canvas(str(tmp), pagesize=(Wmm * MM, Hmm * MM), pageCompression=1,
                         enforceColorSpace='cmyk', invariant=0)
    c.setTitle(titulo)
    c.setAuthor(autor)
    c.setCreator('impressao.py + pdf_cmyk.py')
    for i, arte in enumerate(artes):
        c.saveState()
        c.translate(0, Hmm * MM)
        c.scale(MM, -MM)
        c.translate(MARGEM, MARGEM)     # origem = canto da sangria
        MotorPdf(c, arte).desenhar()
        _marcas(c, arte, rotulos[i] if rotulos else None, fonte_slug)
        c.restoreState()
        c.showPage()
    c.save()

    # PDF/X-1a:2003: caixas, OutputIntent FOGRA39 (condição registrada), Trapped, versão
    pdf = pikepdf.open(tmp)
    for arte, pg in zip(artes, pdf.pages):
        def caixa(x0, y0, x1, y1):  # mm a partir do canto da sangria (y para baixo) → pt PDF
            return pikepdf.Array([
                (MARGEM + x0) * MM, (Hmm - MARGEM - y1) * MM,
                (MARGEM + x1) * MM, (Hmm - MARGEM - y0) * MM])
        s = arte.s
        pg.obj.MediaBox = pikepdf.Array([0, 0, Wmm * MM, Hmm * MM])
        pg.obj.BleedBox = caixa(0, 0, arte.L, arte.A)
        pg.obj.TrimBox = caixa(s, s, s + arte.l, s + arte.a)
        # todo texto está em curvas: remove a fonte padrão que o reportlab declara sem usar
        # (preflight PDF/X acusaria "fonte não embutida")
        conteudo = b''.join(x.read_bytes() for x in (
            pg.obj.Contents if isinstance(pg.obj.Contents, pikepdf.Array) else [pg.obj.Contents]))
        # o reportlab abre cada página com um bloco de texto vazio ("BT /F1 12 Tf … ET")
        limpo = re.sub(rb'BT /F\d+ [\d.]+ Tf [\d.]+ TL ET', b'', conteudo)
        if limpo != conteudo:
            pg.obj.Contents = pdf.make_stream(limpo)
            conteudo = limpo
        if re.search(rb'\bTf\b', conteudo):
            raise RuntimeError('há texto vivo no PDF; tudo deveria estar em curvas')
        if '/Font' in pg.obj.Resources:
            del pg.obj.Resources['/Font']
    pdf.Root.OutputIntents = pikepdf.Array([pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.OutputIntent,
        S=pikepdf.Name.GTS_PDFX,
        OutputConditionIdentifier='FOGRA39',
        OutputCondition='Coated FOGRA39 (ISO 12647-2:2004)',
        RegistryName='http://www.color.org',
        Info='Coated FOGRA39 (ISO 12647-2:2004), offset, papel couché',
    ))])
    info = pdf.docinfo
    info.Title = titulo
    info.Trapped = pikepdf.Name('/False')
    info.GTS_PDFXVersion = 'PDF/X-1a:2003'
    pdf.save(destino, min_version='1.4', fix_metadata_version=False)
    tmp.unlink()
    return destino
