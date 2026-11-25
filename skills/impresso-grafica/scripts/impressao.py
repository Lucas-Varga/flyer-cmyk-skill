"""Base para arte de impressão em SVG: texto em curvas (fontTools + HarfBuzz),
cores CMYK (icc-color + equivalente sRGB para tela), QR vetorial (segno),
medidas em milímetros com sangria."""
from __future__ import annotations

import base64
import io
import re
from dataclasses import dataclass
from pathlib import Path

import segno
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

AQUI = Path(__file__).parent
# Pasta do trabalho: espera subpastas fontes/, marca/ e fotos/. Troque com usar_pasta().
BASE = Path.cwd()


def usar_pasta(pasta) -> None:
    """Define a pasta do trabalho (onde estão fontes/, marca/, fotos/)."""
    global BASE
    BASE = Path(pasta).resolve()


def _arquivo(nome, sub: str) -> Path:
    p = Path(nome)
    return p if p.is_absolute() else BASE / sub / nome
PT = 0.3527777778  # 1 pt em mm


# ── cores ───────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Cmyk:
    nome: str
    c: float
    m: float
    y: float
    k: float
    tela: str | None = None  # prévia sRGB calibrada (ex.: cor da marca); senão, aproxima

    @property
    def rgb_tela(self) -> str:
        """Aproximação sRGB só para visualizar na tela (a gráfica usa o CMYK)."""
        if self.tela:
            return self.tela.lower()
        r = 255 * (1 - self.c / 100) * (1 - self.k / 100)
        g = 255 * (1 - self.m / 100) * (1 - self.k / 100)
        b = 255 * (1 - self.y / 100) * (1 - self.k / 100)
        return '#%02x%02x%02x' % (round(r), round(g), round(b))

    def svg(self) -> str:
        """Valor de fill/stroke: sRGB de tela + icc-color com o CMYK (0–1)."""
        return (
            f'{self.rgb_tela} icc-color(FOGRA39, {self.c/100:.2f}, {self.m/100:.2f}, '
            f'{self.y/100:.2f}, {self.k/100:.2f})'
        )

    @property
    def rotulo(self) -> str:
        f = lambda v: f'{v:g}'
        return f'C{f(self.c)} M{f(self.m)} Y{f(self.y)} K{f(self.k)}'


# ── fontes e texto em curvas ────────────────────────────────────────────────
class Fonte:
    def __init__(self, arquivo: str):
        caminho = _arquivo(arquivo, 'fontes')
        self.tt = TTFont(str(caminho))
        dados = caminho.read_bytes()
        if str(arquivo).endswith('.woff2'):
            buf = io.BytesIO()
            self.tt.flavor = None
            self.tt.save(buf)
            dados = buf.getvalue()
            self.tt = TTFont(io.BytesIO(dados))
        self.hb_font = hb.Font(hb.Face(hb.Blob(dados)))
        self.upm = self.tt['head'].unitsPerEm
        self.glyphs = self.tt.getGlyphSet()
        self.ordem = self.tt.getGlyphOrder()

    def moldar(self, texto: str, rastreio_em: float = 0.0):
        buf = hb.Buffer()
        buf.add_str(texto)
        buf.guess_segment_properties()
        hb.shape(self.hb_font, buf, {'kern': True, 'liga': True})
        saida, x = [], 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            saida.append((self.ordem[info.codepoint], x + pos.x_offset, pos.y_offset))
            x += pos.x_advance + rastreio_em * self.upm
        if saida:
            x -= rastreio_em * self.upm
        return saida, x

    def largura(self, texto: str, tamanho_pt: float, rastreio_em: float = 0.0) -> float:
        _, x = self.moldar(texto, rastreio_em)
        return x / self.upm * tamanho_pt * PT

    def caminho(self, texto: str, x_mm: float, y_mm: float, tamanho_pt: float,
                rastreio_em: float = 0.0) -> str:
        """Path SVG (em mm) do texto com a linha de base em y_mm."""
        esc = tamanho_pt * PT / self.upm
        glifos, _ = self.moldar(texto, rastreio_em)
        pen = SVGPathPen(self.glyphs)
        for nome, gx, gy in glifos:
            t = TransformPen(pen, (esc, 0, 0, -esc, x_mm + gx * esc, y_mm - gy * esc))
            self.glyphs[nome].draw(t)
        return pen.getCommands()


def quebrar(fonte: Fonte, texto: str, tamanho_pt: float, largura_mm: float,
            rastreio_em: float = 0.0) -> list[str]:
    linhas = []
    for paragrafo in texto.split('\n'):
        atual = ''
        for palavra in paragrafo.split(' '):
            teste = f'{atual} {palavra}'.strip()
            if fonte.largura(teste, tamanho_pt, rastreio_em) <= largura_mm or not atual:
                atual = teste
            else:
                linhas.append(atual)
                atual = palavra
        linhas.append(atual)
    return linhas


class Arte:
    """Uma face do impresso. Coordenadas em mm a partir do canto da SANGRIA."""

    def __init__(self, largura_mm: float, altura_mm: float, sangria_mm: float = 3.0,
                 titulo: str = ''):
        self.l, self.a, self.s = largura_mm, altura_mm, sangria_mm
        self.titulo = titulo
        self.el: list[str] = []
        self.cores: dict[str, Cmyk] = {}
        self.ops: list[tuple] = []  # lista de desenho para outros motores (PDF)

    # medidas úteis (área final, sem sangria)
    @property
    def L(self):  # largura total com sangria
        return self.l + 2 * self.s

    @property
    def A(self):
        return self.a + 2 * self.s

    def x(self, mm: float) -> float:  # mm a partir da borda de corte
        return self.s + mm

    def y(self, mm: float) -> float:
        return self.s + mm

    def _cor(self, cor: Cmyk) -> str:
        self.cores[cor.nome] = cor
        return cor.svg()

    def _pinta(self, fill: Cmyk | None = None, stroke: Cmyk | None = None) -> str:
        """Atributo com o hexadecimal (todo programa lê) + style com icc-color/CMYK
        (Inkscape preserva; navegadores ignoram o style inválido e usam o atributo)."""
        attrs, estilo = [], []
        if fill is None:
            attrs.append('fill="none"')
        else:
            self.cores[fill.nome] = fill
            attrs.append(f'fill="{fill.rgb_tela}"')
            estilo.append(f'fill:{fill.svg()}')
        if stroke is not None:
            self.cores[stroke.nome] = stroke
            attrs.append(f'stroke="{stroke.rgb_tela}"')
            estilo.append(f'stroke:{stroke.svg()}')
        if estilo:
            attrs.append(f'style="{";".join(estilo)}"')
        return ' '.join(attrs)

    def ret(self, x, y, w, h, cor: Cmyk | None = None, r=0.0, traco: Cmyk | None = None,
            traco_mm=0.0, tracejado: str | None = None, opac: float | None = None):
        self.ops.append(('ret', x, y, w, h, cor, r, traco, traco_mm, tracejado))
        attrs = [f'x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}"']
        if r:
            attrs.append(f'rx="{r:.3f}"')
        attrs.append(self._pinta(cor, traco))
        if traco:
            attrs.append(f'stroke-width="{traco_mm:.3f}"')
            if tracejado:
                attrs.append(f'stroke-dasharray="{tracejado}"')
        if opac is not None:
            attrs.append(f'fill-opacity="{opac}"')
        self.el.append(f'<rect {" ".join(attrs)}/>')

    def circulo(self, cx, cy, r, cor: Cmyk | None = None, traco: Cmyk | None = None,
                traco_mm=0.0):
        self.ops.append(('circ', cx, cy, r, cor, traco, traco_mm))
        t = f' stroke-width="{traco_mm:.3f}"' if traco else ''
        self.el.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" {self._pinta(cor, traco)}{t}/>')

    def linha(self, x1, y1, x2, y2, cor: Cmyk, esp_mm=0.25, tracejado: str | None = None):
        self.ops.append(('linha', x1, y1, x2, y2, cor, esp_mm, tracejado))
        d = f' stroke-dasharray="{tracejado}"' if tracejado else ''
        self.el.append(
            f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'{self._pinta(None, cor)} stroke-width="{esp_mm:.3f}"{d}/>'
        )

    def caminho(self, d: str, cor: Cmyk, extra: str = ''):
        self.el.append(f'<path d="{d}" {self._pinta(cor)}{extra}/>')

    def texto(self, fonte: Fonte, txt: str, x, y, tam_pt: float, cor: Cmyk,
              ancora: str = 'inicio', rastreio_em: float = 0.0, caixa_alta=False,
              rotulo: str | None = None) -> float:
        """Uma linha de texto em curvas. Retorna a largura em mm."""
        if caixa_alta:
            txt = txt.upper()
        w = fonte.largura(txt, tam_pt, rastreio_em)
        if ancora == 'meio':
            x -= w / 2
        elif ancora == 'fim':
            x -= w
        self.ops.append(('texto', fonte, txt, x, y, tam_pt, rastreio_em, cor))
        d = fonte.caminho(txt, x, y, tam_pt, rastreio_em)
        if d:
            aria = f' aria-label="{esc(rotulo or txt)}"'
            self.el.append(f'<path d="{d}" {self._pinta(cor)}{aria}/>')
        return w

    def paragrafo(self, fonte: Fonte, txt: str, x, y, tam_pt: float, cor: Cmyk,
                  largura_mm: float, entrelinha: float = 1.32, ancora='inicio',
                  rastreio_em: float = 0.0) -> float:
        """Texto com quebra. y = linha de base da 1ª linha. Retorna y da próxima linha."""
        passo = tam_pt * PT * entrelinha
        for i, ln in enumerate(quebrar(fonte, txt, tam_pt, largura_mm, rastreio_em)):
            self.texto(fonte, ln, x, y + i * passo, tam_pt, cor, ancora, rastreio_em)
        return y + len(quebrar(fonte, txt, tam_pt, largura_mm, rastreio_em)) * passo

    def qr(self, url: str, x, y, lado_mm: float, cor: Cmyk, fundo: Cmyk | None = None):
        q = segno.make(url, error='m', micro=False)
        matriz = list(q.matrix)
        n = len(matriz)
        borda = 4  # zona de silêncio em módulos
        m = lado_mm / (n + 2 * borda)
        if fundo:
            self.ret(x, y, lado_mm, lado_mm, fundo, r=0.8)
        partes, modulos = [], []
        for i, linha in enumerate(matriz):
            for j, v in enumerate(linha):
                if v:
                    px = x + (j + borda) * m
                    py = y + (i + borda) * m
                    partes.append(f'M{px:.3f},{py:.3f}h{m:.3f}v{m:.3f}h{-m:.3f}z')
                    modulos.append((px, py))
        self.ops.append(('qr', modulos, m, cor, url))
        self.el.append(f'<path d="{"".join(partes)}" {self._pinta(cor)} '
                       f'shape-rendering="crispEdges" aria-label="QR {esc(url)}"/>')

    def logo(self, arquivo: str, x, y, largura_mm: float, cores: dict[str, Cmyk]):
        """Insere um SVG vetorial da marca, trocando cada fill hex pelo CMYK dado."""
        src = _arquivo(arquivo, 'marca').read_text()
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
        corpo = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', src, flags=re.S)
        corpo = re.sub(r'<title>.*?</title>|<!--.*?-->', '', corpo, flags=re.S)
        for hexa, cmyk in cores.items():
            corpo = re.sub(f'fill="{hexa}"', self._pinta(cmyk), corpo, flags=re.I)
        esc_ = largura_mm / vb[2]
        self.ops.append(('logo', arquivo, x, y, esc_, dict(cores)))
        self.el.append(
            f'<g transform="translate({x:.3f},{y:.3f}) scale({esc_:.6f}) '
            f'translate({-vb[0]},{-vb[1]})" aria-label="logo">{corpo}</g>'
        )
        return vb[3] * esc_  # altura em mm

    def imagem(self, arquivo: Path, x, y, w, h, r=0.0, ajuste='xMidYMid slice'):
        """Foto (raster) embutida. Recorte arredondado opcional."""
        self.ops.append(('img', Path(arquivo), x, y, w, h, r))
        dados = base64.b64encode(arquivo.read_bytes()).decode()
        mime = 'image/jpeg' if arquivo.suffix.lower() in ('.jpg', '.jpeg') else 'image/png'
        cid = f'c{len(self.el)}'
        clip = ''
        if r:
            self.el.append(
                f'<clipPath id="{cid}"><rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" '
                f'height="{h:.3f}" rx="{r:.3f}"/></clipPath>'
            )
            clip = f' clip-path="url(#{cid})"'
        self.el.append(
            f'<image href="data:{mime};base64,{dados}" x="{x:.3f}" y="{y:.3f}" '
            f'width="{w:.3f}" height="{h:.3f}" preserveAspectRatio="{ajuste}"{clip}/>'
        )

    def raw(self, s: str):
        self.el.append(s)

    def svg(self, guias: bool = False) -> str:
        perfil = (
            '<color-profile name="FOGRA39" local="Coated FOGRA39" '
            'xlink:href="CoatedFOGRA39.icc"/>'
        )
        amostras = '\n'.join(
            f'    <!-- {c.nome}: {c.rotulo} (tela {c.rgb_tela}) -->' for c in self.cores.values()
        )
        extra = ''
        if guias:  # só para conferência: linha de corte e margem de segurança
            extra = (
                f'<g id="guias" fill="none" stroke="#00b7ff" stroke-width="0.15">'
                f'<rect x="{self.s}" y="{self.s}" width="{self.l}" height="{self.a}"/>'
                f'<rect x="{self.s+5}" y="{self.s+5}" width="{self.l-10}" height="{self.a-10}" '
                f'stroke-dasharray="1 1"/></g>'
            )
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     version="1.1" width="{self.L:g}mm" height="{self.A:g}mm" viewBox="0 0 {self.L:g} {self.A:g}">
  <title>{esc(self.titulo)}</title>
  <desc>Arte de impressão. Formato final {self.l:g}×{self.a:g} mm + sangria de {self.s:g} mm
  em cada lado ({self.L:g}×{self.A:g} mm). Texto convertido em curvas. Cores definidas em
  CMYK (perfil Coated FOGRA39) via icc-color; o hexadecimal é só a prévia de tela.</desc>
  <defs>
    {perfil}
{amostras}
  </defs>
  {''.join(self.el)}
  {extra}
</svg>
'''


def esc(s: str) -> str:
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


# ── ilustrações e ícones ────────────────────────────────────────────────────
_n_emb = 0


def _embutir_svg(self, arquivo: str, x, y, w, h, raio=0.0):
    """Ilustração vetorial (ex.: brindes) num quadro; ids prefixados por cópia."""
    global _n_emb
    self.ops.append(('ilustracao', arquivo))  # sem suporte no PDF CMYK (RGB)
    _n_emb += 1
    src = _arquivo(arquivo, 'marca').read_text()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    par = re.search(r'preserveAspectRatio="([^"]+)"', src)
    corpo = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', src, flags=re.S)
    p = f'e{_n_emb}_'
    corpo = re.sub(r'id="([^"]+)"', lambda m: f'id="{p}{m.group(1)}"', corpo)
    corpo = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{p}{m.group(1)})', corpo)
    clip = ''
    if raio:
        cid = f'{p}clip'
        self.el.append(f'<clipPath id="{cid}"><rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" '
                       f'height="{h:.3f}" rx="{raio:.3f}"/></clipPath>')
        clip = f' clip-path="url(#{cid})"'
    self.el.append(
        f'<g{clip}><svg x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" viewBox="{vb}" '
        f'preserveAspectRatio="{par.group(1) if par else "xMidYMid slice"}">{corpo}</svg></g>'
    )


Arte.ilustracao = _embutir_svg

# ícones desenhados num quadrado 24×24 (traço), escalados para `tam` mm
_ICONES = {
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6"/>',
    'pino': '<path d="M12 21.5s-7-6.4-7-12a7 7 0 0 1 14 0c0 5.6-7 12-7 12z" fill="none" stroke-width="2"/><circle cx="12" cy="9.5" r="2.6" fill="none" stroke-width="2"/>',
    'relogio': '<circle cx="12" cy="12" r="9" fill="none" stroke-width="2"/><path d="M12 7v5.2l3.4 2.2" fill="none" stroke-linecap="round" stroke-width="2"/>',
    'balao': '<path d="M4 18.5l1.3-3.8A8 8 0 1 1 8.6 18z" fill="none" stroke-linejoin="round" stroke-width="2"/>',
    'tesoura': '<circle cx="6" cy="7" r="3" fill="none" stroke-width="1.8"/><circle cx="6" cy="17" r="3" fill="none" stroke-width="1.8"/><path d="M8.6 8.6L20 18M8.6 15.4L20 6" fill="none" stroke-linecap="round" stroke-width="1.8"/>',
    'presente': '<rect x="3.5" y="9" width="17" height="11.5" rx="1" fill="none" stroke-width="2"/><path d="M12 9v11.5M3.5 13h17M12 9c-1.8-4-6-4-6-1.2S12 9 12 9s6 .9 6-1.8S13.8 5 12 9" fill="none" stroke-width="2" stroke-linejoin="round"/>',
    'qr': '<rect x="3" y="3" width="7" height="7" rx="1" fill="none" stroke-width="2"/><rect x="14" y="3" width="7" height="7" rx="1" fill="none" stroke-width="2"/><rect x="3" y="14" width="7" height="7" rx="1" fill="none" stroke-width="2"/><path d="M14 14h3v3h-3zM18 18h3v3h-3z"/>',
    'seta': '<path d="M5 12h13M13 6.5l5.5 5.5-5.5 5.5" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.4"/>',
}


def _icone(self, nome: str, x, y, tam: float, cor: Cmyk):
    """Ícone de traço (24×24) em tam×tam mm, com canto superior esquerdo em (x, y)."""
    self.cores[cor.nome] = cor
    self.ops.append(('icone', nome, x, y, tam, cor))
    desenho = _ICONES[nome]
    self.el.append(
        f'<g transform="translate({x:.3f},{y:.3f}) scale({tam/24:.5f})" '
        f'stroke="{cor.rgb_tela}" fill="{cor.rgb_tela}" '
        f'style="stroke:{cor.svg()};fill:{cor.svg()}" aria-label="ícone {nome}">{desenho}</g>'
    )


Arte.icone = _icone
