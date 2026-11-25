"""Motor PDF para as artes de `impressao.Arte`.

- CMYK nativo (nenhuma conversão de cor) e cores especiais como Separation (Pantone);
- degradês como shading CMYK (sem transparência, válido em PDF/X-1a);
- texto em curvas, marcas de corte, TrimBox/BleedBox, slug com as especificações;
- PDF/X-1a:2003 com OutputIntent da condição registrada do papel (FOGRA39/FOGRA29);
- acabamentos (verniz UV, hot stamping, relevo, branco, faca) num PDF separado de
  máscaras em K100, uma página por acabamento e face, alinhado à arte.

Uso:
    from pdf_cmyk import gerar_pdf
    r = gerar_pdf([frente, verso], 'saida/flyer-grafica.pdf', 'Título',
                  rotulos=['FRENTE', 'VERSO'], fonte_slug=fonte, autor='Empresa')
    r['arte'], r['acabamentos'] (ou None), r['avisos']
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pikepdf
from fontTools.misc.transform import Transform
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from PIL import Image
from reportlab.lib.colors import CMYKColor, CMYKColorSep
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as rl_canvas

import impressao
from impressao import ACABAMENTOS, PAPEIS, Cmyk, Degrade, Fonte

MM = 72 / 25.4           # pontos por mm
MARGEM = 12.0            # área além da sangria para marcas de corte (mm)
REGISTRO = Cmyk('Registro', 100, 100, 100, 100)
K100 = Cmyk('K100', 0, 0, 0, 100)
NZ = rl_canvas.FILL_NON_ZERO


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


def _rl(cor: Cmyk):
    v = (cor.c / 100, cor.m / 100, cor.y / 100, cor.k / 100)
    if cor.spot:
        return CMYKColorSep(*v, spotName=cor.spot, density=1)
    return CMYKColor(*v)


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


def _svg_pen_path(c, d: str, t: Transform = Transform()):
    p = c.beginPath()
    parse_path(d, TransformPen(_PenCanvas(p), t))
    return p


class MotorPdf:
    """Desenha a lista de operações de uma Arte. mascara=True: tudo em K100 sólido
    (máscara de acabamento); fotos viram a área do quadro."""

    def __init__(self, c, arte: impressao.Arte, mascara: bool = False):
        self.c, self.a, self.mascara = c, arte, mascara

    def _cor(self, cor):
        return K100 if self.mascara else cor

    # pinta um path com Cmyk, Degrade ou nada; e traço opcional
    def _pintar(self, p, fill, traco=None, traco_mm=0.0, tracejado=None, cap=0, join=0):
        c = self.c
        if fill is not None and isinstance(fill, Degrade) and not self.mascara:
            c.saveState()
            c.clipPath(p, stroke=0, fill=0, fillMode=NZ)
            cores = [_rl(cor) for _, cor in fill.paradas]
            pos = [float(pp) for pp, _ in fill.paradas]
            if fill.tipo == 'linear':
                (x0, y0), (x1, y1) = fill.inicio, fill.fim
                c.linearGradient(x0, y0, x1, y1, cores, pos, extend=True)
            else:
                (cx, cy), r = fill.centro, fill.raio
                c.radialGradient(cx, cy, r, cores, pos, extend=True)
            c.restoreState()
            fill = None
        if fill is None and traco is None:
            return
        c.saveState()
        if fill is not None:
            c.setFillColor(_rl(self._cor(fill if isinstance(fill, Cmyk) else K100)))
        if traco is not None:
            c.setStrokeColor(_rl(self._cor(traco)))
            c.setLineWidth(traco_mm)
            c.setLineCap(cap)
            c.setLineJoin(join)
            if tracejado:
                c.setDash([float(v) for v in tracejado.replace(',', ' ').split()])
        c.drawPath(p, stroke=1 if traco is not None else 0, fill=1 if fill is not None else 0,
                   fillMode=NZ)
        c.restoreState()

    # ── operações ──
    def ret(self, x, y, w, h, cor, r, traco, traco_mm, tracejado):
        p = self.c.beginPath()
        p.roundRect(x, y, w, h, r) if r else p.rect(x, y, w, h)
        self._pintar(p, cor, traco, traco_mm, tracejado)

    def circ(self, cx, cy, r, cor, traco, traco_mm):
        p = self.c.beginPath()
        p.circle(cx, cy, r)
        self._pintar(p, cor, traco, traco_mm)

    def linha(self, x1, y1, x2, y2, cor, esp, tracejado):
        p = self.c.beginPath()
        p.moveTo(x1, y1)
        p.lineTo(x2, y2)
        self._pintar(p, None, cor, esp, tracejado)

    def forma(self, d, cor, traco, traco_mm):
        self._pintar(_svg_pen_path(self.c, d), cor, traco, traco_mm, join=1)

    def texto(self, fonte: Fonte, txt, x, y, tam_pt, rastreio, cor, contorno):
        esc = tam_pt * impressao.PT / fonte.upm
        glifos, _ = fonte.moldar(txt, rastreio)
        p = self.c.beginPath()
        pen = _PenCanvas(p, fonte.glyphs)
        for nome, gx, gy in glifos:
            fonte.glyphs[nome].draw(
                TransformPen(pen, (esc, 0, 0, -esc, x + gx * esc, y - gy * esc)))
        if contorno:
            cc, esp = contorno
            self._pintar(p, None, cc, esp, join=1, cap=1)
        else:
            self._pintar(p, cor)

    def qr(self, modulos, m, cor, url):
        p = self.c.beginPath()
        for px, py in modulos:
            p.rect(px, py, m, m)
        self._pintar(p, cor)

    def logo(self, arquivo, x, y, esc, cores):
        raiz = ET.fromstring(impressao._arquivo(arquivo, 'marca').read_text())
        vb = [float(v) for v in raiz.get('viewBox').split()]
        base = Transform().translate(x, y).scale(esc).translate(-vb[0], -vb[1])
        self._svg_no(raiz, base, None, {k.lower(): v for k, v in cores.items()})

    def _svg_no(self, no, t: Transform, fill, mapa):
        tag = no.tag.split('}')[-1]
        t = t.transform(_transform_attr(no.get('transform')))
        f = no.get('fill', fill)
        if tag == 'path' and f and f != 'none':
            cor = mapa.get(f.lower())
            if cor is None:
                raise ValueError(f'cor {f} do logo sem CMYK definido')
            self._pintar(_svg_pen_path(self.c, no.get('d'), t), cor)
        elif tag in ('rect', 'circle', 'ellipse', 'polygon', 'line', 'polyline', 'text', 'image'):
            raise ValueError(f'logo com <{tag}>: converta o logo para paths (contornos)')
        for filho in no:
            self._svg_no(filho, t, f, mapa)

    def icone(self, nome, x, y, tam, cor):
        g = ET.fromstring(f'<g>{impressao._ICONES[nome]}</g>')
        t = Transform().translate(x, y).scale(tam / 24)
        k = tam / 24
        for el in g:
            if el.tag == 'path':
                p = _svg_pen_path(self.c, el.get('d'), t)
            elif el.tag == 'circle':
                cx, cy, r = (float(el.get(a)) for a in ('cx', 'cy', 'r'))
                p = self.c.beginPath()
                p.circle(*t.transformPoint((cx, cy)), r * k)
            elif el.tag == 'rect':
                x0, y0 = t.transformPoint((float(el.get('x')), float(el.get('y'))))
                w, h = float(el.get('width')) * k, float(el.get('height')) * k
                rx = float(el.get('rx', 0)) * k
                p = self.c.beginPath()
                p.roundRect(x0, y0, w, h, rx) if rx else p.rect(x0, y0, w, h)
            else:
                raise ValueError(f'elemento de ícone não suportado: {el.tag}')
            sw = el.get('stroke-width')
            self._pintar(p, cor if el.get('fill') != 'none' else None,
                         cor if sw else None, float(sw) * k if sw else 0,
                         cap={'round': 1, 'square': 2}.get(el.get('stroke-linecap'), 0),
                         join={'round': 1, 'bevel': 2}.get(el.get('stroke-linejoin'), 0))

    def img(self, tif: Path, x, y, w, h, r):
        c = self.c
        if self.mascara:  # verniz/acabamento sobre a foto inteira
            p = c.beginPath()
            p.roundRect(x, y, w, h, r) if r else p.rect(x, y, w, h)
            self._pintar(p, K100)
            return
        im = Image.open(tif)
        im.load()
        if im.mode != 'CMYK':
            raise RuntimeError(f'{tif}: imagem não está em CMYK ({im.mode})')
        c.saveState()
        if r:
            p = c.beginPath()
            p.roundRect(x, y, w, h, r)
            c.clipPath(p, stroke=0, fill=0)
        c.translate(x, y + h)
        c.scale(1, -1)
        c.drawImage(ImageReader(im), 0, 0, w, h)
        c.restoreState()

    def desenhar(self, ops):
        for op in ops:
            getattr(self, op[0])(*op[1:])


def _marcas(c, arte, rotulo, fonte_slug: Fonte | None):
    """Marcas de corte (afastamento = sangria, 5 mm) em cor de registro + linha de info."""
    s, l, a = arte.s, arte.l, arte.a
    c.saveState()
    c.setStrokeColor(_rl(REGISTRO))
    c.setLineWidth(0.25 / MM)  # 0,25 pt
    for xc in (s, s + l):
        for yc in (s, s + a):
            dx = -1 if xc == s else 1
            dy = -1 if yc == s else 1
            c.line(xc + dx * s, yc, xc + dx * (s + 5), yc)
            c.line(xc, yc + dy * s, xc, yc + dy * (s + 5))
    c.restoreState()
    if fonte_slug and rotulo:
        MotorPdf(c, arte).texto(fonte_slug, rotulo, s + 12, -7.0, 6, 0, K100, None)


def _pagina(c, arte, Hmm, desenho, rotulo, fonte_slug):
    c.saveState()
    c.translate(0, Hmm * MM)
    c.scale(MM, -MM)
    c.translate(MARGEM, MARGEM)  # origem = canto da sangria, y para baixo, em mm
    desenho()
    _marcas(c, arte, rotulo, fonte_slug)
    c.restoreState()
    c.showPage()


def _x1a(tmp: Path, destino: Path, paginas_artes, titulo, papel, Hmm):
    """Pós-processo PDF/X-1a:2003: caixas, OutputIntent, Trapped, sem fonte residual."""
    pdf = pikepdf.open(tmp)
    for arte, pg in zip(paginas_artes, pdf.pages):
        def caixa(x0, y0, x1, y1):
            return pikepdf.Array([(MARGEM + x0) * MM, (Hmm - MARGEM - y1) * MM,
                                  (MARGEM + x1) * MM, (Hmm - MARGEM - y0) * MM])
        s = arte.s
        pg.obj.BleedBox = caixa(0, 0, arte.L, arte.A)
        pg.obj.TrimBox = caixa(s, s, s + arte.l, s + arte.a)
        cont = pg.obj.Contents
        dados = b''.join(x.read_bytes() for x in (cont if isinstance(cont, pikepdf.Array)
                                                   else [cont]))
        # o reportlab abre cada página com um bloco de texto vazio ("BT /F1 12 Tf … ET")
        limpo = re.sub(rb'BT /F\d+ [\d.]+ Tf [\d.]+ TL ET', b'', dados)
        if re.search(rb'\bTf\b', limpo):
            raise RuntimeError('há texto vivo no PDF; tudo deveria estar em curvas')
        if limpo != dados:
            pg.obj.Contents = pdf.make_stream(limpo)
        if '/Font' in pg.obj.Resources:
            del pg.obj.Resources['/Font']
    p = PAPEIS[papel]
    pdf.Root.OutputIntents = pikepdf.Array([pdf.make_indirect(pikepdf.Dictionary(
        Type=pikepdf.Name.OutputIntent, S=pikepdf.Name.GTS_PDFX,
        OutputConditionIdentifier=p['id'], OutputCondition=p['condicao'],
        RegistryName='http://www.color.org', Info=p['condicao'],
    ))])
    info = pdf.docinfo
    info.Title = titulo
    info.Trapped = pikepdf.Name('/False')
    info.GTS_PDFXVersion = 'PDF/X-1a:2003'
    pdf.save(destino, min_version='1.4', fix_metadata_version=False)
    tmp.unlink()


def gerar_pdf(artes: list, destino, titulo: str, rotulos: list[str] | None = None,
              fonte_slug: Fonte | None = None, autor: str = '') -> dict:
    """Gera o PDF da arte (CMYK/spot) e, se houver acabamentos, o PDF de máscaras."""
    destino = Path(destino)
    a0 = artes[0]
    for a in artes:
        if (a.l, a.a, a.s, a.papel) != (a0.l, a0.a, a0.s, a0.papel):
            raise ValueError('todas as faces precisam ter o mesmo formato, sangria e papel')
    Wmm, Hmm = a0.L + 2 * MARGEM, a0.A + 2 * MARGEM
    rotulos = rotulos or [f'face {i + 1}' for i in range(len(artes))]
    papel = PAPEIS[a0.papel]
    slug_base = (f'{a0.l:g}×{a0.a:g} mm · sangria {a0.s:g} mm · {papel["id"]} · '
                 f'tinta ≤ {papel["tac"]}% · ')

    def novo_canvas(p):
        c = rl_canvas.Canvas(str(p), pagesize=(Wmm * MM, Hmm * MM), pageCompression=1,
                             enforceColorSpace='sep_cmyk', invariant=0)
        c.setTitle(titulo)
        c.setAuthor(autor)
        c.setCreator('impresso-grafica (impressao.py + pdf_cmyk.py)')
        return c

    tmp = destino.with_suffix('.tmp.pdf')
    c = novo_canvas(tmp)
    for arte, rot in zip(artes, rotulos):
        _pagina(c, arte, Hmm, lambda a=arte: MotorPdf(c, a).desenhar(a.ops),
                slug_base + rot, fonte_slug)
    c.save()
    _x1a(tmp, destino, artes, titulo, a0.papel, Hmm)

    resultado = {'arte': destino, 'acabamentos': None,
                 'avisos': [f'{rot}: {av}' for a, rot in zip(artes, rotulos) for av in a.avisos]}

    paginas = [(a, rot, tipo) for a, rot in zip(artes, rotulos) for tipo in a.camadas]
    if paginas:
        dest_m = destino.with_name(destino.stem + '-acabamentos.pdf')
        tmp_m = dest_m.with_suffix('.tmp.pdf')
        cm = novo_canvas(tmp_m)
        for arte, rot, tipo in paginas:
            nome = ACABAMENTOS[tipo][0]
            _pagina(cm, arte, Hmm,
                    lambda a=arte, t=tipo: MotorPdf(cm, a, mascara=True).desenhar(
                        a.camadas[t]['ops']),
                    f'MÁSCARA DE {nome.upper()} (K100 = área do acabamento) · {rot} · '
                    + slug_base, fonte_slug)
        cm.save()
        _x1a(tmp_m, dest_m, [a for a, _, _ in paginas], f'{titulo} — acabamentos',
             a0.papel, Hmm)
        resultado['acabamentos'] = dest_m
    return resultado
