"""Arte de impressão em SVG + lista de desenho para PDF CMYK (ver pdf_cmyk.py).

- medidas em milímetros, origem no canto da SANGRIA (a classe Face dos exemplos soma a
  sangria para trabalhar a partir do canto de corte);
- cores CMYK de processo ou cores especiais (Pantone/spot) com alternativa CMYK;
- degradês lineares e radiais em CMYK;
- texto convertido em curvas (fontTools + HarfBuzz), com contorno e sombra sólida;
- QR vetorial, logo SVG com troca de cor, fotos com efeitos aplicados em CMYK
  (duotone, fade para cor, escurecer) e limite de tinta;
- camadas de acabamento (verniz UV, hot stamping, relevo, tinta branca, faca especial),
  que viram máscaras separadas no PDF.

Requer macOS para fotos (o `sips` converte RGB→CMYK). O resto é Python puro.
"""
from __future__ import annotations

import base64
import hashlib
import io
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import segno
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTCollection, TTFont
from PIL import Image

AQUI = Path(__file__).parent
PT = 0.3527777778  # 1 pt em mm
BASE = Path.cwd()  # pasta do trabalho: fontes/, marca/, fotos/ (troque com usar_pasta)

PERFIL_CMYK = '/System/Library/ColorSync/Profiles/Generic CMYK Profile.icc'
PERFIL_SRGB = '/System/Library/ColorSync/Profiles/sRGB Profile.icc'


def usar_pasta(pasta) -> None:
    """Define a pasta do trabalho (onde estão fontes/, marca/, fotos/)."""
    global BASE
    BASE = Path(pasta).resolve()


def _arquivo(nome, sub: str) -> Path:
    p = Path(nome)
    return p if p.is_absolute() else BASE / sub / nome


# ── formatos e papéis ────────────────────────────────────────────────────────
FORMATOS = {
    # nome: (largura, altura) em mm, retrato. Os mais pedidos em gráficas no Brasil.
    'A6': (105, 148),
    'A5': (148, 210),
    'A4': (210, 297),
    'A3': (297, 420),
    '10x14': (100, 140),
    '10x15': (100, 150),
    '15x21': (150, 210),
    '20x28': (200, 280),
    'DL': (99, 210),          # 1/3 de A4 (cabe em envelope DL)
    'quadrado-15': (150, 150),
    'quadrado-21': (210, 210),
    'cartao': (90, 50),       # cartão de visita (paisagem)
}

PAPEIS = {
    # registro ICC (color.org) da condição de impressão + limite de tinta recomendado
    'couche': dict(nome='Couché (brilho ou fosco)', id='FOGRA39',
                   condicao='Coated FOGRA39 (ISO 12647-2:2004)', tac=300),
    'offset': dict(nome='Offset / não revestido (sulfite, reciclado)', id='FOGRA29',
                   condicao='Uncoated FOGRA29 (ISO 12647-2:2004)', tac=280),
}


def formato(nome_ou_medidas, orientacao: str = 'retrato') -> tuple[float, float]:
    """'A5' | '10x15' | (120, 180) → (largura, altura) em mm na orientação pedida."""
    if isinstance(nome_ou_medidas, str):
        if nome_ou_medidas not in FORMATOS:
            raise ValueError(f'formato desconhecido: {nome_ou_medidas}. Use {list(FORMATOS)} '
                             'ou (largura, altura) em mm.')
        l, a = FORMATOS[nome_ou_medidas]
    else:
        l, a = nome_ou_medidas
    if orientacao == 'paisagem' and l < a or orientacao == 'retrato' and l > a:
        l, a = a, l
    return float(l), float(a)


# ── cores ───────────────────────────────────────────────────────────────────
_CONV = []


def _cmyk_para_srgb():
    """Transformação CMYK→sRGB com o perfil CMYK do sistema (cacheada); None se faltar."""
    if not _CONV:
        try:
            from PIL import ImageCms
            t = ImageCms.buildTransform(ImageCms.getOpenProfile(PERFIL_CMYK),
                                        ImageCms.createProfile('sRGB'), 'CMYK', 'RGB',
                                        renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)
            _CONV.append(lambda im: ImageCms.applyTransform(im, t))
        except Exception:  # sem perfil (Linux/Windows) ou sem LittleCMS
            _CONV.append(None)
    return _CONV[0]


@dataclass(frozen=True)
class Cmyk:
    """Cor de processo (CMYK 0–100) ou cor especial (spot='PANTONE 186 C'),
    caso em que c/m/y/k é a alternativa CMYK usada na prova e em quem não tem a tinta."""
    nome: str
    c: float
    m: float
    y: float
    k: float
    tela: str | None = None  # prévia sRGB calibrada; senão, aproxima
    spot: str | None = None

    @property
    def rgb_tela(self) -> str:
        """Prévia sRGB: `tela` se informado; senão, conversão pelo perfil CMYK do sistema
        (fiel ao impresso); sem o perfil, uma aproximação simples."""
        if self.tela:
            return self.tela.lower()
        conv = _cmyk_para_srgb()
        if conv:
            im = Image.new('CMYK', (1, 1), tuple(round(v * 2.55) for v in
                                                 (self.c, self.m, self.y, self.k)))
            return '#%02x%02x%02x' % conv(im).getpixel((0, 0))
        r = 255 * (1 - self.c / 100) * (1 - self.k / 100)
        g = 255 * (1 - self.m / 100) * (1 - self.k / 100)
        b = 255 * (1 - self.y / 100) * (1 - self.k / 100)
        return '#%02x%02x%02x' % (round(r), round(g), round(b))

    @property
    def tac(self) -> float:
        return self.c + self.m + self.y + self.k

    def svg(self) -> str:
        return (f'{self.rgb_tela} icc-color(FOGRA39, {self.c/100:.2f}, {self.m/100:.2f}, '
                f'{self.y/100:.2f}, {self.k/100:.2f})')

    @property
    def rotulo(self) -> str:
        f = lambda v: f'{v:g}'
        base = f'C{f(self.c)} M{f(self.m)} Y{f(self.y)} K{f(self.k)}'
        return f'{self.spot} (alternativa {base})' if self.spot else base

    def mistura(self, outra: 'Cmyk', t: float, nome: str = '') -> 'Cmyk':
        """Cor intermediária (processo) entre esta e outra, t de 0 a 1."""
        v = [a + (b - a) * t for a, b in zip((self.c, self.m, self.y, self.k),
                                             (outra.c, outra.m, outra.y, outra.k))]
        return Cmyk(nome or f'{self.nome}~{outra.nome}', *v)


@dataclass
class Degrade:
    """Degradê CMYK. Coordenadas em mm no sistema da Arte (canto da sangria).
    linear: inicio=(x, y), fim=(x, y). radial: centro=(x, y), raio=r.
    paradas: [(posição 0–1, Cmyk), ...] — só cores de processo."""
    paradas: list
    tipo: str = 'linear'
    inicio: tuple = (0.0, 0.0)
    fim: tuple = (0.0, 100.0)
    centro: tuple = (0.0, 0.0)
    raio: float = 50.0
    nome: str = 'degrade'

    def __post_init__(self):
        for _, cor in self.paradas:
            if cor.spot:
                raise ValueError('degradê só com cores de processo (CMYK), não com spot')

    def deslocar(self, dx: float, dy: float) -> 'Degrade':
        return Degrade(self.paradas, self.tipo,
                       (self.inicio[0] + dx, self.inicio[1] + dy),
                       (self.fim[0] + dx, self.fim[1] + dy),
                       (self.centro[0] + dx, self.centro[1] + dy), self.raio, self.nome)


# ── acabamentos especiais ───────────────────────────────────────────────────
ACABAMENTOS = {
    # tipo: (nome para a gráfica, cor de simulação na prévia, opacidade na prévia)
    'verniz-uv': ('Verniz UV localizado', '#7fd6ff', 0.45),
    'hot-stamping': ('Hot stamping (metalizado)', '#d4af37', 0.95),
    'relevo': ('Relevo seco', '#9a9a9a', 0.35),
    'branco': ('Tinta branca', '#ffffff', 0.9),
    'faca': ('Faca especial (linha de corte)', '#ff00ff', 1.0),
}


# ── fontes e texto em curvas ────────────────────────────────────────────────
class Fonte:
    """Fonte TTF/OTF/WOFF2 ou face de uma coleção .ttc (indice)."""

    def __init__(self, arquivo, indice: int = 0):
        caminho = _arquivo(arquivo, 'fontes')
        dados = caminho.read_bytes()
        if str(caminho).lower().endswith('.ttc'):
            self.tt = TTCollection(str(caminho)).fonts[indice]
            buf = io.BytesIO()
            self.tt.save(buf)
            dados = buf.getvalue()
            self.tt = TTFont(io.BytesIO(dados))
        else:
            self.tt = TTFont(str(caminho))
            if str(caminho).lower().endswith('.woff2'):
                buf = io.BytesIO()
                self.tt.flavor = None
                self.tt.save(buf)
                dados = buf.getvalue()
                self.tt = TTFont(io.BytesIO(dados))
        self.hb_font = hb.Font(hb.Face(hb.Blob(dados)))
        self.upm = self.tt['head'].unitsPerEm
        self.glyphs = self.tt.getGlyphSet()
        self.ordem = self.tt.getGlyphOrder()
        self.nome = f'{caminho.name}#{indice}'

    @staticmethod
    def faces(arquivo) -> list[tuple[int, str, str]]:
        """Lista (índice, família, estilo) das faces de um .ttc/.ttf — para escolher a certa."""
        caminho = _arquivo(arquivo, 'fontes')
        fts = TTCollection(str(caminho)).fonts if str(caminho).lower().endswith('.ttc') \
            else [TTFont(str(caminho))]
        out = []
        for i, f in enumerate(fts):
            n = f['name']
            fam = n.getDebugName(16) or n.getDebugName(1)
            est = n.getDebugName(17) or n.getDebugName(2)
            out.append((i, fam, est))
        return out

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
        if any(g == '.notdef' for g, _, _ in saida):
            raise ValueError(f'a fonte {self.nome} não tem glifo para algum caractere de {texto!r}')
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


# ── fotos: preparo em CMYK com efeitos ──────────────────────────────────────
def _sips(origem: Path, perfil: str, destino: Path):
    if sys.platform != 'darwin':
        raise RuntimeError('Conversão de cor da foto usa o `sips` do macOS. Em Linux/Windows, '
                           'troque _sips por PIL.ImageCms ou ImageMagick (veja o README).')
    subprocess.run(['sips', '-m', perfil, str(origem), '--out', str(destino)],
                   check=True, capture_output=True)


def limitar_tac(arr: np.ndarray, tac: float) -> np.ndarray:
    """arr: CMYK float 0–1 (h, w, 4). Reduz C, M e Y proporcionalmente onde a soma passa
    do limite (o K é preservado: mantém o contraste e o preto)."""
    lim = tac / 100
    soma = arr.sum(axis=2)
    k = arr[..., 3]
    cmy = arr[..., :3].sum(axis=2)
    excesso = soma > lim
    fator = np.ones_like(soma)
    fator[excesso] = np.clip((lim - k[excesso]) / np.maximum(cmy[excesso], 1e-6), 0, 1)
    out = arr.copy()
    out[..., :3] *= fator[..., None]
    return out


def _vetor(cor: Cmyk) -> np.ndarray:
    return np.array([cor.c, cor.m, cor.y, cor.k], dtype=np.float32) / 100


def preparar_foto(arquivo: Path, w_mm: float, h_mm: float, efeitos=None, tac: float = 300,
                  dpi: int = 350, cache: Path | None = None):
    """Recorta (cover) na proporção do quadro, reduz/amplia a `dpi`, converte para CMYK,
    aplica efeitos e o limite de tinta. Devolve (TIFF CMYK, JPEG de prévia sRGB, ppi
    efetivo da origem no tamanho de uso).

    efeitos: lista de tuplas
      ('duotone', cor_escura, cor_clara)          — foto em 2 cores da marca
      ('escurecer', cor, intensidade 0–1)         — vela a foto em direção a uma cor
      ('fade', lado, cor, inicio 0–1, fim 0–1)    — funde a foto numa cor sólida; lado:
                                                     'baixo'|'cima'|'esquerda'|'direita'
    """
    arquivo = Path(arquivo)
    efeitos = efeitos or []
    chave = hashlib.sha1(repr((str(arquivo.resolve()), arquivo.stat().st_mtime, w_mm, h_mm,
                               [tuple(str(x) for x in e) for e in efeitos], tac, dpi))
                         .encode()).hexdigest()[:12]
    cache = Path(cache or BASE / '.cache')
    cache.mkdir(parents=True, exist_ok=True)
    tif, jpg = cache / f'{arquivo.stem}-{chave}.tif', cache / f'{arquivo.stem}-{chave}.jpg'
    im = Image.open(arquivo).convert('RGB')
    alvo = w_mm / h_mm
    W, H = im.size
    if W / H > alvo:
        nw = round(H * alvo)
        im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
    else:
        nh = round(W / alvo)
        im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
    ppi_origem = im.size[0] / (w_mm / 25.4)
    if tif.exists() and jpg.exists():
        return tif, jpg, ppi_origem
    px = round(w_mm / 25.4 * dpi)
    im = im.resize((px, max(1, round(px / alvo))), Image.LANCZOS)

    with tempfile.TemporaryDirectory() as tmp:
        rgb, cm = Path(tmp) / 'rgb.tif', Path(tmp) / 'cmyk.tif'
        im.save(rgb)
        _sips(rgb, PERFIL_CMYK, cm)
        c = Image.open(cm)
        c.load()
    arr = np.asarray(c, dtype=np.float32) / 255  # (h, w, 4)
    lum = np.asarray(im.convert('L'), dtype=np.float32) / 255
    h, w = lum.shape
    for ef in efeitos:
        if ef[0] == 'duotone':
            a, b = _vetor(ef[1]), _vetor(ef[2])
            arr = a + (b - a) * lum[..., None]
        elif ef[0] == 'escurecer':
            arr = arr + (_vetor(ef[1]) - arr) * float(ef[2])
        elif ef[0] == 'fade':
            _, lado, cor, ini, fim = ef
            eixo = np.linspace(0, 1, h if lado in ('baixo', 'cima') else w, dtype=np.float32)
            if lado in ('cima', 'esquerda'):
                eixo = eixo[::-1]
            t = np.clip((eixo - ini) / max(fim - ini, 1e-6), 0, 1)
            t = t * t * (3 - 2 * t)  # transição suave (smoothstep)
            t = t[:, None] if lado in ('baixo', 'cima') else t[None, :]
            arr = arr + (_vetor(cor) - arr) * t[..., None]
        else:
            raise ValueError(f'efeito desconhecido: {ef[0]}')
    arr = limitar_tac(np.clip(arr, 0, 1), tac)
    out = Image.fromarray((arr * 255 + 0.5).astype(np.uint8), 'CMYK')
    out.save(tif, compression='tiff_lzw')
    with tempfile.TemporaryDirectory() as tmp:
        srgb = Path(tmp) / 'srgb.tif'
        _sips(tif, PERFIL_SRGB, srgb)
        Image.open(srgb).convert('RGB').save(jpg, quality=88)
    return tif, jpg, ppi_origem


# ── a arte ──────────────────────────────────────────────────────────────────
class Arte:
    """Uma face do impresso. Coordenadas em mm a partir do canto da SANGRIA."""

    def __init__(self, largura_mm: float, altura_mm: float, sangria_mm: float = 3.0,
                 titulo: str = '', papel: str = 'couche'):
        if papel not in PAPEIS:
            raise ValueError(f'papel desconhecido: {papel}. Use {list(PAPEIS)}')
        self.l, self.a, self.s = largura_mm, altura_mm, sangria_mm
        self.titulo = titulo
        self.papel = papel
        self.el: list[str] = []
        self.ops: list[tuple] = []        # lista de desenho para o motor PDF
        self.defs: list[str] = []
        self.cores: dict[str, Cmyk] = {}
        self.camadas: dict[str, dict] = {}  # acabamentos: tipo → {'el': [], 'ops': []}
        self.avisos: list[str] = []
        self._acab: str | None = None
        self._n = 0

    @property
    def L(self):
        return self.l + 2 * self.s

    @property
    def A(self):
        return self.a + 2 * self.s

    def _id(self, pref='i'):
        self._n += 1
        return f'{pref}{self._n}'

    # ── acabamentos: tudo desenhado dentro do bloco vai para a máscara do acabamento ──
    @contextmanager
    def acabamento(self, tipo: str):
        """with arte.acabamento('verniz-uv'): ...  — as formas desenhadas aqui não entram
        na arte CMYK; viram a máscara do acabamento (PDF separado, K100)."""
        if tipo not in ACABAMENTOS:
            raise ValueError(f'acabamento desconhecido: {tipo}. Use {list(ACABAMENTOS)}')
        cam = self.camadas.setdefault(tipo, {'el': [], 'ops': []})
        antes = self.el, self.ops, self._acab
        self.el, self.ops, self._acab = cam['el'], cam['ops'], tipo
        try:
            yield
        finally:
            self.el, self.ops, self._acab = antes

    # ── pintura ──
    def _sim(self) -> Cmyk:
        nome, tela, _ = ACABAMENTOS[self._acab]
        return Cmyk(f'[{nome}]', 0, 0, 0, 100, tela)

    def _fill_svg(self, fill) -> tuple[str, str]:
        if isinstance(fill, Degrade):
            gid = self._id('g')
            stops = ''.join(
                f'<stop offset="{p:.4f}" stop-color="{c.rgb_tela}" '
                f'style="stop-color:{c.svg()}"/>' for p, c in fill.paradas)
            for _, c in fill.paradas:
                self.cores[c.nome] = c
            if fill.tipo == 'linear':
                (x0, y0), (x1, y1) = fill.inicio, fill.fim
                self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                                 f'x1="{x0:.3f}" y1="{y0:.3f}" x2="{x1:.3f}" y2="{y1:.3f}">'
                                 f'{stops}</linearGradient>')
            else:
                cx, cy = fill.centro
                self.defs.append(f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" '
                                 f'cx="{cx:.3f}" cy="{cy:.3f}" r="{fill.raio:.3f}">'
                                 f'{stops}</radialGradient>')
            return f'url(#{gid})', ''
        self.cores[fill.nome] = fill
        return fill.rgb_tela, f'fill:{fill.svg()}'

    def _pinta(self, fill=None, stroke: Cmyk | None = None) -> str:
        if self._acab:  # na prévia, o acabamento aparece com a cor de simulação
            fill = self._sim() if fill is not None else None
            stroke = self._sim() if stroke is not None else None
        attrs, estilo = [], []
        if fill is None:
            attrs.append('fill="none"')
        else:
            v, st = self._fill_svg(fill)
            attrs.append(f'fill="{v}"')
            if st:
                estilo.append(st)
        if stroke is not None:
            self.cores[stroke.nome] = stroke
            attrs.append(f'stroke="{stroke.rgb_tela}"')
            estilo.append(f'stroke:{stroke.svg()}')
        if estilo:
            attrs.append(f'style="{";".join(estilo)}"')
        return ' '.join(attrs)

    # ── primitivas ──
    def ret(self, x, y, w, h, cor=None, r=0.0, traco: Cmyk | None = None,
            traco_mm=0.0, tracejado: str | None = None):
        """Retângulo (cor = Cmyk, Degrade ou None)."""
        self.ops.append(('ret', x, y, w, h, cor, r, traco, traco_mm, tracejado))
        attrs = [f'x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}"']
        if r:
            attrs.append(f'rx="{r:.3f}"')
        attrs.append(self._pinta(cor, traco))
        if traco:
            attrs.append(f'stroke-width="{traco_mm:.3f}"')
            if tracejado:
                attrs.append(f'stroke-dasharray="{tracejado}"')
        self.el.append(f'<rect {" ".join(attrs)}/>')

    def circulo(self, cx, cy, r, cor=None, traco: Cmyk | None = None, traco_mm=0.0):
        self.ops.append(('circ', cx, cy, r, cor, traco, traco_mm))
        t = f' stroke-width="{traco_mm:.3f}"' if traco else ''
        self.el.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" '
                       f'{self._pinta(cor, traco)}{t}/>')

    def linha(self, x1, y1, x2, y2, cor: Cmyk, esp_mm=0.25, tracejado: str | None = None):
        self.ops.append(('linha', x1, y1, x2, y2, cor, esp_mm, tracejado))
        d = f' stroke-dasharray="{tracejado}"' if tracejado else ''
        self.el.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
                       f'{self._pinta(None, cor)} stroke-width="{esp_mm:.3f}"{d}/>')

    def forma(self, d: str, cor=None, traco: Cmyk | None = None, traco_mm=0.0):
        """Qualquer forma vetorial: `d` no formato de path SVG, em mm (sistema da Arte)."""
        self.ops.append(('forma', d, cor, traco, traco_mm))
        t = f' stroke-width="{traco_mm:.3f}" stroke-linejoin="round"' if traco else ''
        self.el.append(f'<path d="{d}" {self._pinta(cor, traco)}{t}/>')

    def texto(self, fonte: Fonte, txt: str, x, y, tam_pt: float, cor,
              ancora: str = 'inicio', rastreio_em: float = 0.0, caixa_alta=False,
              contorno: tuple | None = None, sombra: tuple | None = None) -> float:
        """Uma linha de texto em curvas (y = linha de base). cor = Cmyk ou Degrade.
        contorno=(Cmyk, espessura_mm) — traço por fora do texto;
        sombra=(dx_mm, dy_mm, Cmyk) — sombra sólida deslocada (vetorial, sem transparência).
        Retorna a largura em mm."""
        if caixa_alta:
            txt = txt.upper()
        w = fonte.largura(txt, tam_pt, rastreio_em)
        if ancora == 'meio':
            x -= w / 2
        elif ancora == 'fim':
            x -= w
        if sombra:
            dx, dy, cs = sombra
            self.ops.append(('texto', fonte, txt, x + dx, y + dy, tam_pt, rastreio_em, cs, None))
            d = fonte.caminho(txt, x + dx, y + dy, tam_pt, rastreio_em)
            self.el.append(f'<path d="{d}" {self._pinta(cs)}/>')
        if contorno:
            # contorno por fora: traço com o dobro da espessura, atrás do preenchimento
            cc, esp = contorno
            self.ops.append(('texto', fonte, txt, x, y, tam_pt, rastreio_em, None, (cc, esp * 2)))
            d = fonte.caminho(txt, x, y, tam_pt, rastreio_em)
            self.el.append(f'<path d="{d}" {self._pinta(None, cc)} stroke-width="{esp*2:.3f}" '
                           f'stroke-linejoin="round"/>')
        self.ops.append(('texto', fonte, txt, x, y, tam_pt, rastreio_em, cor, None))
        d = fonte.caminho(txt, x, y, tam_pt, rastreio_em)
        if d:
            self.el.append(f'<path d="{d}" {self._pinta(cor)} aria-label="{esc(txt)}"/>')
        return w

    def paragrafo(self, fonte: Fonte, txt: str, x, y, tam_pt: float, cor,
                  largura_mm: float, entrelinha: float = 1.32, ancora='inicio',
                  rastreio_em: float = 0.0, max_linhas: int | None = None) -> float:
        """Texto com quebra. y = linha de base da 1ª linha. Retorna y da próxima linha."""
        passo = tam_pt * PT * entrelinha
        linhas = quebrar(fonte, txt, tam_pt, largura_mm, rastreio_em)
        if max_linhas and len(linhas) > max_linhas:
            raise ValueError(f'parágrafo passa de {max_linhas} linhas ({len(linhas)}): {txt!r}')
        for i, ln in enumerate(linhas):
            self.texto(fonte, ln, x, y + i * passo, tam_pt, cor, ancora, rastreio_em)
        return y + len(linhas) * passo

    def qr(self, url: str, x, y, lado_mm: float, cor: Cmyk, fundo: Cmyk | None = None):
        """QR vetorial (correção M, zona de silêncio de 4 módulos dentro do lado)."""
        q = segno.make(url, error='m', micro=False)
        matriz = list(q.matrix)
        n = len(matriz)
        borda = 4
        m = lado_mm / (n + 2 * borda)
        if m < 0.4:
            self.avisos.append(f'QR {url}: módulo de {m:.2f} mm (< 0,4 mm) — aumente o QR '
                               'ou encurte a URL')
        if fundo:
            self.ret(x, y, lado_mm, lado_mm, fundo, r=0.8)
        partes, modulos = [], []
        for i, linha in enumerate(matriz):
            for j, v in enumerate(linha):
                if v:
                    px, py = x + (j + borda) * m, y + (i + borda) * m
                    partes.append(f'M{px:.3f},{py:.3f}h{m:.3f}v{m:.3f}h{-m:.3f}z')
                    modulos.append((px, py))
        self.ops.append(('qr', modulos, m, cor, url))
        self.el.append(f'<path d="{"".join(partes)}" {self._pinta(cor)} '
                       f'shape-rendering="crispEdges" aria-label="QR {esc(url)}"/>')

    def logo(self, arquivo: str, x, y, largura_mm: float, cores: dict):
        """SVG vetorial da marca, trocando cada fill hex pela cor dada. Mapeie todos os
        hex do arquivo, e só eles. Retorna a altura em mm."""
        src = _arquivo(arquivo, 'marca').read_text()
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
        corpo = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', src, flags=re.S)
        corpo = re.sub(r'<title>.*?</title>|<!--.*?-->', '', corpo, flags=re.S)
        existentes = {h.lower() for h in re.findall(r'fill="(#[0-9a-fA-F]{6})"', corpo)}
        faltam = existentes - {h.lower() for h in cores}
        if faltam:
            raise ValueError(f'{arquivo}: cores sem CMYK definido: {sorted(faltam)}')
        marcas = {}
        for i, (hexa, cmyk) in enumerate(cores.items()):
            marca = f'@@COR{i}@@'
            corpo = re.sub(f'fill="{hexa}"', marca, corpo, flags=re.I)
            marcas[marca] = cmyk
        for marca, cmyk in marcas.items():  # em 2 passos: evita troca em cascata
            corpo = corpo.replace(marca, self._pinta(cmyk))
        esc_ = largura_mm / vb[2]
        self.ops.append(('logo', arquivo, x, y, esc_, dict(cores)))
        self.el.append(f'<g transform="translate({x:.3f},{y:.3f}) scale({esc_:.6f}) '
                       f'translate({-vb[0]},{-vb[1]})" aria-label="logo">{corpo}</g>')
        return vb[3] * esc_

    def imagem(self, arquivo, x, y, w, h, r=0.0, efeitos=None, dpi: int = 350):
        """Foto/imagem raster no quadro (corte 'cover'), convertida para CMYK com efeitos
        (ver preparar_foto). A prévia SVG usa a versão CMYK convertida de volta para sRGB."""
        tac = PAPEIS[self.papel]['tac']
        tif, jpg, ppi = preparar_foto(_arquivo(arquivo, 'fotos'), w, h, efeitos, tac, dpi)
        if ppi < 200:
            self.avisos.append(f'{Path(arquivo).name}: {ppi:.0f} ppi efetivos no tamanho '
                               f'{w:.0f}×{h:.0f} mm (ideal ≥ 300; < 200 pode sair borrado)')
        self.ops.append(('img', tif, x, y, w, h, r))
        clip = ''
        if r:
            cid = self._id('c')
            self.defs.append(f'<clipPath id="{cid}"><rect x="{x:.3f}" y="{y:.3f}" '
                             f'width="{w:.3f}" height="{h:.3f}" rx="{r:.3f}"/></clipPath>')
            clip = f' clip-path="url(#{cid})"'
        dados = base64.b64encode(jpg.read_bytes()).decode()
        self.el.append(f'<image href="data:image/jpeg;base64,{dados}" x="{x:.3f}" y="{y:.3f}" '
                       f'width="{w:.3f}" height="{h:.3f}" preserveAspectRatio="none"{clip}/>')

    def icone(self, nome: str, x, y, tam: float, cor: Cmyk):
        """Ícone de traço (desenho 24×24 de _ICONES) em tam×tam mm, canto sup. esq. (x, y)."""
        cor_svg = self._sim() if self._acab else cor
        self.cores[cor_svg.nome] = cor_svg
        self.ops.append(('icone', nome, x, y, tam, cor))
        self.el.append(
            f'<g transform="translate({x:.3f},{y:.3f}) scale({tam/24:.5f})" '
            f'stroke="{cor_svg.rgb_tela}" fill="{cor_svg.rgb_tela}" '
            f'style="stroke:{cor_svg.svg()};fill:{cor_svg.svg()}" aria-label="ícone {nome}">'
            f'{_ICONES[nome]}</g>')

    # ── saída ──
    def svg(self, guias: bool = False, simular_acabamentos: bool = False) -> str:
        """SVG da face. As camadas de acabamento vão como camadas do Inkscape ocultas;
        com simular_acabamentos=True, aparecem por cima (prévia para o cliente)."""
        amostras = '\n'.join(f'    <!-- {c.nome}: {c.rotulo} (tela {c.rgb_tela}) -->'
                             for c in self.cores.values())
        camadas = ''
        for tipo, cam in self.camadas.items():
            nome, _, opac = ACABAMENTOS[tipo]
            vis = f'opacity="{opac}"' if simular_acabamentos else 'style="display:none"'
            camadas += (f'<g id="acabamento-{tipo}" inkscape:groupmode="layer" '
                        f'inkscape:label="ACABAMENTO: {esc(nome)}" {vis}>{"".join(cam["el"])}</g>')
        extra = ''
        if guias:
            extra = (f'<g id="guias" fill="none" stroke="#00b7ff" stroke-width="0.15">'
                     f'<rect x="{self.s}" y="{self.s}" width="{self.l}" height="{self.a}"/>'
                     f'<rect x="{self.s+5}" y="{self.s+5}" width="{self.l-10}" '
                     f'height="{self.a-10}" stroke-dasharray="1 1"/></g>')
        papel = PAPEIS[self.papel]
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     version="1.1" width="{self.L:g}mm" height="{self.A:g}mm" viewBox="0 0 {self.L:g} {self.A:g}">
  <title>{esc(self.titulo)}</title>
  <desc>Arte de impressão. Formato final {self.l:g}×{self.a:g} mm + sangria de {self.s:g} mm
  ({self.L:g}×{self.A:g} mm). Texto em curvas. Cores em CMYK ({papel["condicao"]}) via
  icc-color; o hexadecimal é só a prévia de tela. O arquivo para a gráfica é o PDF.</desc>
  <defs>
    <color-profile name="FOGRA39" local="Coated FOGRA39" xlink:href="CoatedFOGRA39.icc"/>
{amostras}
    {''.join(self.defs)}
  </defs>
  <g id="arte" inkscape:groupmode="layer" inkscape:label="ARTE (CMYK)">{''.join(self.el)}</g>
  {camadas}
  {extra}
</svg>
'''


def esc(s: str) -> str:
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


# ícones de traço desenhados num quadrado 24×24
_ICONES = {
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6"/>',
    'pino': '<path d="M12 21.5s-7-6.4-7-12a7 7 0 0 1 14 0c0 5.6-7 12-7 12z" fill="none" stroke-width="2"/><circle cx="12" cy="9.5" r="2.6" fill="none" stroke-width="2"/>',
    'relogio': '<circle cx="12" cy="12" r="9" fill="none" stroke-width="2"/><path d="M12 7v5.2l3.4 2.2" fill="none" stroke-linecap="round" stroke-width="2"/>',
    'balao': '<path d="M4 18.5l1.3-3.8A8 8 0 1 1 8.6 18z" fill="none" stroke-linejoin="round" stroke-width="2"/>',
    'tesoura': '<circle cx="6" cy="7" r="3" fill="none" stroke-width="1.8"/><circle cx="6" cy="17" r="3" fill="none" stroke-width="1.8"/><path d="M8.6 8.6L20 18M8.6 15.4L20 6" fill="none" stroke-linecap="round" stroke-width="1.8"/>',
    'presente': '<rect x="3.5" y="9" width="17" height="11.5" rx="1" fill="none" stroke-width="2"/><path d="M12 9v11.5M3.5 13h17M12 9c-1.8-4-6-4-6-1.2S12 9 12 9s6 .9 6-1.8S13.8 5 12 9" fill="none" stroke-width="2" stroke-linejoin="round"/>',
    'qr': '<rect x="3" y="3" width="7" height="7" rx="1" fill="none" stroke-width="2"/><rect x="14" y="3" width="7" height="7" rx="1" fill="none" stroke-width="2"/><rect x="3" y="14" width="7" height="7" rx="1" fill="none" stroke-width="2"/><path d="M14 14h3v3h-3zM18 18h3v3h-3z"/>',
    'seta': '<path d="M5 12h13M13 6.5l5.5 5.5-5.5 5.5" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.4"/>',
    'ciclo': '<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3" fill="none" stroke-linecap="round" stroke-width="2.2"/><path d="M18.6 2.8l.2 4.6-4.6.2" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2"/>',
    'calendario': '<rect x="3.5" y="5" width="17" height="15.5" rx="1.5" fill="none" stroke-width="2"/><path d="M3.5 10h17M8 3v4M16 3v4" fill="none" stroke-linecap="round" stroke-width="2"/>',
    'telefone': '<path d="M6.6 3.5l3 .5 1.4 4-2 1.6a12 12 0 0 0 5.4 5.4l1.6-2 4 1.4.5 3c0 1.1-.9 2-2 2A17 17 0 0 1 4.6 5.5c0-1.1.9-2 2-2z" fill="none" stroke-linejoin="round" stroke-width="2"/>',
    'estrela': '<path d="M12 3.2l2.7 5.6 6.1.8-4.5 4.2 1.1 6-5.4-2.9-5.4 2.9 1.1-6-4.5-4.2 6.1-.8z" fill="none" stroke-linejoin="round" stroke-width="2"/>',
    'raio': '<path d="M13.5 2.5L5 13.5h6l-1.5 8 8.5-11h-6z" fill="none" stroke-linejoin="round" stroke-width="2"/>',
    'haltere': '<path d="M2.5 12h19M6 7.5v9M18 7.5v9M3.5 9.5v5M20.5 9.5v5" fill="none" stroke-linecap="round" stroke-width="2.2"/>',
    'instagram': '<rect x="3.5" y="3.5" width="17" height="17" rx="5" fill="none" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke-width="2"/><circle cx="17.2" cy="6.8" r="1.1"/>',
    'site': '<circle cx="12" cy="12" r="9" fill="none" stroke-width="2"/><path d="M3 12h18M12 3c2.6 2.6 3.8 5.6 3.8 9s-1.2 6.4-3.8 9c-2.6-2.6-3.8-5.6-3.8-9S9.4 5.6 12 3z" fill="none" stroke-width="2"/>',
}
